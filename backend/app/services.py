import os
from typing import List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import Field, BaseModel


# Helper function to add instructions to the query
def get_detailed_instruct(task_description: str, query: str) -> str:
    """Format a query with a task description to guide the model."""
    return f'Instruct: {task_description}\nQuery: {query}'


# Custom Retriever class with instruction-augmented queries
class InstructRetriever(BaseRetriever, BaseModel):
    """Retriever that adds instruction to queries before retrieval."""
    
    base_retriever: BaseRetriever = Field(...)
    task_description: str = Field(...)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Add instruction to the query before passing to the base retriever."""
        formatted_query = get_detailed_instruct(self.task_description, query)
        return self.base_retriever.invoke(formatted_query)


class VectorStoreService:
    """Service for managing the Chroma vectorstore."""
    
    def __init__(self, persist_directory: str = "./app/chroma"):
        self.persist_directory = persist_directory
        self.embeddings = self._initialize_embeddings()
        self.vectorstore = self._initialize_vectorstore()
        self.retriever = None
        self.instruct_retriever = None
    
    def _initialize_embeddings(self):
        """Initialize HuggingFace embeddings with multilingual model."""
        model_name = "intfloat/multilingual-e5-large-instruct"
        model_kwargs = {'device': 'cpu', "trust_remote_code": False}
        encode_kwargs = {'normalize_embeddings': True}
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    
    def _initialize_vectorstore(self):
        """Initialize or load Chroma vectorstore."""
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    def get_vectorstore(self):
        """Get the vectorstore instance."""
        return self.vectorstore
    
    def get_retriever(self, search_type: str = "similarity", k: int = 15):
        """Get a standard retriever."""
        if self.retriever is None or self.retriever._search_kwargs.get("k") != k:
            self.retriever = self.vectorstore.as_retriever(
                search_type=search_type,
                search_kwargs={"k": k}
            )
        return self.retriever
    
    def get_instruct_retriever(self, search_type: str = "similarity", k: int = 15, 
                              task_description: str = "Retrieve most relevant documents to the query"):
        """Get an instruction-based retriever."""
        base_retriever = self.get_retriever(search_type=search_type, k=k)
        
        self.instruct_retriever = InstructRetriever(
            base_retriever=base_retriever,
            task_description=task_description
        )
        return self.instruct_retriever


# Initialize global service
vectorstore_service = VectorStoreService()
