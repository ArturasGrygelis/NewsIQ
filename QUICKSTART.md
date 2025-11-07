# 🚀 Quick Start Guide - NewsIQ with Docker

Get NewsIQ up and running in less than 5 minutes!

## Step 1: Prerequisites ✅

Make sure you have:
- [ ] Docker Desktop installed and running
- [ ] API keys ready (Groq and Exa at minimum)

## Step 2: Setup Environment 🔧

1. Create your `.env` file:
```powershell
copy .env.docker .env
```

2. Edit `.env` with your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
EXA_API_KEY=your_exa_api_key_here
```

**Get your API keys:**
- Groq: https://console.groq.com (Free tier available)
- Exa: https://exa.ai (Free tier available)

## Step 3: Start NewsIQ 🎬

### Option A: PowerShell Helper (Recommended)

```powershell
# Load helper functions
. .\docker-helpers.ps1

# Start the application
Start-NewsIQ
```

### Option B: Direct Docker Compose

```powershell
docker-compose up -d
```

## Step 4: Access the Application 🌐

Open your browser:
- **NewsIQ App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## Step 5: Try It Out! 🎯

### Ingest Your First Article

1. Go to http://localhost:3000
2. Click "Launch App"
3. Click "Ingest Articles" tab
4. Choose "Search by Topic"
5. Enter a topic (e.g., "artificial intelligence")
6. Click "Ingest Article(s)"
7. Wait for confirmation

### Ask Your First Question

1. Switch to "Chat & Questions" tab
2. Type: "What are the main points from the articles?"
3. Press Enter
4. Get AI-powered answers with sources!

## Useful Commands 📋

### Using PowerShell Helpers

```powershell
# Load helpers (do this first!)
. .\docker-helpers.ps1

# View logs
Show-NewsIQLogs

# Check status
Show-NewsIQStatus

# Restart services
Restart-NewsIQ

# Stop everything
Stop-NewsIQ

# See all commands
Show-NewsIQHelp
```

### Using Docker Compose

```powershell
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart
docker-compose restart

# Stop
docker-compose down
```

## Troubleshooting 🔧

### Services won't start?

1. Check Docker Desktop is running
2. Check if ports are available:
```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

### API errors?

1. Verify your API keys in `.env`
2. Check backend logs:
```powershell
docker-compose logs backend
```

### Frontend can't connect?

1. Wait for backend health check to pass (~30-40 seconds)
2. Check services are running:
```powershell
docker-compose ps
```

### Need a fresh start?

```powershell
# Stop everything and clear data
docker-compose down -v

# Start fresh
docker-compose up -d
```

## What's Next? 🎓

- Read the full [Docker Guide](DOCKER.md) for advanced usage
- Check the [main README](README.md) for detailed documentation
- Explore the [API documentation](http://localhost:8000/docs) when running

## Quick Reference Card 📝

| Action | PowerShell Helper | Docker Compose |
|--------|------------------|----------------|
| Start | `Start-NewsIQ` | `docker-compose up -d` |
| Stop | `Stop-NewsIQ` | `docker-compose down` |
| Logs | `Show-NewsIQLogs` | `docker-compose logs -f` |
| Status | `Show-NewsIQStatus` | `docker-compose ps` |
| Restart | `Restart-NewsIQ` | `docker-compose restart` |
| Rebuild | `Rebuild-NewsIQ` | `docker-compose up -d --build` |
| Clean | `Clean-NewsIQ` | `docker-compose down -v` |

## Support 💬

Having issues? Check:
1. Docker logs: `docker-compose logs -f`
2. Service health: `docker-compose ps`
3. Environment variables: Ensure `.env` is configured
4. API keys: Verify they're valid and have proper permissions

---

**Happy exploring with NewsIQ! 🎉**
