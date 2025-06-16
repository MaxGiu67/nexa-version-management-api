"""
Sistema di gestione file APK/IPA per distribuzione app
"""
import os
import hashlib
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import pymysql
from datetime import datetime
import mimetypes
from pathlib import Path

# Configurazione
UPLOAD_DIR = "uploads"
APK_DIR = os.path.join(UPLOAD_DIR, "android")
IPA_DIR = os.path.join(UPLOAD_DIR, "ios")

# Crea directory se non esistono
os.makedirs(APK_DIR, exist_ok=True)
os.makedirs(IPA_DIR, exist_ok=True)

# Tipi di file consentiti
ALLOWED_EXTENSIONS = {
    'android': ['.apk'],
    'ios': ['.ipa']
}

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

def get_file_hash(file_path):
    """Calcola hash SHA256 del file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def get_file_info(file_path):
    """Ottieni informazioni del file"""
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'hash': get_file_hash(file_path)
    }

async def upload_app_file(
    file: UploadFile,
    version: str,
    platform: str,
    version_code: int,
    is_mandatory: bool = False,
    changelog: str = None
):
    """
    Carica file APK/IPA e aggiorna database
    """
    
    # Validazione piattaforma
    if platform not in ['android', 'ios']:
        raise HTTPException(status_code=400, detail="Platform must be 'android' or 'ios'")
    
    # Validazione estensione file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS[platform]:
        expected = ', '.join(ALLOWED_EXTENSIONS[platform])
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Expected {expected} for {platform}"
        )
    
    # Validazione dimensione
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Nome file: nexa-timesheet-v1.2.0-android.apk
    filename = f"nexa-timesheet-v{version}-{platform}{file_ext}"
    
    # Percorso completo
    upload_path = os.path.join(APK_DIR if platform == 'android' else IPA_DIR, filename)
    
    try:
        # Salva file
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Ottieni info file
        file_info = get_file_info(upload_path)
        
        # URL di download
        download_url = f"/download/{platform}/{filename}"
        
        # Aggiorna database
        conn = pymysql.connect(
            host='tramway.proxy.rlwy.net',
            port=20671,
            user='root',
            password='aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
            database='railway'
        )
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Inserisci/aggiorna versione
        cursor.execute("""
            INSERT INTO app_versions 
            (version, version_code, platform, release_date, is_mandatory, 
             download_url, changelog, file_size, file_hash, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true)
            ON DUPLICATE KEY UPDATE
                version_code = VALUES(version_code),
                is_mandatory = VALUES(is_mandatory),
                download_url = VALUES(download_url),
                changelog = VALUES(changelog),
                file_size = VALUES(file_size),
                file_hash = VALUES(file_hash),
                updated_at = CURRENT_TIMESTAMP
        """, (
            version,
            version_code,
            platform,
            datetime.now().date(),
            is_mandatory,
            download_url,
            changelog,
            file_info['size'],
            file_info['hash']
        ))
        
        conn.commit()
        version_id = cursor.lastrowid or cursor.execute("SELECT LAST_INSERT_ID()")[0]
        conn.close()
        
        return {
            "success": True,
            "message": f"File uploaded successfully for {platform} v{version}",
            "file_info": {
                "filename": filename,
                "size": file_info['size'],
                "hash": file_info['hash'],
                "download_url": download_url
            },
            "version_id": version_id
        }
        
    except Exception as e:
        # Rimuovi file se c'è stato un errore
        if os.path.exists(upload_path):
            os.remove(upload_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def get_app_file(platform: str, filename: str):
    """
    Scarica file APK/IPA
    """
    if platform not in ['android', 'ios']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    file_dir = APK_DIR if platform == 'android' else IPA_DIR
    file_path = os.path.join(file_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determina tipo MIME
    mime_type = 'application/vnd.android.package-archive' if platform == 'android' else 'application/octet-stream'
    
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Platform": platform
        }
    )

def list_uploaded_files():
    """
    Lista tutti i file caricati
    """
    files = []
    
    for platform in ['android', 'ios']:
        file_dir = APK_DIR if platform == 'android' else IPA_DIR
        
        for filename in os.listdir(file_dir):
            file_path = os.path.join(file_dir, filename)
            if os.path.isfile(file_path):
                file_info = get_file_info(file_path)
                files.append({
                    "filename": filename,
                    "platform": platform,
                    "size": file_info['size'],
                    "size_mb": round(file_info['size'] / (1024*1024), 2),
                    "modified": file_info['modified'].isoformat(),
                    "hash": file_info['hash'],
                    "download_url": f"/download/{platform}/{filename}"
                })
    
    return {"files": sorted(files, key=lambda x: x['modified'], reverse=True)}

def delete_app_file(platform: str, filename: str):
    """
    Elimina file APK/IPA
    """
    if platform not in ['android', 'ios']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    file_dir = APK_DIR if platform == 'android' else IPA_DIR
    file_path = os.path.join(file_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        
        # Rimuovi anche dal database
        conn = pymysql.connect(
            host='tramway.proxy.rlwy.net',
            port=20671,
            user='root',
            password='aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
            database='railway'
        )
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE app_versions SET download_url = NULL, is_active = false WHERE download_url LIKE %s",
            (f"%{filename}%",)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"File {filename} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")