#!/bin/bash

# ServerAI Knowledge Engine - Complete Docker Setup
# This script sets up everything needed to run the system

echo "🚀 Setting up ServerAI Knowledge Engine..."

# Create required directories
echo "📁 Creating directory structure..."
mkdir -p frontend backend nginx sql config

# Copy frontend files
echo "📦 Setting up frontend..."
cp -r src/* frontend/ 2>/dev/null || echo "Frontend files ready"

# Set executable permissions
chmod +x deploy.sh

# Build and start all services
echo "🔨 Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ ServerAI Knowledge Engine is ready!"
echo "🌐 Access your application at: http://localhost:420420"
echo "📊 API documentation at: http://localhost:420421/docs"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop all: docker-compose down"
echo "  Restart: docker-compose restart"
echo "  Update: docker-compose pull && docker-compose up -d"
echo ""
echo "📁 Data is stored in Docker volumes:"
echo "  - Database: postgres_data"
echo "  - Cache: redis_data" 
echo "  - Files: crawler_storage"