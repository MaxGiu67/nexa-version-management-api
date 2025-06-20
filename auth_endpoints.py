"""
Authentication endpoints for Version Management System
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from auth_module import (
    AuthService, LoginRequest, TwoFactorRequest, UserCreate, UserResponse,
    get_current_user, require_superadmin
)
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/auth", tags=["Authentication"])

# Helper to get auth service
def get_auth_service(request: Request) -> AuthService:
    # Get DB config from app state or use the global one
    if hasattr(request.app.state, 'db_config'):
        db_config = request.app.state.db_config
    else:
        # Fallback to importing from multi_app_api
        from multi_app_api import DB_CONFIG
        db_config = DB_CONFIG
    return AuthService(db_config)

# Public endpoints
@router.post("/login")
async def login(
    login_data: LoginRequest,
    request: Request
):
    """Login with username and password"""
    auth_service = get_auth_service(request)
    
    # Get IP and user agent for audit
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    
    try:
        result = auth_service.authenticate_user(
            login_data.username,
            login_data.password,
            ip_address,
            user_agent
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il login"
        )

@router.post("/verify-2fa")
async def verify_2fa(
    data: TwoFactorRequest,
    request: Request
):
    """Verify 2FA code"""
    auth_service = get_auth_service(request)
    
    try:
        result = auth_service.verify_2fa(data.session_token, data.totp_code)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante la verifica 2FA"
        )

# Protected endpoints
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Get current user information"""
    auth_service = get_auth_service(request)
    return auth_service.get_user_by_id(current_user['id'])

@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Logout current user"""
    auth_service = get_auth_service(request)
    
    # Get session token from header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        session_token = auth_header[7:]
        auth_service.logout(session_token)
    
    return {"success": True, "message": "Logout effettuato con successo"}

@router.post("/enable-2fa")
async def enable_2fa(
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Enable 2FA for current user"""
    auth_service = get_auth_service(request)
    
    try:
        result = auth_service.enable_2fa(current_user['id'])
        return result
    except Exception as e:
        logger.error(f"Enable 2FA error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'abilitazione 2FA"
        )

@router.post("/disable-2fa")
async def disable_2fa(
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Disable 2FA for current user"""
    auth_service = get_auth_service(request)
    
    try:
        auth_service.disable_2fa(current_user['id'])
        return {"success": True, "message": "2FA disabilitato con successo"}
    except Exception as e:
        logger.error(f"Disable 2FA error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante la disabilitazione 2FA"
        )

# Admin endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user = Depends(require_superadmin),
    request: Request = None
):
    """Create a new admin user (superadmin only)"""
    auth_service = get_auth_service(request)
    
    try:
        new_user = auth_service.create_user(user_data)
        
        # Log audit
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        auth_service.log_audit(
            current_user['id'],
            'CREATE_USER',
            'admin_user',
            str(new_user.id),
            f"Created user: {new_user.username}",
            ip_address,
            user_agent
        )
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante la creazione utente"
        )

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user = Depends(require_superadmin),
    request: Request = None,
    skip: int = 0,
    limit: int = 100
):
    """List all admin users (superadmin only)"""
    auth_service = get_auth_service(request)
    
    try:
        from contextlib import contextmanager
        import pymysql
        
        @contextmanager
        def get_db_connection(db_config):
            connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
            try:
                yield connection
            finally:
                connection.close()
        
        with get_db_connection(request.app.state.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, 
                       (SELECT is_enabled FROM user_2fa_settings WHERE user_id = u.id) as has_2fa
                FROM admin_users u
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, skip))
            
            users = cursor.fetchall()
            
            return [
                UserResponse(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    is_active=user['is_active'],
                    is_superadmin=user['is_superadmin'],
                    has_2fa=bool(user['has_2fa']),
                    created_at=user['created_at'],
                    last_login=user['last_login']
                )
                for user in users
            ]
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il recupero utenti"
        )

@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user = Depends(require_superadmin),
    request: Request = None
):
    """Toggle user active status (superadmin only)"""
    if user_id == current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi disabilitare il tuo stesso account"
        )
    
    try:
        from contextlib import contextmanager
        import pymysql
        
        @contextmanager
        def get_db_connection(db_config):
            connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
            try:
                yield connection
            finally:
                connection.close()
        
        with get_db_connection(request.app.state.db_config) as conn:
            cursor = conn.cursor()
            
            # Toggle active status
            cursor.execute("""
                UPDATE admin_users 
                SET is_active = NOT is_active 
                WHERE id = %s
            """, (user_id,))
            
            # Get updated status
            cursor.execute("SELECT is_active FROM admin_users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utente non trovato"
                )
            
            conn.commit()
            
            # Log audit
            auth_service = get_auth_service(request)
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("User-Agent")
            auth_service.log_audit(
                current_user['id'],
                'TOGGLE_USER_ACTIVE',
                'admin_user',
                str(user_id),
                f"User active status changed to: {result['is_active']}",
                ip_address,
                user_agent
            )
            
            return {
                "success": True,
                "is_active": result['is_active']
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Toggle user active error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'aggiornamento stato utente"
        )

@router.get("/audit-log")
async def get_audit_log(
    current_user = Depends(require_superadmin),
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None
):
    """Get audit log entries (superadmin only)"""
    try:
        from contextlib import contextmanager
        import pymysql
        
        @contextmanager
        def get_db_connection(db_config):
            connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
            try:
                yield connection
            finally:
                connection.close()
        
        with get_db_connection(request.app.state.db_config) as conn:
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT al.*, u.username, u.email
                FROM admin_audit_log al
                LEFT JOIN admin_users u ON al.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if user_id:
                query += " AND al.user_id = %s"
                params.append(user_id)
            
            if action:
                query += " AND al.action = %s"
                params.append(action)
            
            query += " ORDER BY al.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])
            
            cursor.execute(query, params)
            entries = cursor.fetchall()
            
            return {
                "entries": entries,
                "total": len(entries)
            }
    except Exception as e:
        logger.error(f"Get audit log error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il recupero audit log"
        )