# RAG-Based Document Assistant

A lightweight AI-powered document assistant that allows users to upload documents (text/PDF) and ask questions based on the uploaded content.

## Architecture Overview

### Components
1. **Backend (FastAPI)**
   - Document upload and processing
   - Text extraction from PDF/TXT files
   - Vector embeddings generation
   - Semantic search using ChromaDB
   - LLM-based answer generation

2. **Frontend (HTML/CSS/JS)**
   - Document upload interface
   - Question input form
   - Answer display with source context

3. **Vector Database (ChromaDB)**
   - Stores document embeddings
   - Enables semantic search

### Tech Stack
- **Backend**: Python 3.9+, FastAPI, LangChain, ChromaDB
- **LLM**: OpenAI GPT (configurable)
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- OpenAI API key (or other LLM provider)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-document-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
uvicorn main:app --reload
```

6. Open your browser and navigate to:
```
http://localhost:8000
```

## API Documentation

### Endpoints

#### 1. Upload Document
- **URL**: `/api/upload`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Body**: `file` (PDF or TXT)
- **Response**: 
```json
{
  "message": "Document uploaded successfully",
  "filename": "example.pdf",
  "chunks": 15
}
```

#### 2. Ask Question
- **URL**: `/api/query`
- **Method**: POST
- **Content-Type**: application/json
- **Body**:
```json
{
  "question": "What is the main topic of the document?"
}
```
- **Response**:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "content": "relevant text chunk",
      "metadata": {"source": "example.pdf", "page": 1}
    }
  ]
}
```

#### 3. List Documents
- **URL**: `/api/documents`
- **Method**: GET
- **Response**:
```json
{
  "documents": ["doc1.pdf", "doc2.txt"]
}
```

#### 4. Clear Database
- **URL**: `/api/clear`
- **Method**: DELETE
- **Response**:
```json
{
  "message": "All documents cleared"
}
```

## Design Decisions

1. **ChromaDB**: Chosen for its simplicity and no external dependencies (runs in-memory or persists locally)
2. **FastAPI**: Modern, fast, with automatic API documentation
3. **LangChain**: Simplifies RAG pipeline implementation
4. **Chunking Strategy**: 1000 characters with 200 character overlap for context preservation
5. **Embedding Model**: OpenAI text-embedding-ada-002 (cost-effective and performant)

## Assumptions

1. Documents are in English
2. PDF files are text-based (not scanned images)
3. Single-user application (no authentication)
4. Documents stored in vector DB persist between sessions
5. Maximum file size: 10MB per document

## Future Enhancements

- [ ] Support for more file formats (DOCX, CSV, etc.)
- [ ] Multi-user support with authentication
- [ ] Document management (delete individual documents)
- [ ] Conversation history
- [ ] Advanced chunking strategies
- [ ] Support for local LLMs (Ollama, LlamaCPP)
- [ ] Streaming responses

## License

MIT
