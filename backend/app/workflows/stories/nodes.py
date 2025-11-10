def initialize_workflow(state):
    """
    Initialize question and websites
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Updated state with steps, topic, and websites
    """
    # Ensure required fields exist
    if "steps" not in state:
        state["steps"] = []
    if "website_address" not in state:
        state["website_address"] = []

    steps = state["steps"]
    website_address = state.get("website_address", [])
    
    
    # Add initialization steps
    steps.append("topic initialization")
    steps.append("question_asked")
    if website_address:
        steps.append(f"initialized with {len(website_address)} websites")
    
    return {
         
        "website_address": website_address,
        "steps": steps,
       
    }

def web_search(state):
    topic = state["topic"]
    documents = state.get("documents", [])
    steps = state["steps"]
    steps.append("web_search")
    k = 8 - len(documents)
    web_results_list = []
    time = state["todays_date"]
    article_max_age = state.get("article_max_age", 1)
    custom_date = state.get("custom_date", None)
    # Calculate yesterday's date in ISO 8601 format
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    website_address = state.get("website_address", [])

    if custom_date:
        # Use custom date if provided
        published_after = custom_date + "T00:00:00.000Z"
    else:
        # Calculate date based on article_max_age (default 1 day)
        days_ago = datetime.datetime.now() - datetime.timedelta(days=article_max_age)
        published_after = days_ago.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Fetch results from exa
    exa_results_raw = exa.search_and_contents(
        query=topic,
        start_published_date =published_after,
        end_published_date =datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        livecrawl = "auto",
        type="auto",
        

        #exclude_text = ["Market analysis"],
        num_results=6,
        text={"max_characters": 2000},
        summary={
            "query": "Tell in summary a meaning about what is article written. Provide facts, be concise."
        },
        include_domains=websites,
        
    )
    exa_results = exa_results_raw.results if hasattr(exa_results_raw, "results") else []
    cleaned_exa_results = [clean_exa_document(doc) for doc in exa_results]
    return {"documents": combined_documents, "question": question, "steps": steps}


def summarize_article(state, llm, create_article_summarizer):
    """
    Summarize the article and extract main topics using the structured summarizer.
    """

    # Extract from state
    article_text = state["selected_document"]
    steps = state["steps"]

    # Record this step
    steps.append("summarize_article")

    # Create the summarization pipeline
    summarizer = create_article_summarizer(llm)

    # Run the structured LLM call
    result = summarizer.invoke({"article": article_text})

    # Log for debugging (optional)
    print("📝 Article summarization completed.")
    print(f"Summary: {result.summary[:200]}...")
    print(f"Topics: {result.topics}")

    # Return updated state
    return {
        **state,
        "summary": result.summary,
        "topics": result.topics,
        "steps": steps,
    }


def select_article(state,selector_llm):
    """
    Select the most relevant document from the available documents based on the topic.
    LangGraph workflow node for article selection.
    """
    from .checkers import create_article_selector
    import time as time_module

    
    topic = state["topic"]
    documents = state["documents"]
    steps = state["steps"]
    time = state["todays_date"]
    

   
    
    # Initialize document selector
    document_selector = create_article_selector(selector_llm)
    
    # Combine topic with date for context
    topic_with_time = f"{topic} {time}"
    article_summaries = [doc["                                   Apibendrinimas:    "] for doc in documents]
    
    print(f"🔍 Selecting most relevant article from {len(documents)} documents")
    print(f"📅 Topic with context: {topic_with_time}")
    
    # ✅ Add retry logic with fallback to handle LLM tool calling errors
    max_retries = 3
    top_idx = 0  # Default to first article if all retries fail
    
    for attempt in range(max_retries):
        try:
            # Select the most relevant document using the metadata extractor
            selection_result = document_selector.invoke({
                "articles": article_summaries,
                "topic": topic_with_time,
                "max_index": len(documents) - 1
            })
            
            top_idx = selection_result.selected_document_index
            
            # Validate index is within bounds
            if 0 <= top_idx < len(documents):
                print(f"✅ Selected document at index {top_idx} (attempt {attempt + 1})")
                break
            else:
                print(f"⚠️ Invalid index {top_idx}, using first article as fallback")
                top_idx = 0
                break
                
        except Exception as e:
            print(f"⚠️ Article selection attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                # Wait before retrying
                time_module.sleep(1)
                print(f"🔄 Retrying article selection...")
            else:
                # Final fallback: use first article
                print(f"⚠️ All retries failed, defaulting to first article")
                top_idx = 0
    
    selected_doc = documents[top_idx]
    
    print(f"📄 Selected article summary: {article_summaries[top_idx][:100]}...")
    
    steps.append("article_selected")
    
    return {

        "documents": documents,
        "steps": steps,
        "selected_document": selected_doc,
        
    }



def scrape_webpage_content(state, scraper_tool):
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

    result = scraper_tool(website_address)

    if result.get("error"):
        return {"error": result["error"]}

    document = {
        "title": result.get("title"),
        "text": result.get("text"),
        "source": result.get("source"),
    }

    return {"selected_document": [document]}

