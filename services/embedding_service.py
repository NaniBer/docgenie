from langchain_cohere import CohereEmbeddings
from typing import List
from config import settings
from dotenv import load_dotenv
import os

# Load environment variables from parent directory (for when running from tests/ directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)


class EmbeddingService:
    """
    Embedding service using Cohere's embedding models.
    Converts text to vectors for similarity search and retrieval.
    """
    
    @staticmethod
    def get_embeddings(api_key: str = None):
        """
        Get Cohere embeddings instance.
        
        Args:
            api_key: Cohere API key (defaults to config)
        
        Returns:
            CohereEmbeddings instance
        """
        key = api_key or os.getenv("COHERE_API_KEY") or settings.COHERE_API_KEY
        
        if not key:
            raise ValueError("Cohere API key is required. Set COHERE_API_KEY in .env or pass as parameter.")
        
        return CohereEmbeddings(
            cohere_api_key=key,
            model="embed-english-v3.0"
        )
    
    @staticmethod
    def embed_documents(texts: List[str], api_key: str = None) -> List[List[float]]:
        """
        Embed multiple documents.
        
        Args:
            texts: List of text strings to embed
            api_key: Cohere API key (optional)
        
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        embeddings = EmbeddingService.get_embeddings(api_key)
        return embeddings.embed_documents(texts)
    
    @staticmethod
    def embed_query(text: str, api_key: str = None) -> List[float]:
        """
        Embed a single query string.
        
        Args:
            text: Query text to embed
            api_key: Cohere API key (optional)
        
        Returns:
            Embedding vector (list of floats)
        """
        embeddings = EmbeddingService.get_embeddings(api_key)
        return embeddings.embed_query(text)
    
    @staticmethod
    def get_embedding_dimension() -> int:
        """
        Get dimension of embedding vectors.
        
        Returns:
            Embedding dimension (for Cohere embed-english-v3.0, typically 1024)
        """
        # Cohere embed-english-v3.0 produces 1024-dimensional vectors
        return 1024
