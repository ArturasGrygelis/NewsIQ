import os
from langchain_core.retrievers import BaseRetriever
from typing_extensions import TypedDict, List, Annotated
from typing import Optional
from langgraph.graph import  END, StateGraph
import datetime
import uuid
from langchain_groq import ChatGroq
import os
from .nodes import initialize_workflow, retrieve, question_answering, grade_documents, transform_query ,related_documents_count, grade_answer_v_documents






LANGSMITH_API_KEY = os.environ.get('LANGCHAIN_API_KEY')
LANGSMITH_TRACING = os.environ.get('LANGCHAIN_TRACING_V2')
LANGSMITH_ENDPOINT = os.environ.get('LANGCHAIN_ENDPOINT')
LANGSMITH_PROJECT = os.environ.get('LANGCHAIN_PROJECT')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
EXA_API_KEY = os.environ.get('EXA_API_KEY')



def question_answering_graph(retriever):
    """
    Builds the scrape/search workflow graph.

    Args:
        retriever: The retriever used to fetch documents.
    """

    from typing import TypedDict, List

    class GraphState(TypedDict):
        """
        Represents the state of our graph.
        Attributes:
            question: question
            answer: LLM-generated answer
            documents: list of retrieved documents
            steps: list of workflow steps executed
            generation_count: number of LLM generations
            search_type: type of search strategy
            k: number of top documents retrieved
            selected_documents: selected documents for answering
        """
        question: str
        answer: str
        documents: List[str]
        steps: List[str]
        generation_count: int
        search_type: str
        k: int
        selected_documents: str

    llm = ChatGroq(
        model="openai/gpt-oss-20b",  # Specify the Gemma2 9B model
        temperature=0.0,
        max_tokens=4000,
        max_retries=3,
        
    )

    # Graph
    workflow = StateGraph(GraphState)

    # --- Nodes ---
    workflow.add_node("initialize_workflow", lambda state: initialize_workflow(state))
    workflow.add_node("retrieve_documents", lambda state: retrieve(state, retriever))
    workflow.add_node( "question_answering",lambda state: question_answering(state,llm,create_question_answerer))
    workflow.add_node("grade_documents", lambda state: grade_documents(state ,llm, retrieval_grader))
    workflow.add_node("transform_query", lambda state: transform_query(state,llm, create_question_rewriter))

    # --- Graph structure ---
    workflow.set_entry_point("initialize_workflow")

    workflow.add_edge("initialize_workflow", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "grade_documents")

    workflow.add_conditional_edges(
        "grade_documents",
        lambda state: related_documents_count(state),
        {
            "Are related documents": "question_answering",
            "No related documents": "transform_query",
        },
    )

    workflow.add_edge("transform_query", "retrieve_documents")

    workflow.add_conditional_edges(
        "question_answering",
        lambda state: grade_answer_v_documents(state, llm, create_hallucination_checker),
        {
            "Hallucinations": "question_answering",
            "No hallucinations": END,
        },
    )

    # Compile and return
    custom_graph = workflow.compile()
    return custom_graph