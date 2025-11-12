from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="NewsIQ API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances - initialized on startup
vectorstore_service = None
summarizer_graph = None
qa_graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize services and workflows on startup."""
    global vectorstore_service, summarizer_graph, qa_graph
    
    from app.services import VectorStoreService
    from app.workflows.stories.workflows import article_summarization_graph
    from app.workflows.answer.workflows import question_answering_graph
    
    # Initialize services
    print("🚀 Initializing NewsIQ services...")
    vectorstore_service = VectorStoreService(persist_directory="./app/chroma")
    
    # Initialize workflows
    print("📊 Building workflow graphs...")
    vectorstore = vectorstore_service.get_vectorstore()
    instruct_retriever = vectorstore_service.get_instruct_retriever(k=15)
    
    summarizer_graph = article_summarization_graph(vectorstore)
    qa_graph = question_answering_graph(instruct_retriever)
    
    print("✅ NewsIQ is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down NewsIQ...")

# Request/Response Models
class ArticleIngestRequest(BaseModel):
    website: Optional[str] = None
    topic: Optional[str] = None
    max_age_days: Optional[int] = 7
    article_url: Optional[str] = None

class ScrapeAndSummarizeRequest(BaseModel):
    website_address: str

class QuestionAnswerRequest(BaseModel):
    question: str

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    session_id: str

class ArticleIngestResponse(BaseModel):
    success: bool
    message: str
    article_summary: Optional[str] = None
    article_title: Optional[str] = None
    article_url: Optional[str] = None
    article_authors: Optional[str] = None
    article_language: Optional[str] = None
    article_topics: Optional[str] = None
    article_text: Optional[str] = None

# Store for session-based conversations
sessions = {}

@app.get("/")
async def root():
    return {
        "message": "Welcome to NewsIQ API",
        "version": "1.0.0",
        "endpoints": {
            "/api/ingest": "POST - Ingest articles into vectorstore",
            "/api/ask": "POST - Ask questions about articles",
            "/api/health": "GET - Health check"
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/scrape-summarize")
async def scrape_and_summarize(request: ScrapeAndSummarizeRequest):
    """
    Scrape, summarize, and add article to vectorstore using the workflow.
    
    Example request:
    {
        "website_address": "https://www.wired.com/story/the-repair-app/"
    }
    """
    try:
        if not summarizer_graph:
            raise HTTPException(status_code=500, detail="Summarizer workflow not initialized")
        
        # Invoke the summarization workflow asynchronously
        result = await asyncio.to_thread(
            summarizer_graph.invoke,
            {"website_address": request.website_address}
        )
        
        return {
            "success": True,
            "message": "Article scraped, summarized, and added to vectorstore",
            "result": result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing article: {str(e)}")

@app.post("/api/answer")
async def answer_question(request: QuestionAnswerRequest):
    """
    Answer a question using the question-answering workflow.
    
    Example request:
    {
        "question": "Why humanoids can be an issue for humanity?"
    }
    """
    try:
        if not qa_graph:
            raise HTTPException(status_code=500, detail="QA workflow not initialized")
        
        # Invoke the question-answering workflow asynchronously
        result = await asyncio.to_thread(
            qa_graph.invoke,
            {"question": request.question}
        )
        
        # Extract documents/sources if available
        documents = result.get("selected_documents", result.get("documents", []))
        sources = []
        if documents:
            for doc in documents[:5]:  # Show up to 5 source documents
                if hasattr(doc, 'metadata'):
                    sources.append({
                        "title": doc.metadata.get("title", "Unknown"),
                        "url": doc.metadata.get("link", ""),
                        "snippet": doc.page_content[:300] if hasattr(doc, 'page_content') else "",
                        "authors": doc.metadata.get("authors", ""),
                        "language": doc.metadata.get("language", ""),
                        "topics": doc.metadata.get("topics", "")
                    })
        
        return {
            "answer": result.get("answer", "No answer generated"),
            "sources": sources,
            "session_id": str(uuid.uuid4())
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@app.post("/api/ingest", response_model=ArticleIngestResponse)
async def ingest_article(request: ArticleIngestRequest):
    """
    Ingest an article using the scrape-summarize workflow.
    Requires article_url (direct article URL).
    """
    try:
        if not request.article_url:
            raise HTTPException(status_code=400, detail="article_url is required")
        
        if not summarizer_graph:
            raise HTTPException(status_code=500, detail="Summarizer workflow not initialized")
        
        # Invoke the article summarization workflow asynchronously
        result = await asyncio.to_thread(
            summarizer_graph.invoke,
            {"website_address": request.article_url}
        )
        
        # Extract article details from result
        documents = result.get("selected_document", [])
        article = documents[0] if documents else None
        
        topics = result.get("topics", [])
        topics_str = ", ".join(topics) if isinstance(topics, list) else str(topics)
        
        # Convert authors to string if it's a list
        authors = article.metadata.get("authors", "") if article else ""
        authors_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
        
        return ArticleIngestResponse(
            success=True,
            message=f"Article successfully processed and stored in vectorstore",
            article_summary=result.get("summary", ""),
            article_title=article.metadata.get("title", "") if article else "",
            article_url=article.metadata.get("link", "") if article else request.article_url,
            article_authors=authors_str,
            article_language=article.metadata.get("language", "") if article else "",
            article_topics=topics_str,
            article_text=article.page_content[:1000] if article else ""  # First 1000 chars
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error ingesting article: {str(e)}")

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session cleared"}
    return {"message": "Session not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
