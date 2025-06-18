#!/usr/bin/env python3
import socket
import pymysql
import os
from dotenv import load_dotenv
import time

load_dotenv('.env.local')

print("🔍 Quick Database Connection Test")
print("=" * 50)

# Test 1: Network connectivity
host = os.getenv('MYSQL_HOST', 'tramway.proxy.rlwy.net')
port = int(os.getenv('MYSQL_PORT', '20671'))

print(f"1️⃣ Testing network connection to {host}:{port}")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    result = sock.connect_ex((host, port))
    if result == 0:
        print("✅ Port is open - server is reachable")
    else:
        print("❌ Port is closed or unreachable")
        print("   The database server might be down")
except Exception as e:
    print(f"❌ Network error: {e}")
finally:
    sock.close()

# Test 2: MySQL connection with very short timeout
print(f"\n2️⃣ Testing MySQL connection (5 second timeout)")
try:
    start_time = time.time()
    connection = pymysql.connect(
        host=host,
        port=port,
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'railway'),
        connect_timeout=5
    )
    print(f"✅ Connected in {time.time() - start_time:.2f} seconds")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed after {time.time() - start_time:.2f} seconds")
    print(f"   Error: {e}")
    
print("\n🔧 Solutions:")
print("1. Go to railway.app and click on your MySQL service")
print("2. Wait 1-2 minutes for it to wake up")
print("3. Check if credentials have changed in Railway dashboard")
print("4. Try using Railway CLI: railway variables")