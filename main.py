
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path

from services.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv

load_dotenv()

# Verify Groq API key is configured
GROQ_KEY = os.getenv("GROQ_API_KEY", "").strip()
if not GROQ_KEY or GROQ_KEY == "your_groq_api_key_here":
    raise ValueError(
        "CRITICAL: GROQ_API_KEY environment variable is not configured.\n"
        "Please set a valid Groq API key in your .env file."
    )

print("Running in production with Groq API (llama-3.3-70b-versatile)")
from services.vector_store import VectorStoreManager
from services.qa_chain_groq import QAChainGroq as QAChain

# Initialize FastAPI app
app = FastAPI(
    title="RAG Document Assistant",
    description="AI-powered document Q&A system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

doc_processor = DocumentProcessor()
vector_store = VectorStoreManager()
qa_chain = QAChain(vector_store)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

#Pydantic Models
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int


class DocumentListResponse(BaseModel):
    documents: List[str]


# API Endpoints
@app.get("/")
async def root():
  
    return FileResponse("static/index.html")


@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    
    # Validate file type
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )
    
    # Validate file size (10MB max)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )
    
    # Save file temporarily
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    try:
        # Process document
        text = doc_processor.extract_text(file_path)
        chunks = doc_processor.chunk_text(text, file.filename)
        
        # Store in vector database
        vector_store.add_documents(chunks)
        
        return UploadResponse(
            message="Document uploaded and processed successfully",
            filename=file.filename,
            chunks=len(chunks)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        # Get answer from QA chain
        result = qa_chain.ask(request.question)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/api/documents", response_model=DocumentListResponse)
async def list_documents():
  
    try:
        documents = vector_store.list_documents()
        return DocumentListResponse(documents=documents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )


@app.delete("/api/clear")
async def clear_database():
  
    try:
        vector_store.clear()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing database: {str(e)}"
        )



# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
