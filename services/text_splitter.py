from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Dict
from config import settings
import re

class TextSplitter:
    """
    Text splitter service using LangChain's RecursiveCharacterTextSplitter.
    Splits documents into smaller chunks for embedding and vector storage.
    """
    
    @staticmethod
    def get_splitter(
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        """
        Get a RecursiveCharacterTextSplitter instance.
        
        Args:
            chunk_size: Maximum size of chunks in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to split on (in order of priority)
        
        Returns:
            RecursiveCharacterTextSplitter instance
        """
        if separators is None:
            # Default separators for recursive splitting
            separators = ["\n\n", "\n", " ", ""]
        
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
            length_function=len,
            separators=separators
        )
    
    @staticmethod
    def split_documents(documents: List[Document], **kwargs) -> List[Document]:
        """
        Split a list of documents into chunks.
        
        Args:
            documents: List of LangChain Document objects
            **kwargs: Additional arguments for the splitter
        
        Returns:
            List of split Document objects
        """
        splitter = TextSplitter.get_splitter(**kwargs)
        return splitter.split_documents(documents)
    
    @staticmethod
    def detect_section(content: str) -> str:
        """
        Detect the section of a document based on content.
        
        Args:
            content: Document content
        
        Returns:
            Section name or "General"
        """
        # Check for common section headers
        section_patterns = [
            (r'Products and Services', 'Products'),
            (r'Company Culture and Values', 'Values'),
            (r'Our Mission', 'Mission'),
            (r'Intelligent Chatbot', 'Chatbot'),
            (r'Data Analytics', 'Analytics'),
            (r'Cloud Infrastructure', 'Infrastructure'),
            (r'Achievements', 'Achievements'),
            (r'Contact Information', 'Contact'),
        ]
        
        for pattern, section_name in section_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return section_name
        
        return "General"
    
    @staticmethod
    def split_documents_with_metadata(documents: List[Document], **kwargs) -> List[Document]:
        """
        Split documents into chunks with enhanced metadata including section detection.
        
        Args:
            documents: List of LangChain Document objects
            **kwargs: Additional arguments for the splitter
        
        Returns:
            List of split Document objects with section metadata
        """
        splitter = TextSplitter.get_splitter(**kwargs)
        chunks = []
        
        for doc in documents:
            # Split into chunks
            doc_chunks = splitter.split_documents([doc])
            
            # Detect section for each chunk
            for chunk in doc_chunks:
                section = TextSplitter.detect_section(chunk.page_content)
                
                # Update metadata with section information
                chunk.metadata = {
                    **chunk.metadata,
                    "section": section
                }
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def split_text(text: str, **kwargs) -> List[str]:
        """
        Split text directly into chunks.
        
        Args:
            text: Text to split
            **kwargs: Additional arguments for the splitter
        
        Returns:
            List of text chunks
        """
        splitter = TextSplitter.get_splitter(**kwargs)
        return splitter.split_text(text)
    
    @staticmethod
    def print_chunks(chunks: List[Document]):
        """
        Print chunk information for debugging.
        
        Args:
            chunks: List of chunked Document objects
        """
        print(f"\nTotal chunks: {len(chunks)}")
        print("=" * 50)
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"Length: {len(chunk.page_content)} characters")
            print(f"Content preview: {chunk.page_content[:100]}...")
            if chunk.metadata:
                print(f"Metadata: {chunk.metadata}")
