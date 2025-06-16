"""
Implementazione Python degli endpoint di gestione versioni
Compatibile con FastAPI/Flask per il sistema Nexa Timesheet
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import re
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import pymysql
from pymysql.cursors import DictCursor
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="App Version Management API", version="1.0.0")

# Security
security = HTTPBearer()

# Database configuration (will be updated in main.py for Railway)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

# Pydantic models
class UpdateCheckResponse(BaseModel):
    hasUpdate: bool
    latestVersion: Optional[str] = None
    versionCode: Optional[int] = None
    isMandatory: Optional[bool] = None
    minSupportedVersion: Optional[str] = None
    downloadUrl: Optional[str] = None
    changelog: Optional[List[str]] = []
    releaseDate: Optional[str] = None
    message: Optional[str] = None

class VersionInfo(BaseModel):
    version: str
    versionCode: int
    platform: str
    releaseDate: str
    downloadUrl: Optional[str] = None
    changelog: Optional[List[str]] = []
    isMandatory: bool = False
    minSupportedVersion: Optional[str] = None

class UpdateLogRequest(BaseModel):
    from_version: Optional[str] = None
    to_version: str
    platform: str
    update_type: str
    device_info: Optional[Dict[str, Any]] = {}
    
    @validator('to_version', 'from_version')
    def validate_version_format(cls, v):
        if v and not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Invalid version format. Expected: X.Y.Z')
        return v
    
    @validator('platform')
    def validate_platform(cls, v):
        if v not in ['ios', 'android']:
            raise ValueError('Platform must be ios or android')
        return v
    
    @validator('update_type')
    def validate_update_type(cls, v):
        if v not in ['manual', 'forced', 'auto']:
            raise ValueError('Update type must be manual, forced, or auto')
        return v

class CreateVersionRequest(BaseModel):
    version: str
    version_code: int
    platform: str
    release_date: str
    is_mandatory: bool = False
    min_supported_version: Optional[str] = None
    download_url: Optional[str] = None
    changelog: Optional[Dict[str, List[str]]] = {"changes": []}

# Database connection
def get_db():
    """Get database connection"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user info"""
    # In produzione, qui dovrebbe esserci la validazione del JWT
    # Per ora restituiamo un utente mock
    return {"id": 1, "email": "user@example.com", "is_admin": False}

async def require_admin(user: dict = Depends(get_current_user)):
    """Require admin privileges"""
    if not user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

# Helper functions
def compare_versions(v1: str, v2: str) -> int:
    """Compare semantic versions"""
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]
    
    for i in range(3):
        p1 = parts1[i] if i < len(parts1) else 0
        p2 = parts2[i] if i < len(parts2) else 0
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
    return 0

def is_valid_version(version: str) -> bool:
    """Validate version format"""
    return bool(re.match(r'^\d+\.\d+\.\d+$', version))

# API Endpoints

@app.get("/api/v1/app-version/check", response_model=UpdateCheckResponse)
async def check_for_updates(
    current_version: str = Query(..., description="Current app version"),
    platform: str = Query('all', description="Platform (ios/android/all)"),
    db=Depends(get_db)
):
    """Check if updates are available for the current version"""
    try:
        # Validate version format
        if not is_valid_version(current_version):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid version format. Expected: X.Y.Z"
            )
        
        with db.cursor() as cursor:
            # Get latest active version
            query = """
                SELECT * FROM app_versions 
                WHERE platform IN (%s, 'all') 
                AND is_active = true 
                ORDER BY version_code DESC 
                LIMIT 1
            """
            cursor.execute(query, (platform,))
            latest_version = cursor.fetchone()
            
            if not latest_version:
                return UpdateCheckResponse(
                    hasUpdate=False,
                    message="No versions available"
                )
            
            # Compare versions
            has_update = compare_versions(current_version, latest_version['version']) < 0
            
            # Check if mandatory
            is_mandatory = bool(latest_version['is_mandatory'])
            if latest_version['min_supported_version']:
                is_mandatory = is_mandatory or compare_versions(
                    current_version, 
                    latest_version['min_supported_version']
                ) < 0
            
            # Parse changelog
            changelog = []
            if latest_version['changelog']:
                try:
                    changelog_data = json.loads(latest_version['changelog'])
                    changelog = changelog_data.get('changes', [])
                except json.JSONDecodeError:
                    logger.error("Failed to parse changelog JSON")
            
            return UpdateCheckResponse(
                hasUpdate=has_update,
                latestVersion=latest_version['version'],
                versionCode=latest_version['version_code'],
                isMandatory=is_mandatory,
                minSupportedVersion=latest_version['min_supported_version'],
                downloadUrl=latest_version['download_url'],
                changelog=changelog,
                releaseDate=latest_version['release_date'].isoformat() if latest_version['release_date'] else None
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking updates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/v1/app-version/latest", response_model=VersionInfo)
async def get_latest_version(
    platform: str = Query('all', description="Platform (ios/android/all)"),
    db=Depends(get_db)
):
    """Get information about the latest version"""
    try:
        with db.cursor() as cursor:
            query = """
                SELECT * FROM app_versions 
                WHERE platform IN (%s, 'all') 
                AND is_active = true 
                ORDER BY version_code DESC 
                LIMIT 1
            """
            cursor.execute(query, (platform,))
            latest_version = cursor.fetchone()
            
            if not latest_version:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No version found"
                )
            
            # Parse changelog
            changelog = []
            if latest_version['changelog']:
                try:
                    changelog_data = json.loads(latest_version['changelog'])
                    changelog = changelog_data.get('changes', [])
                except json.JSONDecodeError:
                    logger.error("Failed to parse changelog JSON")
            
            return VersionInfo(
                version=latest_version['version'],
                versionCode=latest_version['version_code'],
                platform=latest_version['platform'],
                releaseDate=latest_version['release_date'].isoformat(),
                downloadUrl=latest_version['download_url'],
                changelog=changelog,
                isMandatory=bool(latest_version['is_mandatory']),
                minSupportedVersion=latest_version['min_supported_version']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/v1/app-version/log-update", status_code=status.HTTP_201_CREATED)
async def log_update(
    update_data: UpdateLogRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Log a user's app update"""
    try:
        with db.cursor() as cursor:
            query = """
                INSERT INTO app_update_logs 
                (user_id, from_version, to_version, platform, update_type, device_info) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                current_user['id'],
                update_data.from_version,
                update_data.to_version,
                update_data.platform,
                update_data.update_type,
                json.dumps(update_data.device_info)
            ))
            
            db.commit()
            log_id = cursor.lastrowid
            
            return {
                "success": True,
                "message": "Update logged successfully",
                "log_id": log_id
            }
            
    except Exception as e:
        logger.error(f"Error logging update: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/v1/app-version/history")
async def get_version_history(
    platform: str = Query('all', description="Platform filter"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin)
):
    """Get version history with update counts (admin only)"""
    try:
        with db.cursor() as cursor:
            # Get versions with update count
            query = """
                SELECT 
                    v.*,
                    COUNT(DISTINCT ul.user_id) as update_count
                FROM app_versions v
                LEFT JOIN app_update_logs ul ON ul.to_version = v.version
                WHERE (v.platform = %s OR v.platform = 'all')
                GROUP BY v.id
                ORDER BY v.version_code DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (platform, limit, offset))
            versions = cursor.fetchall()
            
            # Get total count
            count_query = """
                SELECT COUNT(*) as total 
                FROM app_versions 
                WHERE platform IN (%s, 'all')
            """
            cursor.execute(count_query, (platform,))
            total = cursor.fetchone()['total']
            
            # Format response
            formatted_versions = []
            for v in versions:
                formatted_versions.append({
                    'version': v['version'],
                    'versionCode': v['version_code'],
                    'platform': v['platform'],
                    'releaseDate': v['release_date'].isoformat() if v['release_date'] else None,
                    'isActive': bool(v['is_active']),
                    'isMandatory': bool(v['is_mandatory']),
                    'downloadUrl': v['download_url'],
                    'updateCount': v['update_count']
                })
            
            return {
                'versions': formatted_versions,
                'total': total
            }
            
    except Exception as e:
        logger.error(f"Error getting version history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/v1/app-version/stats")
async def get_update_statistics(
    db=Depends(get_db),
    _=Depends(require_admin)
):
    """Get update statistics (admin only)"""
    try:
        with db.cursor() as cursor:
            # Total users
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) as totalUsers FROM app_update_logs"
            )
            total_users = cursor.fetchone()['totalUsers']
            
            # Version distribution
            version_query = """
                SELECT 
                    to_version as version,
                    platform,
                    COUNT(DISTINCT user_id) as count
                FROM (
                    SELECT 
                        user_id, 
                        to_version, 
                        platform,
                        created_at,
                        @row_num := IF(@prev_user = user_id, @row_num + 1, 1) AS rn,
                        @prev_user := user_id
                    FROM app_update_logs,
                    (SELECT @row_num := 0, @prev_user := NULL) AS vars
                    ORDER BY user_id, created_at DESC
                ) latest_updates
                WHERE rn = 1
                GROUP BY to_version, platform
            """
            
            cursor.execute(version_query)
            version_data = cursor.fetchall()
            
            # Process version distribution
            version_distribution = {}
            for row in version_data:
                version = row['version']
                if version not in version_distribution:
                    version_distribution[version] = {
                        'count': 0,
                        'percentage': 0,
                        'platforms': {}
                    }
                version_distribution[version]['count'] += row['count']
                version_distribution[version]['platforms'][row['platform']] = row['count']
            
            # Calculate percentages
            if total_users > 0:
                for version in version_distribution:
                    version_distribution[version]['percentage'] = round(
                        (version_distribution[version]['count'] / total_users) * 100, 1
                    )
            
            # Last updates
            last_updates_query = """
                SELECT 
                    ul.user_id,
                    CONCAT(p.firstName, ' ', p.lastName) as userName,
                    ul.from_version,
                    ul.to_version,
                    ul.platform,
                    ul.created_at as updatedAt
                FROM app_update_logs ul
                LEFT JOIN accounts a ON ul.user_id = a.id
                LEFT JOIN persons p ON a.person_id = p.id
                ORDER BY ul.created_at DESC
                LIMIT 10
            """
            
            cursor.execute(last_updates_query)
            last_updates = cursor.fetchall()
            
            # Format last updates
            formatted_updates = []
            for update in last_updates:
                formatted_updates.append({
                    'userId': update['user_id'],
                    'userName': update['userName'] or 'Unknown',
                    'fromVersion': update['from_version'],
                    'toVersion': update['to_version'],
                    'platform': update['platform'],
                    'updatedAt': update['updatedAt'].isoformat() if update['updatedAt'] else None
                })
            
            return {
                'totalUsers': total_users,
                'versionDistribution': version_distribution,
                'lastUpdates': formatted_updates
            }
            
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/v1/app-version/version", status_code=status.HTTP_201_CREATED)
async def create_or_update_version(
    version_data: CreateVersionRequest,
    db=Depends(get_db),
    _=Depends(require_admin)
):
    """Create or update an app version (admin only)"""
    try:
        with db.cursor() as cursor:
            # Check if version exists
            check_query = "SELECT id FROM app_versions WHERE version = %s AND platform = %s"
            cursor.execute(check_query, (version_data.version, version_data.platform))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing version
                update_query = """
                    UPDATE app_versions SET
                        version_code = %s,
                        release_date = %s,
                        is_mandatory = %s,
                        min_supported_version = %s,
                        download_url = %s,
                        changelog = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(update_query, (
                    version_data.version_code,
                    version_data.release_date,
                    version_data.is_mandatory,
                    version_data.min_supported_version,
                    version_data.download_url,
                    json.dumps(version_data.changelog),
                    existing['id']
                ))
                message = "Version updated successfully"
            else:
                # Create new version
                insert_query = """
                    INSERT INTO app_versions 
                    (version, version_code, platform, release_date, is_mandatory,
                     min_supported_version, download_url, changelog, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true)
                """
                cursor.execute(insert_query, (
                    version_data.version,
                    version_data.version_code,
                    version_data.platform,
                    version_data.release_date,
                    version_data.is_mandatory,
                    version_data.min_supported_version,
                    version_data.download_url,
                    json.dumps(version_data.changelog)
                ))
                message = "Version created successfully"
            
            db.commit()
            
            return {
                "success": True,
                "message": message
            }
            
    except Exception as e:
        logger.error(f"Error creating/updating version: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "app-version-management"}

# Alternative Flask implementation
"""
Se preferisci Flask invece di FastAPI, ecco l'implementazione equivalente:

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/api/v1/app-version/check', methods=['GET'])
def check_for_updates():
    current_version = request.args.get('current_version')
    platform = request.args.get('platform', 'all')
    
    # Implementazione simile a quella FastAPI sopra
    # ...
    
    return jsonify(result)

# Altri endpoint seguirebbero lo stesso pattern
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)