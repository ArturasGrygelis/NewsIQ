import requests
from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urlparse
import html2text
import cloudscraper





def scrape_webpage_content(state):
    """
    Scrapes a webpage and returns its content as part of the updated graph state.

    Args:
        state (dict): The current graph state. Must contain "url".
        scraper_tool (callable): A function that takes a URL and returns a dict
                                 with keys: title, text, source, error.

    Returns:
        dict: Updated state fragment with keys: documents (list of scraped docs)
              and error if scraping fails.
    """
    steps = state["steps"]
    steps.append("web_scraping")

    website_address = state.get("website_address")
    if not website_address:
        return {"error": "No URL provided."}

    loader = NewsURLLoader(
    urls=[website_address],
)
    docs = loader.load()
    print(f"loaded document content:  {docs}")

    

    return {"selected_document": docs}

