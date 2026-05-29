"""
Vector Store Service
Manages ChromaDB for document embeddings using HuggingFace (free, no API key needed)
"""
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()


class VectorStoreManager:
   

    def __init__(self):
  
        print("Loading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        print("Embedding model ready")

        self.persist_directory = "chroma_db"

        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_documents(self, documents: List[Document]):
       
        self.vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
       
        return self.vector_store.similarity_search(query, k=k)

    def list_documents(self) -> List[str]:
        
        try:
            collection = self.vector_store._collection
            results = collection.get()

            if not results or not results.get('metadatas'):
                return []

            sources = set()
            for metadata in results['metadatas']:
                if metadata and 'source' in metadata:
                    sources.add(metadata['source'])

            return sorted(list(sources))
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def clear(self):
   
        try:
            self.vector_store._client.delete_collection("documents")

            self.vector_store = Chroma(
                collection_name="documents",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            raise

    def get_retriever(self, k: int = 4):
    
        return self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )
