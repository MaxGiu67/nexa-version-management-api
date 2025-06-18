#!/usr/bin/env python3
import pymysql
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv('.env.local')

print("🔍 Testing Railway MySQL Connection...")
print("-" * 50)

# Mostra le configurazioni (nasconde la password)
config = {
    'host': os.getenv('MYSQL_HOST', 'not_set'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'not_set'),
    'password': os.getenv('MYSQL_PASSWORD', 'not_set'),
    'database': os.getenv('MYSQL_DATABASE', 'not_set'),
}

print(f"Host: {config['host']}")
print(f"Port: {config['port']}")
print(f"User: {config['user']}")
print(f"Password: {'*' * len(config['password']) if config['password'] != 'not_set' else 'not_set'}")
print(f"Database: {config['database']}")
print("-" * 50)

try:
    print("📡 Attempting connection...")
    connection = pymysql.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        connect_timeout=10
    )
    
    print("✅ Connection successful!")
    
    # Test query
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 MySQL Version: {version[0]}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
    
    connection.close()
    print("✅ Connection closed successfully")
    
except pymysql.err.OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print("\n🔧 Possible solutions:")
    print("1. Check if the database is awake in Railway dashboard")
    print("2. Verify credentials are correct")
    print("3. Check if your IP is whitelisted (if Railway has IP restrictions)")
    print("4. Try again in 1-2 minutes if database was sleeping")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")