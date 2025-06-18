#!/usr/bin/env python3
"""Check versions in database"""

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
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        # Get all versions
        cursor.execute("""
            SELECT 
                v.id,
                v.version,
                v.platform,
                v.version_code,
                v.is_active,
                a.app_identifier
            FROM app_versions v
            JOIN apps a ON v.app_id = a.id
            ORDER BY a.app_identifier, v.platform, v.version_code DESC
        """)
        versions = cursor.fetchall()
        
        print("Versions in database:")
        print("=" * 80)
        print(f"{'ID':<5} {'App':<20} {'Platform':<10} {'Version':<10} {'Code':<10} {'Active':<10}")
        print("-" * 80)
        
        for v in versions:
            active = "✅" if v['is_active'] else "❌"
            print(f"{v['id']:<5} {v['app_identifier']:<20} {v['platform']:<10} {v['version']:<10} {v['version_code']:<10} {active}")
        
        # Check specific version 0.7.1
        print("\nChecking for version 0.7.1:")
        cursor.execute("""
            SELECT id, platform, version_code 
            FROM app_versions 
            WHERE version = '0.7.1'
        """)
        result = cursor.fetchall()
        if result:
            for r in result:
                print(f"Found: ID={r['id']}, Platform={r['platform']}, Code={r['version_code']}")
        else:
            print("❌ Version 0.7.1 not found in database")
        
finally:
    if 'connection' in locals():
        connection.close()