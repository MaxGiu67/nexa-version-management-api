#!/usr/bin/env python3
"""Check saved users with name"""

import pymysql
import json
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
        # Get recent users with name
        cursor.execute("""
            SELECT id, user_uuid, email, name, created_at
            FROM app_users
            WHERE email LIKE '%@nexadata.it'
            ORDER BY id DESC
            LIMIT 10
        """)
        users = cursor.fetchall()
        
        print("Recent users with @nexadata.it email:")
        print("=" * 100)
        print(f"{'ID':<5} {'UUID':<40} {'Email':<30} {'Name':<25} {'Created'}")
        print("-" * 100)
        
        for user in users:
            print(f"{user['id']:<5} {user['user_uuid']:<40} {user['email']:<30} {user['name'] or 'N/A':<25} {user['created_at']}")
        
        # Get recent sessions
        print("\n\nRecent sessions:")
        print("=" * 100)
        cursor.execute("""
            SELECT 
                s.id,
                u.name,
                u.email,
                s.app_version,
                s.platform,
                s.start_time
            FROM user_sessions s
            JOIN app_users u ON s.user_id = u.id
            WHERE u.email LIKE '%@nexadata.it'
            ORDER BY s.id DESC
            LIMIT 10
        """)
        sessions = cursor.fetchall()
        
        print(f"{'ID':<5} {'User Name':<25} {'Email':<30} {'Version':<10} {'Platform':<10} {'Started'}")
        print("-" * 100)
        
        for session in sessions:
            print(f"{session['id']:<5} {session['name'] or 'N/A':<25} {session['email']:<30} {session['app_version']:<10} {session['platform']:<10} {session['start_time']}")
        
finally:
    if 'connection' in locals():
        connection.close()