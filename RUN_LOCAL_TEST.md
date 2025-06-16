# 🧪 Test API in Locale

## 📁 Posizione corretta:
Tutto è ora organizzato in `/version-management/api/`

## 🚀 Comandi per testare:

### 1. Vai nella cartella API:
```bash
cd /Users/maxgiu/Git_progetti/nexa-timsheet/version-management/api
```

### 2. Setup ambiente (solo prima volta):
```bash
./setup_local_test.sh
```

### 3. Avvia il server:
```bash
# Attiva ambiente virtuale
source venv/bin/activate

# Avvia server
python main.py
```

Dovresti vedere:
```
🚀 Starting API server on port 8000
📊 Database: railway @ tramway.proxy.rlwy.net:20671
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. In un NUOVO terminale, testa:
```bash
# Vai nella cartella
cd /Users/maxgiu/Git_progetti/nexa-timsheet/version-management/api

# Attiva ambiente
source venv/bin/activate

# Esegui test
python test_local_api.py
```

## 🌐 Test manuale nel browser:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Test con curl:

```bash
# Check updates
curl "http://localhost:8000/api/v1/app-version/check?current_version=1.0.0&platform=android"

# Latest version
curl "http://localhost:8000/api/v1/app-version/latest?platform=android"

# Health check
curl http://localhost:8000/health
```

## ✅ Risultati attesi:

1. **Health check**: `{"status":"healthy","service":"app-version-management"}`

2. **Check update (v1.0.0)**: Dovrebbe mostrare che c'è un aggiornamento alla 1.2.0

3. **Latest version**: Dovrebbe mostrare la versione 1.2.0

## 🛑 Per fermare:

- **Server**: `CTRL+C` nel terminale del server
- **Disattiva ambiente**: `deactivate`

---

📌 **Nota**: Il server si connette automaticamente al tuo database Railway MySQL con le credenziali corrette!