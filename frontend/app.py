from pathlib import Path
from typing import Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from backend.rag import RAGPipeline
from backend.ingest import ingest_pdfs


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Local PDF RAG API",
    description="Local PDF Question Answering System",
    version="2.0.0"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_FOLDER = BASE_DIR / "data" / "pdfs"

PDF_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# RAG PIPELINE
# ============================================================

try:

    rag = RAGPipeline()

    RAG_STATUS = "ready"

except Exception as error:

    rag = None

    RAG_STATUS = f"error: {error}"


# ============================================================
# REQUEST MODELS
# ============================================================

class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=2,
        description="Question to ask about the indexed PDFs"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant chunks to retrieve"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Local PDF RAG API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "rag_status": RAG_STATUS,
        "pdf_folder": str(PDF_FOLDER),
        "pdf_count": len(list(PDF_FOLDER.glob("*.pdf")))
    }


# ============================================================
# LIST PDFs
# ============================================================

@app.get("/documents")
def list_documents():

    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    documents = []

    for pdf in pdf_files:

        documents.append({
            "filename": pdf.name,
            "size_mb": round(
                pdf.stat().st_size / (1024 * 1024),
                2
            )
        })

    return {
        "count": len(documents),
        "documents": documents
    }


# ============================================================
# UPLOAD PDF
# ============================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )


    # --------------------------------------------------------
    # Validate PDF extension
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )


    # --------------------------------------------------------
    # Prevent unsafe filenames
    # --------------------------------------------------------

    safe_filename = Path(file.filename).name

    file_path = PDF_FOLDER / safe_filename


    # --------------------------------------------------------
    # Save PDF
    # --------------------------------------------------------

    try:

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )


        with open(file_path, "wb") as output:

            output.write(contents)


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save PDF: {error}"
        )


    # --------------------------------------------------------
    # Ingest / index PDFs
    # --------------------------------------------------------

    try:

        result = ingest_pdfs()

        return {
            "status": "success",
            "message": "PDF uploaded and indexed successfully.",
            "filename": safe_filename,
            "path": str(file_path),
            "ingestion_result": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"PDF saved but indexing failed: {error}"
        )


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    # --------------------------------------------------------
    # Check RAG
    # --------------------------------------------------------

    if rag is None:

        raise HTTPException(
            status_code=503,
            detail=f"RAG pipeline is not available: {RAG_STATUS}"
        )


    # --------------------------------------------------------
    # Clean question
    # --------------------------------------------------------

    question = request.question.strip()


    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    try:

        result = rag.generate_answer(
            question,
            top_k=request.top_k
        )


        return {
            "status": "success",
            "question": question,
            "result": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {error}"
        )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )