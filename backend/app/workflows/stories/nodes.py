from .workers import create_article_summarizer
from .tools import scraper_tool


def grade_summary_v_article(state,llm,create_hallucination_checker ):
    """
    Determines whether the generation is grounded in the document and answers the question.
    """
    print("---CHECK HALLUCINATIONS---")
    article_text = state["selected_document"]
    steps = state["steps"]
    summary = state.get("summary")
    
    steps.append("Check for hallucinations")
    hallucination_grader = create_hallucination_checker(llm)
    # Grading hallucinations
    score = hallucination_grader.invoke(
        {"article": article_text, "summary": summary}
    )
    

    # Check hallucination
    if score == "yes":
        print("---Found hallucinations---")
        return "Hallucinations"
        
    if score == "no":
        print("---no hallucinations---")
        return "No hallucinations"



def add_to_chroma(state,vectorstore):
    """
    Adds the article to Chroma using vectorstore from state.
    Stores title, source, topics, summary in metadata, and article text as page_content.
    """

    

    # Extract article info

    documents = state["selected_document"]  # This is a list
    article = documents[0]  # Get the first (and only) document from the list

    summary = state.get("summary", "")
    topics = state.get("topics", [])
    steps = state.get("steps", [])
    steps.append("add_to_chroma")

    article_text = article.page_content  # ← Use .page_content, not .get("text")
    article_title = article.metadata.get("title", "Untitled")  # ← Access metadata
    article_link = article.metadata.get("link", "")
    article_authors = article.metadata.get("authors", "")
    article_language = article.metadata.get("language", "")
    
    
        
    # Create Document
    doc = Document(
    page_content=article_text,
    metadata={
        "title": article_title,
        "link": article_link,
        "summary": summary,
        "topics": ", ".join(topics) if isinstance(topics, list) else str(topics),
        "language": article_language,
        "authors": ", ".join(article_authors) if isinstance(topics, list) else str(article_authors), 
    }
)

    # Add to Chroma
    doc_id = str(uuid4())
    vectorstore.add_documents(documents=[doc], ids=[doc_id])
    

    print(f"✅ Document added to Chroma: {doc_id}")

    # Update state
    return {
        **state,
        "documents": state.get("documents", []) + [doc],
        "steps": steps
    }




def summarize_article(state, llm, create_article_summarizer,create_topics_identifier):
    """
    Summarize the article and extract main topics using the structured summarizer.
    """

    # Extract from state
    article_text = state["selected_document"]
    steps = state["steps"]

    
    steps.append("summarize_article")

    # Create the summarization pipeline
    summarizer = create_article_summarizer(llm)
    topics_identifier = create_topics_identifier(llm)

    
    summary = summarizer.invoke({"article": article_text})
    topics =  topics_identifier.invoke({"article": article_text})

    # Log for debugging (optional)
    print("📝 Article summarization completed.")
    print(f"Summary: {summary}...")
    print(f"Topics: {topics}")

    # Return updated state
    return {
        **state,
        "summary": summary,
        "topics": topics,
        "steps": steps,
    }




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
