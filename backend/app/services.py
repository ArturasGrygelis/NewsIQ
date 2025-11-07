import os
from typing import Dict, List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from exa_py import Exa
from langchain_community.document_loaders import NewsURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import datetime

class VectorStoreService:
    """Service for managing the Chroma vectorstore."""
    
    def __init__(self, persist_directory: str = "./docs/chroma/"):
        self.persist_directory = persist_directory
        self.embeddings = self._initialize_embeddings()
        self.vectorstore = self._initialize_vectorstore()
    
    def _initialize_embeddings(self):
        """Initialize HuggingFace embeddings."""
        model_name = "Alibaba-NLP/gte-base-en-v1.5"
        model_kwargs = {'device': 'cpu', "trust_remote_code": False}
        encode_kwargs = {'normalize_embeddings': True}
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    
    def _initialize_vectorstore(self):
        """Initialize or load Chroma vectorstore."""
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            os.makedirs(self.persist_directory, exist_ok=True)
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
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
