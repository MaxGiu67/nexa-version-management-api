#!/usr/bin/env python3
import pymysql
import time

print("🔍 Testing MySQL connection with confirmed credentials...")

config = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 20671,
    'user': 'root',
    'password': 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
    'database': 'railway',
    'connect_timeout': 10
}

try:
    start = time.time()
    conn = pymysql.connect(**config)
    print(f"✅ Connected in {time.time() - start:.2f} seconds!")
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"📊 Found {len(tables)} tables")
    
    conn.close()
    print("✅ Connection test successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Railway database might be sleeping - check dashboard")
    print("2. Firewall blocking connection")
    print("3. Railway might have IP restrictions")