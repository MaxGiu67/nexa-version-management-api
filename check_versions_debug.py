import pymysql

# Connect to database
connection = pymysql.connect(
    host='centerbeam.proxy.rlwy.net',
    port=22032,
    user='root',
    password='drypjZgjDSozOUrrJJsyUtNGqkDPVsEd',
    database='railway'
)

try:
    with connection.cursor() as cursor:
        # Get app_id for com.nexa.timesheet
        cursor.execute(
            "SELECT id FROM apps WHERE app_identifier = %s",
            ('com.nexa.timesheet',)
        )
        app_result = cursor.fetchone()
        if app_result:
            app_id = app_result[0]
            print(f"App ID: {app_id}")
            
            # Get all versions for this app
            cursor.execute(
                """SELECT version, version_code, platform, release_date, is_active
                   FROM app_versions
                   WHERE app_id = %s
                   ORDER BY version_code DESC, release_date DESC""",
                (app_id,)
            )
            versions = cursor.fetchall()
            
            print("\nAll versions in database:")
            for v in versions:
                print(f"Version: {v[0]}, Code: {v[1]}, Platform: {v[2]}, Date: {v[3]}, Active: {v[4]}")
                
            # Check what the query returns for android
            cursor.execute(
                """SELECT version, version_code, is_mandatory, file_size, 
                          changelog, release_date, platform
                   FROM app_versions
                   WHERE app_id = %s AND (platform = %s OR platform = 'all')
                         AND is_active = true
                   ORDER BY version_code DESC
                   LIMIT 1""",
                (app_id, 'android')
            )
            latest = cursor.fetchone()
            print(f"\nLatest version query returns: {latest[0] if latest else 'None'} (code: {latest[1] if latest else 'None'})")
            
finally:
    connection.close()