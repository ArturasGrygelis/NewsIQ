"""
Simplified workflow for web scraping and summarization
This version works without the full LangGraph complexity for testing
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

from app.workflows.stories.tools import scraper_tool
from app.workflows.stories.workers import create_article_summarizer


def scrape_and_summarize_article(url: str, groq_api_key: Optional[str] = None) -> Dict:
    """
    Scrape a web article and generate a summary with topics.
    
    Args:
        url: The URL of the article to scrape and summarize
        groq_api_key: Optional GROQ API key (will use env var if not provided)
    
    Returns:
        Dict containing:
            - success: bool
            - title: str
            - source: str
            - summary: str
            - topics: List[str]
            - error: Optional[str]
    """
    
    # Step 1: Scrape the article
    print(f"🔍 Scraping article from: {url}")
    scrape_result = scraper_tool(url)
    
    if scrape_result.get("error"):
        return {
            "success": False,
            "error": f"Scraping failed: {scrape_result['error']}"
        }
    
    print(f"✅ Successfully scraped: {scrape_result['title']}")
    
    # Step 2: Initialize LLM
    api_key = groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "GROQ_API_KEY not found in environment"
        }
    
    try:
        llm = ChatGroq(
            model="gemma2-9b-it",
            temperature=0.0,
            max_tokens=4000,
            max_retries=3,
            api_key=api_key
        )
        
        # Step 3: Create summarizer and summarize
        print("📝 Generating summary and extracting topics...")
        summarizer = create_article_summarizer(llm)
        summary_result = summarizer.invoke({"article": scrape_result['text']})
        
        print("✅ Summary generated successfully")
        
        return {
            "success": True,
            "title": scrape_result['title'],
            "source": scrape_result['source'],
            "text_length": len(scrape_result['text']),
            "summary": summary_result.summary,
            "topics": summary_result.topics,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Summarization failed: {str(e)}"
        }


def test_workflow():
    """Test the workflow with a sample article"""
    
    print("=" * 70)
    print("TESTING WEB SCRAPING AND SUMMARIZATION WORKFLOW")
    print("=" * 70 + "\n")
    
    # Test with a BBC technology article
    test_url = "https://www.bbc.com/news/technology"
    
    result = scrape_and_summarize_article(test_url)
    
    if result["success"]:
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"\n📰 Title: {result['title']}")
        print(f"🌐 Source: {result['source']}")
        print(f"📄 Text Length: {result['text_length']} characters")
        print(f"\n📋 SUMMARY:\n{result['summary']}")
        print(f"\n🏷️  TOPICS:")
        for i, topic in enumerate(result['topics'], 1):
            print(f"   {i}. {topic}")
        print("\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed: {result['error']}")


if __name__ == "__main__":
    test_workflow()
