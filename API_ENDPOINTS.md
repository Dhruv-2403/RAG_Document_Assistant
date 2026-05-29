# Developer API & Integrations Guide

This guide details all external/internal API services and REST endpoints implemented in the RAG Document Assistant application, including request/response specifications and their internal mechanics.

---

## 1. REST API Endpoints (FastAPI Backend)

All routes are hosted on our local server instance (by default at `http://localhost:8000`).

### Serving Frontend

#### Serve HTML Page
* **URL**: `/`
* **Method**: `GET`
* **Purpose**: Serves the minimalist dashboard (`static/index.html`).
* **Response**: `200 OK` (HTML file stream).

---

### Document Management Routes

#### 1. Upload Document
* **URL**: `/api/upload`
* **Method**: `POST`
* **Headers**: `Content-Type: multipart/form-data`
* **Payload**: Form data with a single key `file` holding a `.txt` or `.pdf` binary file stream.
* **Under the Hood**:
  1. Validates file extension constraints (PDF or plain text only).
  2. Saves the uploaded file temporarily inside the `/uploads` directory.
  3. Invokes **`DocumentProcessor`** to parse raw text streams (utilizes `PyPDF2` for PDF formats).
  4. Splice raw text into context-rich blocks using LangChain's **`RecursiveCharacterTextSplitter`** (1000 character length, 200 character overlap).
  5. Vectorizes these blocks using local HuggingFace embeddings (`all-MiniLM-L6-v2`) on the CPU.
  6. Registers the vectors inside **ChromaDB** under the `"documents"` collection namespace.
* **Success Response (`200 OK`)**:
  ```json
  {
      "message": "Document uploaded and processed successfully",
      "filename": <filename>.txt/<folder.name>.pdf,  "chunks": <number of chunks>
  }
  ```
* **Error Response (`400 Bad Request` / `500 Internal Server Error`)**:
  ```json
  {
      "detail": "Only PDF and TXT files are supported"
  }
  ```

---

#### 2. List Indexed Documents
* **URL**: `/api/documents`
* **Method**: `GET`
* **Purpose**: Retrieves all unique document filenames currently indexed inside the local vector store.
* **Under the Hood**:
  Queries the primary local Chroma collection metadata directly to aggregate all distinct `source` keys present.
* **Success Response (`200 OK`)**:
  ```json
  Here , sample document is the document or file we uploaded.

  {
      "documents": [
          "sample_document.txt"
      ]
  }
  ```

---

#### 3. Clear Database
* **URL**: `/api/clear`
* **Method**: `DELETE`
* **Purpose**: Wipes out the database contents, clearing space for new documents.
* **Under the Hood**:
  Drops and deletes the `"documents"` vector collection in the active Chroma DB instance and recreates an empty namespace.
* **Success Response (`200 OK`)**:
  ```json
  {
      "message": "All documents cleared successfully"
  }
  ```

---

### Query & Generation Routes

#### 4. Ask a Question (RAG Q&A)
* **URL**: `/api/query`
* **Method**: `POST`
* **Headers**: `Content-Type: application/json`

* **Under the Hood**:
  1. Validates that the question is non-empty.
  2. Converts the raw question string into a normalized 384-dimensional query vector using the local embedding model.
  3. Executes a **K-Nearest Neighbors Similarity Search ($k=4$)** inside ChromaDB to retrieve the most contextually relevant document chunks.
  4. Formulates a structured system prompt combining the retrieved context with the user's question.
  5. Queries the **Groq LLM** (`llama-3.3-70b-versatile`) with the formatted prompt.
  6. Returns the generated answer along with complete source text citations.
* **Success Response (`200 OK`)**

---