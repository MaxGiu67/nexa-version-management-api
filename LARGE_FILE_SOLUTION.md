# 🚨 Soluzione per Upload File Grandi (75MB+)

## Problema Identificato
Railway MySQL free tier ha un limite di `max_allowed_packet` che non può essere modificato dinamicamente. Questo causa l'errore "MySQL server has gone away" quando si cerca di salvare file grandi (>50MB) come BLOB.

## Soluzioni Implementate

### 1. ✅ Chunked Upload (Implementato)
- File divisi in chunk da 5MB
- Upload sequenziale dei chunk
- Riassemblaggio lato server
- **Status**: Funziona per l'upload ma fallisce al salvataggio in DB per file >50MB

### 2. 🔧 Limite File Size (Raccomandato)
```javascript
// In UploadForm.tsx
const MAX_DB_SIZE = 50 * 1024 * 1024; // 50MB limit for Railway MySQL

if (file.size > MAX_DB_SIZE) {
  alert("File troppo grande. Usa storage esterno per file >50MB");
  return;
}
```

### 3. 🌟 Storage Esterno (Soluzione Definitiva)

#### Opzione A: Filesystem Locale
```python
# Salva file su disco invece che in DB
import os
UPLOAD_DIR = "/app/uploads"

# In upload endpoint
file_path = os.path.join(UPLOAD_DIR, f"{version_id}_{file_name}")
with open(file_path, "wb") as f:
    f.write(file_content)

# Salva solo il path in DB
cursor.execute(
    """INSERT INTO app_versions (..., file_path, ...) 
       VALUES (..., %s, ...)""",
    (..., file_path, ...)
)
```

#### Opzione B: Cloud Storage (Consigliato)
```python
# Usa S3, Cloudflare R2, o simili
import boto3

s3 = boto3.client('s3')
s3.upload_fileobj(
    file_content,
    'bucket-name',
    f'versions/{app_id}/{version}/{file_name}'
)

# Salva URL in DB
file_url = f"https://bucket.s3.amazonaws.com/versions/{app_id}/{version}/{file_name}"
```

## Implementazione Immediata

Per risolvere subito il problema con il file da 75MB:

1. **Limita dimensione file nel frontend**:
   - Massimo 50MB per Railway MySQL free tier
   - Mostra messaggio chiaro all'utente

2. **Aggiungi validazione backend**:
   ```python
   if len(file_content) > 50 * 1024 * 1024:
       raise HTTPException(413, "File too large for database storage")
   ```

3. **Per file grandi, suggerisci alternative**:
   - Upload su Google Drive/Dropbox
   - Link diretto al file
   - Upgrade a Railway Pro (supporta file fino a 1GB)

## Configurazione Railway Pro
Se vuoi supportare file fino a 500MB:
- Upgrade a Railway Pro
- `max_allowed_packet` = 1GB su Pro tier
- Costo: ~$5/mese

## Conclusione
Per il caso specifico del file da 75MB:
1. **Immediato**: Usa limite 50MB
2. **Medio termine**: Implementa storage su filesystem
3. **Lungo termine**: Migra a cloud storage (S3/R2)