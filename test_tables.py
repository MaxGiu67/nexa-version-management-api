#!/usr/bin/env python3
"""
Test what tables exist in the database
"""

import pymysql
import os

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQL_PORT', 20671)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'),
    'database': os.environ.get('MYSQL_DATABASE', 'railway'),
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if user_app_installations exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'user_app_installations'
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("\n✅ user_app_installations table exists")
            cursor.execute("DESCRIBE user_app_installations")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("\n❌ user_app_installations table DOES NOT exist")
            
    connection.close()
    
except Exception as e:
    print(f"Error: {str(e)}")