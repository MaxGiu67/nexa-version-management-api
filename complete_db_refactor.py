#!/usr/bin/env python3
"""
Complete database refactoring to align with multi_app_api.py requirements
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def refactor_database():
    """Complete database refactoring"""
    
    print("🔄 Complete Database Refactoring...")
    print("=" * 60)
    
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 1. Add missing columns to user_sessions
        print("\n📊 Fixing user_sessions table...")
        missing_columns = [
            ("device_info", "ALTER TABLE user_sessions ADD COLUMN device_info JSON AFTER metadata")
        ]
        
        for col_name, sql in missing_columns:
            try:
                cursor.execute(sql)
                print(f"   ✅ Added {col_name}")
            except pymysql.err.OperationalError as e:
                if "Duplicate column" in str(e):
                    print(f"   ⚠️  {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
        
        # 2. Add missing columns to user_app_installations
        print("\n📊 Fixing user_app_installations table...")
        missing_columns = [
            ("install_date", "ALTER TABLE user_app_installations ADD COLUMN install_date DATETIME DEFAULT CURRENT_TIMESTAMP AFTER installed_at")
        ]
        
        for col_name, sql in missing_columns:
            try:
                cursor.execute(sql)
                print(f"   ✅ Added {col_name}")
            except pymysql.err.OperationalError as e:
                if "Duplicate column" in str(e):
                    print(f"   ⚠️  {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
        
        # 3. Add missing columns to app_users
        print("\n📊 Fixing app_users table...")
        missing_columns = [
            ("first_seen_at", "ALTER TABLE app_users ADD COLUMN first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER created_at")
        ]
        
        for col_name, sql in missing_columns:
            try:
                cursor.execute(sql)
                print(f"   ✅ Added {col_name}")
            except pymysql.err.OperationalError as e:
                if "Duplicate column" in str(e):
                    print(f"   ⚠️  {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
        
        connection.commit()
        
        # 4. Show current structure
        print("\n📋 Current Database Structure:")
        tables = ['apps', 'app_versions', 'app_users', 'user_sessions', 'user_app_installations', 'app_error_logs']
        
        for table in tables:
            print(f"\n🔸 Table: {table}")
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
        
        # 5. Create indexes for performance
        print("\n🔧 Creating indexes...")
        indexes = [
            ("idx_sessions_device", "CREATE INDEX idx_sessions_device ON user_sessions(user_id, start_time DESC)"),
            ("idx_users_uuid", "CREATE INDEX idx_users_uuid ON app_users(user_uuid)"),
            ("idx_users_email", "CREATE INDEX idx_users_email ON app_users(email)"),
            ("idx_installations_date", "CREATE INDEX idx_installations_date ON user_app_installations(install_date DESC)")
        ]
        
        for idx_name, sql in indexes:
            try:
                cursor.execute(sql)
                print(f"   ✅ Created index: {idx_name}")
            except pymysql.err.OperationalError as e:
                if "Duplicate key name" in str(e):
                    print(f"   ⚠️  Index {idx_name} already exists")
                else:
                    print(f"   ❌ Error creating index {idx_name}: {e}")
        
        connection.commit()
        
        # 6. Insert test data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM app_users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("\n📝 Inserting sample data...")
            
            # Get app_id
            cursor.execute("SELECT id FROM apps WHERE app_identifier = 'nexa-timesheet'")
            app_id = cursor.fetchone()[0]
            
            # Insert a test user
            cursor.execute("""
                INSERT INTO app_users 
                (app_id, device_id, user_uuid, email, device_info, platform, app_version)
                VALUES 
                (%s, 'test-device-001', 'test-uuid-001', 'test@example.com', 
                 '{"model": "Test Device", "os": "Android 13"}', 'android', '1.0.0')
            """, (app_id,))
            
            user_id = cursor.lastrowid
            
            # Insert a test session
            cursor.execute("""
                INSERT INTO user_sessions 
                (user_id, app_id, session_id, session_uuid, app_version, platform, device_info)
                VALUES 
                (%s, %s, 'test-session-001', 'test-session-uuid-001', '1.0.0', 'android',
                 '{"model": "Test Device", "os": "Android 13"}')
            """, (user_id, app_id))
            
            print("   ✅ Sample data inserted")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✅ Database refactoring completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Restart the backend: python multi_app_api.py")
        print("2. The frontend should now load without errors")
        
    except Exception as e:
        print(f"\n❌ Error during refactoring: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    refactor_database()