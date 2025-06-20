#!/bin/bash

# Build and push script for Version Manager Frontend
# Usage: ./build-and-push.sh [version]
# Example: ./build-and-push.sh 1.0.0

VERSION=${1:-latest}
IMAGE_NAME="nexadata/version-manager-frontend"

echo "🚀 Building $IMAGE_NAME:$VERSION..."

# Build the image
docker build -f Dockerfile.production -t $IMAGE_NAME:$VERSION .

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"

# Tag as latest if version specified
if [ "$VERSION" != "latest" ]; then
    echo "🏷️  Tagging as latest..."
    docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest
fi

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push $IMAGE_NAME:$VERSION

if [ $? -ne 0 ]; then
    echo "❌ Push failed! Make sure you're logged in: docker login"
    exit 1
fi

if [ "$VERSION" != "latest" ]; then
    docker push $IMAGE_NAME:latest
fi

echo "✅ Successfully pushed $IMAGE_NAME:$VERSION to Docker Hub!"
echo ""
echo "📦 Image details:"
docker images | grep $IMAGE_NAME | head -2
echo ""
echo "🚀 To deploy on Railway:"
echo "   1. Set Docker image source to: $IMAGE_NAME:$VERSION"
echo "   2. Ensure PORT environment variable is set to 80"
echo "   3. Redeploy the service"