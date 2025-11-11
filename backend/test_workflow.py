"""
Test script for web scraping and summarization workflow
Tests only the scraping and summarization parts of the workflow
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'workflows', 'stories'))

from tools import scraper_tool
from workers import create_article_summarizer
from langchain_groq import ChatGroq

def test_scraping_and_summarization(url: str):
    """
    Test web scraping and article summarization
    
    Args:
        url: The URL of the article to scrape and summarize
    """
    print(f"🔍 Testing workflow with URL: {url}\n")
    
    # Step 1: Test web scraping
    print("=" * 60)
    print("STEP 1: Web Scraping")
    print("=" * 60)
    
    result = scraper_tool(url)
    
    if result.get("error"):
        print(f"❌ Scraping failed: {result['error']}")
        return
    
    print(f"✅ Successfully scraped article")
    print(f"📰 Title: {result['title']}")
    print(f"🌐 Source: {result['source']}")
    print(f"📄 Text length: {len(result['text'])} characters")
    print(f"📝 Preview: {result['text'][:300]}...\n")
    
    # Step 2: Test summarization
    print("=" * 60)
    print("STEP 2: Article Summarization")
    print("=" * 60)
    
    # Initialize LLM
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        return
    
    llm = ChatGroq(
        model="gemma2-9b-it",
        temperature=0.0,
        max_tokens=4000,
        max_retries=3,
        api_key=groq_api_key
    )
    
    # Create summarizer
    summarizer = create_article_summarizer(llm)
    
    # Summarize the article
    try:
        summary_result = summarizer.invoke({"article": result['text']})
        
        print(f"✅ Successfully summarized article")
        print(f"\n📋 SUMMARY:")
        print(f"{summary_result.summary}")
        print(f"\n🏷️  TOPICS:")
        for i, topic in enumerate(summary_result.topics, 1):
            print(f"   {i}. {topic}")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return {
            "scraping": {
                "title": result['title'],
                "source": result['source'],
                "text_length": len(result['text'])
            },
            "summarization": {
                "summary": summary_result.summary,
                "topics": summary_result.topics
            }
        }
        
    except Exception as e:
        print(f"❌ Summarization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_full_workflow_simple(url: str):
    """
    Test the full workflow in a simple way (without LangGraph)
    """
    print("\n" + "=" * 60)
    print("TESTING SIMPLIFIED WORKFLOW")
    print("=" * 60 + "\n")
    
    # Initialize state
    state = {
        "website_address": url,
        "steps": [],
        "selected_document": None,
        "summary": None,
        "topics": None
    }
    
    # Step 1: Initialize
    print("Step 1: Initializing workflow...")
    state["steps"].append("initialization")
    
    # Step 2: Scrape
    print("Step 2: Scraping article...")
    result = scraper_tool(url)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    
    state["selected_document"] = {
        "title": result['title'],
        "text": result['text'],
        "source": result['source']
    }
    state["steps"].append("web_scraping")
    print(f"✅ Scraped: {result['title']}")
    
    # Step 3: Summarize
    print("Step 3: Summarizing article...")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found")
        return
    
    llm = ChatGroq(
        model="gemma2-9b-it",
        temperature=0.0,
        max_tokens=4000,
        max_retries=3,
        api_key=groq_api_key
    )
    
    summarizer = create_article_summarizer(llm)
    summary_result = summarizer.invoke({"article": state["selected_document"]["text"]})
    
    state["summary"] = summary_result.summary
    state["topics"] = summary_result.topics
    state["steps"].append("summarize_article")
    
    print(f"✅ Summarized successfully")
    
    # Print results
    print("\n" + "=" * 60)
    print("WORKFLOW RESULTS")
    print("=" * 60)
    print(f"\n📰 Title: {state['selected_document']['title']}")
    print(f"\n📋 Summary:\n{state['summary']}")
    print(f"\n🏷️  Topics:")
    for i, topic in enumerate(state['topics'], 1):
        print(f"   {i}. {topic}")
    print(f"\n📊 Steps completed: {' → '.join(state['steps'])}")
    
    return state


if __name__ == "__main__":
    # Test URL - you can change this to any news article
    test_url = "https://www.bbc.com/news/technology"
    
    print("=" * 60)
    print("NEWSIQ WORKFLOW TEST")
    print("=" * 60)
    
    # Run individual component tests
    result = test_scraping_and_summarization(test_url)
    
    # Run simplified workflow test
    if result:
        print("\n" * 2)
        workflow_result = test_full_workflow_simple(test_url)
        
        if workflow_result:
            print("\n✅ All tests passed! Your workflow components are working correctly.")
            print("\nYou can now integrate this into your FastAPI app.")
