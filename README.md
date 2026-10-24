# RAGWise — Local PDF Question Answering with RAG

RAGWise is a Retrieval-Augmented Generation (RAG) application that lets users ask questions about PDF documents and receive context-aware answers with source-page citations.

The project combines semantic search, vector similarity retrieval, and a locally hosted language model to make document question answering more useful and transparent.

## Features

- **PDF-based question answering** using retrieved document content.
- **Local semantic embeddings** using the BGE small English embedding model.
- **Vector similarity search** using FAISS.
- **Local LLM inference** using Ollama and `qwen2.5:7b`.
- **Source citations** with PDF filenames and page numbers.
- **FastAPI REST API** with interactive Swagger documentation.
- **Document-aware retrieval** to restrict answers to a selected PDF.
- **Configurable retrieval count** through the `top_k` parameter.

## Architecture

```text
                 ┌──────────────────────┐
                 │      PDF Documents   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Text Extraction and │
                 │   Document Chunks    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ BGE Embedding Model  │
                 │   (384 dimensions)   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     FAISS Index      │
                 └──────────┬───────────┘
                            │
         User Question ─────┤
                            ▼
                 ┌──────────────────────┐
                 │  Semantic Retrieval  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Context + Question  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Ollama: Qwen 2.5 7B  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Answer + Citations   │
                 └──────────────────────┘
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API framework | FastAPI |
| Embedding model | `BAAI/bge-small-en-v1.5` |
| Vector database | FAISS |
| Local language model | Ollama — `qwen2.5:7b` |
| API documentation | Swagger UI |
| Version control | Git and GitHub |

## Prerequisites

Install the following before running the project:

- Python 3.11 recommended
- Git
- Ollama for local language model inference
- The Ollama model `qwen2.5:7b`

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/AvinashShelukar/RAGWise.git
cd RAGWise
git switch local-ollama-rag
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

Install the project's dependencies using its dependency file:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Ensure the dependency file includes the packages required by the current local setup, including `sentence-transformers`, `numpy`, `faiss-cpu`, `fastapi`, `uvicorn`, and `python-multipart`.

### 4. Install and start Ollama

Install Ollama from [ollama.com](https://ollama.com/), then download the model:

```powershell
ollama pull qwen2.5:7b
```

Verify the model:

```powershell
ollama list
```

Ollama usually runs in the background on Windows. If it is not running, start it with:

```powershell
ollama serve
```

The API should be available at `http://127.0.0.1:11434`.

### 5. Add PDF documents

Place your PDF files in the project's configured PDF directory and ensure they are indexed using the project's document-ingestion workflow.

The vector index and metadata must correspond to the embedding model used by the application.

### 6. Run the FastAPI application

```powershell
python -m uvicorn backend.main:app --reload
```

Open the API documentation:

**http://127.0.0.1:8000/docs**

Check API health:

**http://127.0.0.1:8000/health**

## API Usage

### Health check

```http
GET /health
```

### List documents

```http
GET /documents
```

### Ask a question

```http
POST /ask
Content-Type: application/json
```

Example request:

```json
{
  "question": "What is the main objective of the paper?",
  "top_k": 3,
  "source": "N8_LLM_CyberSecurity_SLR_2024.pdf"
}
```

Example response:

```json
{
  "answer": "The paper reviews the application of large language models in cybersecurity tasks.",
  "citations": [
    {
      "source": "N8_LLM_CyberSecurity_SLR_2024.pdf",
      "page": 7,
      "score": 0.6683
    }
  ]
}
```

The answer and citation values above are illustrative; actual results depend on the indexed PDFs and retrieval output.

## Project Structure


## Project Structure

```text
RAGWise/
├── backend/
│   ├── __init__.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── ingest.py
│   ├── main.py
│   ├── pdf_processor.py
│   ├── rag.py
│   ├── retriever.py
│   ├── vector_store.py
│   └── test_*.py
├── data/
│   └── pdfs/             # Local PDF documents (not committed)
├── requirements.txt
├── .gitignore
└── README.md
```

The `test_*.py` files contain tests for individual pipeline components.


The actual project may contain additional files for ingestion, chunking, indexing, configuration, or testing.

## Important Notes

- The local Ollama integration requires Ollama to be installed and running on the machine executing the API.
- The BGE embedding model must be downloaded and available locally on first use.
- PDF content and generated answers can contain errors; verify important claims against the cited pages.
- Do not commit API keys, `.env` files, private PDFs, virtual environments, or downloaded model weights.
- The current local Ollama configuration is not automatically compatible with cloud hosting platforms such as Render. A cloud deployment needs a reachable inference service and an appropriate production configuration.

## Future Improvements

- Build a Streamlit chat interface.
- Improve PDF ingestion and document management.
- Add automated tests for retrieval and answer generation.
- Improve answer-quality evaluation and citation verification.
- Add production deployment configuration and monitoring.


## License

Add a license file if you intend to distribute the project under an open-source license.