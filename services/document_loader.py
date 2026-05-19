from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
import os


class DocumentLoader:

    @staticmethod
    def get_loader(file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        loaders = {'.pdf': PyPDFLoader, '.txt': TextLoader, '.md': TextLoader}
        loader_class = loaders.get(ext, UnstructuredFileLoader)
        return loader_class(file_path)

    @staticmethod
    def load_document(file_path: str):
        return DocumentLoader.get_loader(file_path).load()

    @staticmethod
    def get_supported_extensions():
        return ['.pdf', '.txt', '.md']
