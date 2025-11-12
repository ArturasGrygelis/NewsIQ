import os
from typing import Dict, List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema.retriever import BaseRetriever
from langchain.schema import Document
from langchain_core.pydantic_v1 import Field
from exa_py import Exa
from langchain_community.document_loaders import NewsURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import datetime


# Helper function to add instructions to the query
def get_detailed_instruct(task_description: str, query: str) -> str:
    """Format a query with a task description to guide the model."""
    return f'Instruct: {task_description}\nQuery: {query}'


# Custom Retriever class with instruction-augmented queries
class InstructRetriever(BaseRetriever):
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
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vectorstore."""
        if documents:
            self.vectorstore.add_documents(documents)
            return True
        return False
    
    def search(self, query: str, k: int = 7, search_type: str = "mmr"):
        """Search the vectorstore."""
        retriever = self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
        return retriever.invoke(query)
    
    def clear(self):
        """Clear the vectorstore."""
        # Delete and recreate
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
        self.vectorstore = self._initialize_vectorstore()


class ArticleService:
    """Service for article operations."""
    
    def __init__(self):
        self.exa_api_key = os.getenv("EXA_API_KEY")
        self.exa_client = Exa(api_key=self.exa_api_key) if self.exa_api_key else None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=550,
            chunk_overlap=40
        )
    
    def search_articles(
        self,
        topic: str,
        website: Optional[str] = None,
        max_age_days: int = 7
    ) -> List[Dict]:
        """Search for articles using Exa."""
        if not self.exa_client:
            raise ValueError("EXA_API_KEY not configured")
        
        # Calculate start date
        start_date = (datetime.datetime.now() - datetime.timedelta(days=max_age_days)).strftime("%Y-%m-%d")
        
        # Build search query
        search_options = {
            "query": topic,
            "num_results": 5,
            "use_autoprompt": True,
            "start_published_date": start_date,
            "type": "neural"
        }
        
        if website:
            search_options["include_domains"] = [website]
        
        results = self.exa_client.search_and_contents(**search_options)
        
        articles = []
        for result in results.results:
            articles.append({
                "title": result.title,
                "url": result.url,
                "text": result.text if hasattr(result, 'text') else "",
                "published_date": result.published_date if hasattr(result, 'published_date') else None
            })
        
        return articles
    
    def load_article_from_url(self, url: str) -> Dict:
        """Load article content from URL."""
        try:
            loader = NewsURLLoader(urls=[url])
            documents = loader.load()
            
            if documents:
                doc = documents[0]
                return {
                    "title": doc.metadata.get("title", ""),
                    "url": url,
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", url)
                }
            else:
                raise ValueError("No content loaded from URL")
        except Exception as e:
            raise ValueError(f"Failed to load article: {str(e)}")
    
    def prepare_documents_for_vectorstore(self, article: Dict) -> List[Document]:
        """Split article into chunks and prepare for vectorstore."""
        text = article.get("text", "")
        
        if not text:
            return []
        
        # Create a document
        doc = Document(
            page_content=text,
            metadata={
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "source": article.get("source", article.get("url", "")),
                "summary": article.get("summary", "")
            }
        )
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        return chunks


# Initialize global services
vectorstore_service = VectorStoreService()
article_service = ArticleService()
