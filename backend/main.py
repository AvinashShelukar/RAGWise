from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.rag import RAGPipeline
from backend.ingest import ingest_pdfs


app = FastAPI(
    title="Local PDF RAG API",
    description="Local PDF Question Answering System",
    version="1.0.0"
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

rag = RAGPipeline()


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str
    top_k: int = 5


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Local PDF RAG API is running",
        "status": "success"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# LIST PDFs
# ============================================================

@app.get("/documents")
def documents():

    pdf_files = sorted(
        [
            file.name
            for file in PDF_FOLDER.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".pdf"
        ]
    )

    return {
        "documents": pdf_files,
        "count": len(pdf_files)
    }


# ============================================================
# UPLOAD PDF
# ============================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )


    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )


    # --------------------------------------------------------
    # Secure filename
    # --------------------------------------------------------

    safe_filename = Path(file.filename).name

    file_path = PDF_FOLDER / safe_filename


    # --------------------------------------------------------
    # Save PDF
    # --------------------------------------------------------

    try:

        with open(file_path, "wb") as output:

            shutil.copyfileobj(
                file.file,
                output
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF: {error}"
        )


    # --------------------------------------------------------
    # Index PDFs
    # --------------------------------------------------------

    try:

        ingest_pdfs()

    except Exception as error:

        # Remove uploaded file if indexing failed
        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"PDF ingestion failed: {error}"
        )


    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return {

        "message": "PDF uploaded and indexed successfully.",

        "filename": safe_filename,

        "path": str(file_path),

        "status": "success"
    }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    # --------------------------------------------------------
    # Validate top_k
    # --------------------------------------------------------

    if request.top_k < 1 or request.top_k > 20:

        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20."
        )


    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    try:

        result = rag.generate_answer(
            request.question,
            top_k=request.top_k
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {error}"
        )