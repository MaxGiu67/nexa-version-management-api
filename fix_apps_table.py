#!/usr/bin/env python3
"""
Fix apps table structure to match multi_app_api.py expectations
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def fix_apps_table():
    """Update apps table structure to match API requirements"""
    
    print("🔧 Fixing apps table structure...")
    
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
        
        # Drop the old apps table
        print("🗑️  Dropping old apps table...")
        cursor.execute("DROP TABLE IF EXISTS apps CASCADE")
        
        # Create new apps table with correct structure
        print("🔨 Creating new apps table...")
        cursor.execute("""
            CREATE TABLE apps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_identifier VARCHAR(100) UNIQUE NOT NULL,
                app_name VARCHAR(255) NOT NULL,
                description TEXT,
                platform_support JSON DEFAULT '["android", "ios"]',
                is_active BOOLEAN DEFAULT true,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_apps_identifier (app_identifier)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Insert nexa-timesheet app with correct fields
        print("📝 Inserting nexa-timesheet app...")
        cursor.execute("""
            INSERT INTO apps (app_identifier, app_name, description, platform_support) 
            VALUES (
                'nexa-timesheet',
                'Nexa Timesheet',
                'Mobile app for managing employee timesheets at NEXA DATA Srl',
                '["android", "ios"]'
            )
        """)
        
        connection.commit()
        
        # Verify
        cursor.execute("SELECT * FROM apps")
        apps = cursor.fetchall()
        print(f"\n✅ Apps table fixed! Found {len(apps)} apps")
        
        cursor.execute("DESCRIBE apps")
        columns = cursor.fetchall()
        print("\n📊 New table structure:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Table structure fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_apps_table()