"""
FastAPI endpoint for web scraping and summarization
Add this to your main.py to integrate the workflow
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import the simplified workflow
from app.workflows.stories.simple_workflow import scrape_and_summarize_article


class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    topics: Optional[List[str]] = None
    text_length: Optional[int] = None
    error: Optional[str] = None


# Add this endpoint to your FastAPI app
@app.post("/api/scrape-summarize", response_model=ScrapeResponse)
async def scrape_and_summarize_endpoint(request: ScrapeRequest):
    """
    Scrape a web article and generate a summary with topics.
    
    Example request:
    {
        "url": "https://www.bbc.com/news/technology-12345"
    }
    
    Example response:
    {
        "success": true,
        "title": "Article Title",
        "source": "bbc.com",
        "summary": "A concise summary of the article...",
        "topics": ["AI", "Technology", "Innovation"],
        "text_length": 5000
    }
    """
    try:
        result = scrape_and_summarize_article(request.url)
        return ScrapeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing article: {str(e)}")


# Example: Integration with existing ingest endpoint
@app.post("/api/ingest-from-url")
async def ingest_from_url(request: ScrapeRequest):
    """
    Scrape, summarize, and add article to vectorstore in one step.
    """
    try:
        # Step 1: Scrape and summarize
        result = scrape_and_summarize_article(request.url)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Step 2: Prepare document for vectorstore
        from langchain.schema import Document
        
        document = Document(
            page_content=result["summary"],
            metadata={
                "title": result["title"],
                "source": result["source"],
                "url": request.url,
                "topics": ", ".join(result["topics"]),
                "text_length": result["text_length"]
            }
        )
        
        # Step 3: Add to vectorstore
        vectorstore_service.add_documents([document])
        
        return {
            "success": True,
            "message": f"Article '{result['title']}' scraped, summarized, and added to vectorstore",
            "summary": result["summary"],
            "topics": result["topics"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
