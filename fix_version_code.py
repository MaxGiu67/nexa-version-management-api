import pymysql

connection = pymysql.connect(
    host='centerbeam.proxy.rlwy.net',
    port=22032,
    user='root',
    password='drypjZgjDSozOUrrJJsyUtNGqkDPVsEd',
    database='railway'
)

try:
    with connection.cursor() as cursor:
        # Update version_code for 0.7.5 to be 9 (higher than 0.7.4's 8)
        cursor.execute(
            """UPDATE app_versions 
               SET version_code = 9
               WHERE version = '0.7.5' AND app_id = 2""",
        )
        connection.commit()
        print("✅ Updated version_code for 0.7.5 to 9")
        
        # Verify the fix
        cursor.execute(
            """SELECT version, version_code FROM app_versions 
               WHERE app_id = 2 
               ORDER BY version_code DESC""",
        )
        versions = cursor.fetchall()
        print("\nUpdated versions:")
        for v in versions:
            print(f"Version: {v[0]}, Code: {v[1]}")
            
finally:
    connection.close()