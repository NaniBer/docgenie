from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from config import settings


class TextSplitter:

    @staticmethod
    def get_splitter(
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]

        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
            length_function=len,
            separators=separators
        )

    @staticmethod
    def split_documents(documents: List[Document], **kwargs) -> List[Document]:
        splitter = TextSplitter.get_splitter(**kwargs)
        return splitter.split_documents(documents)
