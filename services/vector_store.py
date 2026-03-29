from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_core.documents import Document
from typing import List, Optional
from config import settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class VectorStore:
    """
    Vector store service using ChromaDB with Cohere embeddings.
    Provides multi-tenancy with isolated collections per customer.
    """
    
    @staticmethod
    def get_collection_name(customer_id: str) -> str:
        """
        Get collection name for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
        
        Returns:
            Collection name for ChromaDB
        """
        return f"customer_{customer_id}"
    
    @staticmethod
    def get_embeddings(api_key: str = None):
        """
        Get Cohere embeddings instance for vector store.
        
        Args:
            api_key: Cohere API key (defaults to env)
        
        Returns:
            CohereEmbeddings instance
        """
        key = api_key or os.getenv("COHERE_API_KEY")
        if not key:
            raise ValueError("Cohere API key is required.")
        
        return CohereEmbeddings(
            cohere_api_key=key,
            model="embed-english-v3.0"
        )
    
    @staticmethod
    def create_collection(customer_id: str, api_key: str = None):
        """
        Create a new collection for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
            api_key: Cohere API key (optional)
        
        Returns:
            Chroma vector store instance
        """
        collection_name = VectorStore.get_collection_name(customer_id)
        embeddings = VectorStore.get_embeddings(api_key)
        
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(persist_directory, exist_ok=True)
        
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
    
    @staticmethod
    def get_collection(customer_id: str, api_key: str = None):
        """
        Get existing collection for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
            api_key: Cohere API key (optional)
        
        Returns:
            Chroma vector store instance
        """
        collection_name = VectorStore.get_collection_name(customer_id)
        embeddings = VectorStore.get_embeddings(api_key)
        
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
    
    @staticmethod
    def add_documents(customer_id: str, documents: List[Document], api_key: str = None):
        """
        Add documents to a customer's vector store.
        
        Args:
            customer_id: Unique identifier for the customer
            documents: List of LangChain Document objects to add
            api_key: Cohere API key (optional)
        
        Returns:
            Number of documents added
        """
        vector_store = VectorStore.get_collection(customer_id, api_key)
        
        ids = vector_store.add_documents(documents)
        
        # Note: ChromaDB automatically persists when persist_directory is set
        # No need to call persist() explicitly

        # Force persistence by accessing the _collection attribute
        try:
            _ = vector_store._collection
        except Exception:
            pass

        return len(ids)
    
    @staticmethod
    def similarity_search(
        customer_id: str,
        query: str,
        k: int = 4,
        api_key: str = None
    ) -> List[Document]:
        """
        Search for similar documents based on query.
        
        Args:
            customer_id: Unique identifier for the customer
            query: Search query string
            k: Number of results to return
            api_key: Cohere API key (optional)
        
        Returns:
            List of similar Document objects
        """
        vector_store = VectorStore.get_collection(customer_id, api_key)
        
        results = vector_store.similarity_search(query, k=k)
        
        return results
    
    @staticmethod
    def similarity_search_with_score(
        customer_id: str,
        query: str,
        k: int = 4,
        api_key: str = None
    ) -> List[tuple]:
        """
        Search for similar documents with similarity scores.
        
        Args:
            customer_id: Unique identifier for the customer
            query: Search query string
            k: Number of results to return
            api_key: Cohere API key (optional)
        
        Returns:
            List of (Document, score) tuples
        """
        vector_store = VectorStore.get_collection(customer_id, api_key)
        
        results = vector_store.similarity_search_with_score(query, k=k)
        
        return results
    
    @staticmethod
    def delete_collection(customer_id: str, api_key: str = None):
        """
        Delete a customer's entire collection.
        
        Args:
            customer_id: Unique identifier for the customer
            api_key: Cohere API key (optional)
        """
        collection_name = VectorStore.get_collection_name(customer_id)
        embeddings = VectorStore.get_embeddings(api_key)
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
        # Create a temporary store to delete the collection
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        # Delete the collection
        try:
            vector_store.delete_collection()
        except Exception:
            # If delete_collection doesn't exist, try alternative method
            import chromadb
            client = chromadb.PersistentClient(path=persist_directory)
            try:
                client.delete_collection(name=collection_name)
            except Exception:
                pass  # Collection might not exist
    
    @staticmethod
    def list_collections(api_key: str = None) -> List[str]:
        """
        List all collections in the vector store.
        
        Args:
            api_key: Cohere API key (optional)
        
        Returns:
            List of collection names
        """
        import chromadb
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        collections = client.list_collections()
        return [col.name for col in collections]
