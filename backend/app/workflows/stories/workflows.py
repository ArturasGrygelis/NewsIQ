import os
from langchain.schema.retriever import BaseRetriever
from typing_extensions import TypedDict, List, Annotated
from typing import Optional
from IPython.display import Image, display
from langchain_core.pydantic_v1 import BaseModel, Field

from langgraph.graph import START, END, StateGraph
import datetime
import uuid
from langchain_groq import ChatGroq
import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END


def article_summarization_graph():
    """
    Builds the scrape/search workflow graph.

    Args:
        search_type (str): The type of search strategy to use.
        k (int): Number of top documents to retrieve.
    """

    class GraphState(TypedDict):
        """
        Represents the state of our graph.
        Attributes:
            question: question
            generation: LLM generation
            search: whether to add search
            documents: list of documents
            generations_count : generations count
        """
        question: str
        generation: str
        search: str
        documents: List[str]
        steps: List[str]
        generation_count: int
        search_type: str
        k: int
        website_address: str
        summary: str
        topic: Optional[str]
        selected_document: str

    #search_type =  search_type
    #k = k 
    #website_address = website_address
    
    # LLM
    llm = ChatGroq(
        model="openai/gpt-oss-20b",  # Specify the Gemma2 9B model
        temperature=0.0,
        max_tokens=4000,
        max_retries=3,
        
    )
    
   

    # Graph
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("initialize_workflow", lambda state: initialize_workflow(state))
    workflow.add_node("web_search", web_search)  
    workflow.add_node("scrape_article", lambda state: scrape_webpage_content(state, scraper_tool))
    workflow.add_node("summarize_article", lambda state: summarize_article(state, llm, create_article_summarizer))
    workflow.add_node("select_article", lambda state: select_article(state, llm, article_summarizer))
    #workflow.add_node("add_to_chroma", lambda state: add_to_chroma(state,vectorstore))

    # Graph structure
    workflow.set_entry_point("initialize_workflow")

    workflow.add_conditional_edges(
        "initialize_workflow",
        lambda state: decide_scrape_or_search(state),
        {
            "web_search": "web_search",
            "scrape_article": "scrape_article",
        },
    )

    workflow.add_edge("web_search", "select_article")
    workflow.add_edge("select_article", "summarize_article")

    #workflow.add_conditional_edges(
    #    "summarize_article",
    #    lambda state: grade_summary(state, create_hallucination_checker(llm)),
    #    {
    #        "halucination": "summarize_article",
    #        "useful": "add_to_chroma",
    #    },
    #)

    workflow.add_edge("scrape_article", "summarize_article")
    workflow.add_edge("summarize_article", END)
    #workflow.add_edge("add_to_chroma", END)

    # Compile and return
    custom_graph = workflow.compile()
    return custom_graph