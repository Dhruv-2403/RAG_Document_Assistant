
from pathlib import Path
from typing import List
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()


class DocumentProcessor:

    
    def __init__(self):
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text(self, file_path: Path) -> str:
       
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
    
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        if not text.strip():
            raise Exception("No text could be extracted from PDF")
        
        return text
    
    def _extract_from_txt(self, file_path: Path) -> str:

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
          
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        
        if not text.strip():
            raise Exception("Text file is empty")
        
        return text
    
    def chunk_text(self, text: str, source: str) -> List[Document]:
        
     
        chunks = self.text_splitter.split_text(text)
        

        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "source": source,
                    "chunk_id": i
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        return documents
