# Deploy Frontend usando Docker Image Pre-buildata

## Opzione 1: Usa la nostra immagine pubblica

Abbiamo già preparato un'immagine Docker pronta all'uso. Segui questi passi in Railway:

### 1. Crea nuovo servizio in Railway
- Vai al tuo progetto Railway
- Click "New Service"
- Seleziona "Deploy a Docker Image"

### 2. Configura l'immagine
Inserisci questo nome immagine:
```
maxgiu67/nexa-version-manager-frontend:latest
```

### 3. Configura le variabili d'ambiente
Aggiungi solo questa variabile:
```
PORT=80
```

### 4. Deploy
Railway scaricherà e avvierà automaticamente l'immagine.

## Opzione 2: Build locale e push

Se vuoi buildare tu stesso l'immagine:

### Prerequisiti
1. Docker Desktop installato e in esecuzione
2. Account Docker Hub (gratuito su hub.docker.com)

### Build e Push
```bash
# 1. Login a Docker Hub
docker login

# 2. Build l'immagine
cd version-management/api/frontend/version-manager
docker build -f Dockerfile.production -t TUO_USERNAME/version-manager-frontend:latest .

# 3. Push su Docker Hub
docker push TUO_USERNAME/version-manager-frontend:latest

# 4. Usa l'immagine in Railway
# Inserisci: TUO_USERNAME/version-manager-frontend:latest
```

## Vantaggi di questo approccio

1. **No build time**: Railway non deve buildare, solo scaricare ed eseguire
2. **Più affidabile**: L'immagine è già testata e funzionante
3. **Più veloce**: Deploy in secondi invece di minuti
4. **Controllo versioni**: Puoi taggare versioni specifiche

## Configurazione Railway

Nel dashboard Railway del servizio:

1. **Source**: Docker Image
2. **Image**: `maxgiu67/nexa-version-manager-frontend:latest`
3. **Environment Variables**:
   - `PORT=80`
4. **Deploy Settings**:
   - Start Command: (lascia vuoto, usa default)
   - Health Check Path: `/`

L'app sarà disponibile all'URL fornito da Railway!