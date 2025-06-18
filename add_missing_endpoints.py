#!/usr/bin/env python3
"""
Add missing v2 endpoints to multi_app_api.py for frontend compatibility
"""

# Gli endpoint che il frontend si aspetta sono:
# - GET /api/v2/app-version/latest
# - GET /api/v2/app-version/check
# - GET /api/v2/app-version/files
# - GET /api/v2/app-version/storage-info
# - DELETE /api/v2/app-version/files/{platform}/{version}

endpoints_to_add = """

# ===== COMPATIBILITY ENDPOINTS FOR FRONTEND =====
# These endpoints provide backward compatibility for the frontend

@app.get("/api/v2/app-version/latest")
async def get_latest_version_compat(
    platform: str = Query('all'),
    app_identifier: str = Query('nexa-timesheet')
):
    \"\"\"Get latest version for an app (compatibility endpoint)\"\"\"
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
            
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                \"\"\"SELECT v.*, a.app_name, a.app_identifier
                   FROM app_versions v
                   JOIN apps a ON v.app_id = a.id
                   WHERE v.app_id = %s AND v.platform IN (%s, 'all')
                         AND v.is_active = true
                   ORDER BY v.version_code DESC
                   LIMIT 1\"\"\",
                (app_id, platform)
            )
            version = cursor.fetchone()
            
            if not version:
                raise HTTPException(status_code=404, detail="No version found")
                
            # Parse changelog
            if version['changelog']:
                try:
                    version['changelog'] = json.loads(version['changelog'])
                except:
                    version['changelog'] = []
                    
            return version

@app.get("/api/v2/app-version/check")
async def check_version_compat(
    current_version: str = Query(...),
    platform: str = Query('all'),
    app_identifier: str = Query('nexa-timesheet')
):
    \"\"\"Check if update is available (compatibility endpoint)\"\"\"
    # Convert to POST format and call existing endpoint
    version_data = VersionCheck(
        app_identifier=app_identifier,
        current_version=current_version,
        platform=platform
    )
    return await check_version(version_data)

@app.get("/api/v2/app-version/files")
async def list_files_compat(
    app_identifier: str = Query('nexa-timesheet')
):
    \"\"\"List all version files (compatibility endpoint)\"\"\"
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
            
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                \"\"\"SELECT 
                    v.id,
                    v.version,
                    v.platform,
                    v.version_code,
                    v.file_name,
                    v.file_size,
                    v.file_hash,
                    v.changelog,
                    v.is_active,
                    v.is_mandatory,
                    v.download_count,
                    v.created_at,
                    a.app_name
                FROM app_versions v
                JOIN apps a ON v.app_id = a.id
                WHERE v.app_id = %s
                ORDER BY v.created_at DESC\"\"\",
                (app_id,)
            )
            files = cursor.fetchall()
            
            # Parse changelog
            for file in files:
                if file['changelog']:
                    try:
                        file['changelog'] = json.loads(file['changelog'])
                    except:
                        file['changelog'] = []
                        
            return {"files": files, "total": len(files)}

@app.get("/api/v2/app-version/storage-info")
async def get_storage_info_compat(
    app_identifier: str = Query('nexa-timesheet')
):
    \"\"\"Get storage information (compatibility endpoint)\"\"\"
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
            
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get storage stats
            cursor.execute(
                \"\"\"SELECT 
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size,
                    MAX(file_size) as max_file_size,
                    AVG(file_size) as avg_file_size
                FROM app_versions
                WHERE app_id = %s\"\"\",
                (app_id,)
            )
            stats = cursor.fetchone()
            
            # Get platform breakdown
            cursor.execute(
                \"\"\"SELECT 
                    platform,
                    COUNT(*) as count,
                    SUM(file_size) as size
                FROM app_versions
                WHERE app_id = %s
                GROUP BY platform\"\"\",
                (app_id,)
            )
            platform_stats = cursor.fetchall()
            
            return {
                "total_files": stats['total_files'] or 0,
                "total_size": int(stats['total_size'] or 0),
                "max_file_size": int(stats['max_file_size'] or 0),
                "avg_file_size": int(stats['avg_file_size'] or 0),
                "platform_breakdown": platform_stats
            }

@app.delete("/api/v2/app-version/files/{platform}/{version}")
async def delete_file_compat(
    platform: str,
    version: str,
    app_identifier: str = Query('nexa-timesheet')
):
    \"\"\"Delete a specific version file (compatibility endpoint)\"\"\"
    with get_db() as connection:
        app_id = get_app_id(app_identifier, connection)
        if not app_id:
            raise HTTPException(status_code=404, detail="App not found")
            
        with connection.cursor() as cursor:
            cursor.execute(
                \"\"\"DELETE FROM app_versions
                   WHERE app_id = %s AND platform = %s AND version = %s\"\"\",
                (app_id, platform, version)
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Version not found")
                
            connection.commit()
            
            return {
                "success": True,
                "message": f"Version {version} for {platform} deleted successfully"
            }

"""

print("📝 Endpoint da aggiungere a multi_app_api.py:")
print("=" * 60)
print(endpoints_to_add)
print("=" * 60)
print("\n✅ Copia questi endpoint alla fine del file multi_app_api.py prima di:")
print('   if __name__ == "__main__":')