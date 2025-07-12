# 🐳 Docker Deployment Guide

## Quick Start (Super Easy!)

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy in one command
./deploy.sh
```

Your ServerAI Knowledge Engine will be running at **http://localhost:420420**

## Manual Docker Commands

### Using Docker Compose (Recommended)
```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Docker directly
```bash
# Build image
docker build -t serverai-engine .

# Run container
docker run -d --name serverai-engine -p 420420:420420 serverai-engine

# Stop container
docker stop serverai-engine && docker rm serverai-engine
```

## Configuration

- **Port**: 420420 (customizable in docker-compose.yml)
- **Image**: Multi-stage build (Node.js + Nginx)
- **Size**: Optimized Alpine-based image
- **Restart**: Automatic restart on failure

## Production Deployment

For production, consider:
- Using a reverse proxy (Traefik, Nginx)
- Adding SSL certificates
- Setting up monitoring
- Using Docker secrets for sensitive data

## Troubleshooting

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs serverai-engine

# Enter container for debugging
docker-compose exec serverai-engine sh

# Rebuild without cache
docker-compose build --no-cache
```