from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import shutil
import zipfile
import os
import uuid
import json
import tempfile
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.create_summary import createSummary, generateWithGemini
from utils.cleaner import unzipAndClean


try:
    from utils.pdf_generator import generate_enhanced_documentation_pdf
    ENHANCED_AVAILABLE = True
except ImportError:
    # Fallback to old generator if enhanced not available
    from utils.pdf_generator import generate_enhanced_documentation_pdf
    ENHANCED_AVAILABLE = False
    print("⚠️ Enhanced PDF generator not found, using basic version")

app = FastAPI(
    title="Enhanced RAG Documentation System",
    description="Advanced RAG system with comprehensive documentation generation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory paths
UPLOAD_DIR = "data"
EXTRACT_DIR = "extracted"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(EXTRACT_DIR).mkdir(parents=True, exist_ok=True)

# Session-based DB storage
session_dbs = {}

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def get_session_dirs(session_id):
    upload_dir = os.path.join(UPLOAD_DIR, session_id)
    extract_dir = os.path.join(EXTRACT_DIR, session_id)
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    Path(extract_dir).mkdir(parents=True, exist_ok=True)
    return upload_dir, extract_dir

def loadDocs(folder):
    loader = DirectoryLoader(
        folder,
        glob="**/*.*",
        loader_cls=UnstructuredFileLoader,
        silent_errors=True
    )
    return loader.load()

def chunkDocs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)

def embedAndStore(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return FAISS.from_documents(chunks, embeddings)

@app.get("/")
async def root():
    return {
        "message": "Enhanced RAG Documentation System",
        "version": "2.0.0",
        "enhanced_available": ENHANCED_AVAILABLE,
        "features": [
            "Advanced project analysis",
            "Comprehensive PDF documentation", 
            "Architecture diagrams",
            "API documentation",
            "Security analysis",
            "Performance recommendations",
            "Knowledge assessment"
        ]
    }

@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    upload_dir, extract_dir = get_session_dirs(session_id)
    zip_path = os.path.join(upload_dir, f"{session_id}.zip")
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extract_to = unzipAndClean(zip_path, extractTo=extract_dir)
    docs = loadDocs(extract_to)
    chunks = chunkDocs(docs)
    session_dbs[session_id] = embedAndStore(chunks)
    return {
        "status": "success",
        "message": "Project uploaded and analyzed successfully.",
        "session_id": session_id,
        "files_processed": len(docs),
        "chunks_created": len(chunks)
    }

@app.get("/generate-summary/")
def generate_summary(session_id: str = Query(...)):
    db = session_dbs.get(session_id)
    if db is None:
        return {"status": "error", "message": "Invalid session ID or no documents loaded. Upload a zip file first."}
    summaries = createSummary(db)
    return {"status": "success", "summaries": summaries}

@app.get("/generate-mcqs/")
def generate_mcqs(session_id: str = Query(...)):
    db = session_dbs.get(session_id)
    if db is None:
        return {"status": "error", "message": "Invalid session ID or no documents loaded. Upload a zip file first."}
    retriever = db.as_retriever()
    context = "\n\n".join([doc.page_content for doc in retriever.get_relevant_documents("project overview")[:6]])
    question = "Generate 20 multiple choice questions from the provided context. Return as JSON with question, options, and correct answer."
    mcq_json = generateWithGemini(context, question)
    try:
        import json as _json
        mcqs = _json.loads(mcq_json) if isinstance(mcq_json, str) else mcq_json
    except Exception:
        mcqs = []
    return {"status": "success", "mcqs": mcqs}

@app.get("/generate-documentation/")
def generate_documentation(session_id: str = Query(...)):
    db = session_dbs.get(session_id)
    if db is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid session ID or no documents loaded. Upload a zip file first."
        )
    upload_dir, extract_dir = get_session_dirs(session_id)
    summaries = createSummary(db)
    print(summaries)
    pdf_filename = f"documentation_{session_id}.pdf"
    pdf_path = os.path.join(upload_dir, pdf_filename)
    # Extract project name from top-level folder in extract_dir
    try:
        top_level_dirs = [d for d in os.listdir(extract_dir)
                          if os.path.isdir(os.path.join(extract_dir, d)) and not d.startswith('.')]
        if top_level_dirs:
            project_title = top_level_dirs[0].replace('_', ' ').replace('-', ' ').title()
        else:
            project_title = "Project Documentation"
    except Exception:
        project_title = "Project Documentation"
    generate_enhanced_documentation_pdf(
        output_path=pdf_path,
        project_title=project_title,
        summary=summaries,
        extract_dir=extract_dir,
        mcqs=[],
        logo_path=None,
        groq_api_key=GROQ_API_KEY
    )
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_filename,
        headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
    )

@app.get("/session-info/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a session"""
    db = session_dbs.get(session_id)
    if db is None:
        return {"status": "error", "message": "Session not found"}
    
    upload_dir, extract_dir = get_session_dirs(session_id)
    
    # Count files in extract directory
    file_count = 0
    for root, dirs, files in os.walk(extract_dir):
        file_count += len(files)
    
    return {
        "status": "success",
        "session_id": session_id,
        "files_count": file_count,
        "vector_store_ready": True,
        "extract_directory": extract_dir
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
