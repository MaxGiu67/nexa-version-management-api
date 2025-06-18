#!/usr/bin/env python3
"""
Add release_date column to app_versions table
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def add_release_date():
    """Add release_date column to app_versions"""
    
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
        
        print("🔧 Adding release_date column to app_versions...")
        
        try:
            cursor.execute("""
                ALTER TABLE app_versions 
                ADD COLUMN release_date DATETIME DEFAULT CURRENT_TIMESTAMP AFTER download_count
            """)
            print("✅ Added release_date column")
            
            # Update existing records to use created_at as release_date
            cursor.execute("""
                UPDATE app_versions 
                SET release_date = created_at 
                WHERE release_date IS NULL
            """)
            print("✅ Updated existing records")
            
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("⚠️  release_date column already exists")
            else:
                print(f"❌ Error: {e}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_release_date()