# 📤 Chunked Upload Implementation Guide

## Overview
This guide explains the chunked upload feature implemented to handle large APK/IPA files (>50MB) that were causing "MySQL server has gone away" errors.

## Problem
When uploading files larger than 50MB to Railway's MySQL database, the connection would timeout with the error:
```
INFO: 127.0.0.1:49932 - "POST /api/v2/version/upload HTTP/1.1" 500 Internal Server Error
pymysql.err.OperationalError: (2006, 'MySQL server has gone away')
```

## Solution
Implemented a chunked upload system that:
1. Splits large files into 5MB chunks
2. Uploads chunks sequentially
3. Reassembles on the server
4. Stores complete file in database

## API Endpoints

### 1. Start Chunked Upload
```http
POST /api/v2/version/upload-chunked/start
Content-Type: multipart/form-data

Parameters:
- app_identifier: string
- version: string
- version_code: integer
- platform: string (android/ios)
- file_size: integer (bytes)
- file_name: string
- is_mandatory: boolean (optional)
- changelog: string (optional, JSON array)

Response:
{
  "upload_id": "uuid",
  "chunk_size": 5242880,
  "total_chunks": 15
}
```

### 2. Upload Chunk
```http
POST /api/v2/version/upload-chunked/{upload_id}/chunk/{chunk_number}
Content-Type: multipart/form-data

Parameters:
- chunk: binary file data

Response:
{
  "chunk_number": 0,
  "size": 5242880,
  "received": true
}
```

### 3. Complete Upload
```http
POST /api/v2/version/upload-chunked/{upload_id}/complete

Response:
{
  "success": true,
  "message": "Version uploaded successfully",
  "version_id": 123,
  "version": "1.0.0",
  "platform": "android",
  "file_hash": "sha256hash"
}
```

## Frontend Implementation

The frontend automatically uses chunked upload for files >50MB:

```typescript
// Automatic detection in UploadForm.tsx
if (selectedFile.size > 50 * 1024 * 1024) {
  setUseChunkedUpload(true);
  // File will be uploaded in chunks
}
```

## Features
- ✅ Automatic chunking for files >50MB
- ✅ Progress tracking per chunk
- ✅ Session timeout after 1 hour
- ✅ SHA256 hash verification
- ✅ Automatic cleanup of expired sessions
- ✅ Error recovery on chunk failure

## Configuration
```python
# In multi_app_api.py
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks
SESSION_TIMEOUT = 3600  # 1 hour
```

## Benefits
1. **Reliability**: No more connection timeouts
2. **Progress Tracking**: Real-time progress updates
3. **Resume Support**: Can be extended to support resume
4. **Scalability**: Works with files up to 500MB

## Usage Example
```bash
# Upload a 75MB APK file
1. Select file in UI
2. System detects size >50MB
3. Automatically uses chunked upload
4. Shows progress: "Upload a blocchi in corso... 45%"
5. File uploaded successfully!
```

## Future Improvements
- [ ] Resume interrupted uploads
- [ ] Parallel chunk uploads
- [ ] Compression before upload
- [ ] External storage (S3) for very large files