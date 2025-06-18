#!/usr/bin/env python3
import psycopg2
import time

print("🔍 Testing PostgreSQL connection...")

# PostgreSQL connection from your JDBC URL
config = {
    'host': 'yamabiko.proxy.rlwy.net',
    'port': 41888,
    'user': 'postgres',  # Usually postgres, but check Railway
    'password': 'YOUR_PASSWORD',  # Get from Railway dashboard
    'database': 'railway'
}

try:
    start = time.time()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        connect_timeout=10
    )
    print(f"✅ Connected to PostgreSQL in {time.time() - start:.2f} seconds!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"📊 PostgreSQL version: {version[0]}")
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"📋 Found {len(tables)} tables")
    
    conn.close()
    print("✅ PostgreSQL connection test successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nNOTE: You need to get the PostgreSQL password from Railway dashboard!")