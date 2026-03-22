from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from typing import List, Optional, Dict, Any
from config import settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ChatService:
    """
    Chat service using RetrievalQA with Google AI Studio for answer generation.
    Integrates Cohere embeddings (query) + ChromaDB (retrieval) + Google AI (generation).
    """
    
    @staticmethod
    def get_google_llm(api_key: str = None):
        """
        Get Google AI LLM instance for answer generation.
        
        Args:
            api_key: Google AI Studio API key (defaults to env)
        
        Returns:
            ChatGoogleGenerativeAI instance
        """
        key = api_key or os.getenv("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
        
        if not key:
            raise ValueError("Google AI API key is required. Set GOOGLE_API_KEY in .env or pass as parameter.")
        
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
    
    @staticmethod
    def get_retriever(customer_id: str, api_key: str = None):
        """
        Get retriever from ChromaDB for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
            api_key: Cohere API key (optional)
        
        Returns:
            ChromaDB retriever
        """
        from services.vector_store import VectorStore
        vector_store = VectorStore.get_collection(customer_id, api_key)
        return vector_store.as_retriever(search_kwargs={"k": 4})
    
    @staticmethod
    def get_qa_chain(customer_id: str, google_api_key: str = None, cohere_api_key: str = None):
        """
        Get RetrievalQA chain for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
            google_api_key: Google AI Studio API key (optional)
            cohere_api_key: Cohere API key (optional)
        
        Returns:
            RetrievalQA chain instance
        """
        llm = ChatService.get_google_llm(google_api_key)
        retriever = ChatService.get_retriever(customer_id, cohere_api_key)
        
        # Create RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type="stuff"
        )
        
        return qa_chain
    
    @staticmethod
    async def query(
        customer_id: str,
        question: str,
        google_api_key: str = None,
        cohere_api_key: str = None
    ) -> Dict[str, Any]:
        """
        Query the chatbot and get an answer with sources.
        
        Args:
            customer_id: Unique identifier for the customer
            question: User's question
            google_api_key: Google AI Studio API key (optional)
            cohere_api_key: Cohere API key (optional)
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Get or create QA chain
            qa_chain = ChatService.get_qa_chain(customer_id, google_api_key, cohere_api_key)
            
            # Invoke the chain
            result = await qa_chain.ainvoke({
                "query": question
            })
            
            # Prepare response
            response = {
                "answer": result["result"],
                "source_documents": result.get("source_documents", []),
                "customer_id": customer_id
            }
            
            # Extract sources
            if "source_documents" in result and result["source_documents"]:
                sources = []
                for doc in result["source_documents"]:
                    source = {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "Unknown")
                    }
                    sources.append(source)
                response["sources"] = sources
            
            return response
            
        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")
    
    @staticmethod
    def query_sync(
        customer_id: str,
        question: str,
        google_api_key: str = None,
        cohere_api_key: str = None
    ) -> Dict[str, Any]:
        """
        Synchronous version of query method.
        
        Args:
            customer_id: Unique identifier for the customer
            question: User's question
            google_api_key: Google AI Studio API key (optional)
            cohere_api_key: Cohere API key (optional)
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        import asyncio
        return asyncio.run(ChatService.query(customer_id, question, google_api_key, cohere_api_key))
