# NewsIQ

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent news knowledge base powered by AI that enables users to ingest, analyze, and query news articles with semantic search and natural language understanding.

## 🌟 Key Features

- **🔗 Article Ingestion**: Import news articles via direct URL with automatic content extraction and processing
- **🤖 AI-Powered Q&A**: Ask natural language questions and receive contextually accurate answers with source citations
- **🔍 Semantic Search**: Vector-based similarity search using multilingual embeddings for precise information retrieval
- **📊 Source Attribution**: Every answer includes metadata-rich source documents with expandable full-text view
- **⚡ Real-time Processing**: Asynchronous workflow execution for non-blocking article ingestion and question answering
- **🎨 Modern Interface**: Responsive UI built with Next.js, TypeScript, and Tailwind CSS

## 🏗️ Architecture

### Technology Stack

**Backend**
- **FastAPI**: High-performance Python web framework with async support
- **LangGraph**: Stateful workflow orchestration for multi-step AI operations
- **LangChain**: Framework for building LLM-powered applications
- **ChromaDB**: Vector database for semantic search and retrieval
- **Groq**: Ultra-fast LLM inference (Gemma-2-9b-it, GPT-OSS-20b)
- **HuggingFace**: Multilingual embeddings (intfloat/multilingual-e5-large-instruct)
- **newspaper3k**: Advanced web scraping and article extraction

**Frontend**
- **Next.js 13**: React framework with server-side rendering
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling framework
- **Axios**: HTTP client with request/response interceptors
- **Lucide React**: Modern icon library

### Workflow Architecture

```
Article Ingestion Workflow:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Initialize │ -> │ Scrape & Parse│ -> │ Summarize & │ -> │   Store in   │
│   Workflow  │    │    Article    │    │Extract Topics│   │  VectorStore │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                                              ↓
                                       ┌──────────────┐
                                       │   Halluc.    │
                                       │  Check & Fix │
                                       └──────────────┘

Question Answering Workflow:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Initialize │ -> │   Retrieve   │ -> │    Grade    │ -> │   Generate   │
│   Workflow  │    │  Documents   │    │  Relevance  │    │    Answer    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                           ↑                   ↓                    ↓
                           │            ┌──────────────┐    ┌──────────────┐
                           └────────────│   Transform  │    │   Halluc.    │
                                       │    Query     │    │Check & Return│
                                       └──────────────┘    └──────────────┘
```

## 📁 Project Structure

```
NewsIQ/
├── backend/
│   ├── app/
│   │   ├── workflows/
│   │   │   ├── stories/              # Article ingestion workflows
│   │   │   │   ├── nodes.py          # Workflow node implementations
│   │   │   │   ├── workers.py        # LLM prompt chains
│   │   │   │   ├── tools.py          # Utility functions
│   │   │   │   └── workflows.py      # LangGraph state machines
│   │   │   └── answer/               # Question answering workflows
│   │   │       ├── nodes.py          # QA node implementations
│   │   │       ├── workers.py        # RAG prompt chains
│   │   │       └── workflows.py      # QA state machines
│   │   ├── services.py               # Vector store & retriever services
│   │   ├── chroma/                   # Persistent vector database
│   │   └── __init__.py
│   ├── main.py                       # FastAPI application & endpoints
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend container definition
│   └── .env.example                  # Environment template
│
├── frontend/
│   ├── pages/
│   │   ├── index.tsx                 # Landing page
│   │   ├── app.tsx                   # Main application (chat + ingest)
│   │   ├── _app.tsx                  # Next.js app wrapper
│   │   └── _document.tsx             # HTML document structure
│   ├── styles/
│   │   └── globals.css               # Global styles & Tailwind directives
│   ├── public/                       # Static assets
│   ├── Dockerfile                    # Frontend container definition
│   ├── next.config.js                # Next.js configuration & API proxy
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── tsconfig.json                 # TypeScript compiler options
│   └── package.json                  # Node.js dependencies
│
├── docker-compose.yml                # Multi-container orchestration
├── .env.docker                       # Docker environment template
├── docker-helpers.ps1                # PowerShell utility scripts
├── README.md                         # This file
├── QUICKSTART.md                     # Quick start guide
└── DOCKER.md                         # Docker deployment guide
```


## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a streamlined setup guide.

### Prerequisites

**Docker Setup (Recommended)**
- [Docker Desktop](https://www.docker.com/products/docker-desktop) 20.10+
- Docker Compose 2.0+ (included with Docker Desktop)
- 4GB+ RAM allocated to Docker
- 10GB+ free disk space

**Manual Setup (Alternative)**
- Python 3.10 or higher
- Node.js 18 or higher
- npm 9+ or yarn 1.22+

### Environment Configuration

1. **Create environment file:**
   ```powershell
   # Windows
   copy .env.docker .env
   
   # Linux/Mac
   cp .env.docker .env
   ```

2. **Configure API keys in `.env`:**
   ```env
   # Required
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx        # Get from https://console.groq.com
   
   # Optional
   LANGCHAIN_API_KEY=lsv2_xxxxxxxxxxxxxxxxxxxx  # For LangSmith tracing
   LANGCHAIN_TRACING_V2=true                     # Enable tracing
   LANGCHAIN_PROJECT=NewsIQ                      # Project name in LangSmith
   ```

### Docker Deployment (Recommended)

1. **Start the application:**
   ```powershell
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```powershell
   docker-compose ps
   ```
   
   Expected output:
   ```
   NAME                IMAGE               STATUS              PORTS
   newsiq-backend      newsiq-backend      Up (healthy)        0.0.0.0:8000->8000/tcp
   newsiq-frontend     newsiq-frontend     Up                  0.0.0.0:3000->3000/tcp
   ```

3. **Access the application:**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/health

4. **View logs:**
   ```powershell
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

5. **Stop the application:**
   ```powershell
   # Stop containers (preserves data)
   docker-compose down
   
   # Stop and remove all data
   docker-compose down -v
   ```

### Manual Setup (Alternative)

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Create virtual environment:**
   ```powershell
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```powershell
   copy .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server:**
   ```powershell
   python main.py
   ```
   
   Backend will be available at http://localhost:8000

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```powershell
   cd frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   # or
   yarn install
   ```

3. **Run development server:**
   ```powershell
   npm run dev
   # or
   yarn dev
   ```
   
   Frontend will be available at http://localhost:3000

</details>

## 📖 Usage Guide

### Ingesting Articles

1. **Navigate to the application:**
   Open http://localhost:3000 and click "Launch App"

2. **Go to the "Ingest Article" tab**

3. **Enter an article URL:**
   - Example: `https://www.bbc.com/news/technology-68945000`
   - Supported sites: Most news websites (BBC, Reuters, NYTimes, etc.)

4. **Click "Ingest Article(s)"**

5. **Monitor processing:**
   - Scraping and parsing (5-10 seconds)
   - Summarization with AI (10-20 seconds)
   - Hallucination checking (5-10 seconds)
   - Storage in vector database (1-2 seconds)

6. **View results:**
   - Article metadata sidebar shows:
     - **Summary**: AI-generated summary
     - **Authors**: Article authors
     - **Language**: Detected language
     - **Topics**: Extracted key topics
   - Full article text displayed in main panel

### Asking Questions

1. **Switch to "Chat & Questions" tab**

2. **Type your question:**
   - Examples:
     - "What are the main findings about AI safety?"
     - "Compare the different viewpoints on climate policy"
     - "Summarize the key statistics mentioned"

3. **Review the answer:**
   - AI-generated response based on retrieved documents
   - Source documents panel on the right shows:
     - Article titles (clickable links)
     - Authors, language, topics
     - AI-generated summary
     - Expandable full document text

4. **Expand source documents:**
   - Click "▶ Document Text" to view full article content
   - Click "▼ Document Text" to collapse

## 🔌 API Reference

### Endpoints

#### `GET /`
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to NewsIQ API",
  "version": "1.0.0",
  "endpoints": {
    "/api/ingest": "POST - Ingest articles into vectorstore",
    "/api/answer": "POST - Ask questions about articles",
    "/api/health": "GET - Health check"
  }
}
```

#### `GET /api/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

#### `POST /api/ingest`
Ingest an article into the knowledge base.

**Request:**
```json
{
  "article_url": "https://example.com/article"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Article successfully processed and stored in vectorstore",
  "article_title": "Example Article Title",
  "article_url": "https://example.com/article",
  "article_summary": "AI-generated summary...",
  "article_authors": "John Doe, Jane Smith",
  "article_language": "en",
  "article_topics": "technology, AI, machine learning",
  "article_text": "Full article text..."
}
```

**Processing Steps:**
1. URL validation and content scraping
2. Article parsing and metadata extraction
3. AI-powered summarization
4. Topic identification
5. Hallucination detection and correction
6. Vector embedding generation
7. Storage in ChromaDB

**Timeout:** 120 seconds (configurable)

#### `POST /api/answer`
Ask a question about ingested articles.

**Request:**
```json
{
  "question": "What are the main points about AI development?"
}
```

**Response:**
```json
{
  "answer": "Based on the articles...",
  "sources": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "snippet": "First 300 characters...",
      "content": "Full article text...",
      "authors": "Author names",
      "language": "en",
      "topics": "topic1, topic2",
      "summary": "Article summary"
    }
  ],
  "session_id": "uuid-string"
}
```

**Processing Steps:**
1. Question embedding generation
2. Vector similarity search (top 15 candidates)
3. Document relevance grading
4. Query transformation if needed
5. Answer generation with RAG
6. Hallucination checking
7. Source compilation with metadata

**Timeout:** 120 seconds (configurable)

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Groq API key for LLM inference |
| `LANGCHAIN_API_KEY` | No | - | LangSmith API key for tracing |
| `LANGCHAIN_TRACING_V2` | No | `false` | Enable LangSmith tracing |
| `LANGCHAIN_PROJECT` | No | `NewsIQ` | LangSmith project name |
| `HOST` | No | `0.0.0.0` | Backend host address |
| `PORT` | No | `8000` | Backend port |

### Docker Configuration

**docker-compose.yml** includes:
- **Hot reload**: Code changes reflect immediately
- **Health checks**: Backend readiness monitoring
- **Persistent storage**: ChromaDB volume preservation
- **Network isolation**: Internal service communication
- **Resource limits**: CPU and memory constraints

**Volumes:**
- `./backend:/app` - Backend code hot reload
- `./frontend:/app` - Frontend code hot reload  
- `chroma-data:/app/app/chroma` - Vector database persistence

### LLM Configuration

**Models Used:**
- **Summarization & Topics**: `openai/gpt-oss-20b` (temperature: 0.0)
- **Question Answering**: `gemma2-9b-it` (temperature: 0.0)
- **Hallucination Checking**: `gemma2-9b-it` (temperature: 0.0)

**Embeddings:**
- **Model**: `intfloat/multilingual-e5-large-instruct`
- **Dimensions**: 1024
- **Device**: CPU
- **Languages**: 100+ languages supported

### Vector Store Configuration

**ChromaDB Settings:**
- **Persistence**: `./app/chroma` directory
- **Collection**: Auto-created per session
- **Similarity Metric**: Cosine similarity
- **Retrieval**: Top-k search (k=15 for QA, k=5 returned)

## 🧪 Development

### Backend Development

**Running tests:**
```powershell
cd backend
python -m pytest
```

**Running workflow tests:**
```powershell
python test_workflow.py
python test_simple_workflow.py
```

**Adding new workflow nodes:**
1. Define node function in `app/workflows/[workflow]/nodes.py`
2. Add to state graph in `app/workflows/[workflow]/workflows.py`
3. Update state schema if needed
4. Test with sample inputs

**Environment variables for development:**
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=NewsIQ-Dev
```

### Frontend Development

**Development server with hot reload:**
```powershell
cd frontend
npm run dev
```

**Building for production:**
```powershell
npm run build
npm start
```

**TypeScript checking:**
```powershell
npm run type-check
```

**Linting:**
```powershell
npm run lint
```

### Code Structure

**Backend Workflows:**
- Each workflow is a LangGraph state machine
- Nodes are pure functions that transform state
- Workers contain LLM chain definitions
- Tools provide utility functions

**Frontend Components:**
- Page components in `pages/`
- Shared styles in `styles/globals.css`
- API calls with axios (2-minute timeout)
- State management with React hooks

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>Backend: "ModuleNotFoundError: No module named 'langchain_core'"</b></summary>

**Solution:**
```powershell
pip install --upgrade langchain-core>=0.3.76
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Frontend: "Failed to proxy http://backend:8000/api/answer Error: socket hang up"</b></summary>

**Causes:**
- Workflow execution exceeding 60-second default timeout
- Backend not fully initialized

**Solutions:**
- Timeout is already set to 120 seconds in axios config
- Wait for backend health check to pass (~30-40 seconds on first start)
- Check backend logs: `docker-compose logs backend`
</details>

<details>
<summary><b>Docker: "Port 3000 or 8000 already in use"</b></summary>

**Solution:**
```powershell
# Find process using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill the process (use PID from netstat output)
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```
</details>

<details>
<summary><b>Vector Store: ChromaDB errors or corrupted database</b></summary>

**Solution:**
```powershell
# Stop containers
docker-compose down

# Remove volume
docker volume rm newsiq_chroma-data

# Restart
docker-compose up -d
```
</details>

<details>
<summary><b>Article Ingestion: "Failed to scrape article"</b></summary>

**Possible causes:**
- Website blocks automated scraping
- Invalid URL format
- Paywall or login required

**Solutions:**
- Try a different news source
- Verify URL is accessible in browser
- Check backend logs for detailed error
</details>

### Debug Mode

**Enable verbose logging:**

Backend (`.env`):
```env
LANGCHAIN_VERBOSE=true
LANGCHAIN_TRACING_V2=true
```

Frontend (browser console):
```javascript
localStorage.setItem('debug', 'true')
```

**View workflow execution in LangSmith:**
1. Set `LANGCHAIN_API_KEY` in `.env`
2. Set `LANGCHAIN_TRACING_V2=true`
3. Visit https://smith.langchain.com
4. View traces in real-time

## 📊 Performance

**Typical Processing Times:**
- Article ingestion: 20-40 seconds
- Question answering: 5-15 seconds
- Vector search: <1 second
- LLM inference: 2-5 seconds per call

**Resource Usage:**
- Backend: ~500MB RAM, <5% CPU (idle)
- Frontend: ~200MB RAM, <2% CPU (idle)
- ChromaDB: Scales with document count (~10MB per 100 articles)

## 🛡️ Security Considerations

- API keys stored in `.env` (not committed to git)
- CORS configured for localhost only
- Input validation on all endpoints
- No user authentication (add if deploying publicly)
- ChromaDB data persists locally (not encrypted)

**For production deployment:**
- Add authentication middleware
- Configure CORS for specific domains
- Enable HTTPS
- Implement rate limiting
- Encrypt sensitive data at rest

## 📝 License

This project is provided for educational and development purposes.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔗 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Groq Documentation](https://console.groq.com/docs)

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review logs: `docker-compose logs -f`

---

**Built with ❤️ using LangChain, LangGraph, FastAPI, and Next.js**
