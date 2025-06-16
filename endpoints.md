# API Endpoints - Sistema Gestione Versioni

## Base URL
```
https://portaljs.nexadata.it/api/v1
```

## Headers Richiesti
```
Authorization: Bearer {jwt_token}  // Solo per endpoint protetti
X-Tenant: NEXA
Content-Type: application/json
```

---

## 1. Check for Updates (Pubblico)
Controlla se sono disponibili aggiornamenti per l'app.

### Request
```http
GET /app-version/check?current_version=1.0.1&platform=android
```

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| current_version | string | Yes | Versione corrente dell'app (es. "1.0.1") |
| platform | string | No | Piattaforma: "ios", "android", "all" (default: "all") |

### Response Success (200)
```json
{
  "hasUpdate": true,
  "latestVersion": "1.1.0",
  "versionCode": 3,
  "isMandatory": false,
  "minSupportedVersion": "1.0.0",
  "downloadUrl": "https://nexadata.it/apps/timesheet/v1.1.0.apk",
  "changelog": [
    "Nuova funzionalità: Export timesheet in PDF",
    "Aggiunta modalità offline con sincronizzazione",
    "Miglioramenti performance significativi",
    "Fix bug minori"
  ],
  "releaseDate": "2025-01-15"
}
```

### Response No Update (200)
```json
{
  "hasUpdate": false,
  "latestVersion": "1.0.1",
  "message": "App is up to date"
}
```

### Error Responses
- `400 Bad Request`: Missing required parameters
- `500 Internal Server Error`: Database error

---

## 2. Get Latest Version (Pubblico)
Ottiene informazioni sull'ultima versione disponibile.

### Request
```http
GET /app-version/latest?platform=ios
```

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| platform | string | No | Piattaforma: "ios", "android", "all" (default: "all") |

### Response (200)
```json
{
  "version": "1.1.0",
  "versionCode": 3,
  "platform": "ios",
  "releaseDate": "2025-01-15",
  "downloadUrl": "https://apps.apple.com/app/nexa-timesheet/id123456789",
  "changelog": [
    "Nuova funzionalità: Export timesheet in PDF",
    "Supporto per Dynamic Island su iPhone 14 Pro"
  ],
  "isMandatory": false,
  "minSupportedVersion": "1.0.0"
}
```

---

## 3. Log Update (Autenticato)
Registra quando un utente aggiorna l'app.

### Request
```http
POST /app-version/log-update
Authorization: Bearer {jwt_token}
```

### Request Body
```json
{
  "from_version": "1.0.1",
  "to_version": "1.1.0",
  "platform": "android",
  "update_type": "manual",
  "device_info": {
    "model": "Samsung Galaxy S22",
    "os_version": "33",
    "expo_version": "53.0.0"
  }
}
```

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| from_version | string | No | Versione precedente (null se prima installazione) |
| to_version | string | Yes | Nuova versione installata |
| platform | string | Yes | "ios" o "android" |
| update_type | string | Yes | "manual", "forced", "auto" |
| device_info | object | No | Informazioni sul dispositivo |

### Response Success (201)
```json
{
  "success": true,
  "message": "Update logged successfully",
  "log_id": 123
}
```

### Error Responses
- `401 Unauthorized`: Missing or invalid token
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Database error

---

## 4. Get Version History (Autenticato - Admin)
Ottiene lo storico delle versioni rilasciate.

### Request
```http
GET /app-version/history?platform=all&limit=10
Authorization: Bearer {admin_jwt_token}
```

### Response (200)
```json
{
  "versions": [
    {
      "version": "1.1.0",
      "versionCode": 3,
      "platform": "all",
      "releaseDate": "2025-01-15",
      "isActive": true,
      "isMandatory": false,
      "downloadUrl": "https://nexadata.it/apps/timesheet/v1.1.0.apk",
      "updateCount": 45
    },
    {
      "version": "1.0.1",
      "versionCode": 2,
      "platform": "all",
      "releaseDate": "2025-01-10",
      "isActive": true,
      "isMandatory": false,
      "downloadUrl": "https://nexadata.it/apps/timesheet/v1.0.1.apk",
      "updateCount": 128
    }
  ],
  "total": 2
}
```

---

## 5. Get Update Statistics (Autenticato - Admin)
Ottiene statistiche sugli aggiornamenti.

### Request
```http
GET /app-version/stats
Authorization: Bearer {admin_jwt_token}
```

### Response (200)
```json
{
  "totalUsers": 250,
  "versionDistribution": {
    "1.1.0": {
      "count": 45,
      "percentage": 18.0,
      "platforms": {
        "android": 30,
        "ios": 15
      }
    },
    "1.0.1": {
      "count": 180,
      "percentage": 72.0,
      "platforms": {
        "android": 100,
        "ios": 80
      }
    },
    "1.0.0": {
      "count": 25,
      "percentage": 10.0,
      "platforms": {
        "android": 20,
        "ios": 5
      }
    }
  },
  "lastUpdates": [
    {
      "userId": 123,
      "userName": "Mario Rossi",
      "fromVersion": "1.0.1",
      "toVersion": "1.1.0",
      "platform": "android",
      "updatedAt": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

## Codici di Errore Standard

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Parametri mancanti o invalidi |
| 401 | Unauthorized - Token mancante o invalido |
| 403 | Forbidden - Permessi insufficienti |
| 404 | Not Found - Risorsa non trovata |
| 500 | Internal Server Error |

---

## Note Implementazione

1. **Cache**: Implementare cache con TTL di 5 minuti per ridurre carico DB
2. **Rate Limiting**: Max 100 richieste/ora per IP su endpoint pubblici
3. **Sicurezza**: Validare sempre i parametri di input
4. **Logging**: Registrare tutte le richieste per analisi
5. **CORS**: Abilitare CORS per permettere richieste dall'app