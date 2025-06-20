# Quick Start - Docker Deployment

## Step 1: Ensure Docker is Running
```bash
# Check if Docker is running
docker version

# If not, start Docker Desktop (macOS/Windows) or Docker service (Linux)
```

## Step 2: Build the Image
```bash
# Build production image
docker build -f Dockerfile.production -t nexadata/version-manager-frontend:latest .
```

## Step 3: Test Locally
```bash
# Run the container
docker run -d -p 3000:80 --name vm-frontend nexadata/version-manager-frontend:latest

# Open in browser
open http://localhost:3000

# Check logs
docker logs vm-frontend

# Stop when done
docker stop vm-frontend && docker rm vm-frontend
```

## Step 4: Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Push the image
docker push nexadata/version-manager-frontend:latest
```

## Step 5: Deploy on Railway
1. Go to Railway dashboard
2. Update your service settings:
   - Source: Docker Hub
   - Image: `nexadata/version-manager-frontend:latest`
   - Remove build command
3. Set environment variable: `PORT=80`
4. Deploy!

## Alternative: Use the Script
```bash
# One command to build and push
./build-and-push.sh 1.0.0
```

## Environment Variables
The image has these defaults built-in:
- `REACT_APP_API_URL=https://nexa-version-management-be.up.railway.app`
- `REACT_APP_API_KEY=nexa_internal_app_key_2025`

You can override them in Railway if needed.