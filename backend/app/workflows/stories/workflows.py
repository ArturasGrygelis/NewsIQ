import os
from typing_extensions import TypedDict, List, Annotated
from typing import Optional


from langgraph.graph import END, StateGraph
import datetime
import uuid
from langchain_groq import ChatGroq
from typing import TypedDict, List

from .nodes import initialize_workflow, scrape_webpage_content, summarize_article, add_to_chroma, grade_summary_v_article
from .workers import create_article_summarizer, create_topics_identifier,  create_hallucination_checker





def article_summarization_graph(vectorstore):
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
        topics: List[str]
        selected_document: str

    
    
    # LLM
    llm = ChatGroq(
        model="openai/gpt-oss-120b",  
        temperature=0.0,
        max_tokens=6000,
        max_retries=3,
        
        
    )
    
   

    # Graph
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("initialize_workflow", lambda state: initialize_workflow(state))
     
    workflow.add_node("scrape_article", lambda state: scrape_webpage_content(state))
    workflow.add_node("summarize_article", lambda state: summarize_article(state, llm, create_article_summarizer,create_topics_identifier))
    workflow.add_node("add_to_chroma", lambda state: add_to_chroma(state,vectorstore))

    # Graph structure
    workflow.set_entry_point("initialize_workflow")

    workflow.add_edge("initialize_workflow", "scrape_article")
    workflow.add_edge("scrape_article", "summarize_article")
    workflow.add_conditional_edges(
        "summarize_article",
        lambda state: grade_summary_v_article(state,llm,create_hallucination_checker),
        {
            "Hallucinations": "summarize_article",
            "No hallucinations": "add_to_chroma",
        },
    )
    
    
    workflow.add_edge("add_to_chroma", END)

    # Compile and return
    custom_graph = workflow.compile()
    return custom_graph








