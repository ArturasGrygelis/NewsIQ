import requests
from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urlparse
import html2text
import cloudscraper


def clean_exa_document(doc):
    """
    Extracts and retains only the title, url, text, summary, and image from the exa result document.
    """
    return {
        "Pavadinimas:    ": doc.title,
        "        Straipnsio internetinis adresas:    ": doc.url,
        "Tekstas:    ": doc.text,
        "                                   Apibendrinimas:    ": doc.summary,
        "image": getattr(doc, 'image', None),  # Extract image if available
    }



def scraper_tool(url: str) -> dict:
    """
    web scraper using cloudscraper.
    Returns dict: {title, text, source, error}
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # choose session type
    session = cloudscraper.create_scraper() if cloudscraper else requests

    try:
        resp = session.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        # 1️⃣ Try readability extraction
        try:
            doc = Document(resp.text)
            title = doc.short_title()
            html = doc.summary()
            soup = BeautifulSoup(html, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            text = "\n".join(p for p in paragraphs if p)
        except Exception:
            # 2️⃣ Fallback to html2text
            text = html2text.html2text(resp.text)
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string if soup.title else "Untitled"

        return {
            "title": title.strip() if title else "Untitled",
            "text": text.strip() if text else None,
            "source": urlparse(url).netloc,
        }

    except Exception as e:
        return {"title": None, "text": None, "source": url, "error": str(e)}




def decide_scrape_or_search(state):
    """
    Determines the next step based on the scrape_article flag.

    Args:
        state (dict): The current graph state. Must contain a boolean key 'scrape_article'.

    Returns:
        str: 'scrape_article' if True, otherwise 'web_search'.
    """
    print("---DECIDE SCRAPE OR SEARCH---")
    search_type = state.get("search_type", "web_search")

    if search_type == "scrape_article":
        print("---DECISION: SCRAPE ARTICLE---")
        return "scrape_article"
    else:
        print("---DECISION: WEB SEARCH---")
        return "web_search"
