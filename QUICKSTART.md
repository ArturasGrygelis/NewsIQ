# 🚀 NewsIQ Quick Start Guide

Get NewsIQ up and running in **under 5 minutes** with Docker!

## ⚡ Prerequisites

Before you begin, ensure you have:

- ✅ **Docker Desktop** installed and running
  - Download: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Minimum version: 20.10+
  - Minimum 4GB RAM allocated to Docker

- ✅ **API Keys** (free tiers available):
  - **Groq API Key** (Required) - [Get it here](https://console.groq.com)
    - Free tier: 30 requests/minute
    - Used for: AI summarization and question answering
  
  - **LangSmith API Key** (Optional) - [Get it here](https://smith.langchain.com)
    - Used for: Workflow tracing and debugging

## 📋 Step-by-Step Setup

### Step 1: Clone or Download the Repository

```powershell
# If using Git
git clone <repository-url>
cd NewsIQ

# Or download and extract ZIP, then:
cd path\to\NewsIQ
```

### Step 2: Configure Environment

1. **Create your `.env` file:**

   ```powershell
   # Windows
   copy .env.docker .env
   
   # Linux/Mac
   cp .env.docker .env
   ```

2. **Edit the `.env` file** with your favorite text editor:

   ```env
   # REQUIRED - Get from https://console.groq.com
   GROQ_API_KEY=gsk_your_groq_api_key_here
   
   # OPTIONAL - For debugging and tracing
   LANGCHAIN_API_KEY=lsv2_your_langchain_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=NewsIQ
   
   # Backend configuration (usually no need to change)
   HOST=0.0.0.0
   PORT=8000
   ```

   > ⚠️ **Important**: Replace `your_groq_api_key_here` with your actual API key!

### Step 3: Launch NewsIQ

**Option A: Using PowerShell Helpers** (Recommended for Windows)

```powershell
# Load helper functions
. .\docker-helpers.ps1

# Start the application
Start-NewsIQ

# The command will:
# - Build Docker images (first time only, ~2-3 minutes)
# - Start backend and frontend services
# - Wait for health checks to pass
# - Display access URLs
```

**Option B: Using Docker Compose** (Works on all platforms)

```powershell
# Build and start services
docker-compose up -d

# The -d flag runs containers in the background
```

### Step 4: Verify Services

**Check service status:**
```powershell
docker-compose ps
```

Expected output:
```
NAME                IMAGE               STATUS              PORTS
newsiq-backend      newsiq-backend      Up (healthy)        0.0.0.0:8000->8000/tcp
newsiq-frontend     newsiq-frontend     Up                  0.0.0.0:3000->3000/tcp
```

> 💡 **Tip**: Backend may take 30-40 seconds on first start while downloading ML models.

**View startup logs:**
```powershell
docker-compose logs -f
```

Look for these success messages:
- Backend: `✅ NewsIQ is ready!`
- Frontend: `ready - started server on 0.0.0.0:3000`

Press `Ctrl+C` to stop viewing logs (containers keep running).

### Step 5: Access the Application

Open your web browser and navigate to:

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3000 | NewsIQ user interface |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **API Root** | http://localhost:8000 | API information endpoint |
| **Health Check** | http://localhost:8000/api/health | Backend health status |

## 🎯 Your First Article Workflow

### 1. Ingest an Article

1. **Open** http://localhost:3000
2. **Click** "Launch App" button
3. **Navigate** to the "Ingest Article" tab
4. **Enter** an article URL, for example:
   ```
   https://www.bbc.com/news/technology
   ```
5. **Click** "Ingest Article(s)"
6. **Wait** for processing (~20-40 seconds):
   - Scraping content
   - Generating summary
   - Extracting topics
   - Storing in vector database

7. **View results** in the sidebar:
   - Article summary
   - Authors
   - Language
   - Key topics
   - Full text (scrollable)

### 2. Ask Questions

1. **Switch** to "Chat & Questions" tab
2. **Type** a question about your ingested articles:
   ```
   What are the main points in the article?
   ```
3. **Press** Enter or click send
4. **Review** the AI-generated answer
5. **Explore** source documents in the right sidebar:
   - Click article titles to open original links
   - View metadata (authors, language, topics, summary)
   - Click "▶ Document Text" to expand full article content

### 3. Try More Questions

```
What technologies are mentioned in the articles?
Who are the key people or organizations discussed?
Summarize the different viewpoints presented
What are the potential impacts described?
```

## 📚 PowerShell Helper Commands

NewsIQ includes convenient PowerShell scripts for managing Docker containers.

### Loading Helpers

```powershell
# Run this in your PowerShell terminal (in the NewsIQ directory)
. .\docker-helpers.ps1
```

### Available Commands

| Command | Description | Equivalent Docker Compose |
|---------|-------------|---------------------------|
| `Start-NewsIQ` | Start all services | `docker-compose up -d` |
| `Stop-NewsIQ` | Stop all services | `docker-compose down` |
| `Restart-NewsIQ` | Restart all services | `docker-compose restart` |
| `Show-NewsIQLogs` | View real-time logs | `docker-compose logs -f` |
| `Show-NewsIQStatus` | Check service status | `docker-compose ps` |
| `Rebuild-NewsIQ` | Rebuild images | `docker-compose up -d --build` |
| `Clean-NewsIQ` | Stop and remove all data | `docker-compose down -v` |
| `Show-NewsIQHelp` | Display all commands | - |

### Usage Examples

```powershell
# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart single service
docker-compose restart backend

# View last 50 log lines
docker-compose logs --tail=50 backend

# Follow logs from specific time
docker-compose logs --since 10m -f
```

## 🛠️ Troubleshooting

### Issue: Ports Already in Use

**Symptom:**
```
Error: Port 3000 (or 8000) is already allocated
```

**Solution:**
```powershell
# Find process using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill the process using the port
taskkill /PID <process_id> /F

# Or change ports in docker-compose.yml
```

### Issue: Backend Not Starting

**Symptom:**
```
Backend service unhealthy or exiting
```

**Solutions:**

1. **Check logs:**
   ```powershell
   docker-compose logs backend
   ```

2. **Verify API key:**
   - Open `.env` file
   - Ensure `GROQ_API_KEY` is set correctly
   - No quotes needed around the key

3. **Restart services:**
   ```powershell
   docker-compose restart backend
   ```

### Issue: Frontend Can't Connect to Backend

**Symptom:**
```
Failed to proxy http://backend:8000/api/answer
Error: socket hang up
```

**Solutions:**

1. **Wait for backend initialization:**
   ```powershell
   # Backend takes 30-40 seconds on first start
   docker-compose logs -f backend
   # Wait for: "✅ NewsIQ is ready!"
   ```

2. **Check backend health:**
   ```powershell
   # Open in browser
   http://localhost:8000/api/health
   # Should return: {"status": "healthy"}
   ```

3. **Restart frontend:**
   ```powershell
   docker-compose restart frontend
   ```

### Issue: Article Ingestion Timeout

**Symptom:**
```
Request timeout after 120 seconds
```

**Solutions:**

1. **Check article URL accessibility:**
   - Open URL in browser
   - Ensure it's not behind paywall
   - Try a different news source

2. **Check backend processing:**
   ```powershell
   docker-compose logs -f backend
   # Look for error messages during scraping
   ```

3. **Verify Groq API limits:**
   - Check your Groq dashboard
   - Ensure you haven't hit rate limits

### Issue: ChromaDB Errors

**Symptom:**
```
ChromaDB connection errors or corrupted database
```

**Solution:**
```powershell
# Stop all services
docker-compose down

# Remove the vector database volume
docker volume rm newsiq_chroma-data

# Start fresh
docker-compose up -d
```

### Issue: Docker Out of Memory

**Symptom:**
```
Container crashes or slow performance
```

**Solutions:**

1. **Increase Docker memory:**
   - Docker Desktop → Settings → Resources
   - Increase Memory to at least 4GB
   - Click "Apply & Restart"

2. **Free up space:**
   ```powershell
   # Remove unused Docker resources
   docker system prune -a --volumes
   ```

## 🔄 Maintenance Commands

### Updating the Application

```powershell
# Pull latest code (if using Git)
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Viewing Resource Usage

```powershell
# Check container resource usage
docker stats

# Check disk space
docker system df
```

### Cleaning Up

```powershell
# Stop services (keeps data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v

# Remove unused Docker resources
docker system prune -a --volumes
```

### Backing Up Data

```powershell
# Backup ChromaDB volume
docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup busybox tar czf /backup/chroma-backup.tar.gz -C /data .

# Restore ChromaDB volume
docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup busybox tar xzf /backup/chroma-backup.tar.gz -C /data
```

## 🎓 Next Steps

### Learn More

- 📖 **Full Documentation**: See [README.md](README.md) for comprehensive guide
- 🐳 **Docker Details**: See [DOCKER.md](DOCKER.md) for advanced Docker configurations
- 🔌 **API Reference**: Visit http://localhost:8000/docs when running

### Explore Features

1. **Try different article sources:**
   - BBC: https://www.bbc.com/news/technology
   - Reuters: https://www.reuters.com/technology
   - NYTimes: https://www.nytimes.com/section/technology

2. **Experiment with questions:**
   - Summaries: "Summarize the main findings"
   - Comparisons: "Compare the different approaches"
   - Analysis: "What are the potential risks?"
   - Details: "What statistics are mentioned?"

3. **Check the source sidebar:**
   - Expand document texts
   - Explore article metadata
   - Click through to original sources

### Enable Advanced Features

1. **LangSmith Tracing** (for debugging):
   ```env
   LANGCHAIN_API_KEY=your_key_here
   LANGCHAIN_TRACING_V2=true
   ```
   Then visit: https://smith.langchain.com

2. **Custom Configuration:**
   - Edit `docker-compose.yml` for ports, resources
   - Modify `backend/main.py` for workflow settings
   - Adjust `frontend/pages/app.tsx` for UI changes

## 📞 Getting Help

### Check Logs First

```powershell
# All services
docker-compose logs -f

# Specific service with timestamps
docker-compose logs -f --timestamps backend

# Last 100 lines
docker-compose logs --tail=100
```

### Common Log Messages

**Backend:**
- `✅ NewsIQ is ready!` - Backend successfully started
- `📊 Building workflow graphs...` - Initializing AI workflows
- `📄 loaded document content` - Article successfully scraped
- `✅ Document added to Chroma` - Article stored successfully

**Frontend:**
- `ready - started server on 0.0.0.0:3000` - Frontend ready
- `Compiled successfully` - Code compiled without errors
- `wait - compiling...` - Hot reload in progress

### Still Having Issues?

1. **Restart everything:**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

2. **Fresh start (removes all data):**
   ```powershell
   docker-compose down -v
   docker-compose up -d
   ```

3. **Check Docker:**
   ```powershell
   docker --version
   docker-compose --version
   docker ps
   ```

4. **Verify environment:**
   ```powershell
   # Check .env file exists and has API keys
   cat .env
   ```

## 📊 Quick Reference Card

### Essential Commands

```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Restart
docker-compose restart

# Fresh start (removes data)
docker-compose down -v && docker-compose up -d
```

### Application URLs

```
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
Health:    http://localhost:8000/api/health
```

### Typical Processing Times

- Article ingestion: **20-40 seconds**
- Question answering: **5-15 seconds**
- First-time startup: **2-3 minutes** (downloading models)
- Subsequent startups: **30-40 seconds**

---

**🎉 You're all set! Happy exploring with NewsIQ!**

> 💡 **Pro Tip**: Keep the backend logs open in a terminal (`docker-compose logs -f backend`) to monitor AI workflow execution in real-time.
