"""
API completa per gestione versioni con upload/download file
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pymysql
import json
import os
# from file_management import upload_app_file, get_app_file, list_uploaded_files, delete_app_file

app = FastAPI(title="Version Management API", version="1.0.0")

# Monta directory statica per i file
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Configurazione database
DB_CONFIG = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 20671,
    'user': 'root',
    'password': 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
    'database': 'railway'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "version-management"}

@app.get("/api/v1/app-version/check")
def check_for_updates(current_version: str, platform: str = "all"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Query semplice per ultima versione
        cursor.execute("""
            SELECT * FROM app_versions 
            WHERE platform IN (%s, 'all') 
            AND is_active = true 
            ORDER BY version_code DESC 
            LIMIT 1
        """, (platform,))
        
        latest = cursor.fetchone()
        
        if not latest:
            return {"hasUpdate": False, "message": "No versions available"}
        
        # Confronto semplice
        current_parts = [int(x) for x in current_version.split('.')]
        latest_parts = [int(x) for x in latest['version'].split('.')]
        
        has_update = current_parts < latest_parts
        
        # Parse changelog
        changelog = []
        if latest['changelog']:
            try:
                changelog_data = json.loads(latest['changelog'])
                changelog = changelog_data.get('changes', [])
            except:
                pass
        
        return {
            "hasUpdate": has_update,
            "latestVersion": latest['version'],
            "versionCode": latest['version_code'],
            "isMandatory": bool(latest['is_mandatory']),
            "changelog": changelog,
            "releaseDate": latest['release_date'].isoformat() if latest['release_date'] else None
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

@app.get("/api/v1/app-version/latest")
def get_latest_version(platform: str = "all"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT * FROM app_versions 
            WHERE platform IN (%s, 'all') 
            AND is_active = true 
            ORDER BY version_code DESC 
            LIMIT 1
        """, (platform,))
        
        latest = cursor.fetchone()
        
        if not latest:
            return {"error": "No version found"}
        
        changelog = []
        if latest['changelog']:
            try:
                changelog_data = json.loads(latest['changelog'])
                changelog = changelog_data.get('changes', [])
            except:
                pass
        
        return {
            "version": latest['version'],
            "versionCode": latest['version_code'],
            "platform": latest['platform'],
            "releaseDate": latest['release_date'].isoformat() if latest['release_date'] else None,
            "changelog": changelog,
            "isMandatory": bool(latest['is_mandatory'])
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

# File management endpoints disabilitati per ora - test basic API prima

@app.get("/api/v1/app-version/files")
def list_files():
    """Lista file (placeholder)"""
    return {"files": [], "message": "File management not yet implemented in this test"}

@app.get("/api/v1/app-version/upload-form")
def upload_form():
    """Form placeholder"""
    return {"message": "Upload form available after full implementation"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting complete API server with file management...")
    uvicorn.run(app, host="0.0.0.0", port=8000)