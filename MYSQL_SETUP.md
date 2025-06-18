# MySQL Backend Setup Guide

## 🚀 Quick Start

### 1. Configuration Already Set
The `.env.local` file is already configured with MySQL credentials:
```env
DB_HOST=tramway.proxy.rlwy.net
DB_PORT=20671
DB_USER=root
DB_PASSWORD=aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP
DB_NAME=railway
```

### 2. Test Connection
```bash
cd version-management/api/
python test_mysql_connection.py
```

### 3. Start Backend
```bash
python multi_app_api.py
```

### 4. Start Frontend (in another terminal)
```bash
cd version-management/api/frontend/version-manager/
npm start
```

## 📋 Available Commands

### Backend API (Terminal 1)
```bash
cd version-management/api/
source venv/bin/activate  # or .venvwsl/bin/activate
python multi_app_api.py
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

### Frontend Web (Terminal 2)
```bash
cd version-management/api/frontend/version-manager/
npm start
```

The frontend will be available at:
- http://localhost:3000

## 🔍 Verify Setup

1. **Test API Health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check Database Connection**:
   ```bash
   curl http://localhost:8000/ping
   ```

3. **View API Documentation**:
   Open http://localhost:8000/docs in your browser

## 📊 Database Information
- **Type**: MySQL 8.0
- **Host**: tramway.proxy.rlwy.net
- **Port**: 20671
- **Database**: railway
- **Provider**: Railway Cloud
- **Connection String**: `mysql://root:aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP@tramway.proxy.rlwy.net:20671/railway`

## 🚨 Troubleshooting

### Connection Timeout
If you see connection timeout errors:
1. Check Railway dashboard - ensure MySQL service is running
2. Verify your IP is not blocked by Railway
3. Try the wake_and_test.py script to diagnose

### Frontend Can't Connect to Backend
1. Ensure backend is running on port 8000
2. Check CORS is enabled in the backend
3. Verify API_KEY header is set correctly

### Database Tables Not Created
The backend automatically creates tables on startup. If missing:
1. Check backend logs for errors
2. Manually run SQL from the startup script
3. Verify database permissions