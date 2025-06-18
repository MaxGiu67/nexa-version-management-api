#!/usr/bin/env python3
"""
Version Management API - Local Development Version
With better error handling and shorter timeouts
"""
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import hashlib
from contextlib import contextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import pymysql
import pymysql.cursors
from pymysql.err import OperationalError
import uvicorn
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv('.env.local')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration with shorter timeouts for local development
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'tramway.proxy.rlwy.net'),
    'port': int(os.getenv('MYSQL_PORT', '20671')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'railway'),
    'connect_timeout': 5,  # Reduced from 30
    'read_timeout': 5,     # Reduced from 30
    'write_timeout': 5,    # Reduced from 30
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

# API Configuration
API_KEY = os.getenv('API_KEY', 'nexa_internal_app_key_2025')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '500'))
ALLOWED_EXTENSIONS = {'.apk', '.ipa'}

# Create FastAPI app
app = FastAPI(
    title="Nexa Version Management API - Local",
    description="API for managing app versions with LOCAL development settings",
    version="2.0.0-local"
)

# CORS middleware - allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Database connection with better error handling
@contextmanager
def get_db():
    """Get database connection with timeout and error handling"""
    connection = None
    try:
        logger.info("Attempting database connection...")
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("Database connected successfully")
        yield connection
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        if "2013" in str(e) or "timeout" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="Database is not responding. It might be sleeping. Please try again in 1-2 minutes or check Railway dashboard."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database test"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": e.detail,
                "timestamp": datetime.now().isoformat()
            }
        )

# Test endpoint that doesn't require database
@app.get("/ping")
async def ping():
    """Simple ping endpoint that doesn't touch the database"""
    return {
        "message": "pong",
        "timestamp": datetime.now().isoformat(),
        "environment": "local"
    }

# Models
class App(BaseModel):
    id: Optional[int] = None
    name: str
    package_name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class AppVersion(BaseModel):
    id: Optional[int] = None
    app_id: int
    version: str
    version_code: int
    platform: str
    changelog: Optional[Dict[str, Any]] = None
    is_mandatory: bool = False
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    download_count: int = 0
    created_at: Optional[datetime] = None

# Apps endpoints
@app.get("/api/v2/apps", response_model=List[App])
async def list_apps(
    x_api_key: Optional[str] = Header(None)
):
    """List all registered apps"""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM apps ORDER BY name")
                apps = cursor.fetchall()
                return apps
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing apps: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/apps", response_model=App)
async def create_app(
    app: App,
    x_api_key: Optional[str] = Header(None)
):
    """Create a new app"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO apps (name, package_name, description)
                    VALUES (%s, %s, %s)
                """, (app.name, app.package_name, app.description))
                
                app.id = cursor.lastrowid
                app.created_at = datetime.now()
                return app
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Version check endpoint for mobile apps
@app.get("/api/v2/version/check")
async def check_version(
    app_name: str = Query(..., description="App name (e.g., 'nexa-timesheet')"),
    platform: str = Query(..., description="Platform: 'android' or 'ios'"),
    current_version: str = Query(..., description="Current app version")
):
    """Check if update is available for the app"""
    try:
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Get app info
                cursor.execute("""
                    SELECT id FROM apps WHERE name = %s
                """, (app_name,))
                app = cursor.fetchone()
                
                if not app:
                    return {
                        "update_available": False,
                        "message": "App not found"
                    }
                
                # Get latest version
                cursor.execute("""
                    SELECT version, version_code, is_mandatory, changelog
                    FROM app_versions
                    WHERE app_id = %s AND platform = %s AND is_active = 1
                    ORDER BY version_code DESC
                    LIMIT 1
                """, (app['id'], platform))
                
                latest = cursor.fetchone()
                
                if not latest:
                    return {
                        "update_available": False,
                        "message": "No versions available"
                    }
                
                # Simple version comparison
                update_available = latest['version'] != current_version
                
                return {
                    "update_available": update_available,
                    "latest_version": latest['version'],
                    "is_mandatory": latest['is_mandatory'],
                    "changelog": latest['changelog'] or {},
                    "download_url": f"/api/v2/download/{app_name}/{platform}/{latest['version']}"
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking version: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a startup event to test database connection
@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""
    logger.info("Starting up...")
    try:
        with get_db() as conn:
            logger.info("✅ Database connection successful on startup")
    except Exception as e:
        logger.error(f"⚠️  Database connection failed on startup: {e}")
        logger.error("The API will start anyway, but database operations will fail")

# Run the server
if __name__ == "__main__":
    port = int(os.getenv('PORT', '8000'))
    logger.info(f"Starting server on port {port}")
    logger.info(f"Database config: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    logger.info("Note: Using shorter timeouts for local development")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=True,  # Auto-reload on changes
        log_level="info"
    )