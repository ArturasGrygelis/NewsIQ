# NewsIQ

An intelligent news knowledge base application that allows users to ingest, analyze, and query news articles using AI-powered insights.

## Features

- **Article Ingestion**: Import articles from direct URLs or search by topic across multiple news sources
- **Intelligent Q&A**: Ask questions about ingested articles and receive AI-powered answers with source citations
- **Vector Search**: Semantic search powered by ChromaDB for finding relevant information across articles
- **Modern UI**: Clean, responsive interface built with React and Next.js

## Architecture

### Backend (FastAPI + Python)
- FastAPI REST API
- LangGraph workflows for article processing
- ChromaDB vector store for semantic search
- Groq LLM integration for question answering
- Exa API for article search

### Frontend (Next.js + React)
- Server-side rendering with Next.js
- Tailwind CSS for styling
- Responsive design
- Real-time chat interface

## Project Structure

```
NewsIQ/
├── backend/
│   ├── app/
│   │   ├── workflows/
│   │   │   └── stories/
│   │   │       ├── nodes.py          # LangGraph workflow nodes
│   │   │       └── workflows.py      # LangGraph workflow definitions
│   │   └── services.py               # Vector store & article services
│   ├── main.py                       # FastAPI application
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment variables template
└── frontend/
    ├── pages/
    │   ├── index.tsx                 # Homepage
    │   ├── app.tsx                   # Main application page
    │   ├── _app.tsx                  # Next.js app wrapper
    │   └── _document.tsx             # Next.js document wrapper
    ├── styles/
    │   └── globals.css               # Global styles
    ├── package.json                  # Node dependencies
    ├── tsconfig.json                 # TypeScript config
    ├── tailwind.config.js            # Tailwind CSS config
    └── next.config.js                # Next.js config
```

## Setup Instructions

### Prerequisites

**Option 1: Docker (Recommended)**
- Docker Desktop for Windows
- Docker Compose

**Option 2: Manual Setup**
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

### Quick Start with Docker 🐳

1. Clone the repository and navigate to the project directory

2. Create a `.env` file in the root directory with your API keys:
   ```powershell
   copy .env.docker .env
   ```

3. Edit `.env` and add your API keys:
   - `GROQ_API_KEY` - Required for LLM inference
   - `EXA_API_KEY` - Required for article search
   - `LANGCHAIN_API_KEY` - Optional for LangSmith tracing
   - `SERPER_API_KEY` - Optional for Google search

4. Build and start the containers:
   ```powershell
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

6. View logs:
   ```powershell
   docker-compose logs -f
   ```

7. Stop the application:
   ```powershell
   docker-compose down
   ```

8. Stop and remove volumes (clears vector database):
   ```powershell
   docker-compose down -v
   ```

### Manual Setup (Alternative to Docker)

#### Backend Setup

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```

2. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```powershell
   copy .env.example .env
   ```

5. Edit `.env` and add your API keys

6. Run the backend server:
   ```powershell
   python main.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Run the development server:
   ```powershell
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage

### Ingesting Articles

1. Navigate to the "Ingest Articles" tab
2. Choose between two methods:
   - **Search by Topic**: Enter a topic, optional website filter, and max age
   - **Direct URL**: Paste a specific article URL
3. Click "Ingest Article(s)" to add them to the knowledge base

### Asking Questions

1. Navigate to the "Chat & Questions" tab
2. Type your question in the input field
3. Press Enter or click the send button
4. The AI will search the vector store and provide an answer with sources

## API Endpoints

### `GET /`
Health check and API information

### `GET /api/health`
Backend health status

### `POST /api/ingest`
Ingest articles into the vectorstore

**Request Body:**
```json
{
  "article_url": "https://example.com/article",  // Optional: direct URL
  "topic": "artificial intelligence",             // Optional: search topic
  "website": "bbc.com",                          // Optional: filter by website
  "max_age_days": 7                              // Optional: max article age
}
```

### `POST /api/ask`
Ask a question about ingested articles

**Request Body:**
```json
{
  "question": "What are the latest developments in AI?",
  "session_id": "optional-session-id"
}
```

### `DELETE /api/session/{session_id}`
Clear a chat session

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: LLM application framework
- **LangGraph**: Workflow orchestration
- **ChromaDB**: Vector database
- **Groq**: LLM inference
- **Exa**: News article search API
- **HuggingFace**: Embeddings model

### Frontend
- **Next.js**: React framework with SSR
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Icon library

## Development

### Backend Development

The backend uses LangGraph workflows defined in `backend/app/workflows/stories/`. The workflows handle:
- Article retrieval and processing
- Document chunking and embedding
- Question answering with RAG (Retrieval Augmented Generation)

### Frontend Development

The frontend is built with Next.js and uses:
- TypeScript for type safety
- Tailwind CSS for styling
- Component-based architecture
- API proxy configuration in `next.config.js`

## Troubleshooting

### Backend Issues

1. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **API key errors**: Verify all required API keys are set in `.env`
3. **ChromaDB errors**: Delete `docs/chroma/` directory to reset the vector store

### Frontend Issues

1. **Module not found**: Run `npm install` to install dependencies
2. **Connection errors**: Ensure the backend is running on port 8000
3. **Build errors**: Delete `.next/` directory and rebuild

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
