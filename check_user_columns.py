#!/usr/bin/env python3
"""Check if app_users table has name column"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment
env = os.environ.get('ENVIRONMENT', 'local')
if env == 'local':
    load_dotenv('.env.local')
else:
    load_dotenv('.env.production')

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', os.environ.get('MYSQL_HOST', 'centerbeam.proxy.rlwy.net')),
    'port': int(os.environ.get('DB_PORT', os.environ.get('MYSQL_PORT', 22032))),
    'user': os.environ.get('DB_USER', os.environ.get('MYSQL_USER', 'root')),
    'password': os.environ.get('DB_PASSWORD', os.environ.get('MYSQL_PASSWORD', 'drypjZgjDSozOUrrJJsyUtNGqkDPVsEd')),
    'database': os.environ.get('DB_NAME', os.environ.get('MYSQL_DATABASE', 'railway')),
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        # Check current columns
        cursor.execute("DESCRIBE app_users")
        columns = cursor.fetchall()
        
        print("Current app_users columns:")
        print("=" * 60)
        
        has_email = False
        has_name = False
        
        for col in columns:
            print(f"{col[0]:<20} {col[1]:<30}")
            if col[0] == 'email':
                has_email = True
            if col[0] == 'name':
                has_name = True
        
        print("\nColumn status:")
        print(f"email column: {'✅ EXISTS' if has_email else '❌ MISSING'}")
        print(f"name column: {'✅ EXISTS' if has_name else '❌ MISSING'}")
        
        # Add missing columns
        if not has_name:
            print("\nAdding name column...")
            cursor.execute("""
                ALTER TABLE app_users 
                ADD COLUMN name VARCHAR(255) AFTER email
            """)
            connection.commit()
            print("✅ name column added")
            
            # Add index for name
            cursor.execute("""
                CREATE INDEX idx_app_users_name ON app_users(name)
            """)
            connection.commit()
            print("✅ Index on name column created")
        
finally:
    if 'connection' in locals():
        connection.close()