#!/usr/bin/env python3
"""
Fix large file upload issues by optimizing MySQL connection handling
"""
import os

# Create an optimized version of multi_app_api.py with better connection handling
optimized_code = '''
# Add these imports at the top
import pymysql.connections
from pymysql.constants import CLIENT

# Update the DB_CONFIG with better settings for large files
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', os.environ.get('MYSQL_HOST', 'centerbeam.proxy.rlwy.net')),
    'port': int(os.environ.get('DB_PORT', os.environ.get('MYSQL_PORT', 22032))),
    'user': os.environ.get('DB_USER', os.environ.get('MYSQL_USER', 'root')),
    'password': os.environ.get('DB_PASSWORD', os.environ.get('MYSQL_PASSWORD', 'drypjZgjDSozOUrrJJsyUtNGqkDPVsEd')),
    'database': os.environ.get('DB_NAME', os.environ.get('MYSQL_DATABASE', 'railway')),
    'charset': 'utf8mb4',
    'max_allowed_packet': 1024 * 1024 * 100,  # 100MB
    'connect_timeout': 30,
    'read_timeout': 600,  # 10 minutes for large file operations
    'write_timeout': 600,  # 10 minutes for large file operations
    'client_flag': CLIENT.MULTI_STATEMENTS
}

# Update the upload endpoint to handle large files better
# Find the upload endpoint and modify it to:
# 1. Use a single transaction
# 2. Set connection parameters before inserting BLOB
# 3. Handle connection timeouts gracefully
'''

print("🔧 To fix large file uploads, we need to:")
print()
print("1. Update the connection configuration in multi_app_api.py")
print("2. Modify the upload endpoint to handle large BLOBs better")
print("3. Consider chunking large files or using external storage")
print()
print("For now, let's create a patch for the upload endpoint...")

# Create a patched upload function
patch_content = '''
import logging
logger = logging.getLogger(__name__)

def get_db_for_upload():
    """Get database connection optimized for large file uploads"""
    import pymysql
    from pymysql.constants import CLIENT
    
    connection = pymysql.connect(
        host=os.environ.get('DB_HOST', 'centerbeam.proxy.rlwy.net'),
        port=int(os.environ.get('DB_PORT', 22032)),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'drypjZgjDSozOUrrJJsyUtNGqkDPVsEd'),
        database=os.environ.get('DB_NAME', 'railway'),
        charset='utf8mb4',
        max_allowed_packet=1024 * 1024 * 100,  # 100MB
        connect_timeout=30,
        read_timeout=600,  # 10 minutes
        write_timeout=600,  # 10 minutes
        client_flag=CLIENT.MULTI_STATEMENTS
    )
    
    # Set session variables for large data
    with connection.cursor() as cursor:
        cursor.execute("SET SESSION max_allowed_packet = 104857600")  # 100MB
        cursor.execute("SET SESSION wait_timeout = 600")
        cursor.execute("SET SESSION interactive_timeout = 600")
    
    return connection

# In the upload endpoint, replace the database connection part with:
# with get_db_for_upload() as connection:
#     # ... rest of the upload logic
'''

with open('upload_patch.py', 'w') as f:
    f.write(patch_content)

print("✅ Created upload_patch.py with optimized connection handling")
print()
print("Quick fix options:")
print("1. Reduce file size limit to 50MB in the frontend")
print("2. Use external storage (S3, etc.) for files > 50MB")
print("3. Implement chunked upload for large files")