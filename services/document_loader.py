from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from typing import List
import os

class DocumentLoader:
    """
    Document loader service using LangChain to load various document formats.
    Supports PDF, TXT, MD, and DOCX files.
    """
    
    @staticmethod
    def get_loader(file_path: str, file_content: bytes = None):
        """
        Get the appropriate LangChain loader based on file extension.
        
        Args:
            file_path: Path to the file (or filename for uploaded files)
            file_content: File content as bytes (optional, for in-memory files)
        
        Returns:
            LangChain document loader instance
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        loader_map = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.md': TextLoader,  # TextLoader works well for markdown
        }
        
        loader_class = loader_map.get(file_extension)
        
        if loader_class:
            return loader_class(file_path)
        else:
            # For unsupported formats, use UnstructuredFileLoader
            return UnstructuredFileLoader(file_path)
    
    @staticmethod
    def load_document(file_path: str):
        """
        Load a document and return the pages/chunks.
        
        Args:
            file_path: Path to the document file
        
        Returns:
            List of Document objects from LangChain
        """
        loader = DocumentLoader.get_loader(file_path)
        documents = loader.load()
        return documents
    
    @staticmethod
    def load_document_from_bytes(file_content: bytes, filename: str, temp_dir: str = "./temp_uploads"):
        """
        Load a document from bytes (useful for API uploads).
        Saves the file temporarily, loads it, then cleans up.
        
        Args:
            file_content: File content as bytes
            filename: Name of the file
            temp_dir: Directory to temporarily store files
        
        Returns:
            List of Document objects from LangChain
        """
        # Create temp directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save file temporarily
        temp_file_path = os.path.join(temp_dir, filename)
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        try:
            # Load the document
            documents = DocumentLoader.load_document(temp_file_path)
            return documents
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    @staticmethod
    def get_supported_extensions():
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions (e.g., ['.pdf', '.txt', '.md'])
        """
        return ['.pdf', '.txt', '.md']
