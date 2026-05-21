from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from typing import Dict, Optional
from config import settings


class ChatService:

    @staticmethod
    def get_llm():
        if settings.MODE == "self-hosted":
            return ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.7
            )
        return ChatService._get_cloud_llm()

    @staticmethod
    def _get_cloud_llm():
        provider = settings.LLM_PROVIDER
        if provider == "google":
            return ChatService._get_google_llm()
        elif provider == "openrouter":
            return ChatService._get_openrouter_llm()
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

    @staticmethod
    def _get_openrouter_llm():
        key = settings.OPENROUTER_API_KEY
        if not key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY in .env")
        return ChatOpenAI(
            model=settings.OPENROUTER_MODEL,
            openai_api_key=key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "DocGenie"
            }
        )

    @staticmethod
    def _get_google_llm(api_key: str = None):
        key = api_key or settings.GOOGLE_API_KEY
        if not key:
            raise ValueError("Google AI API key required. Set GOOGLE_API_KEY in .env")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=key,
            temperature=0.7,
            convert_system_message_to_human=True
        )

    @staticmethod
    async def query(question: str, k: int = None) -> Dict[str, any]:
        import time
        start_time = time.time()

        try:
            llm = ChatService.get_llm()

            from services.vector_store import VectorStore
            k_value = k or settings.DEFAULT_K
            docs = VectorStore.similarity_search(question, k_value)

            context = "\n\n".join([doc.page_content for doc in docs])

            from langchain_core.prompts import PromptTemplate
            prompt = PromptTemplate.from_template(
                """Use the following pieces of context to answer the question at the end.
                If you don't know the answer, just say that you don't know, don't try to make up an answer.

                Context:
                {context}

                Question:
                {question}

                Answer:"""
            )

            from langchain_core.output_parsers import StrOutputParser
            chain = prompt | llm | StrOutputParser()
            answer = await chain.ainvoke({"context": context, "question": question})

            sources = []
            for doc in docs:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "Unknown")
                })

            return {
                "answer": answer,
                "sources": sources,
                "query_time_ms": (time.time() - start_time) * 1000
            }

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")
