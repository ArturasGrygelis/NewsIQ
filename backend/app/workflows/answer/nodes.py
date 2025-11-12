from .workers import (create_question_answerer, retrieval_grader, create_question_rewriter, create_hallucination_checker)


def initialize_workflow(state):
    """
    Initialize the question and steps for the graph state.
    
    Args:
        state (dict): The current graph state.
        
    Returns:
        dict: Updated state with steps and question initialized.
    """
    # Get or initialize question and steps
    question = state.get("question", "")
    steps = state.get("steps", [])
    
    # Add initialization step
    steps.append("Graph Initialization")
    
    return {
        "question": question,
        "steps": steps,
    }


def grade_documents(state,llm, retrieval_grader):
    question = state.get("question","")
    documents = state["documents"]
    steps = state["steps"]
    steps.append("grade_document_retrieval")
    
    filtered_docs = []
    web_results_list = []
    search = "No"
    retrieval_grader = retrieval_grader(llm)
    
    for d in documents:
        # Call the grading function
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        print(f"Grader output for document: {score}")  # Detailed debugging output
        
        
        if score.lower() in ["yes", "true", "1"]:
            filtered_docs.append(d)
            
    # ✅ Fixed f-string syntax
    print(f"Filtered documents count: {len(filtered_docs)} from total document amount {len(documents)}")
    
    return {
        "selected_documents": filtered_docs,
        "question": question,
        "steps": steps,
    }


def grade_answer_v_documents(state,llm,create_hallucination_checker ):
    """
    Determines whether the generation is grounded in the document and answers the question.
    """
    print("---CHECK HALLUCINATIONS---")
    answer = state.get("answer","")
    documents = state['selected_documents']
    steps = state["steps"]
    
    
    steps.append("Check for hallucinations")
    hallucination_grader = create_hallucination_checker(llm)
    # Grading hallucinations
    score = hallucination_grader.invoke(
        {"answer": answer, "documents": documents}
    )
    

    # Check hallucination
    if score == "yes":
        print("---Found hallucinations---")
        return "Hallucinations"
        
    if score == "no":
        print("---no hallucinations---")
        return "No hallucinations"
    


def transform_query(state,llm, create_question_rewriter):
    """
    Transform the query to produce a better question.
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    
    steps = state["steps"]
    steps.append("question_transformation")

    # Re-write question
    question_rewriter =  create_question_rewriter(llm)
    updated_question = question_rewriter.invoke({"question": question})
    print(f" Transformed question:  {updated_question}")
    return { "question": updated_question} 



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



def question_answering(state,llm,create_question_answerer):
    """
    Generate answer
    """
    question = state.get("question","")
    documents = state["documents"]
    question_answerer =  create_question_answerer(llm)
    answer = question_answerer.invoke({"documents": documents, "question": question})
    steps = state["steps"]
    steps.append("generate_answer")
    
        
    return {
        "documents": documents,
        "question": question,
        "answer": answer,
        "steps": steps,
    }


def related_documents_count(state):
    selected_documents = state.get("selected_documents")
    if len(selected_documents) > 0 :
        return  "Are related documents"
    else:
        return  "No related documents"