"""
File Storage Version Management API
Saves files to filesystem instead of database BLOB
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
import pymysql
import os
import hashlib
import json
import uuid
from contextlib import contextmanager
import logging
import io
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="File Storage Version Management API",
    description="Version management with file system storage",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.environ.get('API_KEY', 'nexa_internal_app_key_2025')
UPLOAD_DIR = Path("./uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

# API Key verification middleware
@app.middleware("http")
async def verify_api_key_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    if request.method == "OPTIONS":
        return await call_next(request)
    
    if request.url.path.startswith("/api/"):
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "API Key missing or invalid"}
            )
    
    response = await call_next(request)
    return response

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQL_PORT', 20671)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'),
    'database': os.environ.get('MYSQL_DATABASE', 'railway'),
    'charset': 'utf8mb4'
}

# Database connection manager
@contextmanager
def get_db():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()

# Helper to save file to disk
def save_file_to_disk(app_id: int, version: str, platform: str, file_content: bytes, filename: str) -> str:
    """Save file to disk and return the file path"""
    # Create directory structure: uploaded_files/app_id/platform/
    app_dir = UPLOAD_DIR / str(app_id) / platform
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(filename).suffix
    safe_version = version.replace(".", "_").replace(" ", "_")
    file_path = app_dir / f"{safe_version}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return str(file_path.relative_to(UPLOAD_DIR))

# Helper to get app ID
def get_app_id(app_identifier: str, connection) -> Optional[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM apps WHERE app_identifier = %s",
            (app_identifier,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

# File Upload Endpoint
@app.post("/api/v3/version/upload")
async def upload_version(
    app_identifier: str = Form(...),
    version: str = Form(...),
    platform: str = Form(...),
    version_code: int = Form(...),
    is_mandatory: bool = Form(False),
    changelog: str = Form(None),
    file: UploadFile = File(...)
):
    """Upload new version with file system storage"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Validate file
        if platform == "android" and not file.filename.endswith('.apk'):
            raise HTTPException(status_code=400, detail="Android requires APK file")
        elif platform == "ios" and not file.filename.endswith('.ipa'):
            raise HTTPException(status_code=400, detail="iOS requires IPA file")
        
        # Read file
        file_content = await file.read()
        file_size = len(file_content)
        
        logger.info(f"Uploading file: {file.filename}, size: {file_size / (1024*1024):.2f}MB")
        
        # Calculate hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Save file to disk
        file_path = save_file_to_disk(app_id, version, platform, file_content, file.filename)
        logger.info(f"File saved to: {file_path}")
        
        # Parse changelog
        changelog_list = []
        if changelog:
            try:
                changelog_list = json.loads(changelog)
            except:
                changelog_list = [changelog]
        
        # Save metadata to database (without the file content)
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO app_versions 
                   (app_id, version, platform, version_code, file_path, file_name, 
                    file_size, file_hash, changelog, is_mandatory)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (app_id, version, platform, version_code, file_path, 
                 file.filename, file_size, file_hash,
                 json.dumps(changelog_list), is_mandatory)
            )
            connection.commit()
            
        return {
            "message": "Version uploaded successfully",
            "app": app_identifier,
            "version": version,
            "platform": platform,
            "file_size": file_size,
            "file_hash": file_hash,
            "file_path": file_path
        }

# Download endpoint
@app.get("/download/{app_identifier}/{platform}/{version}")
async def download_version(app_identifier: str, platform: str, version: str):
    """Download specific version file"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """SELECT file_path, file_name, file_size
                   FROM app_versions 
                   WHERE app_id = %s AND platform = %s AND version = %s 
                   AND is_active = true""",
                (app_id, platform, version)
            )
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Version not found")
            
            # Update download count
            cursor.execute(
                """UPDATE app_versions 
                   SET download_count = download_count + 1 
                   WHERE app_id = %s AND platform = %s AND version = %s""",
                (app_id, platform, version)
            )
            connection.commit()
        
        # Read file from disk
        file_path = UPLOAD_DIR / result['file_path']
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file_path,
            filename=result['file_name'],
            media_type='application/octet-stream'
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "3.0.0", "storage": "filesystem"}

if __name__ == "__main__":
    import uvicorn
    
    # Create required tables if they don't exist
    with get_db() as connection:
        with connection.cursor() as cursor:
            # Check if file_path column exists, if not alter table
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'app_versions' 
                AND COLUMN_NAME = 'file_path'
            """)
            if not cursor.fetchone():
                logger.info("Adding file_path column to app_versions table")
                cursor.execute("""
                    ALTER TABLE app_versions 
                    ADD COLUMN file_path VARCHAR(500) DEFAULT NULL
                """)
                connection.commit()
    
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)