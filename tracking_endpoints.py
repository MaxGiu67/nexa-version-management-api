"""
Additional endpoints for session and error tracking dashboards
To be added to multi_app_api.py
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta
from typing import Optional
import pymysql
import json

# Create router for tracking endpoints
tracking_router = APIRouter(prefix="/api/v2", tags=["tracking"])

# Analytics endpoints for sessions
@tracking_router.get("/analytics/{app_identifier}/sessions")
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

@tracking_router.get("/sessions/recent/{app_identifier}")
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
                    s.device_info,
                    s.end_reason
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
                if session['device_info']:
                    try:
                        import json
                        session['device_info'] = json.loads(session['device_info'])
                    except:
                        pass
            
            return {"sessions": sessions}

@tracking_router.get("/analytics/{app_identifier}/sessions/daily")
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

# Error tracking endpoints
@tracking_router.get("/errors/recent/{app_identifier}")
async def get_recent_errors(
    app_identifier: str,
    limit: int = Query(10, ge=1, le=50),
    severity: Optional[str] = None
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

# Override the existing analytics endpoint to include more detailed error stats
@tracking_router.get("/analytics/{app_identifier}/errors/detailed")
async def get_detailed_error_analytics(
    app_identifier: str,
    days: int = Query(7, ge=1, le=365),
    severity: Optional[str] = None
):
    """Get detailed error analytics with grouping"""
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get error summary grouped by type and severity
            query = """
                SELECT 
                    error_type,
                    severity,
                    COUNT(*) as error_count,
                    MAX(created_at) as last_occurrence,
                    COUNT(DISTINCT user_id) as affected_users,
                    MIN(app_version) as first_version,
                    MAX(app_version) as last_version,
                    SUBSTRING(error_message, 1, 200) as sample_message
                FROM app_error_logs
                WHERE app_id = %s 
                    AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            params = [app_id, days]
            
            if severity:
                query += " AND severity = %s"
                params.append(severity)
            
            query += """
                GROUP BY error_type, severity
                ORDER BY severity DESC, error_count DESC
                LIMIT 50
            """
            
            cursor.execute(query, params)
            errors = cursor.fetchall()
            
            return {
                "app_identifier": app_identifier,
                "errors": errors,
                "period_days": days
            }

# Session start endpoint enhancement
@tracking_router.post("/session/start/v2")
async def start_session_v2(session_data: UserSession):
    """Enhanced session start with better device tracking"""
    with get_db() as connection:
        app_id = get_app_id(session_data.app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Enhanced user creation/update with device info
        user_id = get_or_create_user(
            session_data.user_uuid,
            session_data.email,
            session_data.device_info,
            connection
        )
        
        # Create session
        with connection.cursor() as cursor:
            # Generate session UUID
            import uuid
            session_uuid = str(uuid.uuid4())
            
            # Extract platform from device_info or use provided platform
            platform = 'web'
            if hasattr(session_data, 'platform') and session_data.platform:
                platform = session_data.platform
            elif session_data.device_info and 'os' in session_data.device_info:
                os_name = session_data.device_info['os'].lower()
                if os_name in ['android', 'ios']:
                    platform = os_name
            
            cursor.execute(
                """INSERT INTO user_sessions 
                   (user_id, app_id, session_uuid, start_time, app_version, platform, device_info, is_active)
                   VALUES (%s, %s, %s, NOW(), %s, %s, %s, 1)""",
                (user_id, app_id, session_uuid, session_data.app_version, platform,
                 json.dumps(session_data.device_info) if session_data.device_info else None)
            )
            session_id = cursor.lastrowid
            
            # Update user's last activity
            cursor.execute(
                """UPDATE app_users 
                   SET last_seen_at = NOW() 
                   WHERE id = %s""",
                (user_id,)
            )
            
            connection.commit()
            
        return {
            "session_id": session_id,
            "user_id": user_id,
            "started_at": datetime.now().isoformat()
        }

# Add these endpoints to your main app
# In multi_app_api.py, add:
# app.include_router(tracking_router)