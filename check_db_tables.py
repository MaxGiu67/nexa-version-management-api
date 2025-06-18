#!/usr/bin/env python3
"""Check database tables"""

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
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        print("=" * 50)
        for table in tables:
            print(f"- {table[0]}")
        
        # Check specific tables
        expected_tables = [
            'apps',
            'app_versions',
            'app_users',
            'user_app_installations',
            'user_sessions',
            'app_error_logs'
        ]
        
        print("\nTable status:")
        print("=" * 50)
        for table_name in expected_tables:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            exists = cursor.fetchone() is not None
            status = "✅" if exists else "❌"
            print(f"{status} {table_name}")
            
            if exists:
                # Get column info
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"   Columns: {', '.join([col[0] for col in columns[:5]])}...")
        
finally:
    if 'connection' in locals():
        connection.close()