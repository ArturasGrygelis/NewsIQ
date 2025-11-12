from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
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
article_service = None
summarizer_graph = None
qa_graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize services and workflows on startup."""
    global vectorstore_service, article_service, summarizer_graph, qa_graph
    
    from app.services import VectorStoreService, ArticleService
    from app.workflows.stories.workflows import article_summarization_graph
    from app.workflows.answer.workflows import question_answering_graph
    
    # Initialize services
    print("🚀 Initializing NewsIQ services...")
    vectorstore_service = VectorStoreService(persist_directory="./app/chroma")
    article_service = ArticleService()
    
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
        
        # Invoke the summarization workflow
        result = summarizer_graph.invoke({
            "website_address": request.website_address,
        })
        
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
        
        # Invoke the question-answering workflow
        result = qa_graph.invoke({
            "question": request.question,
        })
        
        return {
            "success": True,
            "answer": result.get("answer", "No answer generated"),
            "result": result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

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
