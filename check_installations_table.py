#!/usr/bin/env python3
"""Check user_app_installations table structure"""

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
        # Get user_app_installations structure
        cursor.execute("DESCRIBE user_app_installations")
        columns = cursor.fetchall()
        
        print("user_app_installations table structure:")
        print("=" * 80)
        print(f"{'Field':<25} {'Type':<30} {'Null':<5} {'Key':<5} {'Default':<10}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<25} {col[1]:<30} {col[2]:<5} {col[3]:<5} {str(col[4]):<10}")
        
finally:
    if 'connection' in locals():
        connection.close()