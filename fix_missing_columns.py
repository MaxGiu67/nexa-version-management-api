#!/usr/bin/env python3
"""
Fix missing columns in database tables
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def fix_missing_columns():
    """Add missing columns to database tables"""
    
    print("🔧 Fixing missing columns in database tables...")
    
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
        
        # Check current structure of app_users table
        print("\n📊 Checking app_users table structure...")
        cursor.execute("DESCRIBE app_users")
        columns = cursor.fetchall()
        existing_columns = [col[0] for col in columns]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns to app_users
        if 'user_uuid' not in existing_columns:
            print("➕ Adding user_uuid column...")
            cursor.execute("""
                ALTER TABLE app_users 
                ADD COLUMN user_uuid VARCHAR(255) UNIQUE AFTER device_id
            """)
            
        if 'email' not in existing_columns:
            print("➕ Adding email column...")
            cursor.execute("""
                ALTER TABLE app_users 
                ADD COLUMN email VARCHAR(255) AFTER user_uuid
            """)
        
        # Check user_sessions table
        print("\n📊 Checking user_sessions table structure...")
        cursor.execute("DESCRIBE user_sessions")
        columns = cursor.fetchall()
        existing_columns = [col[0] for col in columns]
        print(f"Existing columns: {existing_columns}")
        
        if 'app_id' not in existing_columns:
            print("➕ Adding app_id column...")
            cursor.execute("""
                ALTER TABLE user_sessions 
                ADD COLUMN app_id INT AFTER user_id,
                ADD FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
            """)
            
        if 'session_uuid' not in existing_columns:
            print("➕ Adding session_uuid column...")
            cursor.execute("""
                ALTER TABLE user_sessions 
                ADD COLUMN session_uuid VARCHAR(255) AFTER session_id
            """)
            
        if 'platform' not in existing_columns:
            print("➕ Adding platform column...")
            cursor.execute("""
                ALTER TABLE user_sessions 
                ADD COLUMN platform VARCHAR(20) AFTER app_version
            """)
            
        if 'is_active' not in existing_columns:
            print("➕ Adding is_active column...")
            cursor.execute("""
                ALTER TABLE user_sessions 
                ADD COLUMN is_active BOOLEAN DEFAULT 0
            """)
        
        # Check user_app_installations table
        print("\n📊 Checking user_app_installations table structure...")
        cursor.execute("DESCRIBE user_app_installations")
        columns = cursor.fetchall()
        existing_columns = [col[0] for col in columns]
        print(f"Existing columns: {existing_columns}")
        
        if 'app_id' not in existing_columns:
            print("➕ Adding app_id column...")
            cursor.execute("""
                ALTER TABLE user_app_installations 
                ADD COLUMN app_id INT NOT NULL AFTER user_id,
                ADD FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
            """)
            
        if 'current_version' not in existing_columns:
            print("➕ Adding current_version column...")
            cursor.execute("""
                ALTER TABLE user_app_installations 
                ADD COLUMN current_version VARCHAR(50) AFTER app_version_id
            """)
            
        if 'platform' not in existing_columns:
            print("➕ Adding platform column...")
            cursor.execute("""
                ALTER TABLE user_app_installations 
                ADD COLUMN platform VARCHAR(20) AFTER current_version
            """)
            
        if 'last_update_date' not in existing_columns:
            print("➕ Adding last_update_date column...")
            cursor.execute("""
                ALTER TABLE user_app_installations 
                ADD COLUMN last_update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            """)
        
        # Add unique constraint if not exists
        try:
            cursor.execute("""
                ALTER TABLE user_app_installations 
                ADD UNIQUE KEY unique_user_app (user_id, app_id)
            """)
            print("➕ Added unique constraint on user_app_installations")
        except:
            print("⚠️  Unique constraint already exists")
        
        connection.commit()
        
        # Show final structure
        print("\n✅ All columns fixed! Final structure:")
        
        for table in ['app_users', 'user_sessions', 'user_app_installations']:
            print(f"\n📋 {table}:")
            cursor.execute(f"DESCRIBE {table}")
            for col in cursor.fetchall():
                print(f"   - {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Database structure fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_missing_columns()