#!/usr/bin/env python3
"""
Script per verificare l'integrazione dell'autenticazione in multi_app_api.py
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['bcrypt', 'pyotp', 'qrcode', 'PIL']
    missing = []
    
    for module in required:
        try:
            if module == 'PIL':
                __import__('PIL')
            else:
                __import__(module)
            print(f"  ✅ {module} installed")
        except ImportError:
            print(f"  ❌ {module} missing")
            missing.append(module)
    
    if missing:
        print("\n⚠️  Missing dependencies detected!")
        print("Run: pip install bcrypt pyotp qrcode pillow")
        return False
    
    return True

def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'multi_app_api.py',
        'auth_module.py',
        'auth_endpoints.py',
        'auth_migration.sql'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} exists")
        else:
            print(f"  ❌ {file} missing")
            missing.append(file)
    
    if missing:
        print("\n⚠️  Missing files detected!")
        return False
    
    return True

def check_database_tables():
    """Check if auth tables exist in database"""
    print("\n🔍 Checking database tables...")
    
    try:
        import pymysql
        from dotenv import load_dotenv
        
        # Load environment
        env = os.environ.get('ENVIRONMENT', 'local')
        if env == 'local':
            load_dotenv('.env.local')
        else:
            load_dotenv('.env.production')
        
        # Database config
        DB_CONFIG = {
            'host': os.environ.get('DB_HOST', os.environ.get('MYSQL_HOST')),
            'port': int(os.environ.get('DB_PORT', os.environ.get('MYSQL_PORT', 3306))),
            'user': os.environ.get('DB_USER', os.environ.get('MYSQL_USER')),
            'password': os.environ.get('DB_PASSWORD', os.environ.get('MYSQL_PASSWORD')),
            'database': os.environ.get('DB_NAME', os.environ.get('MYSQL_DATABASE')),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**DB_CONFIG)
        
        tables_to_check = [
            'admin_users',
            'user_2fa_settings',
            'admin_sessions',
            'admin_audit_log'
        ]
        
        with connection.cursor() as cursor:
            for table in tables_to_check:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone():
                    print(f"  ✅ Table {table} exists")
                else:
                    print(f"  ❌ Table {table} missing")
                    print("     Run: python integrate_auth.py")
                    return False
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        return False

def test_import():
    """Test if the integrated API can be imported"""
    print("\n🔍 Testing API import...")
    
    try:
        import multi_app_api
        print("  ✅ multi_app_api imported successfully")
        
        # Check if auth router is included
        if hasattr(multi_app_api.app, 'routes'):
            auth_routes = [r for r in multi_app_api.app.routes if '/auth/' in str(r.path)]
            if auth_routes:
                print(f"  ✅ Found {len(auth_routes)} auth routes")
            else:
                print("  ⚠️  No auth routes found")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def main():
    print("="*60)
    print("Version Management Authentication Integration Checker")
    print("="*60)
    
    all_good = True
    
    # Run checks
    all_good &= check_dependencies()
    all_good &= check_files()
    all_good &= check_database_tables()
    all_good &= test_import()
    
    print("\n" + "="*60)
    if all_good:
        print("✅ All checks passed! Authentication is integrated.")
        print("\nYou can now run: python multi_app_api.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nSteps to fix:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run integration: python integrate_auth.py")
        print("3. Start the API: python multi_app_api.py")
    print("="*60)

if __name__ == "__main__":
    main()