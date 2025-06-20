# Sistema di Autenticazione con 2FA per Version Management

## 🔐 Overview

Sistema completo di autenticazione con supporto per **Google Authenticator** (2FA) per il Version Management di Nexa Timesheet.

### Funzionalità Implementate

- ✅ **Login con username/password**
- ✅ **Autenticazione a due fattori (2FA) con Google Authenticator**
- ✅ **Gestione sessioni con JWT-like tokens**
- ✅ **Protezione brute-force con account lockout**
- ✅ **Codici di backup per 2FA**
- ✅ **Audit log completo**
- ✅ **Gestione utenti admin (CRUD)**
- ✅ **Componenti React per login e profilo**

## 🚀 Quick Start

### 1. Installazione e Setup

```bash
# Naviga nella directory API
cd version-management/api/

# Attiva virtual environment
source venv/bin/activate

# Installa nuove dipendenze
pip install -r requirements.txt

# Esegui migration database e setup
python integrate_auth.py
```

### 2. Avvio Sistema con Autenticazione

```bash
# Avvia API con autenticazione integrata
python integrated_api.py

# In un altro terminale, avvia il frontend
cd frontend/version-manager/
npm start
```

### 3. Credenziali Default

```
Username: admin
Password: admin123
```

⚠️ **IMPORTANTE**: Cambiare la password al primo accesso!

## 📱 Configurazione Google Authenticator

### Per gli Utenti

1. **Accedi** con le tue credenziali
2. Vai su **Profilo** → **Abilita 2FA**
3. **Scansiona il QR code** con Google Authenticator
4. **Salva i codici di backup** in un posto sicuro
5. **Conferma** l'attivazione inserendo un codice

### App Supportate

- Google Authenticator (consigliato)
- Microsoft Authenticator
- Authy
- Qualsiasi app TOTP compatibile

## 🔒 Sicurezza

### Protezioni Implementate

1. **Password Hashing**: bcrypt con salt automatico
2. **Brute Force Protection**: 
   - Max 5 tentativi login
   - Account lockout per 30 minuti
3. **Session Management**:
   - Token sicuri con expiry
   - Cleanup automatico sessioni scadute
4. **2FA Security**:
   - Secret keys univoci per utente
   - Codici backup monouso
   - Time-based OTP (30 secondi)

### Best Practices

- Usa password complesse (min 8 caratteri)
- Abilita sempre 2FA per admin
- Conserva i codici backup offline
- Monitora l'audit log regolarmente

## 🛠️ API Endpoints

### Autenticazione Pubblica

```http
POST /api/v2/auth/login
{
  "username": "admin",
  "password": "password123"
}

POST /api/v2/auth/verify-2fa
{
  "session_token": "xxx",
  "totp_code": "123456"
}
```

### Endpoints Protetti (Require Auth)

```http
GET    /api/v2/auth/me              # Profilo utente corrente
POST   /api/v2/auth/logout          # Logout
POST   /api/v2/auth/enable-2fa      # Abilita 2FA
POST   /api/v2/auth/disable-2fa     # Disabilita 2FA
```

### Admin Only (Superadmin)

```http
POST   /api/v2/auth/users           # Crea nuovo admin
GET    /api/v2/auth/users           # Lista admin
PUT    /api/v2/auth/users/{id}/toggle-active
GET    /api/v2/auth/audit-log       # Audit log
```

## 🎨 Componenti Frontend

### Login Component

```tsx
import { Login } from './components/Login';

<Login onLogin={(token, user) => {
  // Salva token e user data
  localStorage.setItem('authToken', token);
  setCurrentUser(user);
}} />
```

### User Profile Component

```tsx
import { UserProfile } from './components/UserProfile';

<UserProfile 
  user={currentUser}
  authToken={authToken}
/>
```

## 🗃️ Database Schema

### Tabelle Aggiunte

1. **admin_users**: Utenti amministratori
2. **user_2fa_settings**: Configurazioni 2FA
3. **admin_sessions**: Sessioni attive
4. **admin_audit_log**: Log delle azioni

## 🧪 Testing

### Test Automatico

```bash
# Esegui test suite autenticazione
python test_auth.py
```

### Test Manuale 2FA

1. Login normale → ricevi session_token
2. Se 2FA abilitato → inserisci codice da app
3. Oppure usa un codice backup

### Test con cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -H "X-API-Key: nexa_internal_app_key_2025" \
  -d '{"username":"admin","password":"admin123"}'

# Get profile (con token)
curl -X GET http://localhost:8000/api/v2/auth/me \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "X-API-Key: nexa_internal_app_key_2025"
```

## 🐛 Troubleshooting

### Problema: "Account bloccato"
**Soluzione**: Attendere 30 minuti o sbloccare da DB:
```sql
UPDATE admin_users SET locked_until = NULL, failed_login_attempts = 0 WHERE username = 'admin';
```

### Problema: "Codice 2FA non valido"
**Possibili cause**:
- Orario dispositivo non sincronizzato
- Codice scaduto (attendi nuovo codice)
- App authenticator non configurata correttamente

### Problema: "Sessione scaduta"
**Soluzione**: Le sessioni durano 24 ore. Effettua nuovo login.

## 📈 Monitoraggio

### Audit Log

Tutte le azioni sono tracciate:
- Login/logout
- Abilitazione/disabilitazione 2FA
- Creazione/modifica utenti
- Tentativi di accesso falliti

### Query Utili

```sql
-- Ultimi login
SELECT * FROM admin_audit_log 
WHERE action = 'LOGIN_ATTEMPT' 
ORDER BY created_at DESC LIMIT 10;

-- Utenti con 2FA abilitato
SELECT u.*, s.is_enabled as has_2fa 
FROM admin_users u
LEFT JOIN user_2fa_settings s ON u.id = s.user_id;

-- Sessioni attive
SELECT * FROM admin_sessions 
WHERE expires_at > NOW();
```

## 🚀 Deploy in Produzione

### Checklist Pre-Deploy

- [ ] Cambiare password admin default
- [ ] Configurare HTTPS/SSL
- [ ] Abilitare 2FA per tutti gli admin
- [ ] Configurare backup database
- [ ] Testare recovery con codici backup
- [ ] Impostare monitoring alerts

### Environment Variables

```env
# Aggiungi a .env.production
JWT_SECRET_KEY=your-secure-random-key
SESSION_TIMEOUT_HOURS=24
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
TOTP_ISSUER_NAME=Nexa Version Manager
```

## 📞 Supporto

Per problemi o domande:
1. Controlla i log: `tail -f logs/auth.log`
2. Verifica audit log nel database
3. Contatta il team DevOps

---

**Versione**: 1.0.0  
**Ultimo aggiornamento**: 20 Gennaio 2025