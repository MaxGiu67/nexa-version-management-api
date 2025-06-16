# 🚂 Railway Pro Deployment Guide

## 🚀 Overview
This guide covers deploying the Version Management API on Railway Pro with enhanced file upload capabilities.

## ✨ Railway Pro Benefits
- **Larger File Uploads**: Support for APK/IPA files up to 1GB
- **Higher MySQL Limits**: `max_allowed_packet` up to 1GB
- **Better Performance**: More CPU and memory resources
- **No Sleep Mode**: Always-on service availability

## 📋 Prerequisites
1. Railway Pro subscription active
2. MySQL database provisioned on Railway
3. Environment variables configured

## 🔧 Configuration

### 1. Environment Variables
Set these in your Railway project settings:

```bash
# Database Connection (auto-provided by Railway)
MYSQL_DATABASE_URL=mysql://user:password@host:port/database

# File Size Limits
MAX_FILE_SIZE_MB=500  # Can be increased up to 1024 (1GB) with Pro

# MySQL Configuration
MYSQL_MAX_ALLOWED_PACKET=1073741824  # 1GB in bytes

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=nexa_internal_app_key_2025

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.railway.app
```

### 2. MySQL Configuration
Railway Pro automatically configures MySQL with higher limits, but you can verify:

```sql
SHOW VARIABLES LIKE 'max_allowed_packet';
-- Should show: 1073741824 (1GB)
```

### 3. File Upload Limits
The API now supports configurable file size limits:

- **Default**: 500MB (safe for most mobile apps)
- **Maximum with Railway Pro**: 1GB
- **Configure via**: `MAX_FILE_SIZE_MB` environment variable

## 🚀 Deployment Steps

### 1. Connect GitHub Repository
```bash
# In Railway dashboard
1. Create new project
2. Deploy from GitHub repo
3. Select your repository
4. Railway auto-detects Python app
```

### 2. Add MySQL Service
```bash
# In Railway project
1. New Service > Database > MySQL
2. Railway provisions MySQL with Pro limits
3. Connection URL auto-added to env vars
```

### 3. Configure Environment
```bash
# Set required environment variables
# Railway dashboard > Variables
# Add all variables from section above
```

### 4. Deploy
```bash
# Automatic deployment on git push
git push origin main

# Or manual deploy
railway up
```

## 📊 Monitoring

### Check File Upload Status
```python
# In logs, look for:
"Successfully uploaded version X.Y.Z"
"File size: XXX MB"
```

### Database Storage
```sql
-- Check total storage used
SELECT 
    table_schema AS 'Database',
    SUM(data_length + index_length) / 1024 / 1024 / 1024 AS 'Size (GB)'
FROM information_schema.tables
WHERE table_schema = 'railway'
GROUP BY table_schema;

-- Check app_versions table size
SELECT 
    COUNT(*) as total_versions,
    SUM(file_size) / 1024 / 1024 / 1024 as total_gb
FROM app_versions;
```

## 🔍 Troubleshooting

### 1. File Upload Fails
```bash
# Check error in logs
"File size XXX MB exceeds limit of YYY MB"

# Solution: Increase MAX_FILE_SIZE_MB
```

### 2. MySQL Packet Error
```bash
# Error: "Packet too large"

# Solution: Verify MYSQL_MAX_ALLOWED_PACKET
# Railway Pro should auto-configure to 1GB
```

### 3. Memory Issues
```bash
# If uploads fail for large files
# Railway Pro provides 8GB RAM
# Monitor usage in Railway metrics
```

## 🎯 Best Practices

### 1. Progressive File Sizes
- Start with 500MB limit
- Monitor usage patterns
- Increase gradually if needed

### 2. Cleanup Old Versions
```python
# Implement retention policy
# Keep only last 5 versions per platform
DELETE FROM app_versions 
WHERE id NOT IN (
    SELECT id FROM (
        SELECT id FROM app_versions 
        WHERE app_id = ? AND platform = ?
        ORDER BY created_at DESC 
        LIMIT 5
    ) AS keep_versions
);
```

### 3. Monitor Storage
- Set up alerts for database size
- Regular cleanup of old versions
- Consider external storage for very large files

## 📈 Performance Tips

### 1. Connection Pooling
```python
# Already implemented in multi_app_api.py
# Adjust pool size based on load
pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
```

### 2. Async Uploads
- Current implementation handles large files well
- Consider background jobs for very large files

### 3. CDN for Downloads
- For global distribution, consider CDN
- Railway provides good bandwidth for most use cases

## 🔐 Security

### 1. API Key Protection
- Rotate API keys regularly
- Use different keys for different environments

### 2. File Validation
- Always validate file types
- Check file signatures, not just extensions
- Scan for malware if possible

### 3. Rate Limiting
- Implement rate limits for uploads
- Prevent abuse of storage

## 📝 Maintenance

### Regular Tasks
1. **Weekly**: Check storage usage
2. **Monthly**: Review upload patterns
3. **Quarterly**: Clean old versions
4. **Yearly**: Review and optimize schema

### Backup Strategy
```bash
# Railway provides automated backups with Pro
# Additional backup via mysqldump
mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD railway > backup.sql
```

## 🆘 Support

### Railway Pro Support
- Priority support channel
- Direct access to Railway team
- SLA guarantees

### Common Issues
1. **Deployment fails**: Check build logs
2. **Database connection**: Verify credentials
3. **File uploads slow**: Check metrics, consider CDN

---

**Last Updated**: January 2025  
**Tested with**: Railway Pro, MySQL 8.0, Python 3.11