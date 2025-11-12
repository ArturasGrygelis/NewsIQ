from typing_extensions import TypedDict, List, Annotated
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate


def create_hallucination_checker(llm):
    """
    Function to create a hallucination checker object using a passed LLM model.
    
    Args:
        llm: The language model to be used for checking hallucinations in the student's answer.
        
    Returns:
        Callable: A pipeline function that checks if the student's answer contains hallucinations.
    """
    

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are professional fact checker,  you need to check summary: {summary}, which is made from an article: {article}, was there made any factual mistakes, hallucinations.
        If there are mistakes , return 'yes', if no mistakes, return 'no'
        return answer as yes or no.
        """,
        input_variables=["article", "summary"],
    )
    
    # Combine the prompt with the structured LLM hallucination checker
    hallucination_grader = prompt | llm |  StrOutputParser()

    # Return the hallucination checker object
    return hallucination_grader




def create_topics_identifier(llm):
    """
    Creates a structured-output summarizer that summarizes an article 
    and extracts main topics in a single call.

    Args:
        llm: The language model used for topic extraction.

    Returns:
        Callable: A topics identifier pipeline that outputs article 'topics'.
    """

    

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are a professional content summarizer.
        Read the article provided below and:
        Identify and list the main topics, entities, or concepts mentioned in the article.
        Do not add anything else!
        
        ARTICLE:
        {article}
        """,
        input_variables=["article"],
    )

    # Combine prompt and model into a reusable summarization pipeline
    topic_identifier = prompt | llm | StrOutputParser()

    # Return the ready-to-use summarizer pipeline
    return topic_identifier




def create_article_summarizer(llm):
    """
    Creates a structured-output summarizer that summarizes an article 
    and extracts main topics in a single call.

    Args:
        llm: The language model used for summarization.

    Returns:
        Callable: A summarization pipeline that outputs summary.
    """

   

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are a professional content summarizer.
        Read the article provided below and:
        1. Write a concise and factual summary (1-3 sentences).
        Do not add anything else!
        
        ARTICLE:
        {article}
        """,
        input_variables=["article"],
    )

    # Combine prompt and model into a reusable summarization pipeline
    summarizer = prompt | llm | StrOutputParser()

    # Return the ready-to-use summarizer pipeline
    return summarizer







