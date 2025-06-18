#!/usr/bin/env python3
"""
Simple MySQL connection test with different configurations
"""

import pymysql
import ssl
import time

# Direct connection parameters
host = 'tramway.proxy.rlwy.net'
port = 20671
user = 'root'
password = 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'
database = 'railway'

def test_basic_connection():
    """Test with basic configuration"""
    print("Test 1: Basic connection...")
    try:
        start = time.time()
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=60
        )
        elapsed = time.time() - start
        print(f"✅ Success! Connected in {elapsed:.2f} seconds")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_ssl_connection():
    """Test with SSL configuration"""
    print("\nTest 2: Connection with SSL...")
    try:
        start = time.time()
        # Create SSL context that accepts any certificate
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=60,
            ssl=ssl_context
        )
        elapsed = time.time() - start
        print(f"✅ Success! Connected with SSL in {elapsed:.2f} seconds")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_minimal_connection():
    """Test with minimal parameters"""
    print("\nTest 3: Minimal connection (no database selection)...")
    try:
        start = time.time()
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=60
        )
        elapsed = time.time() - start
        print(f"✅ Success! Connected in {elapsed:.2f} seconds")
        
        # Try to select database after connection
        cursor = conn.cursor()
        cursor.execute(f"USE {database}")
        print(f"✅ Selected database '{database}'")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_connection_with_protocol():
    """Test with different protocol settings"""
    print("\nTest 4: Connection with protocol settings...")
    try:
        start = time.time()
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=60,
            autocommit=True,
            local_infile=False
        )
        elapsed = time.time() - start
        print(f"✅ Success! Connected in {elapsed:.2f} seconds")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Query test successful: {result}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_mysql_url():
    """Test parsing MySQL URL format"""
    print("\nTest 5: MySQL URL format...")
    mysql_url = f"mysql://{user}:{password}@{host}:{port}/{database}"
    print(f"URL: mysql://{user}:{'*' * 8}@{host}:{port}/{database}")
    
    try:
        # Parse URL manually since pymysql doesn't support URLs directly
        from urllib.parse import urlparse
        parsed = urlparse(mysql_url)
        
        start = time.time()
        conn = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            connect_timeout=60
        )
        elapsed = time.time() - start
        print(f"✅ Success! Connected via URL parsing in {elapsed:.2f} seconds")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("Railway MySQL Connection Tests")
    print("=" * 50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Basic", test_basic_connection()))
    results.append(("SSL", test_ssl_connection()))
    results.append(("Minimal", test_minimal_connection()))
    results.append(("Protocol", test_connection_with_protocol()))
    results.append(("URL", test_mysql_url()))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS:")
    if not any(r[1] for r in results):
        print("❌ All connection attempts failed!")
        print("Possible issues:")
        print("1. Railway database might be down or paused")
        print("2. Credentials might have changed")
        print("3. Network/firewall issues")
        print("4. Railway might have IP restrictions enabled")
        print("\nAction items:")
        print("1. Check Railway dashboard for database status")
        print("2. Verify credentials in Railway variables tab")
        print("3. Try connecting from Railway's own terminal")
        print("4. Check if database needs to be 'woken up'")
    else:
        successful = [r[0] for r in results if r[1]]
        print(f"✅ Successful connection methods: {', '.join(successful)}")
        print("Use one of these methods in your application")