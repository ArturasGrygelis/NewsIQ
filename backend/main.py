from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
from dotenv import load_dotenv
from app.services import vectorstore_service, article_service

# Load environment variables
load_dotenv()

app = FastAPI(title="NewsIQ API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ArticleIngestRequest(BaseModel):
    website: Optional[str] = None
    topic: Optional[str] = None
    max_age_days: Optional[int] = 7
    article_url: Optional[str] = None

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

@app.post("/api/ingest", response_model=ArticleIngestResponse)
async def ingest_article(request: ArticleIngestRequest):
    """
    Ingest an article into the vectorstore.
    Can use exact URL or search by topic/website/max_age.
    """
    try:
        if request.article_url:
            # Load article from direct URL
            article = article_service.load_article_from_url(request.article_url)
            
            # Prepare documents for vectorstore
            documents = article_service.prepare_documents_for_vectorstore(article)
            
            # Add to vectorstore
            vectorstore_service.add_documents(documents)
            
            return ArticleIngestResponse(
                success=True,
                message=f"Article '{article.get('title', 'Unknown')}' successfully ingested",
                article_summary=article.get('text', '')[:500] + "..." if len(article.get('text', '')) > 500 else article.get('text', '')
            )
        else:
            # Search for articles
            if not request.topic:
                raise HTTPException(status_code=400, detail="Either article_url or topic must be provided")
            
            articles = article_service.search_articles(
                topic=request.topic,
                website=request.website,
                max_age_days=request.max_age_days or 7
            )
            
            if not articles:
                return ArticleIngestResponse(
                    success=False,
                    message="No articles found matching the criteria"
                )
            
            # Process all found articles
            total_docs = 0
            for article in articles:
                documents = article_service.prepare_documents_for_vectorstore(article)
                vectorstore_service.add_documents(documents)
                total_docs += len(documents)
            
            return ArticleIngestResponse(
                success=True,
                message=f"Successfully ingested {len(articles)} articles ({total_docs} chunks)",
                article_summary=f"Found articles: {', '.join([a.get('title', 'Unknown') for a in articles[:3]])}"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask", response_model=ChatResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer based on articles in the vectorstore.
    """
    try:
        from langchain_groq import ChatGroq
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Create or retrieve session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions:
            sessions[session_id] = {"history": []}
        
        # Search vectorstore for relevant documents
        documents = vectorstore_service.search(request.question, k=7, search_type="mmr")
        
        if not documents:
            return ChatResponse(
                answer="I couldn't find any relevant articles in the knowledge base. Please ingest some articles first.",
                sources=[],
                session_id=session_id
            )
        
        # Initialize LLM
        llm = ChatGroq(
            model="gemma2-9b-it",
            temperature=0.0,
            max_tokens=400,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Create QA chain
        prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks. 
            Use the following pieces of retrieved documents to answer the question. If you don't know the answer, just say that you don't know.
            Do not repeat yourself!
            Be informative and concise.
            Question: {question} 
            Documents: {documents} 
            Answer:
            """,
            input_variables=["question", "documents"],
        )
        
        qa_chain = prompt | llm | StrOutputParser()
        
        # Format documents
        docs_text = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(documents)])
        
        # Generate answer
        answer = qa_chain.invoke({
            "question": request.question,
            "documents": docs_text
        })
        
        # Extract sources
        sources = []
        for doc in documents:
            source_info = {
                "title": doc.metadata.get("title", "Unknown"),
                "url": doc.metadata.get("url", ""),
                "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            if source_info not in sources:  # Avoid duplicates
                sources.append(source_info)
        
        # Store in session history
        sessions[session_id]["history"].append({
            "question": request.question,
            "answer": answer
        })
        
        return ChatResponse(
            answer=answer,
            sources=sources[:3],  # Limit to top 3 sources
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
