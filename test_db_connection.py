#!/usr/bin/env python3
"""
Test database connection to Railway MySQL
"""

import pymysql
import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables
env = os.environ.get('ENVIRONMENT', 'local')
if env == 'local':
    load_dotenv('.env.local')
else:
    load_dotenv('.env.production')

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQL_PORT', 20671)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'),
    'database': os.environ.get('MYSQL_DATABASE', 'railway'),
    'charset': 'utf8mb4'
}

def test_connection():
    """Test the database connection"""
    print("Testing database connection...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Port: {DB_CONFIG['port']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Password: {'*' * len(DB_CONFIG['password'])}")
    
    try:
        # Try to connect with different timeout values
        print("\nAttempting connection with 30 second timeout...")
        start_time = time.time()
        
        connection = pymysql.connect(
            **DB_CONFIG,
            connect_timeout=30,
            read_timeout=30,
            write_timeout=30
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ Connection successful! (took {elapsed_time:.2f} seconds)")
        
        # Test query
        with connection.cursor() as cursor:
            # Check if we can run a simple query
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL Version: {version[0]}")
            
            # Check if apps table exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = 'apps'
            """, (DB_CONFIG['database'],))
            
            table_exists = cursor.fetchone()[0] > 0
            if table_exists:
                print("✅ Table 'apps' exists")
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM apps")
                count = cursor.fetchone()[0]
                print(f"   Records in apps table: {count}")
            else:
                print("❌ Table 'apps' does not exist")
            
            # List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name
            """, (DB_CONFIG['database'],))
            
            tables = cursor.fetchall()
            print(f"\nTables in database '{DB_CONFIG['database']}':")
            for table in tables:
                print(f"   - {table[0]}")
        
        connection.close()
        print("\n✅ Connection closed successfully")
        
    except pymysql.err.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print(f"Error code: {e.args[0]}")
        print(f"Error message: {e.args[1]}")
        
        # Common error troubleshooting
        if e.args[0] == 2003:
            print("\n🔍 Troubleshooting tips for 'Can't connect' error:")
            print("1. Check if the host is reachable:")
            print(f"   ping {DB_CONFIG['host']}")
            print("2. Check if the port is open:")
            print(f"   telnet {DB_CONFIG['host']} {DB_CONFIG['port']}")
            print("3. Verify Railway database is still active")
            print("4. Check Railway dashboard for any maintenance notices")
        elif e.args[0] == 1045:
            print("\n🔍 Access denied - check your credentials")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")

def test_network():
    """Test network connectivity to the host"""
    import socket
    
    print("\n📡 Testing network connectivity...")
    
    host = DB_CONFIG['host']
    port = DB_CONFIG['port']
    
    try:
        # DNS resolution test
        print(f"Resolving {host}...")
        ip = socket.gethostbyname(host)
        print(f"✅ Resolved to: {ip}")
        
        # Port connectivity test
        print(f"\nTesting connection to {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open")
        else:
            print(f"❌ Port {port} is closed or filtered (error code: {result})")
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
    except socket.timeout:
        print(f"❌ Connection timeout - host may be unreachable")
    except Exception as e:
        print(f"❌ Network test failed: {e}")

if __name__ == "__main__":
    print("Railway MySQL Connection Test")
    print("=" * 50)
    
    # Test network first
    test_network()
    
    # Then test database connection
    print("\n" + "=" * 50)
    test_connection()