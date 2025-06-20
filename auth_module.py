"""
Authentication module with 2FA support using Google Authenticator
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import bcrypt
import pyotp
import qrcode
import io
import base64
import secrets
import json
import logging
from contextlib import contextmanager
import pymysql

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class TwoFactorRequest(BaseModel):
    session_token: str
    totp_code: str

class LoginResponse(BaseModel):
    session_token: str
    requires_2fa: bool
    user: Optional[Dict[str, Any]] = None

class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_superadmin: bool
    has_2fa: bool
    created_at: datetime
    last_login: Optional[datetime]

# Database connection manager
@contextmanager
def get_db_connection(db_config):
    """Create a database connection context manager"""
    connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    try:
        yield connection
    finally:
        connection.close()

class AuthService:
    def __init__(self, db_config):
        self.db_config = db_config
        self.token_expiry_hours = 24
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new admin user"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                "SELECT id FROM admin_users WHERE username = %s OR email = %s",
                (user_data.username, user_data.email)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username o email già esistenti"
                )
            
            # Hash password and create user
            password_hash = self.hash_password(user_data.password)
            cursor.execute("""
                INSERT INTO admin_users (username, email, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_data.username,
                user_data.email,
                password_hash,
                user_data.first_name,
                user_data.last_name
            ))
            conn.commit()
            
            user_id = cursor.lastrowid
            return self.get_user_by_id(user_id)
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> LoginResponse:
        """Authenticate user with username and password"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            
            # Get user
            cursor.execute(
                "SELECT * FROM admin_users WHERE username = %s OR email = %s",
                (username, username)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenziali non valide"
                )
            
            # Check if account is locked
            if user['locked_until'] and user['locked_until'] > datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account bloccato fino alle {user['locked_until'].strftime('%H:%M:%S')}"
                )
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                # Increment failed attempts
                cursor.execute(
                    "UPDATE admin_users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = %s",
                    (user['id'],)
                )
                
                # Lock account if too many attempts
                if user['failed_login_attempts'] + 1 >= self.max_login_attempts:
                    locked_until = datetime.now() + timedelta(minutes=self.lockout_duration_minutes)
                    cursor.execute(
                        "UPDATE admin_users SET locked_until = %s WHERE id = %s",
                        (locked_until, user['id'])
                    )
                
                conn.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenziali non valide"
                )
            
            # Reset failed attempts on successful login
            cursor.execute(
                "UPDATE admin_users SET failed_login_attempts = 0, last_login = NOW() WHERE id = %s",
                (user['id'],)
            )
            
            # Create session
            session_token = self.generate_session_token()
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
            
            cursor.execute("""
                INSERT INTO admin_sessions (user_id, session_token, ip_address, user_agent, expires_at, is_2fa_verified)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user['id'], session_token, ip_address, user_agent, expires_at, False))
            
            # Check if user has 2FA enabled
            cursor.execute(
                "SELECT is_enabled FROM user_2fa_settings WHERE user_id = %s",
                (user['id'],)
            )
            has_2fa = cursor.fetchone()
            
            conn.commit()
            
            # Log authentication attempt
            self.log_audit(user['id'], 'LOGIN_ATTEMPT', 'user', str(user['id']), 
                          'Login attempt', ip_address, user_agent)
            
            if has_2fa and has_2fa['is_enabled']:
                return LoginResponse(
                    session_token=session_token,
                    requires_2fa=True
                )
            else:
                # Mark session as verified if no 2FA
                cursor.execute(
                    "UPDATE admin_sessions SET is_2fa_verified = TRUE WHERE session_token = %s",
                    (session_token,)
                )
                conn.commit()
                
                return LoginResponse(
                    session_token=session_token,
                    requires_2fa=False,
                    user=self._sanitize_user(user)
                )
    
    def verify_2fa(self, session_token: str, totp_code: str) -> Dict[str, Any]:
        """Verify 2FA code"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            
            # Get session
            cursor.execute("""
                SELECT s.*, u.* FROM admin_sessions s
                JOIN admin_users u ON s.user_id = u.id
                WHERE s.session_token = %s AND s.expires_at > NOW()
            """, (session_token,))
            
            session = cursor.fetchone()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Sessione non valida o scaduta"
                )
            
            # Get 2FA settings
            cursor.execute(
                "SELECT * FROM user_2fa_settings WHERE user_id = %s AND is_enabled = TRUE",
                (session['user_id'],)
            )
            twofa_settings = cursor.fetchone()
            
            if not twofa_settings:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="2FA non abilitato per questo utente"
                )
            
            # Verify TOTP code
            totp = pyotp.TOTP(twofa_settings['secret_key'])
            if totp.verify(totp_code, valid_window=1):
                # Mark session as verified
                cursor.execute(
                    "UPDATE admin_sessions SET is_2fa_verified = TRUE WHERE session_token = %s",
                    (session_token,)
                )
                cursor.execute(
                    "UPDATE user_2fa_settings SET last_used_at = NOW() WHERE user_id = %s",
                    (session['user_id'],)
                )
                conn.commit()
                
                return {
                    "success": True,
                    "user": self._sanitize_user(session)
                }
            else:
                # Check backup codes
                backup_codes = json.loads(twofa_settings['backup_codes'] or '[]')
                if totp_code in backup_codes:
                    # Remove used backup code
                    backup_codes.remove(totp_code)
                    cursor.execute(
                        "UPDATE user_2fa_settings SET backup_codes = %s WHERE user_id = %s",
                        (json.dumps(backup_codes), session['user_id'])
                    )
                    cursor.execute(
                        "UPDATE admin_sessions SET is_2fa_verified = TRUE WHERE session_token = %s",
                        (session_token,)
                    )
                    conn.commit()
                    
                    return {
                        "success": True,
                        "user": self._sanitize_user(session),
                        "backup_code_used": True,
                        "remaining_backup_codes": len(backup_codes)
                    }
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Codice 2FA non valido"
                )
    
    def enable_2fa(self, user_id: int) -> Enable2FAResponse:
        """Enable 2FA for user"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            
            # Get user
            cursor.execute("SELECT * FROM admin_users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utente non trovato"
                )
            
            # Generate secret
            secret = pyotp.random_base32()
            
            # Generate QR code
            provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user['email'],
                issuer_name='Nexa Version Manager'
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            qr_code_base64 = base64.b64encode(buf.getvalue()).decode()
            
            # Generate backup codes
            backup_codes = self.generate_backup_codes()
            
            # Save to database
            cursor.execute("""
                INSERT INTO user_2fa_settings (user_id, secret_key, backup_codes, is_enabled)
                VALUES (%s, %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE
                secret_key = VALUES(secret_key),
                backup_codes = VALUES(backup_codes),
                is_enabled = TRUE,
                updated_at = NOW()
            """, (user_id, secret, json.dumps(backup_codes)))
            
            conn.commit()
            
            return Enable2FAResponse(
                secret=secret,
                qr_code=f"data:image/png;base64,{qr_code_base64}",
                backup_codes=backup_codes
            )
    
    def disable_2fa(self, user_id: int):
        """Disable 2FA for user"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_2fa_settings SET is_enabled = FALSE WHERE user_id = %s",
                (user_id,)
            )
            conn.commit()
    
    def get_current_user(self, session_token: str) -> Dict[str, Any]:
        """Get current user from session token"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.*, s.is_2fa_verified, 
                       (SELECT is_enabled FROM user_2fa_settings WHERE user_id = u.id) as has_2fa
                FROM admin_sessions s
                JOIN admin_users u ON s.user_id = u.id
                WHERE s.session_token = %s 
                AND s.expires_at > NOW()
                AND u.is_active = TRUE
            """, (session_token,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Sessione non valida o scaduta"
                )
            
            if result['has_2fa'] and not result['is_2fa_verified']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Verifica 2FA richiesta"
                )
            
            # Update last activity
            cursor.execute(
                "UPDATE admin_sessions SET last_activity = NOW() WHERE session_token = %s",
                (session_token,)
            )
            conn.commit()
            
            return self._sanitize_user(result)
    
    def get_user_by_id(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, 
                       (SELECT is_enabled FROM user_2fa_settings WHERE user_id = u.id) as has_2fa
                FROM admin_users u
                WHERE u.id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utente non trovato"
                )
            
            return UserResponse(
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
    
    def logout(self, session_token: str):
        """Logout user by invalidating session"""
        with get_db_connection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM admin_sessions WHERE session_token = %s",
                (session_token,)
            )
            conn.commit()
    
    def log_audit(self, user_id: Optional[int], action: str, resource_type: Optional[str] = None,
                  resource_id: Optional[str] = None, description: Optional[str] = None,
                  ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log audit entry"""
        try:
            with get_db_connection(self.db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO admin_audit_log 
                    (user_id, action, resource_type, resource_id, description, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, action, resource_type, resource_id, description, ip_address, user_agent))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log audit: {str(e)}")
    
    def _sanitize_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from user data"""
        sanitized = {k: v for k, v in user.items() if k not in ['password_hash', 'secret_key']}
        sanitized['has_2fa'] = bool(user.get('has_2fa', False))
        return sanitized

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> Dict[str, Any]:
    """FastAPI dependency to get current user from bearer token"""
    auth_service = AuthService(request.app.state.db_config)
    return auth_service.get_current_user(credentials.credentials)

# Dependency to require superadmin
async def require_superadmin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require superadmin privileges"""
    if not current_user.get('is_superadmin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilegi di superadmin richiesti"
        )
    return current_user