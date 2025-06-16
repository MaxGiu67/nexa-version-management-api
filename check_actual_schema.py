#!/usr/bin/env python3
"""
Script to check the actual database schema and compare with expected schema
"""

import pymysql
import os
import json
from tabulate import tabulate

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQL_PORT', 20671)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP'),
    'database': os.environ.get('MYSQL_DATABASE', 'railway'),
    'charset': 'utf8mb4'
}

def check_table_schema(connection, table_name):
    """Check the schema of a specific table"""
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        # Get column information
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_KEY,
                EXTRA
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        if not columns:
            print(f"\n❌ Table '{table_name}' does not exist!")
            return False
        
        print(f"\n📋 Schema for table: {table_name}")
        print("=" * 80)
        
        # Format and display columns
        headers = ['Column', 'Type', 'Nullable', 'Key', 'Default', 'Extra']
        rows = []
        for col in columns:
            rows.append([
                col['COLUMN_NAME'],
                col['COLUMN_TYPE'],
                col['IS_NULLABLE'],
                col['COLUMN_KEY'] or '-',
                col['COLUMN_DEFAULT'] or '-',
                col['EXTRA'] or '-'
            ])
        
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        
        # Get indexes
        cursor.execute("""
            SELECT 
                INDEX_NAME,
                GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as COLUMNS,
                INDEX_TYPE,
                NON_UNIQUE
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            GROUP BY INDEX_NAME, INDEX_TYPE, NON_UNIQUE
        """, (table_name,))
        
        indexes = cursor.fetchall()
        if indexes:
            print(f"\n🔍 Indexes for {table_name}:")
            index_headers = ['Index Name', 'Columns', 'Type', 'Unique']
            index_rows = []
            for idx in indexes:
                index_rows.append([
                    idx['INDEX_NAME'],
                    idx['COLUMNS'],
                    idx['INDEX_TYPE'],
                    'No' if idx['NON_UNIQUE'] else 'Yes'
                ])
            print(tabulate(index_rows, headers=index_headers, tablefmt='grid'))
        
        return True

def check_expected_vs_actual(connection):
    """Check expected columns vs actual columns"""
    expected_columns = {
        'app_error_logs': {
            'correct': ['id', 'app_id', 'user_id', 'session_id', 'error_type', 
                       'error_message', 'error_stack', 'metadata', 'severity', 
                       'app_version', 'platform', 'created_at'],
            'old': ['device_info', 'context', 'is_resolved', 'error_hash', 
                   'resolved_at', 'resolved_by', 'error_count']
        },
        'user_sessions': {
            'correct': ['id', 'user_id', 'app_id', 'session_uuid', 'start_time', 
                       'end_time', 'duration_seconds', 'app_version', 'platform', 
                       'device_info', 'ip_address', 'end_reason', 'is_active', 
                       'created_at'],
            'old': ['session_start', 'session_end']
        }
    }
    
    print("\n\n🔍 Checking for column discrepancies...")
    print("=" * 80)
    
    for table_name, cols in expected_columns.items():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
            """, (table_name,))
            
            actual_columns = [row[0] for row in cursor.fetchall()]
            
            if not actual_columns:
                print(f"\n❌ Table '{table_name}' not found!")
                continue
            
            print(f"\n📊 Table: {table_name}")
            
            # Check for old columns that should not exist
            old_cols_found = [col for col in cols.get('old', []) if col in actual_columns]
            if old_cols_found:
                print(f"  ⚠️  Old columns found (should be removed): {', '.join(old_cols_found)}")
            
            # Check for missing correct columns
            missing_cols = [col for col in cols['correct'] if col not in actual_columns]
            if missing_cols:
                print(f"  ❌ Missing columns: {', '.join(missing_cols)}")
            
            # Check for unexpected columns
            expected_all = cols['correct'] + cols.get('old', [])
            unexpected_cols = [col for col in actual_columns if col not in expected_all]
            if unexpected_cols:
                print(f"  ℹ️  Additional columns found: {', '.join(unexpected_cols)}")
            
            if not old_cols_found and not missing_cols:
                print(f"  ✅ Schema is correct!")

def main():
    """Main function"""
    print("🔄 Connecting to database...")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Connected successfully!")
        
        # Check main tables
        tables_to_check = ['app_error_logs', 'user_sessions', 'apps', 'app_users']
        
        for table in tables_to_check:
            check_table_schema(connection, table)
        
        # Check for discrepancies
        check_expected_vs_actual(connection)
        
        # Show sample data if tables exist
        print("\n\n📊 Sample data check...")
        print("=" * 80)
        
        with connection.cursor() as cursor:
            # Check error logs count
            cursor.execute("SELECT COUNT(*) as count FROM app_error_logs")
            error_count = cursor.fetchone()[0]
            print(f"app_error_logs: {error_count} records")
            
            # Check sessions count
            cursor.execute("SELECT COUNT(*) as count FROM user_sessions")
            session_count = cursor.fetchone()[0]
            print(f"user_sessions: {session_count} records")
            
            # Show a sample error record if any exist
            if error_count > 0:
                cursor.execute("""
                    SELECT * FROM app_error_logs 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)
                sample = cursor.fetchone()
                print(f"\nSample error record columns: {list(sample) if sample else 'None'}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())