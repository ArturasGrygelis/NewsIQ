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
from .nodes import (
    
    web_search,
    initialize_topic,
    generate_script,
    audio_transcript,
    select_article,
    generate_script_from_article,
    initialize_manual_topic
)

LANGSMITH_API_KEY = os.environ.get('LANGCHAIN_API_KEY')
LANGSMITH_TRACING = os.environ.get('LANGCHAIN_TRACING_V2')
LANGSMITH_ENDPOINT = os.environ.get('LANGCHAIN_ENDPOINT')
LANGSMITH_PROJECT = os.environ.get('LANGCHAIN_PROJECT')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
EXA_API_KEY = os.environ.get('EXA_API_KEY')

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
        k : int
        website_adress: str
        summary:str

    llm = ChatGroq(
    model="gemma2-9b-it",  # Specify the Gemma2 9B model
    temperature=0.0,
    max_tokens=400,
    max_retries=3
    )
    
    retriever = create_retriever_from_chroma(vectorstore_path="docs/chroma/", search_type=search_type, k=k, chunk_size=550, chunk_overlap=40)
    


    # Graph
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("initialize_workflow", lambda state: initialize_workflow(state, retriever))
    workflow.add_node("retrieve", lambda state: retrieve(state, retriever))  
    workflow.add_node("grade_documents", lambda state: grade_documents(state, retrieval_grader_grader(llm) ))  # grade documents
    workflow.add_node("generate", lambda state: generate(state,QA_chain(llm) ))  # generatae
    workflow.add_node("web_search", web_search)  # web search
    workflow.add_node("transform_query", lambda state: transform_query(state,create_question_rewriter(llm) ))
    workflow.add_node("scrape_webpage_content", lambda state: scrape_webpage_content(state,llm))
    workflow.add_node("summarize_article", lambda state: summarize_article(state,llm,article_summarizer))


    # Build graph
    workflow.set_entry_point("initialize_workflow")
    workflow.add_conditional_edges(
        "ask_question",
        lambda state: retrieve-or_not(state),
    
        {
        "retrieve": "retrieve",
        'web_content': "web_content",
        
        },
    )

    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "improve_query": "improve_query",
            "generate": "generate",
        
        },
    )
    workflow.add_edge("transform_query", "retrieve")
    workflow.add_conditional_edges(
        "generate",
        lambda state: grade_generation_v_documents_and_question(state, create_hallucination_checker(llm), create_helpfulness_checker(llm)),
        {
            "halucination": "generate",
            "useful": END,
            
        },
    )

    workflow.add_edge("transform_query", "retrieve")


    workflow.add_conditional_edges(
        "web_content",
        lambda state: scrape_or_not(state),
        {
            "web_search": "web_search",
            "scrape_article": "scrape_article",
            
        },
    )
    workflow.add_edge("web_search", "select_article")
    workflow.add_edge("select_article", "summarize_article")
    workflow.add_conditional_edges(
        "summarize_article",
        lambda state: grade_summary(state, create_hallucination_checker(llm)),
        {
            "halucination": "summarize_article",
            "useful": "add_to_chroma",
            
        },
    )
    
    workflow.add_edge("scrape_article", "summarize_article")
    workflow.add_edge("add_to_chroma", END)
    
    
    


    custom_graph = workflow.compile()
    return custom_graph