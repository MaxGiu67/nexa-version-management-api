
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
