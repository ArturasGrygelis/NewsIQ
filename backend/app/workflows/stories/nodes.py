from langgraph.graph import START, END, StateGraph
from exa_py import Exa
from langchain_groq import ChatGroq
from typing_extensions import TypedDict, List, Annotated
from IPython.display import Image, display
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.vectorstores.utils import filter_complex_metadata
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import datetime
import uuid
from langchain_groq import ChatGroq
import os
from langchain.prompts import PromptTemplate
import numpy as np
import torch
from torch import nn
import datetime
import os
from exa_py import Exa
from langchain_groq import ChatGroq
from typing_extensions import TypedDict, List, Annotated



30.8 kB
import os
import streamlit as st
from typing_extensions import TypedDict, List
from IPython.display import Image, display
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema import Document
from langgraph.graph import START, END, StateGraph
from langchain.prompts import PromptTemplate
import uuid
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_chroma import Chroma
from langchain_community.document_loaders import NewsURLLoader
from langchain_community.retrievers.wikipedia import WikipediaRetriever
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredURLLoader, NewsURLLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain.schema import Document
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain.document_loaders import TextLoader
from langgraph.graph import START, END, StateGraph



async def handle_userinput(user_question, custom_graph):
    # Add the user's question to the chat history and display it in the UI
    st.session_state.messages.append({"role": "user", "content": user_question})
    st.chat_message("user").write(user_question)

    # Generate a unique thread ID for the graph's state
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    try:
        # Invoke the custom graph with the input question
        state_dict = await custom_graph.ainvoke(
            {"question": user_question, "steps": []}, config
        )

        # Retrieve the documents from the graph's state (if available)
        docs = state_dict["documents"]
        
        # Display the retrieved documents in the sidebar
        with st.sidebar:
            st.subheader("Your documents")
            with st.spinner("Processing"):
                for doc in docs:
                    # Extract document content
                    content = doc.page_content  # Assuming the document has a `page_content` attribute
                    
                    # Extract document metadata if available
                    metadata = doc.metadata if hasattr(doc, 'metadata') else {}

                    # Display content and metadata
                    st.write(f"Document: {content}")
                    
                    # Display metadata (assuming it's a dictionary)
                    if metadata:
                        st.write("Metadata:")
                        for key, value in metadata.items():
                            st.write(f"- {key}: {value}")
                    else:
                        st.write("No metadata available.")

        # Check if a response (generation) was produced by the graph
        if 'generation' in state_dict and state_dict['generation']:
            response = state_dict["generation"]

            # Add the assistant's response to the chat history and display it
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
        else:
            # Handle cases where no valid generation is present
            st.chat_message("assistant").write("Your question violates toxicity rules or contains sensitive information.")

    except Exception as e:
        # Display an error message in case of failure
        st.chat_message("assistant").write("An error occurred: Try to change the question.")
        st.chat_message("assistant").write(e)


def create_retriever_from_chroma(vectorstore_path="./docs/chroma/", search_type='mmr', k=7, chunk_size=550, chunk_overlap=40):
    model_name = "Alibaba-NLP/gte-base-en-v1.5"
    model_kwargs = {'device': 'cpu', "trust_remote_code": 'False'}
    encode_kwargs = {'normalize_embeddings': True}

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    if os.path.exists(vectorstore_path) and os.listdir(vectorstore_path):
        vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embeddings)
    else:
        st.write("Vector store doesn't exist and will be created now")

        urls = [
 
"https://github.com/zedr/clean-code-python",
"https://tenthousandmeters.com/blog/python-behind-the-scenes-10-how-python-dictionaries-work/",
"https://realpython.com/python-testing/",
"https://docs.python-guide.org/writing/license/",
    "https://blogs.nvidia.com/blog/what-is-a-transformer-model/",
    "https://research.google/blog/transformer-a-novel-neural-network-architecture-for-language-understanding/",
"https://realpython.com/python-pep8/",
"https://towardsdatascience.com/ideal-python-environment-setup-for-data-science-cdb03a447de8",
"https://realpython.com/python3-object-oriented-programming/",
"https://realpython.com/python-functional-programming/",
"https://fivethirtyeight.com/features/science-isnt-broken/",
"https://github.com/renatofillinich/ab_test_guide_in_python/blob/master/AB%20testing%20with%20Python.ipynb",
"https://towardsdatascience.com/why-is-data-science-failing-to-solve-the-right-problems-7b5b6121e3b4",
"https://medium.com/@srowen/common-probability-distributions-347e6b945ce4",
"https://github.com/renatofillinich/ab_test_guide_in_python/blob/master/AB%20testing%20with%20Python.ipynb",
"https://scikit-learn.org/stable/modules/compose.html",
"https://machinelearningmastery.com/light-gradient-boosted-machine-lightgbm-ensemble/",
"https://neptune.ai/blog/xgboost-vs-lightgbm",
"https://towardsdatascience.com/interpretable-machine-learning-with-xgboost-9ec80d148d27",
"https://www.cio.com/article/247005/what-are-containers-and-why-do-you-need-them.html",
"https://mitsloan.mit.edu/ideas-made-to-matter/machine-learning-explained",
"https://towardsdatascience.com/making-friends-with-machine-learning-5e28d5205a29",
"https://towardsdatascience.com/handling-imbalanced-datasets-in-machine-learning-7a0e84220f28",
"https://machinelearningmastery.com/multi-class-imbalanced-classification/",
"https://imbalanced-learn.org/stable/auto_examples/applications/plot_impact_imbalanced_classes.html",
"https://docs.ray.io/en/master/tune/examples/tune-sklearn.html",
"https://www.kaggle.com/code/ldfreeman3/a-data-science-framework-to-achieve-99-accuracy",
"https://cs231n.github.io/optimization-2/",
"https://alexander-schiendorfer.github.io/2020/02/24/a-worked-example-of-backprop.html",
"https://www.analyticsvidhya.com/blog/2020/01/fundamentals-deep-learning-activation-functions-when-to-use-them/",
"https://ml-cheatsheet.readthedocs.io/en/latest/activation_functions.html",
"https://d2l.ai/chapter_multilayer-perceptrons/mlp.html",
"https://d2l.ai/chapter_linear-classification/softmax-regression.html#loss-function",
"https://d2l.ai/chapter_optimization/",
    "https://www.investopedia.com/terms/s/statistical-significance.asp",
"https://d2l.ai/chapter_linear-classification/softmax-regression.html#loss-function",
"https://d2l.ai/chapter_convolutional-neural-networks/why-conv.html",
"https://d2l.ai/chapter_convolutional-modern/alexnet.html",
"https://d2l.ai/chapter_convolutional-modern/vgg.html",
"https://d2l.ai/chapter_convolutional-modern/nin.html",
"https://d2l.ai/chapter_convolutional-modern/googlenet.html",
    'https://python.langchain.com/v0.1/docs/guides/productionization/evaluation/',
    'https://python.langchain.com/v0.1/docs/guides/productionization/evaluation/string/',
    'https://python.langchain.com/v0.1/docs/guides/productionization/evaluation/comparison/',
    'https://python.langchain.com/v0.1/docs/guides/productionization/evaluation/trajectory/',
    "https://langchain-ai.github.io/langgraph/concepts/high_level/#why-langgraph",
    'https://langchain-ai.github.io/langgraph/concepts/low_level/#only-stream-tokens-from-specific-nodesllms',
    "https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/#reflection",
    "https://langchain-ai.github.io/langgraph/concepts/faq/",
    "https://www.geeksforgeeks.org/python-oops-concepts/",
    "https://www.mckinsey.com/featured-insights/mckinsey-explainers/what-is-fintech",
    "https://datascientest.com/en/adversarial-attack-definition-and-protection-against-this-threat",
    "https://datascientest.com/en/all-about-dspy",
    "https://datascientest.com/en/arithmetic-and-data-science",
    "https://datascientest.com/en/all-about-machine-learning-metrics",
    "https://datascientest.com/en/all-about-procedural-programming",
    "https://datascientest.com/en/all-about-cryptography",
   "https://datascientest.com/en/all-about-predictive-coding",
    "https://datascientest.com/en/all-about-network-convergence",
    "https://datascientest.com/en/all-about-forensic-analysis",
    "https://datascientest.com/en/all-about-chatgpt-jailbreak",
    "https://datascientest.com/en/all-about-pentest",
    "https://datascientest.com/en/all-about-embedded-systems",
    "https://datascientest.com/en/all-about-network-operating-system",
    "https://datascientest.com/en/all-about-ai-and-cybersecurity",
    "https://datascientest.com/en/all-about-cybernetics",
    "https://datascientest.com/en/all-about-seo",
    "https://datascientest.com/en/all-about-expert-system",
    "https://datascientest.com/en/all-about-telecommunications",
    "https://datascientest.com/en/all-about-smart-cities",
    "https://datascientest.com/en/all-about-artificial-intelligence-and-finance-sector",
    "https://datascientest.com/en/all-about-generated-pre-trained-transformers",
    "https://datascientest.com/en/all-about-iso-27001",
    "https://datascientest.com/en/all-about-smart-sensors",
    "https://datascientest.com/en/all-about-virtual-networks",
    "https://datascientest.com/en/all-about-ethical-ai",
    "https://datascientest.com/en/all-about-saio",
    "https://datascientest.com/en/all-about-recommendation-algorithm",
    "https://www.geeksforgeeks.org/activation-functions-neural-networks/",
    "https://www.geeksforgeeks.org/activation-functions-in-neural-networks-set2/?ref=oin_asr1",
    "https://www.geeksforgeeks.org/choosing-the-right-activation-function-for-your-neural-network/?ref=oin_asr3",
    "https://www.geeksforgeeks.org/difference-between-feed-forward-neural-networks-and-recurrent-neural-networks/?ref=oin_asr2",
    "https://www.geeksforgeeks.org/recurrent-neural-networks-explanation/?ref=oin_asr11",
    "https://www.geeksforgeeks.org/deeppose-human-pose-estimation-via-deep-neural-networks/?ref=oin_asr13",
    "https://www.geeksforgeeks.org/auto-associative-neural-networks/?ref=oin_asr18",
    "https://www.geeksforgeeks.org/what-are-graph-neural-networks/?ref=oin_asr30",
    "https://hdsr.mitpress.mit.edu/pub/la3vitqm/release/2",
    "https://datasciencedojo.com/blog/a-guide-to-large-language-models/",
    "https://datasciencedojo.com/blog/bootstrap-sampling/",
    "https://datasciencedojo.com/blog/top-statistical-concepts/",
    "https://datasciencedojo.com/blog/probability-for-data-science/",
    "https://datasciencedojo.com/blog/top-statistical-techniques/",
    "https://datasciencedojo.com/blog/statistical-distributions/",
    "https://datasciencedojo.com/blog/data-science-in-finance/",
    "https://datasciencedojo.com/blog/random-forest-algorithm/",
    "https://datasciencedojo.com/blog/gini-index-and-entropy/",
    "https://datasciencedojo.com/blog/boosting-algorithms-in-machine-learning/",
    "https://datasciencedojo.com/blog/ensemble-methods-in-machine-learning/",
    "https://datasciencedojo.com/blog/langgraph-tutorial/",
    "https://datasciencedojo.com/blog/data-driven-marketing-in-2024/",
    "https://datasciencedojo.com/blog/on-device-ai/",
    
    
]
        
        def extract_sentences_from_web(links, chunk_size=500, chunk_overlap=30):
            data = []
            for link in links:
                loader = NewsURLLoader(urls=[link])
                data += loader.load()
            return data

        docs = extract_sentences_from_web(links=urls)

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap,
            separators=["\n\n \n\n", "\n\n\n", "\n\n", r"In \[[0-9]+\]", r"\n+", r"\s+"],
            is_separator_regex=True
        )
        split_docs = text_splitter.split_documents(docs)

        vectorstore = Chroma.from_documents(
            documents=split_docs, embedding=embeddings, persist_directory=vectorstore_path
        )

    retriever = vectorstore.as_retriever(search_type=search_type, search_kwargs={"k": k})
    
    return retriever


def retrieval_grader_grader(llm):
    """
    Function to create a grader object using a passed LLM model.
    
    Args:
        llm: The language model to be used for grading.
        
    Returns:
        Callable: A pipeline function that grades relevance based on the LLM.
    """
    
    # Define the class for grading documents inside the function
    class GradeDocuments(BaseModel):
        """Binary score for relevance check on retrieved documents."""
        binary_score: str = Field(
            description="Documents are relevant to the question, 'yes' or 'no'"
        )
    
    # Create the structured LLM grader using the passed LLM
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""You are a teacher grading a quiz. You will be given: 
        1/ a QUESTION
        2/ A FACT provided by the student
        
        You are grading RELEVANCE RECALL:
        A score of 1 means that  the  FACT is relevant to the QUESTION. 
        A score of 0 means that the FACT is relevant to the QUESTION. 
        1 is the highest (best) score. 0 is the lowest score you can give. 
        
        Explain your reasoning in a step-by-step manner. Ensure your reasoning and conclusion are correct. 
        
        Avoid simply stating the correct answer at the outset.
        
        Question: {question} \n
        Fact: \n\n {documents} \n\n
        
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
        """,
        input_variables=['documents', 'question'],
    )
    
    # Combine the prompt with the structured LLM grader
    retrieval_grader = prompt | structured_llm_grader

    # Return the grader object
    return retrieval_grader    


def create_toxicity_checker(llm):
    """
    Function to create a toxicity checker object using a passed LLM model.
    
    Args:
        llm: The language model to be used for toxicity checking.
        
    Returns:
        Callable: A pipeline function that checks for toxicity based on the LLM.
    """
    
    # Define the class for toxicity check inside the function
    class PromtGuard(BaseModel):
        """Binary score for toxicity check on question."""
        score: str = Field(
            description="Is the question toxic, 'yes' or 'no'"
        )
    
    # Create the structured LLM toxicity checker using the passed LLM
    structured_llm_toxicity_checker = llm.with_structured_output(PromtGuard)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""You are a classifier that will score a text based upon supplied criteria. 
        Here is the criteria for scoring:
        
        (1) insults
        
        (2) threats
        
        (3) highly negative comments
        
        (4) any Personally Identifiable Information such as API Keys
        
        Score:
        
        A score of yes means that the text meets ANY of the criteria. 
        
        A score of no means that the text does not meet ALL of the criteria. 
        
        Here is the question: {question}
        
        Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question.
        If the answer contains repeated phrases, repetition, then return 'no'\n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["question"],
    )
    
    # Combine the prompt with the structured LLM toxicity checker
    toxicity_grader = prompt | structured_llm_toxicity_checker

    # Return the toxicity checker object
    return toxicity_grader


def grade_question_toxicity(state, toxicity_grader):
    """
    Grades the question for toxicity.
    
    Args:
        state (dict): The current graph state.
        
    Returns:
        str: 'good' if the question passes the toxicity check, 'bad' otherwise.
    """
    steps = state["steps"]
    steps.append("promt guard")
    score = toxicity_grader.invoke({"question": state["question"]})
    grade = getattr(score, 'score', None)
    
    if grade == "yes":
        return "bad" 
    else:
        return "good"


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

    url = state.get("url")
    if not url:
        return {"error": "No URL provided."}

    result = scraper_tool(url)

    if result.get("error"):
        return {"error": result["error"]}

    document = {
        "title": result.get("title"),
        "text": result.get("text"),
        "source": result.get("source"),
    }

    return {"documents": [document]}


def create_helpfulness_checker(llm):
    """
    Function to create a helpfulness checker object using a passed LLM model.
    
    Args:
        llm: The language model to be used for checking the helpfulness of answers.
        
    Returns:
        Callable: A pipeline function that checks if the student's answer is helpful.
    """
    
    # Define the class for helpfulness grading inside the function
    class GradeHelpfulness(BaseModel):
        """Binary score for Helpfulness check on answer."""
        score: str = Field(
            description="Is the answer helpfulness, 'yes' or 'no'"
        )
    
    # Create the structured LLM helpfulness checker using the passed LLM
    structured_llm_helpfulness_checker = llm.with_structured_output(GradeHelpfulness)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""You will be given a QUESTION and a STUDENT ANSWER. 
        Here is the grade criteria to follow:
        (1) Ensure the STUDENT ANSWER is concise and relevant to the QUESTION
        (2) Ensure the STUDENT ANSWER helps to answer the QUESTION
        Score:
        A score of yes means that the student's answer meets all of the criteria. This is the highest (best) score. 
        A score of no means that the student's answer does not meet all of the criteria. This is the lowest possible score you can give.
        Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 
        Avoid simply stating the correct answer at the outset.
        
        If the answer contains repeated phrases, repetition, then return 'no'\n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["generation", "question"],
    )
    
    # Combine the prompt with the structured LLM helpfulness checker
    helpfulness_grader = prompt | structured_llm_helpfulness_checker

    # Return the helpfulness checker object
    return helpfulness_grader





def create_hallucination_checker(llm):
    """
    Function to create a hallucination checker object using a passed LLM model.
    
    Args:
        llm: The language model to be used for checking hallucinations in the student's answer.
        
    Returns:
        Callable: A pipeline function that checks if the student's answer contains hallucinations.
    """
    
    # Define the class for hallucination grading inside the function
    class GradeHaliucinations(BaseModel):
        """Binary score for hallucinations check on answer."""
        score: str = Field(
            description="Answer contains hallucinations, 'yes' or 'no'"
        )
    
    # Create the structured LLM hallucination checker using the passed LLM
    structured_llm_haliucinations_checker = llm.with_structured_output(GradeHaliucinations)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""You are a teacher grading a quiz. 
        You will be given FACTS and a STUDENT ANSWER. 
        You are grading STUDENT ANSWER of source FACTS. Focus on correctness of the STUDENT ANSWER and detection of any hallucinations.
        Ensure that the STUDENT ANSWER meets the following criteria: 
        (1) it does not contain information outside of the FACTS
        (2) the STUDENT ANSWER should be fully grounded in and based upon information in the source documents
        Score:
        A score of yes means that the student's answer meets all of the criteria. This is the highest (best) score. 
        A score of no means that the student's answer does not meet all of the criteria. This is the lowest possible score you can give.
        Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 
        Avoid simply stating the correct answer at the outset.
        STUDENT ANSWER: {generation} \n
        Fact: \n\n {documents} \n\n
        
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
        """,
        input_variables=["generation", "documents"],
    )
    
    # Combine the prompt with the structured LLM hallucination checker
    hallucination_grader = prompt | structured_llm_haliucinations_checker

    # Return the hallucination checker object
    return hallucination_grader


def create_question_rewriter(llm):
    """
    Function to create a question rewriter object using a passed LLM model.
    
    Args:
        llm: The language model to be used for rewriting questions.
        
    Returns:
        Callable: A pipeline function that rewrites questions for optimized vector store retrieval.
    """
    
    # Define the prompt template for question rewriting
    re_write_prompt = PromptTemplate(
        template="""You are a question re-writer that converts an input question to a better version that is optimized for vector store retrieval.\n
        Your task is to enhance the question by clarifying the intent, removing any ambiguity, and including specific details to retrieve the most relevant information.\n
        I don't need explanations, only the enhanced question.
        Here is the initial question: \n\n {question}. Improved question with no preamble: \n """,
        input_variables=["question"],
    )
    
    # Combine the prompt with the LLM and output parser
    question_rewriter = re_write_prompt | llm | StrOutputParser()

    # Return the question rewriter object
    return question_rewriter


def transform_query(state, question_rewriter):
    """
    Transform the query to produce a better question.
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]
    steps = state["steps"]
    steps.append("question_transformation")

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    print(f" Transformed question:  {better_question}")
    return {"documents": documents, "question": better_question}




def format_google_results(google_results):
    formatted_documents = []
    
    # Loop through each organic result and create a Document for it
    for result in google_results['organic']:
        title = result.get('title', 'No title')
        link = result.get('link', 'No link')
        snippet = result.get('snippet', 'No summary available')

        # Create a Document object with similar metadata structure to WikipediaRetriever
        document = Document(
            metadata={
                'title': title,
                'summary': snippet,
                'source': link
            },
            page_content=snippet  # Using the snippet as the page content
        )
        
        formatted_documents.append(document)
    
    return formatted_documents


def QA_chain(llm):
    """
    Creates a question-answering chain using the provided language model.
    Args:
        llm: The language model to use for generating answers.
    Returns:
        An LLMChain configured with the question-answering prompt and the provided model.
    """
    # Define the prompt template
    prompt = PromptTemplate(
        template="""You are an assistant for question-answering tasks. 
        Use the following pieces of retrieved documents to answer the question. If you don't know the answer, just say that you don't know.
        Do not repeat yourself!
        Be informative and concise.
        Question: {question} 
        Documents: {documents} 
        Answer:
        """,
        input_variables=["question", "documents"],
    )

    
    rag_chain = prompt | llm | StrOutputParser()

    
    return rag_chain

def decide_scrape_or_search(state):
    """
    Determines the next step based on the scrape_article flag.

    Args:
        state (dict): The current graph state. Must contain a boolean key 'scrape_article'.

    Returns:
        str: 'scrape_article' if True, otherwise 'web_search'.
    """
    print("---DECIDE SCRAPE OR SEARCH---")
    scrape_article = state.get("scrape_article", False)

    if scrape_article:
        print("---DECISION: SCRAPE ARTICLE---")
        return "scrape_article"
    else:
        print("---DECISION: WEB SEARCH---")
        return "web_search"

def grade_generation_v_documents_and_question(state,hallucination_grader,answer_grader ):
    """
    Determines whether the generation is grounded in the document and answers the question.
    """
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    generation_count = state.get("generation_count")  # Use state.get to avoid KeyError
    print(f" generation number:  {generation_count}")
    
    # Grading hallucinations
    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = getattr(score, 'score', None)

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = getattr(score, 'score', None)
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        if generation_count > 1:
            print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, TRANSFORM QUERY---")
              # Reset count if it exceeds limit
            return "not useful"
        else:
            print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
             # Increment correctly here
            print(f" generation number after increment:  {state['generation_count']}")
            return "not supported"
    

def ask_question(state, retriever):
    """
    Initialize question
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Question
    """
    steps = state["steps"]
    question = state["question"]
    generations_count = state.get("generations_count", 0) 
    documents = retriever.invoke(question)
    
    steps.append("question_asked")
    return {"question": question, "steps": steps,"generation_count": generations_count}
        
        
def retrieve(state , retriever):
    """
    Retrieve documents
    Args:
        state (dict): The current graph state
        retriever: The retriever object
    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    steps = state["steps"]
    question = state["question"]
   
    documents = retriever.invoke(question)
    
    steps.append("retrieve_documents")
    return {"documents": documents, "question": question, "steps": steps}


def generate(state,QA_chain):
    """
    Generate answer
    """
    question = state["question"]
    documents = state["documents"]
    generation = QA_chain.invoke({"documents": documents, "question": question})
    steps = state["steps"]
    steps.append("generate_answer")
    generation_count = state["generation_count"]
    
    generation_count += 1
        
    return {
        "documents": documents,
        "question": question,
        "generation": generation,
        "steps": steps,
        "generation_count": generation_count  # Include generation_count in return
    }


def grade_documents(state, retrieval_grader):
    question = state["question"]
    documents = state["documents"]
    steps = state["steps"]
    steps.append("grade_document_retrieval")
    
    filtered_docs = []
    web_results_list = []
    search = "No"
    
    for d in documents:
        # Call the grading function
        score = retrieval_grader.invoke({"question": question, "documents": d.page_content})
        print(f"Grader output for document: {score}")  # Detailed debugging output
        
        # Extract the grade
        grade = getattr(score, 'binary_score', None)
        if grade and grade.lower() in ["yes", "true", "1"]:
            filtered_docs.append(d)
        elif len(filtered_docs) < 4:  
            search = "Yes"
            
    # Check the decision-making process
    print(f"Final decision - Perform web search: {search}")
    print(f"Filtered documents count: {len(filtered_docs)}")
    
    return {
        "documents": filtered_docs,
        "question": question,
        "search": search,
        "steps": steps,
    }

def web_search(state):
    question = state["question"]
    documents = state.get("documents")
    steps = state["steps"]
    steps.append("web_search")
    k = 4 - len(documents)
    good_wiki_splits = []
    good_exa_splits = []
    web_results_list = []

    wiki_results = WikipediaRetriever( lang = 'en',top_k_results = 1,doc_content_chars_max = 1000).invoke(question)
       
        
    if k<1:
        combined_documents = documents + wiki_results 
    else:
        web_results = GoogleSerperAPIWrapper(k = k).results(question)
        formatted_documents = format_google_results(web_results)
        for doc in formatted_documents:
            web_results_list.append(doc)
            
        
        combined_documents = documents + wiki_results + web_results_list

    return {"documents": combined_documents, "question": question, "steps": steps}

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.
    Args:
        state (dict): The current graph state
    Returns:
        str: Binary decision for next node to call
    """
    search = state["search"]
    if search == "Yes":
        return "search"
    else:
        return "generate"


