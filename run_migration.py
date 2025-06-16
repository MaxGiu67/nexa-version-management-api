#!/usr/bin/env python3
"""
Script per eseguire la migrazione del database
Aggiunge le tabelle per session tracking ed error management
"""

import pymysql
import os
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQL_PORT', 20671)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'),
    'database': os.environ.get('MYSQL_DATABASE', 'railway'),
    'charset': 'utf8mb4'
}

def run_migration():
    """Execute the migration to add tracking tables"""
    
    print(f"🚀 Starting migration at {datetime.now()}")
    print(f"📊 Connecting to database at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    try:
        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ Connected to database successfully")
        
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrate_add_tracking.sql')
        
        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found at: {migration_file}")
            return False
            
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("📝 Executing migration script...")
        
        # Split by delimiter to handle stored procedures
        statements = []
        delimiter = ';'
        current_statement = []
        in_delimiter = False
        
        for line in migration_sql.split('\n'):
            if line.strip().upper().startswith('DELIMITER'):
                if '//' in line:
                    delimiter = '//'
                    in_delimiter = True
                else:
                    delimiter = ';'
                    in_delimiter = False
                continue
                
            current_statement.append(line)
            
            if line.strip().endswith(delimiter):
                statement = '\n'.join(current_statement)
                if delimiter == '//':
                    statement = statement.rstrip('//')
                else:
                    statement = statement.rstrip(';')
                    
                if statement.strip():
                    statements.append(statement)
                current_statement = []
        
        # Execute each statement
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                if statement.strip():
                    cursor.execute(statement)
                    success_count += 1
                    
                    # Check if it was a CREATE TABLE statement
                    if 'CREATE TABLE' in statement.upper():
                        table_match = statement.upper().split('CREATE TABLE')[1].split('(')[0].strip()
                        print(f"  ✅ Created table: {table_match}")
                    elif 'CREATE VIEW' in statement.upper():
                        print(f"  ✅ Created view")
                    elif 'CREATE TRIGGER' in statement.upper():
                        print(f"  ✅ Created trigger")
                    elif 'CREATE PROCEDURE' in statement.upper():
                        print(f"  ✅ Created procedure")
                        
            except pymysql.Error as e:
                error_count += 1
                if 'already exists' in str(e):
                    print(f"  ℹ️  Skipped (already exists): Statement {i}")
                else:
                    print(f"  ❌ Error in statement {i}: {e}")
        
        # Commit changes
        connection.commit()
        
        print(f"\n📊 Migration Summary:")
        print(f"  ✅ Successful statements: {success_count}")
        print(f"  ⚠️  Skipped/Error statements: {error_count}")
        
        # Verify tables were created
        print("\n🔍 Verifying tables...")
        cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name IN ('app_users', 'user_sessions', 'app_error_logs', 
                              'user_app_installations', 'update_history', 
                              'app_analytics_daily', 'error_groups')
        """)
        result = cursor.fetchone()
        
        print(f"  📋 Tracking tables found: {result[0]}/7")
        
        # List created tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name IN ('app_users', 'user_sessions', 'app_error_logs', 
                              'user_app_installations', 'update_history', 
                              'app_analytics_daily', 'error_groups')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("\n  📋 Tables in database:")
        for table in tables:
            print(f"     ✓ {table[0]}")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ Migration completed successfully at {datetime.now()}")
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ Database connection error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)