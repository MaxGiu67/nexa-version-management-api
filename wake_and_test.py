#!/usr/bin/env python3
import pymysql
import time
import socket

print("🔍 MySQL Connection Diagnostic Tool")
print("=" * 50)

# Test 1: DNS Resolution
print("\n1️⃣ Testing DNS resolution...")
try:
    ip = socket.gethostbyname('tramway.proxy.rlwy.net')
    print(f"✅ DNS resolved to: {ip}")
except Exception as e:
    print(f"❌ DNS resolution failed: {e}")

# Test 2: Port connectivity
print("\n2️⃣ Testing port connectivity...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    result = sock.connect_ex(('tramway.proxy.rlwy.net', 20671))
    if result == 0:
        print("✅ Port 20671 is open")
    else:
        print(f"❌ Port 20671 is closed (error code: {result})")
except Exception as e:
    print(f"❌ Port test failed: {e}")
finally:
    sock.close()

# Test 3: MySQL Connection with multiple attempts
print("\n3️⃣ Testing MySQL connection (3 attempts)...")

config = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 20671,
    'user': 'root',
    'password': 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
    'database': 'railway',
    'charset': 'utf8mb4',
    'connect_timeout': 10,
    'autocommit': True
}

for attempt in range(3):
    print(f"\nAttempt {attempt + 1}/3...")
    try:
        start = time.time()
        
        # Try different connection parameters
        if attempt == 1:
            # Try without database selection
            config_copy = config.copy()
            del config_copy['database']
            conn = pymysql.connect(**config_copy)
        elif attempt == 2:
            # Try with ssl disabled
            config['ssl_disabled'] = True
            conn = pymysql.connect(**config)
        else:
            # Standard connection
            conn = pymysql.connect(**config)
            
        elapsed = time.time() - start
        print(f"✅ Connected successfully in {elapsed:.2f} seconds!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 MySQL Version: {version[0]}")
        
        # Show databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print(f"📋 Databases: {[db[0] for db in databases]}")
        
        conn.close()
        print("\n✅ All tests passed! Database is accessible.")
        break
        
    except pymysql.err.OperationalError as e:
        elapsed = time.time() - start
        print(f"❌ Connection failed after {elapsed:.2f} seconds")
        print(f"   Error code: {e.args[0]}")
        print(f"   Error message: {e.args[1]}")
        
        if "2003" in str(e):
            print("   → Can't connect to MySQL server (network issue)")
        elif "2013" in str(e):
            print("   → Lost connection during query (timeout)")
        elif "1045" in str(e):
            print("   → Access denied (wrong credentials)")
            
        if attempt < 2:
            print("   Waiting 5 seconds before retry...")
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("📌 SOLUTIONS:")
print("1. Go to railway.app and click on your MySQL service")
print("2. Check the 'Logs' tab for any errors")
print("3. Verify the connection string in Variables tab")
print("4. Try using Railway CLI: railway mysql")
print("5. Consider restarting the MySQL service on Railway")