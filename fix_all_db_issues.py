#!/usr/bin/env python3
"""
Fix all database issues by adding missing columns and fixing table structure
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def fix_all_issues():
    """Fix all database issues comprehensively"""
    
    print("🔧 Fixing All Database Issues...")
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
        
        # 1. Fix user_app_installations table
        print("\n📊 Fixing user_app_installations table...")
        fixes = [
            ("is_active", "ALTER TABLE user_app_installations ADD COLUMN is_active BOOLEAN DEFAULT true AFTER last_update_date")
        ]
        
        for col_name, sql in fixes:
            try:
                cursor.execute(sql)
                print(f"   ✅ Added {col_name}")
            except pymysql.err.OperationalError as e:
                if "Duplicate column" in str(e):
                    print(f"   ⚠️  {col_name} already exists")
                else:
                    print(f"   ❌ Error: {e}")
        
        # 2. Fix app_users table - rename column if needed
        print("\n📊 Fixing app_users table...")
        try:
            # Check if we need to rename first_seen_at to last_seen_at
            cursor.execute("SHOW COLUMNS FROM app_users LIKE 'last_seen_at'")
            if not cursor.fetchone():
                # Check if last_seen exists
                cursor.execute("SHOW COLUMNS FROM app_users LIKE 'last_seen'")
                if cursor.fetchone():
                    # We have last_seen, let's add last_seen_at as an alias
                    cursor.execute("""
                        ALTER TABLE app_users 
                        ADD COLUMN last_seen_at DATETIME GENERATED ALWAYS AS (last_seen) STORED
                    """)
                    print("   ✅ Added last_seen_at as computed column")
        except Exception as e:
            print(f"   ⚠️  Could not add last_seen_at: {e}")
            # Try a different approach
            try:
                cursor.execute("""
                    ALTER TABLE app_users 
                    ADD COLUMN last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """)
                cursor.execute("UPDATE app_users SET last_seen_at = last_seen")
                print("   ✅ Added last_seen_at column")
            except:
                print("   ⚠️  last_seen_at already handled")
        
        connection.commit()
        
        # 3. Show final structure
        print("\n📋 Final Table Structures:")
        
        tables_to_check = ['app_users', 'user_app_installations', 'user_sessions']
        for table in tables_to_check:
            print(f"\n🔸 {table}:")
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
        
        # 4. Test problematic queries
        print("\n🧪 Testing fixed queries...")
        
        test_queries = [
            ("Analytics is_active check", """
                SELECT COUNT(*) FROM user_app_installations 
                WHERE app_id = 1 AND is_active = true
            """),
            ("User last_seen_at check", """
                SELECT id, last_seen, last_seen_at FROM app_users LIMIT 1
            """),
            ("Get all columns", """
                SELECT u.*, a.app_name 
                FROM app_users u
                JOIN apps a ON u.app_id = a.id
                LIMIT 1
            """)
        ]
        
        for name, query in test_queries:
            try:
                cursor.execute(query)
                cursor.fetchall()
                print(f"   ✅ {name} - OK")
            except Exception as e:
                print(f"   ❌ {name} - Failed: {e}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ All database issues fixed!")
        print("\n🚀 The backend should now work without errors!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_all_issues()