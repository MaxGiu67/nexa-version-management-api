# Docker Deployment Guide for Version Manager Frontend

## Prerequisites
- Docker installed on your machine
- Docker Hub account
- Access to push to your Docker Hub repository

## Building the Docker Image

### 1. Build the Production Image Locally

```bash
# Navigate to the frontend directory
cd /Users/maxgiu/Git_progetti/nexa-timsheet/version-management/api/frontend/version-manager

# Build the Docker image
docker build -f Dockerfile.production -t nexadata/version-manager-frontend:latest .

# Tag with version number (optional but recommended)
docker tag nexadata/version-manager-frontend:latest nexadata/version-manager-frontend:1.0.0
```

### 2. Test the Image Locally

```bash
# Run the container
docker run -d -p 3000:80 --name version-manager-test nexadata/version-manager-frontend:latest

# Check if it's running
docker ps

# Test the application
open http://localhost:3000

# View logs if needed
docker logs version-manager-test

# Stop and remove test container
docker stop version-manager-test
docker rm version-manager-test
```

## Pushing to Docker Hub

### 1. Login to Docker Hub

```bash
docker login
# Enter your Docker Hub username and password
```

### 2. Push the Image

```bash
# Push the latest tag
docker push nexadata/version-manager-frontend:latest

# Push the version tag (if created)
docker push nexadata/version-manager-frontend:1.0.0
```

## Using Docker Compose

### Local Development/Testing

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment on Railway

1. **Update Railway Configuration**:
   - Remove the build configuration
   - Set the Docker image source to: `nexadata/version-manager-frontend:latest`

2. **Environment Variables on Railway**:
   ```
   PORT=80
   REACT_APP_API_URL=https://nexa-version-management-be.up.railway.app
   REACT_APP_API_KEY=nexa_internal_app_key_2025
   ```

3. **Deploy from Docker Hub**:
   Railway will automatically pull the image from Docker Hub instead of building it.

## Automated Build Script

Create a `build-and-push.sh` script for easy updates:

```bash
#!/bin/bash
VERSION=${1:-latest}

echo "Building version-manager-frontend:$VERSION..."
docker build -f Dockerfile.production -t nexadata/version-manager-frontend:$VERSION .

if [ "$VERSION" != "latest" ]; then
    docker tag nexadata/version-manager-frontend:$VERSION nexadata/version-manager-frontend:latest
fi

echo "Pushing to Docker Hub..."
docker push nexadata/version-manager-frontend:$VERSION

if [ "$VERSION" != "latest" ]; then
    docker push nexadata/version-manager-frontend:latest
fi

echo "Done! Image pushed: nexadata/version-manager-frontend:$VERSION"
```

Make it executable:
```bash
chmod +x build-and-push.sh
```

Use it:
```bash
./build-and-push.sh 1.0.0
```

## Best Practices

1. **Version Tagging**: Always tag your images with version numbers in addition to `latest`
2. **Security**: Don't hardcode sensitive data in Dockerfiles - use environment variables
3. **Size Optimization**: The multi-stage build reduces the final image size significantly
4. **Cache**: Docker Hub will cache layers, making subsequent pulls faster

## Troubleshooting

### Image Too Large
The multi-stage build should keep the image small (~50MB), but if needed:
- Check for unnecessary files in the build
- Use `.dockerignore` to exclude files

### Environment Variables Not Working
- Ensure variables are set at build time for React apps
- Use `REACT_APP_` prefix for Create React App

### Railway Not Pulling Latest Image
- Make sure to push with the exact tag Railway expects
- You might need to trigger a redeploy in Railway

## Docker Hub Repository Structure

Your Docker Hub repository should be organized as:
```
nexadata/version-manager-frontend
├── Tags
│   ├── latest (always points to newest version)
│   ├── 1.0.0
│   ├── 1.0.1
│   └── ... (semantic versioning)
```

## Quick Reference Commands

```bash
# Build
docker build -f Dockerfile.production -t nexadata/version-manager-frontend:latest .

# Run locally
docker run -d -p 3000:80 nexadata/version-manager-frontend:latest

# Push to Docker Hub
docker push nexadata/version-manager-frontend:latest

# Pull from Docker Hub
docker pull nexadata/version-manager-frontend:latest

# View image details
docker inspect nexadata/version-manager-frontend:latest
```