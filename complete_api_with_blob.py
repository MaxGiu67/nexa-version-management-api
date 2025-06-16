"""
API completa con gestione file BLOB nel database
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import json
from blob_file_management import (
    upload_app_to_database, 
    download_app_from_database, 
    list_database_files, 
    delete_app_from_database,
    get_database_storage_info
)

app = FastAPI(title="Version Management API with BLOB Storage", version="2.0.0")

# Configurazione CORS per frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ======================================================
# ENDPOINTS BASE (check updates, latest version)
# ======================================================

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "version-management", "storage": "database-blob"}

@app.get("/api/v1/app-version/check")
def check_for_updates(current_version: str, platform: str = "all"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Query per l'ultima versione attiva
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
        
        # Confronto semplice versioni
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
        
        # Download URL (se file presente nel database)
        download_url = None
        if latest['app_file'] is not None:
            download_url = f"/download/{platform}/{latest['version']}"
        
        return {
            "hasUpdate": has_update,
            "latestVersion": latest['version'],
            "versionCode": latest['version_code'],
            "isMandatory": bool(latest['is_mandatory']),
            "downloadUrl": download_url,
            "changelog": changelog,
            "releaseDate": latest['release_date'].isoformat() if latest['release_date'] else None,
            "fileSize": latest['file_size'] if latest['file_size'] else None
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
        
        # Download URL se file presente
        download_url = None
        if latest['app_file'] is not None:
            download_url = f"/download/{platform}/{latest['version']}"
        
        return {
            "version": latest['version'],
            "versionCode": latest['version_code'],
            "platform": latest['platform'],
            "releaseDate": latest['release_date'].isoformat() if latest['release_date'] else None,
            "downloadUrl": download_url,
            "changelog": changelog,
            "isMandatory": bool(latest['is_mandatory']),
            "fileSize": latest['file_size'] if latest['file_size'] else None,
            "fileName": latest['file_name'] if latest['file_name'] else None
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

# ======================================================
# ENDPOINTS GESTIONE FILE BLOB
# ======================================================

@app.post("/api/v1/app-version/upload")
async def upload_app_file(
    file: UploadFile = File(...),
    version: str = Form(...),
    platform: str = Form(...),
    version_code: int = Form(...),
    is_mandatory: bool = Form(False),
    changelog: str = Form(None)
):
    """
    Carica file APK/IPA nel database come BLOB
    """
    return await upload_app_to_database(file, version, platform, version_code, is_mandatory, changelog)

@app.get("/download/{platform}/{version}")
async def download_app_file(platform: str, version: str):
    """
    Scarica file APK/IPA dal database
    """
    return download_app_from_database(platform, version)

@app.get("/api/v1/app-version/files")
def list_uploaded_files():
    """
    Lista tutti i file nel database
    """
    return list_database_files()

@app.delete("/api/v1/app-version/files/{platform}/{version}")
def delete_uploaded_file(platform: str, version: str):
    """
    Elimina file dal database
    """
    return delete_app_from_database(platform, version)

@app.get("/api/v1/app-version/storage-info")
def get_storage_info():
    """
    Informazioni sull'utilizzo dello storage
    """
    return get_database_storage_info()

# ======================================================
# FORM WEB PER UPLOAD
# ======================================================

@app.get("/api/v1/app-version/upload-form", response_class=HTMLResponse)
def upload_form():
    """
    Form HTML per upload file con info storage
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload App - Database BLOB Storage</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; margin-right: 10px; }
            button:hover { background: #0056b3; }
            .info { background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin-bottom: 20px; }
            .success { background: #d4edda; border-left: 4px solid #28a745; }
            .warning { background: #fff3cd; border-left: 4px solid #ffc107; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f8f9fa; }
            .small { font-size: 0.9em; color: #666; }
        </style>
    </head>
    <body>
        <h1>📱 Upload App File - Database BLOB Storage</h1>
        
        <div class="info">
            <strong>🗄️ Storage Method:</strong> Files are saved as BLOB directly in MySQL database<br>
            <strong>📁 Supported files:</strong> Android (.apk), iOS (.ipa)<br>
            <strong>📏 Max file size:</strong> 500MB<br>
            <strong>🔒 Security:</strong> SHA256 hash verification, secure database storage
        </div>
        
        <!-- Storage Info -->
        <div id="storage-info" class="info">
            <strong>💾 Storage Usage:</strong> Loading...
        </div>
        
        <form action="/api/v1/app-version/upload" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label>📁 App File:</label>
                <input type="file" name="file" accept=".apk,.ipa" required>
                <div class="small">Select .apk file for Android or .ipa file for iOS</div>
            </div>
            
            <div class="form-group">
                <label>🏷️ Version (e.g., 1.2.0):</label>
                <input type="text" name="version" pattern="\\d+\\.\\d+\\.\\d+" required placeholder="1.2.0">
            </div>
            
            <div class="form-group">
                <label>📱 Platform:</label>
                <select name="platform" required>
                    <option value="">Select platform</option>
                    <option value="android">🤖 Android</option>
                    <option value="ios">🍎 iOS</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>🔢 Version Code:</label>
                <input type="number" name="version_code" min="1" required placeholder="5">
                <div class="small">Incremental number for version comparison</div>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_mandatory"> 
                    ⚠️ Mandatory Update
                </label>
                <div class="small">Force users to update before using the app</div>
            </div>
            
            <div class="form-group">
                <label>📋 Changelog (JSON format):</label>
                <textarea name="changelog" rows="4" placeholder='{"changes": ["New feature X", "Bug fix Y", "Performance improvements"]}'></textarea>
                <div class="small">Optional: List of changes in JSON format</div>
            </div>
            
            <button type="submit">🚀 Upload to Database</button>
            <button type="button" onclick="location.reload()">🔄 Refresh</button>
        </form>
        
        <h2>📂 Files in Database</h2>
        <div id="files-list">Loading...</div>
        
        <script>
            // Carica info storage
            fetch('/api/v1/app-version/storage-info')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('storage-info').innerHTML = 
                        `<strong>💾 Database Storage:</strong> ${data.total_files} files, ${data.total_size_mb} MB total, ${data.total_downloads} downloads`;
                })
                .catch(() => {
                    document.getElementById('storage-info').innerHTML = '<strong>💾 Storage info unavailable</strong>';
                });
            
            // Carica lista file
            fetch('/api/v1/app-version/files')
                .then(r => r.json())
                .then(data => {
                    const list = document.getElementById('files-list');
                    if (data.files.length === 0) {
                        list.innerHTML = '<p>No files in database yet.</p>';
                        return;
                    }
                    
                    list.innerHTML = `
                        <table>
                            <tr>
                                <th>File</th>
                                <th>Platform</th>
                                <th>Version</th>
                                <th>Size</th>
                                <th>Downloads</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                            ${data.files.map(f => `
                                <tr>
                                    <td>${f.filename || 'N/A'}</td>
                                    <td>${f.platform}</td>
                                    <td>${f.version}</td>
                                    <td>${f.size_mb} MB</td>
                                    <td>${f.download_count}</td>
                                    <td>${f.is_active ? '✅ Active' : '❌ Inactive'}</td>
                                    <td>
                                        <a href="${f.download_url}" download>⬇️ Download</a> |
                                        <a href="#" onclick="deleteFile('${f.platform}', '${f.version}')">🗑️ Delete</a>
                                    </td>
                                </tr>
                            `).join('')}
                        </table>
                        <p class="small">Files are stored as binary data (BLOB) in MySQL database</p>
                    `;
                })
                .catch(e => {
                    document.getElementById('files-list').innerHTML = '<p>Error loading files: ' + e.message + '</p>';
                });
            
            function deleteFile(platform, version) {
                if (confirm(`Delete ${platform} v${version} from database?`)) {
                    fetch(`/api/v1/app-version/files/${platform}/${version}`, {method: 'DELETE'})
                        .then(r => r.json())
                        .then(data => {
                            alert(data.message);
                            location.reload();
                        })
                        .catch(e => alert('Error: ' + e.message));
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting API server with Database BLOB storage...")
    print("📁 Files will be saved directly in MySQL database")
    uvicorn.run(app, host="0.0.0.0", port=8000)