from pydantic_settings import BaseSettings
from typing import Optional, Literal

class Settings(BaseSettings):
    # Mode: "cloud" (external APIs) or "self-hosted" (local models)
    MODE: Literal["cloud", "self-hosted"] = "self-hosted"

    # Embedding Model Provider (for cloud mode)
    COHERE_API_KEY: Optional[str] = None

    # LLM Provider
    LLM_PROVIDER: str = "openrouter"

    # Google AI (for cloud mode)
    GOOGLE_API_KEY: Optional[str] = None

    # OpenRouter (for cloud mode)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openrouter/free"

    # Ollama (for self-hosted mode)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    COLLECTION_NAME: str = "documents"

    # Chunking Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Retrieval Settings
    DEFAULT_K: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
