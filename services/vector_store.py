from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List
from config import settings
import os


class VectorStore:

    @staticmethod
    def get_embeddings():
        if settings.MODE == "self-hosted":
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        key = os.getenv("COHERE_API_KEY")
        if not key:
            raise ValueError("Cohere API key required for cloud mode. Set COHERE_API_KEY in .env")
        return CohereEmbeddings(cohere_api_key=key, model="embed-english-v3.0")

    @staticmethod
    def get_collection():
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        return Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=VectorStore.get_embeddings(),
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )

    @staticmethod
    def add_documents(documents: List[Document]) -> int:
        ids = VectorStore.get_collection().add_documents(documents)
        return len(ids)

    @staticmethod
    def similarity_search(query: str, k: int = 4) -> List[Document]:
        return VectorStore.get_collection().similarity_search(query, k=k)

    @staticmethod
    def similarity_search_with_score(query: str, k: int = 4) -> List[tuple]:
        return VectorStore.get_collection().similarity_search_with_score(query, k=k)

    @staticmethod
    def delete_collection():
        import chromadb
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        try:
            client.delete_collection(name=settings.COLLECTION_NAME)
        except Exception:
            pass
