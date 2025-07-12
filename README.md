# 🚀 ServerAI Knowledge Engine - Complete Docker Setup

## One-Command Deployment

```bash
# Clone or download files to a directory, then:
chmod +x setup.sh && ./setup.sh
```

Your complete ServerAI Knowledge Engine will be running at **http://localhost:420420**

## 🏗️ Architecture

This is a complete microservices setup with:

- **Frontend** (React/Vite): Web interface on port 420420
- **Backend** (Python/FastAPI): REST API on port 420421  
- **Database** (PostgreSQL): Data storage
- **Cache** (Redis): Task queue and caching
- **Worker** (Celery): Background crawling tasks
- **Nginx**: Load balancer and reverse proxy

## 📁 Complete File Structure

```
serverai-engine/
├── docker-compose.yml          # Main orchestration
├── setup.sh                   # One-command setup
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── (React app files)
├── backend/
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   ├── requirements.txt
│   ├── main.py                 # FastAPI app
│   ├── crawler.py              # Web crawler
│   ├── database.py             # Database layer
│   ├── models.py               # Data models
│   └── worker.py               # Background tasks
├── nginx/
│   └── nginx.conf              # Load balancer config
├── sql/
│   └── init.sql                # Database schema
└── config/
    └── crawler.yml             # Crawler configuration
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `STORAGE_PATH`: File storage location

### Crawler Settings
Edit `config/crawler.yml` to:
- Add more crawl targets
- Modify topic classifications
- Adjust crawler behavior

## 📊 Features

### Web Interface
- Real-time dashboard with stats
- Topic-based content organization
- Crawler status monitoring
- Search functionality

### Backend API
- RESTful API with FastAPI
- Real-time crawler control
- Content classification
- Full-text search

### Data Storage
- PostgreSQL for structured data
- File system for organized content
- Redis for task queuing
- Persistent Docker volumes

## 🎛️ Management Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart [service-name]

# Scale workers
docker-compose up -d --scale crawler-worker=4

# Database access
docker-compose exec postgres psql -U serverai -d serverai_db

# Redis access
docker-compose exec redis redis-cli

# File system access
docker-compose exec backend bash
```

## 📈 Scaling

To handle more load:

```bash
# Scale crawler workers
docker-compose up -d --scale crawler-worker=4

# Add more backend instances
docker-compose up -d --scale backend=2

# Update nginx config for load balancing
```

## 🔒 Security

For production:
- Change default passwords in docker-compose.yml
- Add SSL certificates
- Configure firewall rules
- Enable authentication
- Use Docker secrets

## 🚨 Troubleshooting

```bash
# Check service health
curl http://localhost:420420/health

# View API docs
open http://localhost:420421/docs

# Reset everything
docker-compose down -v && docker-compose up --build -d
```

## 📦 Storage Volumes

Data persists in Docker volumes:
- `postgres_data`: Database storage
- `redis_data`: Cache and queue data
- `crawler_storage`: Organized content files

## 🔄 Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up --build -d
```

This setup provides a complete, production-ready knowledge crawling system that's easy to deploy and scale!