# PostgreSQL Backend Setup Guide

## 🚀 Quick Start

### 1. Add PostgreSQL Password
Open `.env.local` and replace `INSERISCI_LA_PASSWORD_QUI` with your actual Railway PostgreSQL password:
```bash
PGPASSWORD=your_actual_password_here
```

### 2. Test Connection
```bash
python test_postgres_quick.py
```

### 3. Start Backend
```bash
python multi_app_api_postgres.py
```

## 📋 Complete Setup Steps

### Step 1: Get PostgreSQL Password from Railway
1. Go to Railway dashboard
2. Click on your PostgreSQL service
3. Go to "Variables" tab
4. Copy the value of `PGPASSWORD`

### Step 2: Update Environment File
Edit `version-management/api/.env.local`:
```env
PGHOST=yamabiko.proxy.rlwy.net
PGPORT=41888
PGUSER=postgres
PGPASSWORD=YOUR_RAILWAY_PASSWORD_HERE  # <-- Replace this
PGDATABASE=railway
```

### Step 3: Verify Connection
```bash
cd version-management/api/
python test_postgres_quick.py
```

Expected output:
```
🔍 Testing PostgreSQL connection...
Host: yamabiko.proxy.rlwy.net
Port: 41888
Database: railway
✅ Connected successfully!
📊 PostgreSQL: PostgreSQL 16.x ...
```

### Step 4: Start Backend API
```bash
python multi_app_api_postgres.py
```

The API will:
- Start on http://localhost:8000
- Create necessary tables automatically
- Show API documentation at http://localhost:8000/docs

### Step 5: Start Frontend (in another terminal)
```bash
cd version-management/api/frontend/version-manager/
npm start
```

Frontend will be available at http://localhost:3000

## 🔍 Troubleshooting

### Connection Failed
If you see "Connection failed", check:
1. Password is correctly copied (no extra spaces)
2. Railway PostgreSQL service is active
3. Your IP is not blocked by Railway

### Test Endpoints
Once running, test these:
- http://localhost:8000/ping - Should return "pong"
- http://localhost:8000/health - Shows database status
- http://localhost:8000/docs - Interactive API documentation

## 📝 Database Info
- **Type**: PostgreSQL 16+
- **Host**: yamabiko.proxy.rlwy.net
- **Port**: 41888
- **Database**: railway
- **Connection URL**: `postgresql://postgres:PASSWORD@yamabiko.proxy.rlwy.net:41888/railway`