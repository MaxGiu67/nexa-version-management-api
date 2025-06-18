#!/usr/bin/env python3
"""Test user insert with name"""

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
    with connection.cursor() as cursor:
        # Test direct insert
        user_uuid = "test-user-direct"
        email = "test@example.com"
        name = "Test User"
        device_info = {"test": "device"}
        app_id = 1
        device_id = "test-device"
        
        try:
            cursor.execute(
                """INSERT INTO app_users (user_uuid, email, name, device_info, app_id, device_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_uuid, email, name, json.dumps(device_info), app_id, device_id)
            )
            connection.commit()
            print("✅ Successfully inserted user with name")
            
            # Clean up
            cursor.execute("DELETE FROM app_users WHERE user_uuid = %s", (user_uuid,))
            connection.commit()
            print("✅ Cleaned up test user")
            
        except Exception as e:
            print(f"❌ Error inserting user: {e}")
            connection.rollback()
        
finally:
    if 'connection' in locals():
        connection.close()