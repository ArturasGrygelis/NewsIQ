def retrieval_grader(llm):
    """
    Function to create a grader object using a passed LLM model.
    
    Args:
        llm: The language model to be used for grading.
        
    Returns:
        Callable: A pipeline function that grades relevance based on the LLM.
    """
    
    

    # Define the prompt template
    prompt = PromptTemplate(
        template="""You are a professional in understanding documents context.
        You have to identify is the retrieved document: {document} related or could be helpfull to user given question:  {question} .
        If document is related to the question , return 'yes', if no , return 'no'. 
        return answer as yes or no and no preamble or explanation.
        
        """,
        input_variables=['document', 'question'],
    )
    
    # Combine the prompt with the structured LLM grader
    retrieval_grader = prompt | llm | StrOutputParser()

    # Return the grader object
    return retrieval_grader  



def create_question_answerer(llm):
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
        You have to answer to the question: {question} only using these documents {documents}
        Do not repeat yourself!
        Be informative and concise.
        Use only given documents!
        """,
        input_variables=["question", "documents"],
    )

    
    rag_chain = prompt | llm | StrOutputParser()

    
    return rag_chain


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
        No preamble or explanation, only the enhanced question.
        Here is the initial question: \n\n {question}.
        """,
        input_variables=["question"],
    )
    
    # Combine the prompt with the LLM and output parser
    question_rewriter = re_write_prompt | llm | StrOutputParser()

    # Return the question rewriter object
    return question_rewriter


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
        You are professional fact checker,  you need to check the answer: {answer} is generated using related documents {documents}, or was there made any factual mistakes, hallucinations.
        If there are mistakes , return 'yes', if no mistakes, return 'no'
        return answer as yes or no and no preamble or explanation.
        """,
        input_variables=["article", "answer"],
    )
    
    # Combine the prompt with the structured LLM hallucination checker
    hallucination_grader = prompt | llm |  StrOutputParser()

    # Return the hallucination checker object
    return hallucination_grader