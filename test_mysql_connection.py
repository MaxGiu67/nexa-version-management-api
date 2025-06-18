#!/usr/bin/env python3
"""Test MySQL connection with Railway database"""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

print("🔍 Testing MySQL connection...")
print(f"Host: {os.getenv('DB_HOST', 'tramway.proxy.rlwy.net')}")
print(f"Port: {os.getenv('DB_PORT', '20671')}")
print(f"Database: {os.getenv('DB_NAME', 'railway')}")

try:
    # Connect to MySQL
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'tramway.proxy.rlwy.net'),
        port=int(os.getenv('DB_PORT', '20671')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'),
        database=os.getenv('DB_NAME', 'railway'),
        charset='utf8mb4',
        connect_timeout=10
    )
    
    print("✅ Connected successfully!")
    
    # Test query
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 MySQL Version: {version[0]}")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📋 Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
    
    connection.close()
    print("\n✅ All tests passed! MySQL is working correctly.")
    
except pymysql.err.OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print("\n📌 Check that:")
    print("  1. The database is running on Railway")
    print("  2. Your IP is not blocked")
    print("  3. The credentials are correct")
except Exception as e:
    print(f"❌ Unexpected error: {e}")