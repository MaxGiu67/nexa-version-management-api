# 🗄️ Version Manager Frontend

Frontend React per la gestione delle versioni dell'app Nexa Timesheet con storage BLOB nel database.

## 🚀 Funzionalità

### ✅ Implementato

- **📊 Dashboard**: Panoramica storage con statistiche in tempo reale
- **📤 Upload Manager**: Form per caricare file APK/IPA con validazione
- **📱 Gestione Versioni**: Lista completa con azioni (download, elimina)
- **🎨 UI Moderna**: Design responsive con styled-components
- **📈 Statistiche**: Analytics dettagliate per piattaforma
- **🔍 Filtri**: Ricerca e filtri per versione/piattaforma/stato

### 🚧 Da Sviluppare

- **👥 Gestione Utenti**: Sistema autenticazione e permessi
- **⚙️ Impostazioni**: Configurazione sistema e preferenze

## 🏗️ Struttura Progetto

```
src/
├── components/          # Componenti React
│   ├── Dashboard.tsx    # Dashboard principale
│   ├── UploadForm.tsx   # Form upload file
│   └── VersionsList.tsx # Lista e gestione versioni
├── services/           # Servizi API
│   └── api.ts          # Client API e utilities
├── types/              # TypeScript types
│   └── index.ts        # Definizioni tipi
├── App.tsx             # App principale con routing
└── index.tsx           # Entry point

```

## 🛠️ Tecnologie

- **React 18** + TypeScript
- **React Router** per navigazione
- **Styled Components** per styling
- **Axios** per API calls
- **Lucide React** per icone

## 📦 Installazione

```bash
# Installa dipendenze
npm install

# Avvia development server
npm start

# Build per produzione
npm run build
```

## ⚙️ Configurazione

### Environment Variables

```env
# .env
REACT_APP_API_URL=http://localhost:8000
GENERATE_SOURCEMAP=false
```

### API Backend

Il frontend comunica con l'API FastAPI tramite:

- **Health Check**: `GET /health`
- **Upload File**: `POST /api/v1/app-version/upload`
- **Lista File**: `GET /api/v1/app-version/files`
- **Storage Info**: `GET /api/v1/app-version/storage-info`
- **Download**: `GET /download/{platform}/{version}`
- **Elimina**: `DELETE /api/v1/app-version/files/{platform}/{version}`

## 🎨 Design System

### Colori

```css
--primary: #1a237e;      /* Blu primario */
--secondary: #ff6b35;    /* Arancione accento */
--success: #28a745;      /* Verde successo */
--danger: #dc3545;       /* Rosso errore */
--android: #a4c639;      /* Verde Android */
--ios: #007aff;          /* Blu iOS */
```

### Layout

- **Sidebar**: Navigazione collassabile
- **TopBar**: Header con titoli dinamici
- **MainContent**: Area contenuto principale
- **Cards**: Design moderno con shadow e bordi arrotondati

## 📱 Responsive Design

- **Desktop**: Layout sidebar + content
- **Tablet**: Sidebar collassabile
- **Mobile**: Sidebar overlay con hamburger menu

## 🔧 Componenti Principali

### Dashboard

- **Storage Stats**: File totali, spazio utilizzato, download
- **Platform Breakdown**: Statistiche separate Android/iOS
- **Recent Files**: Ultimi file caricati
- **Real-time Updates**: Aggiornamento automatico dati

### Upload Form

- **Drag & Drop**: Area upload intuitiva
- **Validazione**: Controllo tipo file e dimensioni
- **Progress Bar**: Indicatore upload
- **Changelog**: Editor modifiche strutturato

### Versions List

- **Grid Layout**: Cards per ogni versione
- **Filtri**: Piattaforma, stato, ricerca
- **Actions**: Download e eliminazione
- **Metadata**: Hash, dimensioni, download count

## 🚀 Deployment

### Development

```bash
npm start
# Apre http://localhost:3000
```

### Production Build

```bash
npm run build
# Genera build/ directory
```

### Deployment Server

```bash
# Serve build statica
npx serve -s build -l 3000

# O con nginx
server {
    listen 80;
    root /path/to/build;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 🔗 Integrazione con Backend

### CORS Configuration

Il backend deve permettere richieste da frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Setup

1. **Backend**: Avvia API su `localhost:8000`
2. **Frontend**: Avvia React su `localhost:3000`
3. **Database**: Railway MySQL configurato

## 🧪 Testing

```bash
# Run tests
npm test

# Test coverage
npm run test:coverage
```

## 📈 Performance

- **Code Splitting**: Lazy loading componenti
- **Image Optimization**: Icone SVG ottimizzate
- **Bundle Size**: Webpack optimization
- **API Caching**: Cache API responses

## 🛡️ Security

- **Environment Variables**: API URL configurabile
- **HTTPS Ready**: SSL/TLS support
- **Input Validation**: Validazione lato client e server
- **File Type Validation**: Solo APK/IPA permessi

## 🤝 Contributi

1. Fork il repository
2. Crea feature branch
3. Commit modifiche
4. Push to branch
5. Crea Pull Request

## 📄 License

Questo progetto è proprietà di NEXA DATA Srl.

---

**Frontend pronto per la gestione completa del database delle versioni!** 🚀