#!/bin/bash

# ServerAI Knowledge Engine - Easy Docker Deployment Script
# Usage: ./deploy.sh

echo "🚀 Deploying ServerAI Knowledge Engine on port 420420..."

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker-compose down 2>/dev/null || true

# Build and start the container
echo "🔨 Building and starting container..."
docker-compose up --build -d

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Success! ServerAI Knowledge Engine is running!"
    echo "🌐 Access your app at: http://localhost:420420"
    echo "📊 Check container status: docker-compose ps"
    echo "📝 View logs: docker-compose logs -f"
    echo "🛑 Stop container: docker-compose down"
else
    echo "❌ Deployment failed. Check logs: docker-compose logs"
    exit 1
fi