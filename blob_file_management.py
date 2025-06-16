"""
Gestione file APK/IPA salvati come BLOB nel database
"""
import hashlib
import pymysql
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
from datetime import datetime

# Configurazione database
DB_CONFIG = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 20671,
    'user': 'root',
    'password': 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
    'database': 'railway'
}

# Tipi MIME supportati
MIME_TYPES = {
    '.apk': 'application/vnd.android.package-archive',
    '.ipa': 'application/octet-stream'
}

# Dimensione massima file (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024

def get_file_hash(file_content: bytes) -> str:
    """Calcola hash SHA256 del contenuto file"""
    return hashlib.sha256(file_content).hexdigest()

def get_mime_type(filename: str) -> str:
    """Determina tipo MIME dal nome file"""
    for ext, mime in MIME_TYPES.items():
        if filename.lower().endswith(ext):
            return mime
    return 'application/octet-stream'

async def upload_app_to_database(
    file: UploadFile,
    version: str,
    platform: str,
    version_code: int,
    is_mandatory: bool = False,
    changelog: str = None
):
    """
    Carica file APK/IPA nel database come BLOB
    """
    
    # Validazione piattaforma
    if platform not in ['android', 'ios']:
        raise HTTPException(status_code=400, detail="Platform must be 'android' or 'ios'")
    
    # Validazione estensione
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    expected_ext = 'apk' if platform == 'android' else 'ipa'
    
    if file_ext != expected_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected .{expected_ext} for {platform}"
        )
    
    # Leggi contenuto file
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validazione dimensione
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    # Calcola hash e altri metadati
    file_hash = get_file_hash(file_content)
    mime_type = get_mime_type(file.filename)
    file_name = f"nexa-timesheet-v{version}-{platform}.{file_ext}"
    
    try:
        # Connetti al database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Verifica se la versione esiste già
        cursor.execute("""
            SELECT id FROM app_versions 
            WHERE version = %s AND platform = %s
        """, (version, platform))
        
        existing = cursor.fetchone()
        
        if existing:
            # Aggiorna versione esistente
            cursor.execute("""
                UPDATE app_versions SET
                    version_code = %s,
                    is_mandatory = %s,
                    changelog = %s,
                    app_file = %s,
                    file_name = %s,
                    mime_type = %s,
                    file_size = %s,
                    file_hash = %s,
                    download_url = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                version_code,
                is_mandatory,
                changelog,
                file_content,
                file_name,
                mime_type,
                file_size,
                file_hash,
                f"/download/{platform}/{version}",  # URL per download
                existing['id']
            ))
            version_id = existing['id']
            message = f"Version {version} for {platform} updated successfully"
        else:
            # Inserisci nuova versione
            cursor.execute("""
                INSERT INTO app_versions 
                (version, version_code, platform, release_date, is_mandatory,
                 changelog, app_file, file_name, mime_type, file_size, file_hash,
                 download_url, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
            """, (
                version,
                version_code,
                platform,
                datetime.now().date(),
                is_mandatory,
                changelog,
                file_content,
                file_name,
                mime_type,
                file_size,
                file_hash,
                f"/download/{platform}/{version}"
            ))
            version_id = cursor.lastrowid
            message = f"Version {version} for {platform} uploaded successfully"
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": message,
            "version_id": version_id,
            "file_info": {
                "filename": file_name,
                "size": file_size,
                "size_mb": round(file_size / (1024*1024), 2),
                "hash": file_hash,
                "mime_type": mime_type,
                "download_url": f"/download/{platform}/{version}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def download_app_from_database(platform: str, version: str):
    """
    Scarica file APK/IPA dal database
    """
    if platform not in ['android', 'ios']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Cerca il file nel database
        cursor.execute("""
            SELECT app_file, file_name, mime_type, file_size, download_count
            FROM app_versions 
            WHERE platform = %s AND version = %s AND app_file IS NOT NULL
            ORDER BY version_code DESC
            LIMIT 1
        """, (platform, version))
        
        result = cursor.fetchone()
        
        if not result or not result['app_file']:
            conn.close()
            raise HTTPException(status_code=404, detail="File not found")
        
        # Incrementa contatore download
        cursor.execute("""
            UPDATE app_versions 
            SET download_count = download_count + 1 
            WHERE platform = %s AND version = %s
        """, (platform, version))
        conn.commit()
        
        # Prepara risposta streaming
        file_content = result['app_file']
        file_name = result['file_name']
        mime_type = result['mime_type']
        
        conn.close()
        
        # Crea stream da bytes
        file_stream = io.BytesIO(file_content)
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_name}",
                "Content-Length": str(len(file_content)),
                "X-Platform": platform,
                "X-Version": version
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

def list_database_files():
    """
    Lista tutti i file salvati nel database
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT version, platform, file_name, file_size, file_hash, 
                   download_count, created_at, updated_at, is_active
            FROM app_versions 
            WHERE app_file IS NOT NULL
            ORDER BY created_at DESC
        """)
        
        files = cursor.fetchall()
        conn.close()
        
        # Formatta risposta
        formatted_files = []
        for file_info in files:
            formatted_files.append({
                "version": file_info['version'],
                "platform": file_info['platform'],
                "filename": file_info['file_name'],
                "size": file_info['file_size'],
                "size_mb": round(file_info['file_size'] / (1024*1024), 2) if file_info['file_size'] else 0,
                "hash": file_info['file_hash'],
                "download_count": file_info['download_count'],
                "is_active": bool(file_info['is_active']),
                "created_at": file_info['created_at'].isoformat() if file_info['created_at'] else None,
                "updated_at": file_info['updated_at'].isoformat() if file_info['updated_at'] else None,
                "download_url": f"/download/{file_info['platform']}/{file_info['version']}"
            })
        
        return {"files": formatted_files, "total": len(formatted_files)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def delete_app_from_database(platform: str, version: str):
    """
    Elimina file dal database (imposta app_file = NULL)
    """
    if platform not in ['android', 'ios']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Verifica che il file esista
        cursor.execute("""
            SELECT id, file_name FROM app_versions 
            WHERE platform = %s AND version = %s AND app_file IS NOT NULL
        """, (platform, version))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="File not found")
        
        # Rimuovi il file (imposta NULL)
        cursor.execute("""
            UPDATE app_versions SET
                app_file = NULL,
                file_name = NULL,
                mime_type = NULL,
                file_size = NULL,
                file_hash = NULL,
                download_url = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (result['id'],))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"File {result['file_name']} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

def get_database_storage_info():
    """
    Informazioni sull'utilizzo storage database
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Calcola spazio totale usato dai file
        cursor.execute("""
            SELECT 
                COUNT(*) as total_files,
                SUM(file_size) as total_size,
                AVG(file_size) as avg_size,
                MAX(file_size) as max_size,
                SUM(download_count) as total_downloads
            FROM app_versions 
            WHERE app_file IS NOT NULL
        """)
        
        stats = cursor.fetchone()
        
        # Statistiche per piattaforma
        cursor.execute("""
            SELECT 
                platform,
                COUNT(*) as files,
                SUM(file_size) as size,
                SUM(download_count) as downloads
            FROM app_versions 
            WHERE app_file IS NOT NULL
            GROUP BY platform
        """)
        
        platform_stats = cursor.fetchall()
        conn.close()
        
        return {
            "total_files": stats['total_files'] or 0,
            "total_size_bytes": stats['total_size'] or 0,
            "total_size_mb": round((stats['total_size'] or 0) / (1024*1024), 2),
            "average_size_mb": round((stats['avg_size'] or 0) / (1024*1024), 2),
            "max_size_mb": round((stats['max_size'] or 0) / (1024*1024), 2),
            "total_downloads": stats['total_downloads'] or 0,
            "platform_breakdown": [
                {
                    "platform": p['platform'],
                    "files": p['files'],
                    "size_mb": round((p['size'] or 0) / (1024*1024), 2),
                    "downloads": p['downloads']
                }
                for p in platform_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")