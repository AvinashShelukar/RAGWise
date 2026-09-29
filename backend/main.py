from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="RAGWise PDF RAG API",
    description="PDF Question Answering System using RAG",
    version="1.0.0"
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_FOLDER = BASE_DIR / "data" / "pdfs"
PDF_FOLDER.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Lazy RAG Pipeline
# --------------------------------------------------

rag = None


def get_rag():
    global rag

    if rag is None:
        from backend.rag import RAGPipeline
        rag = RAGPipeline()

    return rag


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "RAGWise PDF RAG API is running",
        "status": "success"
    }


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Documents
# --------------------------------------------------

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


# --------------------------------------------------
# Upload PDF
# --------------------------------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

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

    safe_filename = Path(file.filename).name
    file_path = PDF_FOLDER / safe_filename

    # Save PDF
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

    # Import ingestion only when needed
    try:

        from backend.ingest import ingest_pdfs

        ingest_pdfs()

    except Exception as error:

        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"PDF ingestion failed: {error}"
        )

    # Reload RAG pipeline
    global rag

    try:

        from backend.rag import RAGPipeline

        rag = RAGPipeline()

    except Exception as error:

        rag = None

        raise HTTPException(
            status_code=500,
            detail=f"RAG pipeline reload failed: {error}"
        )

    return {
        "message": "PDF uploaded and indexed successfully.",
        "filename": safe_filename,
        "status": "success"
    }


# --------------------------------------------------
# Ask Question
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if request.top_k < 1 or request.top_k > 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20."
        )

    try:

        pipeline = get_rag()

        result = pipeline.generate_answer(
            request.question,
            top_k=request.top_k
        )

        return result

    except FileNotFoundError:

        raise HTTPException(
            status_code=400,
            detail=(
                "No PDF has been indexed yet. "
                "Upload a PDF using the /upload endpoint first."
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {error}"
        )