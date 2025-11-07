# Docker Deployment Guide for NewsIQ

This guide explains how to run NewsIQ using Docker and Docker Compose.

## Prerequisites

- Docker Desktop for Windows (or Docker Engine + Docker Compose on Linux)
- At least 4GB of available RAM
- API keys for the required services

## Quick Start

### 1. Prepare Environment Variables

Create a `.env` file in the root directory:

```powershell
copy .env.docker .env
```

Edit the `.env` file and add your API keys:

```env
LANGCHAIN_API_KEY=your_langchain_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here
EXA_API_KEY=your_exa_api_key_here
```

**Required Keys:**
- `GROQ_API_KEY` - For LLM inference (get from https://console.groq.com)
- `EXA_API_KEY` - For article search (get from https://exa.ai)

**Optional Keys:**
- `LANGCHAIN_API_KEY` - For LangSmith tracing
- `SERPER_API_KEY` - For Google search functionality

### 2. Build and Run

```powershell
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Docker Commands

### Basic Operations

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View logs from last 100 lines
docker-compose logs --tail=100 -f
```

### Build and Update

```powershell
# Rebuild images after code changes
docker-compose build

# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Data Management

```powershell
# Remove containers but keep volumes (preserves ChromaDB data)
docker-compose down

# Remove containers and volumes (clears ChromaDB data)
docker-compose down -v

# View volumes
docker volume ls

# Inspect ChromaDB volume
docker volume inspect newsiq_chroma-data
```

### Debugging

```powershell
# Execute commands in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View container resource usage
docker stats

# Inspect container details
docker-compose exec backend python --version
docker-compose exec frontend node --version

# Check backend health
docker-compose exec backend curl http://localhost:8000/api/health
```

## Docker Architecture

### Services

#### Backend Service
- **Image**: Custom Python 3.11 image
- **Port**: 8000
- **Volumes**: 
  - `chroma-data:/app/docs/chroma` - Persistent ChromaDB storage
- **Health Check**: HTTP request to `/api/health` endpoint

#### Frontend Service
- **Image**: Custom Node.js 18 Alpine image
- **Port**: 3000
- **Dependencies**: Waits for backend health check before starting
- **Build**: Multi-stage build for optimized production image

### Networking

Both services run on a shared Docker network (`newsiq-network`) which allows:
- Frontend to communicate with backend using service name (`http://backend:8000`)
- Isolated network from host except exposed ports

### Volumes

- **chroma-data**: Named volume for ChromaDB vector database
  - Persists article embeddings across container restarts
  - Can be backed up and restored
  - Location: Docker's volume directory

## Production Deployment

### Environment Variables for Production

Create a production `.env` file:

```env
# Production API Keys
GROQ_API_KEY=your_production_groq_key
EXA_API_KEY=your_production_exa_key
LANGCHAIN_API_KEY=your_production_langchain_key

# Production Settings
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=newsiq-production

# Optional: Add domain-specific settings
# CORS_ORIGINS=https://yourdomain.com
```

### Using Docker Compose Override

Create a `docker-compose.prod.yml` for production overrides:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - CORS_ORIGINS=https://yourdomain.com
    
  frontend:
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

Run with:
```powershell
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Backup and Restore

#### Backup ChromaDB Data

```powershell
# Create backup
docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .

# Or using PowerShell variable
docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .
```

#### Restore ChromaDB Data

```powershell
# Stop services
docker-compose down

# Restore backup
docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/chroma-backup.tar.gz -C /data"

# Start services
docker-compose up -d
```

## Troubleshooting

### Container Won't Start

```powershell
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart backend
```

### Port Already in Use

```powershell
# Find process using port 8000 or 3000
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill the process or change ports in docker-compose.yml
```

### Backend Can't Connect to APIs

```powershell
# Verify environment variables are loaded
docker-compose exec backend env | grep API_KEY

# Check network connectivity
docker-compose exec backend curl https://api.groq.com
```

### Frontend Can't Connect to Backend

```powershell
# Check if backend is healthy
docker-compose exec backend curl http://localhost:8000/api/health

# Check network
docker network inspect newsiq_newsiq-network

# Verify frontend can reach backend
docker-compose exec frontend wget -O- http://backend:8000/api/health
```

### ChromaDB Issues

```powershell
# Clear and reset ChromaDB
docker-compose down -v
docker-compose up -d

# Check ChromaDB volume
docker volume inspect newsiq_chroma-data
```

### Memory Issues

```powershell
# Check Docker resource usage
docker stats

# Increase Docker Desktop memory allocation
# Settings > Resources > Advanced > Memory
```

## Performance Optimization

### Image Size Optimization

The frontend uses multi-stage builds to minimize image size:
- Builder stage: Compiles and builds application
- Runner stage: Only includes production dependencies
- Alpine Linux base: Smaller footprint

### Caching

Docker layer caching is optimized by:
- Copying `requirements.txt` before code (backend)
- Copying `package.json` before code (frontend)
- Using `.dockerignore` to exclude unnecessary files

### Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          memory: 512M
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file to version control
2. **API Keys**: Use separate keys for development and production
3. **Network Isolation**: Services are isolated on private network
4. **Non-Root User**: Frontend runs as non-root user
5. **Health Checks**: Services monitor their own health

## Monitoring

### Health Checks

Both services include health checks:
- **Backend**: HTTP check on `/api/health`
- **Frontend**: Node.js HTTP check

View health status:
```powershell
docker-compose ps
```

### Logs

```powershell
# All services
docker-compose logs -f

# With timestamps
docker-compose logs -f -t

# Last 100 lines
docker-compose logs --tail=100 -f

# Specific time range
docker-compose logs --since 30m
```

## Scaling

For horizontal scaling (multiple instances):

```powershell
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Note: You'll need a load balancer for this to be effective
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
