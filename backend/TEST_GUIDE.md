# NewsIQ Backend - Testing Web Scraping and Summarization

This guide will help you test the web scraping and summarization workflow.

## Prerequisites

1. **Python Environment**: Make sure you have Python 3.8+ installed
2. **API Key**: You need a GROQ API key

## Setup

### 1. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your GROQ API key:

```powershell
cp .env.example .env
```

Edit `.env` and add your GROQ API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

## Testing the Workflow

### Option 1: Simple Test Script (Recommended)

This tests just the scraping and summarization components:

```powershell
python test_simple_workflow.py
```

This will:
- Scrape a web article (default: BBC Technology page)
- Extract the article content
- Generate a summary using GROQ LLM
- Extract main topics from the article

### Option 2: Detailed Component Test

For more detailed testing of individual components:

```powershell
python test_workflow.py
```

### Option 3: Integration with FastAPI

To integrate into your FastAPI app, add an endpoint in `main.py`:

```python
from app.workflows.stories.simple_workflow import scrape_and_summarize_article

@app.post("/api/scrape-summarize")
async def scrape_and_summarize(request: dict):
    """Scrape and summarize a web article"""
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    result = scrape_and_summarize_article(url)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
```

## Expected Output

When the test runs successfully, you should see:

```
🔍 Scraping article from: https://...
✅ Successfully scraped: [Article Title]
📝 Generating summary and extracting topics...
✅ Summary generated successfully

==================================================
RESULTS
==================================================

📰 Title: [Article Title]
🌐 Source: [Website]
📄 Text Length: [X] characters

📋 SUMMARY:
[AI-generated summary of the article]

🏷️  TOPICS:
   1. [Topic 1]
   2. [Topic 2]
   ...

✅ Test completed successfully!
```

## Common Issues

### Import Errors
If you see import errors, make sure you're in the `backend` directory and have installed all dependencies.

### API Key Errors
Make sure your `.env` file contains a valid GROQ API key:
```
GROQ_API_KEY=gsk_...
```

### Scraping Errors
Some websites block scraping. Try different URLs if one doesn't work. News sites like BBC, CNN, or Reuters usually work well.

## Next Steps

Once the workflow tests successfully:

1. ✅ The workflow components work correctly
2. ✅ You can integrate them into your FastAPI endpoints
3. ✅ You can connect them to your vectorstore for storage
4. ✅ You can use the full LangGraph workflow if needed

## Custom URLs

To test with your own URL, modify the test script:

```python
# In test_simple_workflow.py
test_url = "https://your-article-url-here.com"
```
