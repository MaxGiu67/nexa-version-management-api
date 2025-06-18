#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

print("🔍 Testing PostgreSQL connection...")
print(f"Host: {os.getenv('PGHOST')}")
print(f"Port: {os.getenv('PGPORT')}")
print(f"Database: {os.getenv('PGDATABASE')}")

try:
    conn = psycopg2.connect(
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        database=os.getenv('PGDATABASE'),
        connect_timeout=5
    )
    print("✅ Connected successfully!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    print(f"📊 PostgreSQL: {cursor.fetchone()[0]}")
    
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n📌 Assicurati di aver inserito la password nel file .env.local!")