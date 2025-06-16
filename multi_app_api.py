"""
Multi-App Version Management API with User Tracking and Error Reporting
Supports multiple applications, user analytics, and error monitoring
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-App Version Management API",
    description="Gestione versioni per multiple applicazioni con tracking utenti ed errori",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
API_KEY = os.environ.get('API_KEY', 'nexa_internal_app_key_2025')

# API Key verification middleware
@app.middleware("http")
async def verify_api_key_middleware(request: Request, call_next):
    # Exclude health check and docs
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Allow CORS preflight requests (OPTIONS method)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Verify API key for all API endpoints
    if request.url.path.startswith("/api/"):
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "API Key mancante o non valida"}
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

# Models
class App(BaseModel):
    app_identifier: str
    app_name: str
    description: Optional[str] = None
    platform_support: List[str] = ["android", "ios"]

class VersionCheck(BaseModel):
    app_identifier: str
    current_version: str
    platform: str
    user_uuid: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None

class UserSession(BaseModel):
    app_identifier: str
    user_uuid: str
    email: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    app_version: str

class ErrorReport(BaseModel):
    app_identifier: str
    user_uuid: Optional[str] = None
    error_type: str
    error_message: str
    error_stack: Optional[str] = None
    app_version: str
    platform: str
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[int] = None
    severity: str = "medium"

class UpdateStatus(BaseModel):
    app_identifier: str
    user_uuid: str
    from_version: str
    to_version: str
    status: str  # started, downloaded, installed, failed
    failure_reason: Optional[str] = None

# Database connection manager
@contextmanager
def get_db():
    """Database connection with increased limits for large files"""
    connection = pymysql.connect(
        **DB_CONFIG,
        connect_timeout=300,  # 5 minutes
        read_timeout=300,
        write_timeout=300
    )
    try:
        # Increase MySQL timeouts for large file uploads
        with connection.cursor() as cursor:
            try:
                # Only set timeouts, not max_allowed_packet (read-only)
                cursor.execute("SET SESSION net_read_timeout = 300")
                cursor.execute("SET SESSION net_write_timeout = 300")
                cursor.execute("SET SESSION wait_timeout = 300")
                cursor.execute("SET SESSION interactive_timeout = 300")
            except Exception as e:
                logger.warning(f"Could not set session variables: {e}")
        yield connection
    finally:
        connection.close()

# Helper functions
def get_app_id(app_identifier: str, connection) -> Optional[int]:
    """Get app ID from identifier"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM apps WHERE app_identifier = %s",
            (app_identifier,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_or_create_user(user_uuid: str, email: Optional[str], device_info: Optional[Dict], connection) -> int:
    """Get or create user and return user ID"""
    with connection.cursor() as cursor:
        # Check if user exists
        cursor.execute(
            "SELECT id FROM app_users WHERE user_uuid = %s",
            (user_uuid,)
        )
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            # Update last seen
            cursor.execute(
                "UPDATE app_users SET last_seen_at = NOW(), email = COALESCE(%s, email), device_info = %s WHERE id = %s",
                (email, json.dumps(device_info) if device_info else None, user_id)
            )
        else:
            # Create new user
            cursor.execute(
                """INSERT INTO app_users (user_uuid, email, device_info) 
                   VALUES (%s, %s, %s)""",
                (user_uuid, email, json.dumps(device_info) if device_info else None)
            )
            user_id = cursor.lastrowid
        
        connection.commit()
        return user_id

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "multi_app": True}

# App Management Endpoints
@app.post("/api/v2/apps")
async def create_app(app_data: App):
    """Create a new app in the system"""
    with get_db() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO apps (app_identifier, app_name, description, platform_support)
                       VALUES (%s, %s, %s, %s)""",
                    (app_data.app_identifier, app_data.app_name, app_data.description, 
                     json.dumps(app_data.platform_support))
                )
                connection.commit()
                return {"message": "App created successfully", "app_id": cursor.lastrowid}
        except pymysql.IntegrityError:
            raise HTTPException(status_code=400, detail="App identifier already exists")

@app.get("/api/v2/apps")
async def list_apps():
    """List all registered apps"""
    with get_db() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """SELECT id, app_identifier, app_name, description, platform_support,
                          is_active, created_at
                   FROM apps
                   ORDER BY app_name"""
            )
            apps = cursor.fetchall()
            for app in apps:
                app['platform_support'] = json.loads(app['platform_support'])
            return {"apps": apps}

@app.put("/api/v2/apps/{app_identifier}")
async def update_app(app_identifier: str, app_data: App):
    """Update an existing app"""
    with get_db() as connection:
        with connection.cursor() as cursor:
            # Check if app exists
            cursor.execute(
                "SELECT id FROM apps WHERE app_identifier = %s",
                (app_identifier,)
            )
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="App not found")
            
            app_id = result[0]
            
            # Update app
            cursor.execute(
                """UPDATE apps 
                   SET app_name = %s, description = %s, platform_support = %s, 
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = %s""",
                (app_data.app_name, app_data.description, 
                 json.dumps(app_data.platform_support), app_id)
            )
            connection.commit()
            
            return {"message": "App updated successfully", "app_identifier": app_identifier}

@app.delete("/api/v2/apps/{app_identifier}")
async def delete_app(app_identifier: str):
    """Delete an app and all its related data"""
    with get_db() as connection:
        with connection.cursor() as cursor:
            # Check if app exists
            cursor.execute(
                "SELECT id FROM apps WHERE app_identifier = %s",
                (app_identifier,)
            )
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="App not found")
            
            app_id = result[0]
            
            # Check if there are any versions
            cursor.execute(
                "SELECT COUNT(*) FROM app_versions WHERE app_id = %s",
                (app_id,)
            )
            version_count = cursor.fetchone()[0]
            
            # Delete the app (CASCADE will delete all related data)
            cursor.execute(
                "DELETE FROM apps WHERE id = %s",
                (app_id,)
            )
            connection.commit()
            
            return {
                "message": f"App '{app_identifier}' deleted successfully",
                "versions_deleted": version_count
            }

# Get all versions across all apps
@app.get("/api/v2/versions")
async def get_all_versions(
    app_identifier: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """Get all versions across all apps with optional filtering"""
    with get_db() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT 
                    v.id,
                    v.version,
                    v.platform,
                    v.version_code,
                    v.file_name,
                    v.file_size,
                    v.file_hash,
                    v.changelog,
                    v.is_active,
                    v.is_mandatory,
                    v.download_count,
                    v.release_date,
                    v.created_at,
                    a.app_identifier,
                    a.app_name
                FROM app_versions v
                JOIN apps a ON v.app_id = a.id
                WHERE 1=1
            """
            params = []
            
            if app_identifier:
                query += " AND a.app_identifier = %s"
                params.append(app_identifier)
            
            if platform:
                query += " AND v.platform = %s"
                params.append(platform)
                
            if is_active is not None:
                query += " AND v.is_active = %s"
                params.append(is_active)
            
            query += " ORDER BY v.created_at DESC"
            
            cursor.execute(query, params)
            versions = cursor.fetchall()
            
            # Parse changelog
            for version in versions:
                if version['changelog']:
                    try:
                        version['changelog'] = json.loads(version['changelog'])
                    except:
                        version['changelog'] = []
            
            return {"versions": versions}

# Version Check Endpoint (Multi-App)
@app.post("/api/v2/version/check")
async def check_version(version_data: VersionCheck):
    """Check if update is available for specific app"""
    with get_db() as connection:
        app_id = get_app_id(version_data.app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Track user if UUID provided
        user_id = None
        if version_data.user_uuid:
            user_id = get_or_create_user(
                version_data.user_uuid, 
                None, 
                version_data.device_info,
                connection
            )
            
            # Update user installation info
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO user_app_installations 
                       (user_id, app_id, current_version, platform)
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE 
                       current_version = VALUES(current_version),
                       platform = VALUES(platform),
                       last_update_date = NOW()""",
                    (user_id, app_id, version_data.current_version, version_data.platform)
                )
                connection.commit()
        
        # Get latest version
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """SELECT version, version_code, is_mandatory, file_size, 
                          changelog, release_date
                   FROM app_versions
                   WHERE app_id = %s AND platform IN (%s, 'all') 
                         AND is_active = true
                   ORDER BY version_code DESC
                   LIMIT 1""",
                (app_id, version_data.platform)
            )
            latest = cursor.fetchone()
            
            if not latest:
                return {
                    "current_version": version_data.current_version,
                    "is_update_available": False
                }
            
            # Compare versions
            is_update_available = latest['version'] != version_data.current_version
            
            response = {
                "current_version": version_data.current_version,
                "latest_version": latest['version'],
                "is_update_available": is_update_available,
                "is_mandatory": bool(latest['is_mandatory']),
                "download_url": f"/api/v2/download/{version_data.app_identifier}/{version_data.platform}/{latest['version']}",
                "file_size": latest['file_size'],
                "release_date": latest['release_date'].isoformat() if latest['release_date'] else None,
                "changelog": json.loads(latest['changelog']) if latest['changelog'] else []
            }
            
            return response

# File Upload Endpoint (Multi-App)
@app.post("/api/v2/version/upload")
async def upload_version(
    app_identifier: str = Form(...),
    version: str = Form(...),
    platform: str = Form(...),
    version_code: int = Form(...),
    is_mandatory: bool = Form(False),
    changelog: str = Form(None),
    file: UploadFile = File(...)
):
    """Upload new version for specific app"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Get app details to validate platform
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT platform_support FROM apps WHERE app_identifier = %s",
                (app_identifier,)
            )
            result = cursor.fetchone()
            if result:
                supported_platforms = json.loads(result[0])
                if platform not in supported_platforms:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Platform '{platform}' is not supported by app '{app_identifier}'. Supported platforms: {', '.join(supported_platforms)}"
                    )
        
        # Validate file
        if platform == "android" and not file.filename.endswith('.apk'):
            raise HTTPException(status_code=400, detail="Android requires APK file")
        elif platform == "ios" and not file.filename.endswith('.ipa'):
            raise HTTPException(status_code=400, detail="iOS requires IPA file")
        
        # Read file in chunks to handle large files
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size (max 500MB)
        MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        logger.info(f"Uploading file: {file.filename}, size: {file_size / (1024*1024):.2f}MB")
        
        # Calculate hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Parse changelog
        changelog_list = []
        if changelog:
            try:
                changelog_list = json.loads(changelog)
            except:
                changelog_list = [changelog]
        
        # For Railway MySQL, we need to check if the file size is within limits
        # Railway Pro has much higher limits (up to 1GB max_allowed_packet)
        # Set a reasonable limit for mobile app files
        RAILWAY_MAX_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', '500')) * 1024 * 1024  # Default 500MB, configurable via env
        
        if file_size > RAILWAY_MAX_SIZE:
            # For larger files, we need to save to filesystem or use cloud storage
            logger.warning(f"File size {file_size / (1024*1024):.2f}MB exceeds limit of {RAILWAY_MAX_SIZE / (1024*1024)}MB")
            
            # Option 1: Save reference only (recommended for production)
            # You would save the file to S3/GCS/local filesystem here
            # For now, we'll save a smaller placeholder
            
            raise HTTPException(
                status_code=413,
                detail=f"File size {file_size / (1024*1024):.2f}MB exceeds limit of {RAILWAY_MAX_SIZE / (1024*1024)}MB. Please use a smaller file or contact support."
            )
        
        # Save to database with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with connection.cursor() as cursor:
                    # Use smaller chunks and commit immediately
                    cursor.execute(
                        """INSERT INTO app_versions 
                           (app_id, version, platform, version_code, app_file, file_name, 
                            file_size, file_hash, changelog, is_mandatory)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (app_id, version, platform, version_code, file_content, 
                         file.filename, file_size, file_hash,
                         json.dumps(changelog_list), is_mandatory)
                    )
                    connection.commit()
                    logger.info(f"Successfully uploaded version {version} for {app_identifier}")
                    break
            except pymysql.err.OperationalError as e:
                logger.error(f"Database error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    # Reconnect and retry
                    connection.ping(reconnect=True)
                    continue
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Database connection error. The file might be too large for the current database configuration."
                    )
            
        return {
            "message": "Version uploaded successfully",
            "app": app_identifier,
            "version": version,
            "platform": platform,
            "file_size": len(file_content),
            "file_hash": file_hash
        }

@app.delete("/api/v2/versions/{app_identifier}/{platform}/{version}")
async def delete_version(app_identifier: str, platform: str, version: str):
    """Delete a specific version"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor() as cursor:
            # Check if version exists
            cursor.execute(
                """SELECT id FROM app_versions 
                   WHERE app_id = %s AND platform = %s AND version = %s""",
                (app_id, platform, version)
            )
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Version not found")
            
            # Delete the version
            cursor.execute(
                """DELETE FROM app_versions 
                   WHERE app_id = %s AND platform = %s AND version = %s""",
                (app_id, platform, version)
            )
            connection.commit()
            
            return {"message": f"Version {version} for {platform} deleted successfully"}

# User Session Tracking
@app.post("/api/v2/session/start")
async def start_session(session_data: UserSession):
    """Track user session start"""
    with get_db() as connection:
        app_id = get_app_id(session_data.app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        user_id = get_or_create_user(
            session_data.user_uuid,
            session_data.email,
            session_data.device_info,
            connection
        )
        
        # Create session
        with connection.cursor() as cursor:
            # Generate session UUID
            session_uuid = str(uuid.uuid4())
            
            # Extract platform from device_info or default to 'web'
            platform = 'web'
            if session_data.device_info and 'os' in session_data.device_info:
                os_name = session_data.device_info['os'].lower()
                if os_name in ['android', 'ios']:
                    platform = os_name
            
            cursor.execute(
                """INSERT INTO user_sessions 
                   (user_id, app_id, session_uuid, app_version, platform, device_info, start_time, is_active)
                   VALUES (%s, %s, %s, %s, %s, %s, NOW(), 1)""",
                (user_id, app_id, session_uuid, session_data.app_version, platform,
                 json.dumps(session_data.device_info) if session_data.device_info else None)
            )
            session_id = cursor.lastrowid
            connection.commit()
            
        return {"session_id": session_id, "user_id": user_id}

@app.post("/api/v2/session/{session_id}/end")
async def end_session(session_id: int):
    """End user session"""
    with get_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE user_sessions 
                   SET end_time = NOW(),
                       is_active = 0,
                       duration_seconds = TIMESTAMPDIFF(SECOND, start_time, NOW())
                   WHERE id = %s""",
                (session_id,)
            )
            connection.commit()
            
    return {"message": "Session ended"}

# Error Reporting
@app.post("/api/v2/errors/report")
async def report_error(error_data: ErrorReport):
    """Report app error"""
    with get_db() as connection:
        app_id = get_app_id(error_data.app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        user_id = None
        if error_data.user_uuid:
            user_id = get_or_create_user(error_data.user_uuid, None, error_data.device_info, connection)
        
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO app_error_logs 
                   (app_id, user_id, session_id, error_type, error_message, error_stack,
                    app_version, platform, metadata, severity)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (app_id, user_id, error_data.session_id, error_data.error_type, error_data.error_message,
                 error_data.error_stack, error_data.app_version, error_data.platform,
                 json.dumps(error_data.metadata) if error_data.metadata else None,
                 error_data.severity)
            )
            connection.commit()
            
        return {"message": "Error reported", "error_id": cursor.lastrowid}

# Analytics Endpoints
@app.get("/api/v2/analytics/{app_identifier}/overview")
async def get_app_analytics(app_identifier: str, days: int = Query(30, ge=1, le=365)):
    """Get analytics overview for specific app"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get user stats
            cursor.execute(
                """SELECT 
                    COUNT(DISTINCT uai.user_id) as total_users,
                    COUNT(DISTINCT CASE WHEN DATE(us.start_time) = CURDATE() 
                          THEN us.user_id END) as daily_active_users,
                    COUNT(DISTINCT CASE WHEN DATE(us.start_time) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
                          THEN us.user_id END) as weekly_active_users,
                    COUNT(DISTINCT CASE WHEN DATE(us.start_time) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) 
                          THEN us.user_id END) as monthly_active_users,
                    COUNT(DISTINCT CASE WHEN DATE(uai.install_date) = CURDATE() 
                          THEN uai.user_id END) as new_users_today
                FROM apps a
                LEFT JOIN user_app_installations uai ON a.id = uai.app_id
                LEFT JOIN user_sessions us ON a.id = us.app_id
                WHERE a.id = %s""",
                (app_id,)
            )
            user_stats = cursor.fetchone()
            
            # Get error stats
            cursor.execute(
                """SELECT 
                    COUNT(*) as total_errors,
                    COUNT(DISTINCT user_id) as affected_users,
                    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_errors,
                    COUNT(*) as total_errors  -- All errors since is_resolved column doesn't exist
                FROM app_error_logs
                WHERE app_id = %s AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)""",
                (app_id, days)
            )
            error_stats = cursor.fetchone()
            
            # Get version distribution
            cursor.execute(
                """SELECT 
                    current_version,
                    platform,
                    COUNT(*) as user_count
                FROM user_app_installations
                WHERE app_id = %s AND is_active = true
                GROUP BY current_version, platform
                ORDER BY user_count DESC""",
                (app_id,)
            )
            version_distribution = cursor.fetchall()
            
            return {
                "app_identifier": app_identifier,
                "user_stats": user_stats,
                "error_stats": error_stats,
                "version_distribution": version_distribution,
                "period_days": days
            }

@app.get("/api/v2/analytics/{app_identifier}/errors")
async def get_error_summary(
    app_identifier: str,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get error summary for specific app"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT 
                    error_type,
                    severity,
                    COUNT(*) as error_count,
                    MAX(created_at) as last_occurrence,
                    COUNT(DISTINCT user_id) as affected_users,
                    MIN(app_version) as first_version,
                    MAX(app_version) as last_version
                FROM app_error_logs
                WHERE app_id = %s
            """
            params = [app_id]
            
            if severity:
                query += " AND severity = %s"
                params.append(severity)
            
            query += """
                GROUP BY error_type, severity
                ORDER BY severity DESC, error_count DESC
                LIMIT %s
            """
            params.append(limit)
            
            cursor.execute(query, params)
            errors = cursor.fetchall()
            
            return {"app_identifier": app_identifier, "errors": errors}

# Download endpoint (updated for multi-app)
@app.get("/api/v2/download/{app_identifier}/{platform}/{version}")
async def download_version(app_identifier: str, platform: str, version: str):
    """Download specific version"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT app_file, file_name, file_size
                   FROM app_versions
                   WHERE app_id = %s AND platform = %s AND version = %s""",
                (app_id, platform, version)
            )
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Version not found")
            
            file_content, file_name, file_size = result
            
            # Update download count
            cursor.execute(
                """UPDATE app_versions 
                   SET download_count = download_count + 1
                   WHERE app_id = %s AND platform = %s AND version = %s""",
                (app_id, platform, version)
            )
            connection.commit()
            
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Length": str(file_size)
                }
            )

# Update status tracking
@app.post("/api/v2/update/status")
async def track_update_status(update_data: UpdateStatus):
    """Track update installation status"""
    with get_db() as connection:
        app_id = get_app_id(update_data.app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        user_id = get_or_create_user(update_data.user_uuid, None, None, connection)
        
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO update_history 
                   (user_id, app_id, from_version, to_version, update_status, failure_reason)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, app_id, update_data.from_version, update_data.to_version,
                 update_data.status, update_data.failure_reason)
            )
            connection.commit()
            
        return {"message": "Update status tracked"}

# Missing endpoints for frontend dashboards

# Get recent errors with details
@app.get("/api/v2/errors/recent/{app_identifier}")
async def get_recent_errors(
    app_identifier: str,
    limit: int = Query(10, ge=1, le=50),
    severity: Optional[str] = Query(None)
):
    """Get recent errors for specific app"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT 
                    id,
                    error_type,
                    error_message,
                    error_stack,
                    severity,
                    user_id,
                    session_id,
                    app_version,
                    platform,
                    metadata,
                    created_at
                FROM app_error_logs
                WHERE app_id = %s
            """
            params = [app_id]
            
            if severity:
                query += " AND severity = %s"
                params.append(severity)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            errors = cursor.fetchall()
            
            # Parse JSON fields
            for error in errors:
                if error.get('metadata'):
                    try:
                        error['metadata'] = json.loads(error['metadata'])
                    except:
                        error['metadata'] = {}
            
            return {"errors": errors}

# Get session analytics
@app.get("/api/v2/analytics/{app_identifier}/sessions")
async def get_session_analytics(
    app_identifier: str,
    days: int = Query(7, ge=1, le=365)
):
    """Get session analytics for specific app"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get session stats
            cursor.execute(
                """SELECT 
                    COUNT(DISTINCT u.id) as total_users,
                    COUNT(DISTINCT CASE WHEN DATE(s.start_time) = CURDATE() 
                          THEN s.user_id END) as daily_active_users,
                    COUNT(DISTINCT CASE WHEN DATE(s.start_time) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
                          THEN s.user_id END) as weekly_active_users,
                    COUNT(DISTINCT CASE WHEN DATE(s.start_time) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) 
                          THEN s.user_id END) as monthly_active_users,
                    COUNT(DISTINCT CASE WHEN DATE(u.first_seen_at) = CURDATE() 
                          THEN u.id END) as new_users_today,
                    AVG(s.duration_seconds) as avg_session_duration,
                    COUNT(s.id) as total_sessions
                FROM apps a
                LEFT JOIN user_app_installations uai ON a.id = uai.app_id
                LEFT JOIN app_users u ON uai.user_id = u.id
                LEFT JOIN user_sessions s ON a.id = s.app_id 
                    AND s.start_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                WHERE a.id = %s""",
                (days, app_id)
            )
            stats = cursor.fetchone()
            
            return {"stats": stats, "period_days": days}

# Get recent sessions
@app.get("/api/v2/sessions/recent/{app_identifier}")
async def get_recent_sessions(
    app_identifier: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get recent sessions for specific app"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """SELECT 
                    s.id,
                    s.user_id,
                    u.email,
                    s.start_time as session_start,
                    s.end_time as session_end,
                    s.duration_seconds,
                    s.app_version,
                    s.platform,
                    s.device_info
                FROM user_sessions s
                JOIN app_users u ON s.user_id = u.id
                WHERE s.app_id = %s
                ORDER BY s.start_time DESC
                LIMIT %s""",
                (app_id, limit)
            )
            sessions = cursor.fetchall()
            
            # Parse device_info JSON
            for session in sessions:
                if session.get('device_info'):
                    try:
                        session['device_info'] = json.loads(session['device_info'])
                    except:
                        pass
            
            return {"sessions": sessions}

# Get daily session statistics
@app.get("/api/v2/analytics/{app_identifier}/sessions/daily")
async def get_daily_session_stats(
    app_identifier: str,
    days: int = Query(7, ge=1, le=90)
):
    """Get daily session statistics"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """SELECT 
                    DATE(start_time) as date,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(*) as total_sessions,
                    AVG(duration_seconds) as avg_duration
                FROM user_sessions
                WHERE app_id = %s
                    AND start_time >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(start_time)
                ORDER BY date DESC""",
                (app_id, days)
            )
            daily_stats = cursor.fetchall()
            
            return {"daily_stats": daily_stats}

# Get all users across all applications
@app.get("/api/v2/users")
async def get_all_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Get all users across all applications with their app usage details"""
    with get_db() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get users with their basic info and session counts
            cursor.execute(
                """SELECT 
                    u.id,
                    u.user_uuid,
                    u.email,
                    u.first_seen_at,
                    u.last_seen_at,
                    COUNT(DISTINCT us.id) as total_sessions,
                    COUNT(DISTINCT uai.app_id) as app_count
                FROM app_users u
                LEFT JOIN user_app_installations uai ON u.id = uai.user_id
                LEFT JOIN user_sessions us ON u.id = us.user_id
                GROUP BY u.id
                ORDER BY u.last_seen_at DESC
                LIMIT %s OFFSET %s""",
                (limit, offset)
            )
            users = cursor.fetchall()
            
            # For each user, get their app details
            for user in users:
                cursor.execute(
                    """SELECT 
                        a.app_name,
                        a.app_identifier,
                        uai.platform,
                        uai.current_version,
                        uai.last_update_date
                    FROM user_app_installations uai
                    JOIN apps a ON uai.app_id = a.id
                    WHERE uai.user_id = %s
                    ORDER BY uai.last_update_date DESC""",
                    (user['id'],)
                )
                user['apps'] = cursor.fetchall()
            
            # Get total count for pagination
            cursor.execute("SELECT COUNT(*) as total FROM app_users")
            total_count = cursor.fetchone()['total']
            
            return {
                "users": users,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }

# Get user details by ID
@app.get("/api/v2/users/{user_id}")
async def get_user_details(user_id: int):
    """Get detailed information about a specific user"""
    with get_db() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get user basic info
            cursor.execute(
                """SELECT 
                    u.id,
                    u.user_uuid,
                    u.email,
                    u.first_seen_at,
                    u.last_seen_at,
                    COUNT(DISTINCT us.id) as total_sessions,
                    u.device_info
                FROM app_users u
                LEFT JOIN user_sessions us ON u.id = us.user_id
                WHERE u.id = %s
                GROUP BY u.id""",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Parse device_info if it exists
            if user.get('device_info'):
                try:
                    user['device_info'] = json.loads(user['device_info'])
                except:
                    pass
            
            # Get user's app installations
            cursor.execute(
                """SELECT 
                    a.id as app_id,
                    a.app_name,
                    a.app_identifier,
                    uai.platform,
                    uai.current_version,
                    uai.install_date,
                    uai.last_update_date,
                    uai.is_active,
                    uai.device_model,
                    uai.os_version
                FROM user_app_installations uai
                JOIN apps a ON uai.app_id = a.id
                WHERE uai.user_id = %s
                ORDER BY uai.last_update_date DESC""",
                (user_id,)
            )
            user['installations'] = cursor.fetchall()
            
            # Get recent sessions
            cursor.execute(
                """SELECT 
                    s.id,
                    s.start_time as session_start,
                    s.end_time as session_end,
                    s.duration_seconds,
                    s.app_version,
                    s.platform,
                    a.app_name,
                    a.app_identifier
                FROM user_sessions s
                JOIN apps a ON s.app_id = a.id
                WHERE s.user_id = %s
                ORDER BY s.start_time DESC
                LIMIT 20""",
                (user_id,)
            )
            user['recent_sessions'] = cursor.fetchall()
            
            # Get error count
            cursor.execute(
                """SELECT COUNT(*) as error_count
                FROM app_error_logs
                WHERE user_id = %s""",
                (user_id,)
            )
            user['error_count'] = cursor.fetchone()['error_count']
            
            return user

# Get all users with their app usage
@app.get("/api/v2/users")
async def get_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all users with their app installations and session counts"""
    with get_db() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get users with their stats
            cursor.execute(
                """SELECT 
                    u.id,
                    u.user_uuid,
                    u.email,
                    u.first_seen_at,
                    u.last_seen_at,
                    COUNT(DISTINCT us.id) as total_sessions,
                    COUNT(DISTINCT uai.app_id) as app_count
                FROM app_users u
                LEFT JOIN user_app_installations uai ON u.id = uai.user_id
                LEFT JOIN user_sessions us ON u.id = us.user_id
                GROUP BY u.id, u.user_uuid, u.email, u.first_seen_at, u.last_seen_at
                ORDER BY u.last_seen_at DESC
                LIMIT %s OFFSET %s""",
                (limit, offset)
            )
            users = cursor.fetchall()
            
            # For each user, get their apps
            for user in users:
                cursor.execute(
                    """SELECT 
                        a.app_identifier,
                        a.app_name,
                        uai.current_version,
                        uai.platform,
                        uai.last_update_date,
                        COUNT(us.id) as session_count
                    FROM user_app_installations uai
                    JOIN apps a ON uai.app_id = a.id
                    LEFT JOIN user_sessions us ON uai.user_id = us.user_id AND uai.app_id = us.app_id
                    WHERE uai.user_id = %s
                    GROUP BY a.id, a.app_identifier, a.app_name, uai.current_version, uai.platform, uai.last_update_date
                    ORDER BY uai.last_update_date DESC
                    LIMIT 5""",
                    (user['id'],)
                )
                user['apps'] = cursor.fetchall()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM app_users")
            total = cursor.fetchone()['total']
            
            return {
                "users": users,
                "total": total,
                "limit": limit,
                "offset": offset
            }

# Get single user details
@app.get("/api/v2/users/{user_id}")
async def get_user_details(user_id: int):
    """Get detailed information about a specific user"""
    with get_db() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get user info
            cursor.execute(
                """SELECT * FROM app_users WHERE id = %s""",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get user's apps
            cursor.execute(
                """SELECT 
                    a.app_identifier,
                    a.app_name,
                    uai.*
                FROM user_app_installations uai
                JOIN apps a ON uai.app_id = a.id
                WHERE uai.user_id = %s""",
                (user_id,)
            )
            user['installations'] = cursor.fetchall()
            
            # Get recent sessions
            cursor.execute(
                """SELECT 
                    us.*,
                    a.app_name
                FROM user_sessions us
                JOIN apps a ON us.app_id = a.id
                WHERE us.user_id = %s
                ORDER BY us.start_time DESC
                LIMIT 10""",
                (user_id,)
            )
            user['recent_sessions'] = cursor.fetchall()
            
            # Get error count
            cursor.execute(
                """SELECT COUNT(*) as error_count
                FROM app_error_logs
                WHERE user_id = %s""",
                (user_id,)
            )
            user['error_count'] = cursor.fetchone()['error_count']
            
            return user

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)