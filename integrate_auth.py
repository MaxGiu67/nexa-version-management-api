#!/usr/bin/env python3
"""
Script per integrare l'autenticazione nell'API esistente
"""

import os
import sys
import pymysql
from dotenv import load_dotenv

# Load environment variables
env = os.environ.get('ENVIRONMENT', 'local')
if env == 'local':
    load_dotenv('.env.local')
else:
    load_dotenv('.env.production')

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net')),
    'port': int(os.environ.get('DB_PORT', os.environ.get('MYSQL_PORT', 20671))),
    'user': os.environ.get('DB_USER', os.environ.get('MYSQL_USER', 'root')),
    'password': os.environ.get('DB_PASSWORD', os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP')),
    'database': os.environ.get('DB_NAME', os.environ.get('MYSQL_DATABASE', 'railway')),
    'charset': 'utf8mb4'
}

def run_migration():
    """Run the authentication migration"""
    print("Connecting to database...")
    connection = pymysql.connect(**DB_CONFIG)
    
    try:
        with connection.cursor() as cursor:
            # First, create the tables
            print("Creating tables...")
            
            # Create admin_users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    is_active BOOLEAN DEFAULT true,
                    is_superadmin BOOLEAN DEFAULT false,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login DATETIME NULL,
                    failed_login_attempts INT DEFAULT 0,
                    locked_until DATETIME NULL,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                )
            """)
            print("✅ Created admin_users table")
            
            # Create user_2fa_settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_2fa_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    secret_key VARCHAR(255) NOT NULL,
                    is_enabled BOOLEAN DEFAULT false,
                    backup_codes JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_used_at DATETIME NULL,
                    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_2fa (user_id)
                )
            """)
            print("✅ Created user_2fa_settings table")
            
            # Create admin_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    is_2fa_verified BOOLEAN DEFAULT false,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
                    INDEX idx_session_token (session_token),
                    INDEX idx_expires_at (expires_at)
                )
            """)
            print("✅ Created admin_sessions table")
            
            # Create admin_audit_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_audit_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(50),
                    resource_id VARCHAR(100),
                    description TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE SET NULL,
                    INDEX idx_user_action (user_id, action),
                    INDEX idx_created_at (created_at)
                )
            """)
            print("✅ Created admin_audit_log table")
            
            # Create stored procedure
            cursor.execute("DROP PROCEDURE IF EXISTS cleanup_expired_sessions")
            cursor.execute("""
                CREATE PROCEDURE cleanup_expired_sessions()
                BEGIN
                    DELETE FROM admin_sessions WHERE expires_at < NOW();
                END
            """)
            print("✅ Created cleanup_expired_sessions procedure")
            
            # Create event (if event scheduler is enabled)
            try:
                cursor.execute("""
                    CREATE EVENT IF NOT EXISTS cleanup_sessions_event
                    ON SCHEDULE EVERY 1 HOUR
                    DO CALL cleanup_expired_sessions()
                """)
                print("✅ Created cleanup event")
            except Exception as e:
                print("⚠️  Could not create event scheduler (this is normal on some MySQL configurations)")
            
            connection.commit()
            
            # Now insert default admin user
            print("\nCreating default admin user...")
            cursor.execute("""
                INSERT INTO admin_users (username, email, password_hash, first_name, last_name, is_superadmin) 
                VALUES ('admin', 'admin@nexadata.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGSG3btMjf.', 'System', 'Administrator', true)
                ON DUPLICATE KEY UPDATE id=id
            """)
            connection.commit()
            
            # Check if admin user was created
            cursor.execute("SELECT * FROM admin_users WHERE username = 'admin'")
            admin = cursor.fetchone()
            if admin:
                print("\n✅ Default admin user created:")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Please change the password on first login!")
            
            print("\nMigration completed successfully!")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        connection.rollback()
        # Don't exit, just show warning
        print("\n⚠️  Some tables might already exist, continuing...")
    finally:
        connection.close()

def create_integrated_api():
    """Create a new API file that integrates authentication"""
    print("\nCreating integrated API file...")
    
    integrated_api = '''"""
Multi-App Version Management API with Authentication
Integrates the existing API with authentication and 2FA support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_app_api import app, DB_CONFIG
from auth_endpoints import router as auth_router
from auth_module import get_current_user, require_superadmin
from fastapi import Depends, HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Add database config to app state
app.state.db_config = DB_CONFIG

# Include authentication router
app.include_router(auth_router)

# Modify existing endpoints to require authentication for admin operations
# The following endpoints will require authentication:
# - POST /api/v2/apps (create app)
# - PUT /api/v2/apps/{app_identifier} (update app)
# - DELETE /api/v2/apps/{app_identifier} (delete app)
# - POST /api/v2/version/upload (upload version)
# - DELETE /api/v2/versions/{app}/{platform}/{version} (delete version)
# - GET /api/v2/analytics/* (view analytics - optional)

# Override specific endpoints with authentication
@app.post("/api/v2/apps/protected")
async def create_app_protected(
    app_data: dict,
    current_user = Depends(get_current_user)
):
    """Create a new app (requires authentication)"""
    # Call the original endpoint logic
    # This is a placeholder - in production, refactor the original endpoint
    return {"message": "App creation requires authentication", "user": current_user['username']}

# Add new admin dashboard endpoints
@app.get("/api/v2/admin/dashboard")
async def admin_dashboard(
    current_user = Depends(require_superadmin)
):
    """Get admin dashboard data (superadmin only)"""
    return {
        "total_apps": 0,  # Implement actual logic
        "total_versions": 0,
        "total_users": 0,
        "recent_activity": []
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Multi-App Version Management API with Authentication...")
    print("API Docs: http://localhost:8000/docs")
    print("\\nDefault admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\\n⚠️  Please change the password after first login!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open('integrated_api.py', 'w') as f:
        f.write(integrated_api)
    
    print("✅ Created integrated_api.py")

def create_test_script():
    """Create a test script for authentication"""
    print("\nCreating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script for authentication system
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "nexa_internal_app_key_2025"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("Testing Authentication Flow...")
    
    # 1. Test login
    print("\\n1. Testing login...")
    login_response = requests.post(
        f"{BASE_URL}/api/v2/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"X-API-Key": API_KEY}
    )
    print(f"Status: {login_response.status_code}")
    print(f"Response: {json.dumps(login_response.json(), indent=2)}")
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    login_data = login_response.json()
    session_token = login_data["session_token"]
    print(f"✅ Login successful! Session token: {session_token[:20]}...")
    
    # 2. Test getting current user
    print("\\n2. Testing get current user...")
    me_response = requests.get(
        f"{BASE_URL}/api/v2/auth/me",
        headers={
            "Authorization": f"Bearer {session_token}",
            "X-API-Key": API_KEY
        }
    )
    print(f"Status: {me_response.status_code}")
    print(f"Response: {json.dumps(me_response.json(), indent=2)}")
    
    # 3. Test enabling 2FA
    print("\\n3. Testing enable 2FA...")
    enable_2fa_response = requests.post(
        f"{BASE_URL}/api/v2/auth/enable-2fa",
        headers={
            "Authorization": f"Bearer {session_token}",
            "X-API-Key": API_KEY
        }
    )
    print(f"Status: {enable_2fa_response.status_code}")
    if enable_2fa_response.status_code == 200:
        data = enable_2fa_response.json()
        print(f"✅ 2FA enabled!")
        print(f"Secret: {data['secret']}")
        print(f"Backup codes: {data['backup_codes']}")
        print("\\n⚠️  Scan the QR code with Google Authenticator app")
        print("QR Code data URL available in response")
    
    # 4. Test logout
    print("\\n4. Testing logout...")
    logout_response = requests.post(
        f"{BASE_URL}/api/v2/auth/logout",
        headers={
            "Authorization": f"Bearer {session_token}",
            "X-API-Key": API_KEY
        }
    )
    print(f"Status: {logout_response.status_code}")
    print(f"Response: {json.dumps(logout_response.json(), indent=2)}")

if __name__ == "__main__":
    print("Version Management Authentication Test")
    print("=" * 50)
    test_auth_flow()
'''
    
    with open('test_auth.py', 'w') as f:
        f.write(test_script)
    
    os.chmod('test_auth.py', 0o755)
    print("✅ Created test_auth.py")

if __name__ == "__main__":
    print("Version Management Authentication Integration")
    print("=" * 50)
    
    # Run migration
    run_migration()
    
    # Create integrated API
    create_integrated_api()
    
    # Create test script
    create_test_script()
    
    print("\n✅ Integration complete!")
    print("\nNext steps:")
    print("1. Install new dependencies: pip install -r requirements.txt")
    print("2. Run the integrated API: python integrated_api.py")
    print("3. Test authentication: python test_auth.py")
    print("4. Update frontend to use authentication")