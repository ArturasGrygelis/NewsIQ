def create_article_summarizer(llm):
    """
    Creates a structured-output summarizer that summarizes an article 
    and extracts main topics in a single call.

    Args:
        llm: The language model used for summarization and topic extraction.

    Returns:
        Callable: A summarization pipeline that outputs structured data with 'summary' and 'topics'.
    """

    # Define structured output schema
    class ArticleSummary(BaseModel):
        """Structured summary and topics extracted from an article."""
        summary: str = Field(
            description="A clear and concise summary of the given article."
        )
        topics: list[str] = Field(
            description="A list of 3–10 main topics or keywords that capture the article's content."
        )

    # Create the structured-output LLM
    structured_summarizer = llm.with_structured_output(ArticleSummary)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are a professional content summarizer.
        Read the article provided below and:
        1. Write a concise and factual summary (1-3 sentences).
        2. Identify and list the main topics, entities, or concepts mentioned in the article.

        Return your result as a JSON object with keys 'summary' and 'topics'.
        
        ARTICLE:
        {article}
        """,
        input_variables=["article"],
    )

    # Combine prompt and model into a reusable summarization pipeline
    summarizer = prompt | structured_summarizer

    # Return the ready-to-use summarizer pipeline
    return summarizer



def create_article_selector(llm):
    """
    Creates a document selector based on topic relevance.
    
    Args:
        llm: The language model to be used for selecting the most relevant document.
        
    Returns:
        Callable: A pipeline function that selects the most relevant document based on the topic.
    """
    
    class SelectedDocument(BaseModel):
        """Structured output for document selection."""
        selected_document_index: int = Field(
            description="Index of the most relevant document in the provided list (0-based indexing)"
        )
        reasoning: str = Field(
            description="Brief explanation of why this article was selected",
            default=""
        )
    
    # ✅ Use function_calling method for more reliable structured output
    structured_metadata_extractor = llm.with_structured_output(
        SelectedDocument,
        method="function_calling"
    )

    prompt = PromptTemplate(
        template="""You are a professional article selector tasked with finding the most relevant article.

**Topic:** {topic}

**Available Articles (by index):**
{articles}

**Task:**
Analyze the topic and select the index (0-based) of the article that best matches the topic.

**Instructions:**
1. Carefully read the topic: {topic}
2. Review all article summaries in the list
3. Identify which article is most relevant to the topic
4. Return the 0-based index of that article
5. Provide brief reasoning for your selection
6Select the article that best matches the topic.
If several are equally relevant, prefer the one that would be most engaging or impactful for readers and society.

**Important:**
- You MUST return a valid index number
- Index must be between 0 and {max_index}
- If no article is highly relevant, select the closest match
- Always provide the selected_document_index field

Select the most relevant article now:
""",
        input_variables=["articles", "topic", "max_index"],
    )
    
    metadata_extractor = prompt | structured_metadata_extractor
    return metadata_extractor