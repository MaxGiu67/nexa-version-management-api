#!/usr/bin/env python3
"""
Version Management API - PostgreSQL Version
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
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError
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

# PostgreSQL Configuration
DB_CONFIG = {
    'host': os.getenv('PGHOST', 'yamabiko.proxy.rlwy.net'),
    'port': int(os.getenv('PGPORT', '41888')),
    'user': os.getenv('PGUSER', 'postgres'),
    'password': os.getenv('PGPASSWORD', ''),
    'database': os.getenv('PGDATABASE', 'railway'),
    'connect_timeout': 10,
}

# API Configuration
API_KEY = os.getenv('API_KEY', 'nexa_internal_app_key_2025')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '500'))
ALLOWED_EXTENSIONS = {'.apk', '.ipa'}

# Create FastAPI app
app = FastAPI(
    title="Nexa Version Management API - PostgreSQL",
    description="API for managing app versions with PostgreSQL database",
    version="2.0.0-postgres"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Database connection
@contextmanager
def get_db():
    """Get PostgreSQL database connection"""
    connection = None
    try:
        logger.info("Attempting PostgreSQL connection...")
        connection = psycopg2.connect(**DB_CONFIG)
        connection.autocommit = True
        logger.info("PostgreSQL connected successfully")
        yield connection
    except OperationalError as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database is not responding. Please check PostgreSQL connection."
        )
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection:
            connection.close()
            logger.info("PostgreSQL connection closed")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database test"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
        return {
            "status": "healthy",
            "database": "connected",
            "db_type": "postgresql",
            "db_version": version[0] if version else "unknown",
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

# Test endpoint
@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {
        "message": "pong",
        "timestamp": datetime.now().isoformat(),
        "database": "postgresql"
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

# Initialize database tables
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    logger.info("Starting up PostgreSQL version...")
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Create apps table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS apps (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        package_name VARCHAR(255) UNIQUE NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create app_versions table with BYTEA for file storage
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_versions (
                        id SERIAL PRIMARY KEY,
                        app_id INTEGER NOT NULL REFERENCES apps(id),
                        version VARCHAR(50) NOT NULL,
                        version_code INTEGER NOT NULL,
                        platform VARCHAR(20) NOT NULL,
                        app_file BYTEA,
                        file_name VARCHAR(255),
                        file_size BIGINT,
                        file_hash VARCHAR(64),
                        changelog JSONB,
                        is_active BOOLEAN DEFAULT true,
                        is_mandatory BOOLEAN DEFAULT false,
                        download_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(app_id, platform, version)
                    )
                """)
                
                # Create indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_app_versions_app_platform 
                    ON app_versions(app_id, platform)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_app_versions_active 
                    ON app_versions(is_active, version_code)
                """)
                
                logger.info("✅ PostgreSQL tables initialized successfully")
                
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize database: {e}")

# Apps endpoints
@app.get("/api/v2/apps", response_model=List[App])
async def list_apps(
    x_api_key: Optional[str] = Header(None)
):
    """List all registered apps"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        with get_db() as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM apps ORDER BY name")
                apps = cursor.fetchall()
                return apps
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
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO apps (name, package_name, description)
                    VALUES (%s, %s, %s)
                    RETURNING id, created_at
                """, (app.name, app.package_name, app.description))
                
                result = cursor.fetchone()
                app.id = result['id']
                app.created_at = result['created_at']
                return app
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Upload version endpoint
@app.post("/api/v2/version/upload")
async def upload_version(
    app_name: str = Form(...),
    version: str = Form(...),
    version_code: int = Form(...),
    platform: str = Form(...),
    is_mandatory: bool = Form(False),
    changelog: Optional[str] = Form(None),
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """Upload a new app version"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Validate file
        if not file.filename.endswith(('.apk', '.ipa')):
            raise HTTPException(status_code=400, detail="Only APK and IPA files are allowed")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB")
        
        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Get or create app
                cursor.execute("SELECT id FROM apps WHERE name = %s", (app_name,))
                app = cursor.fetchone()
                
                if not app:
                    cursor.execute("""
                        INSERT INTO apps (name, package_name) 
                        VALUES (%s, %s) 
                        RETURNING id
                    """, (app_name, f"com.{app_name.replace('-', '.')}"))
                    app = cursor.fetchone()
                
                app_id = app[0]
                
                # Parse changelog
                changelog_json = None
                if changelog:
                    try:
                        changelog_json = json.dumps(json.loads(changelog))
                    except:
                        changelog_json = json.dumps({"en": [changelog]})
                
                # Insert version with file
                cursor.execute("""
                    INSERT INTO app_versions 
                    (app_id, version, version_code, platform, app_file, file_name, 
                     file_size, file_hash, changelog, is_mandatory)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (app_id, platform, version) 
                    DO UPDATE SET 
                        version_code = EXCLUDED.version_code,
                        app_file = EXCLUDED.app_file,
                        file_name = EXCLUDED.file_name,
                        file_size = EXCLUDED.file_size,
                        file_hash = EXCLUDED.file_hash,
                        changelog = EXCLUDED.changelog,
                        is_mandatory = EXCLUDED.is_mandatory
                    RETURNING id
                """, (app_id, version, version_code, platform, psycopg2.Binary(content), 
                      file.filename, file_size, file_hash, changelog_json, is_mandatory))
                
                version_id = cursor.fetchone()[0]
                
        return {
            "success": True,
            "message": "Version uploaded successfully",
            "version_id": version_id,
            "file_hash": file_hash,
            "file_size": file_size
        }
        
    except Exception as e:
        logger.error(f"Error uploading version: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    # Promemoria per l'utente
    print("\n⚠️  IMPORTANTE: Inserisci la password PostgreSQL nel file .env.local!")
    print("   Vai su Railway dashboard e copia PGPASSWORD")
    print(f"\n📊 Database config: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    port = int(os.getenv('PORT', '8000'))
    logger.info(f"Starting PostgreSQL server on port {port}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=True,
        log_level="info"
    )