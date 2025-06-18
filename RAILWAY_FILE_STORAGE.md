# 🚀 Railway File Storage Configuration

## Overview
Implementazione completa del file storage su disco per gestire file APK/IPA grandi (>50MB) su Railway.

## ✅ Cosa è stato implementato

### 1. **File Storage Manager**
- Classe `FileStorageManager` per gestire file su disco
- Struttura directory: `/app/storage/versions/{app_id}/{platform}/{version}/`
- Metadata JSON per ogni file salvato
- Supporto per file fino a 500MB

### 2. **Database Schema Update**
```sql
ALTER TABLE app_versions 
ADD COLUMN file_path VARCHAR(500) AFTER file_hash;
```
- Campo `file_path` per salvare il percorso del file
- Supporto retrocompatibile con BLOB esistenti

### 3. **Logic Update**
- File ≤50MB: Salvati come BLOB nel database
- File >50MB: Salvati su disco, solo path nel DB
- Chunked upload automatico per file >50MB

### 4. **API Endpoints Updated**
- `/api/v2/version/upload`: Supporta entrambi i metodi di storage
- `/api/v2/version/upload-chunked/*`: Upload ottimizzato per file grandi
- `/api/v2/download/{app}/{platform}/{version}`: Legge da BLOB o file storage

## 🔧 Configurazione Railway

### 1. **Mount Persistent Volume**
```yaml
# railway.json
{
  "services": {
    "api": {
      "volumes": [
        {
          "mount": "/app/storage",
          "name": "version-storage"
        }
      ]
    }
  }
}
```

### 2. **Environment Variables**
```bash
# Railway Dashboard > Variables
STORAGE_PATH=/app/storage
USE_FILE_STORAGE=true
MAX_FILE_SIZE_MB=500
ENVIRONMENT=production
```

### 3. **Volume Setup**
1. Go to Railway Dashboard
2. Select your service
3. Settings > Volumes
4. Add Volume:
   - Name: `version-storage`
   - Mount path: `/app/storage`
   - Size: 10GB (adjust as needed)

## 📁 Directory Structure
```
/app/storage/
├── versions/
│   ├── 1/                    # app_id
│   │   ├── android/
│   │   │   ├── 1.0.0/
│   │   │   │   ├── app.apk
│   │   │   │   └── app.apk.json
│   │   │   └── 1.0.1/
│   │   └── ios/
│   │       └── 1.0.0/
│   │           ├── app.ipa
│   │           └── app.ipa.json
├── temp/
└── backups/
```

## 🚀 Deploy su Railway

### 1. **Update Dockerfile**
```dockerfile
# Add to Dockerfile
RUN mkdir -p /app/storage/versions /app/storage/temp /app/storage/backups
RUN chmod -R 755 /app/storage
```

### 2. **Deploy Commands**
```bash
# Push changes
git add .
git commit -m "Add file storage support for large APK/IPA files"
git push

# Railway will auto-deploy
```

### 3. **Verify Storage**
```python
# Test endpoint to check storage
@app.get("/api/v2/storage/info")
async def get_storage_info():
    if storage_manager:
        return storage_manager.get_storage_stats()
    return {"error": "Storage not configured"}
```

## 📱 Frontend Changes
- Limite aumentato a 500MB
- Chunked upload automatico per file >50MB
- Indicatore "Storage su disco" per file grandi

## 🔍 Monitoring
```bash
# Check storage usage
df -h /app/storage

# List stored files
find /app/storage/versions -name "*.apk" -o -name "*.ipa" | wc -l

# Check file sizes
du -sh /app/storage/versions/*
```

## ⚠️ Important Notes
1. **Backup**: Railway volumes are persistent but implement regular backups
2. **Scaling**: Each instance needs access to the same volume
3. **Migration**: Existing BLOB data remains in DB, new large files use disk
4. **Cleanup**: Implement periodic cleanup of old versions

## 🐛 Troubleshooting

### File not found errors
```bash
# Check if volume is mounted
ls -la /app/storage

# Check permissions
chmod -R 755 /app/storage
```

### Upload fails for large files
```bash
# Increase timeouts in nginx/proxy
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
```

## 🎉 Benefits
- ✅ Support for APK/IPA files up to 500MB
- ✅ Reduced database load
- ✅ Better performance for large files
- ✅ Easier backup and migration
- ✅ Cost-effective storage solution