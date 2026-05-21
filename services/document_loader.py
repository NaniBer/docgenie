from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
import os


class DocumentLoader:

    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md'}

    _loaders = {
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.md': TextLoader,
    }
    @staticmethod
    def get_loader(file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in DocumentLoader.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(DocumentLoader.SUPPORTED_EXTENSIONS))}")
        loader_class = DocumentLoader._loaders[ext]
        return loader_class(file_path)

    @staticmethod
    def load_document(file_path: str):
        return DocumentLoader.get_loader(file_path).load()

    @staticmethod
    def get_supported_extensions():
        return sorted(DocumentLoader.SUPPORTED_EXTENSIONS)
