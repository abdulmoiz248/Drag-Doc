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

# Import the enhanced PDF generator (you'll need to create this file)
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
    version="2.0.0"
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

@app.post("/ask-question/")
def ask_question(question: str = Form(...), session_id: str = Form(...)):
    db = session_dbs.get(session_id)
    if db is None:
        return {"status": "error", "message": "Invalid session ID or no documents loaded. Upload a zip file first."}
    
    retriever = db.as_retriever()
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs[:4]])
    answer = generateWithGemini(context, question)
    
    return {"status": "success", "answer": answer, "sources": len(docs)}

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

# OLD endpoint for backward compatibility
@app.get("/generate-documentation/")
def generate_documentation_old(session_id: str = Query(...)):
    """Old documentation endpoint for backward compatibility"""
    return generate_documentation_enhanced(session_id)

# NEW enhanced endpoint
@app.get("/api/v1/generate-documentation/")
def generate_documentation_enhanced(session_id: str = Query(...)):
    """
    Generate comprehensive project documentation with enhanced design and analysis
    """
    db = session_dbs.get(session_id)
    if db is None:
        raise HTTPException(
            status_code=404, 
            detail="Invalid session ID or no documents loaded. Upload a zip file first."
        )

    try:
        upload_dir, extract_dir = get_session_dirs(session_id)
        
        print(f"🚀 Starting documentation generation for session: {session_id}")
        
        # Generate comprehensive summary using RAG
        print("📝 Generating project summary...")
        summaries = createSummary(db)
        
        # Convert summaries to text
        if isinstance(summaries, dict):
            summary_text = "\n\n".join([f"**{filename}**\n{summary}" 
                                       for filename, summary in summaries.items()])
        elif isinstance(summaries, list):
            summary_text = "\n".join(summaries)
        else:
            summary_text = str(summaries)
        
        # Generate enhanced project overview using RAG
        print("🔍 Generating enhanced project overview...")
        retriever = db.as_retriever()
        
        # Get comprehensive context for project analysis
        overview_queries = [
            "project overview and main purpose",
            "architecture and design patterns", 
            "key features and functionality",
            "technology stack and dependencies"
        ]
        
        enhanced_context = ""
        for query in overview_queries:
            docs = retriever.get_relevant_documents(query)
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
            enhanced_context += f"\n\n=== {query.upper()} ===\n{context}"
        
        # Generate comprehensive project description
        project_analysis_prompt = """
        Based on the provided codebase context, create a comprehensive project analysis that includes:
        
        1. Project purpose and main objectives
        2. Key features and capabilities  
        3. Target audience and use cases
        4. Technical approach and methodology
        5. Notable implementation details
        
        Make it professional and detailed for technical documentation.
        """
        
        enhanced_summary = generateWithGemini(enhanced_context, project_analysis_prompt)
        
        # Combine original summary with enhanced analysis
        final_summary = f"{summary_text}\n\n=== DETAILED ANALYSIS ===\n{enhanced_summary}"
        
        # Generate MCQs for knowledge assessment
        print("❓ Generating knowledge assessment questions...")
        mcq_context = "\n\n".join([doc.page_content for doc in retriever.get_relevant_documents("project overview")[:8]])
        
        mcq_prompt = """
        Generate 15 comprehensive multiple choice questions about this project that test understanding of:
        - Project architecture and design
        - Key features and functionality  
        - Technology choices and implementation
        - Best practices and patterns used
        
        Return as valid JSON array with this exact format:
        [
            {
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }
        ]
        
        Make questions challenging but fair, covering different aspects of the project.
        """
        
        try:
            mcq_response = generateWithGemini(mcq_context, mcq_prompt)
            # Clean up the response to ensure valid JSON
            mcq_response = mcq_response.strip()
            if mcq_response.startswith('```json'):
                mcq_response = mcq_response[7:]
            if mcq_response.endswith('```'):
                mcq_response = mcq_response[:-3]
            
            mcqs = json.loads(mcq_response)
            
            # Validate MCQ structure
            if not isinstance(mcqs, list):
                mcqs = []
            else:
                # Filter valid MCQs
                valid_mcqs = []
                for mcq in mcqs:
                    if (isinstance(mcq, dict) and 
                        'question' in mcq and 
                        'options' in mcq and 
                        'answer' in mcq and
                        isinstance(mcq['options'], list) and
                        len(mcq['options']) >= 2):
                        valid_mcqs.append(mcq)
                mcqs = valid_mcqs[:15]  # Limit to 15 questions
                
        except Exception as e:
            print(f"⚠️ Error generating MCQs: {e}")
            mcqs = []
        
        # Detect project logo/image
        print("🖼️ Looking for project logo...")
        logo_path = None
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_lower = file.lower()
                if any(ext in file_lower for ext in image_extensions):
                    if any(keyword in file_lower for keyword in ['logo', 'icon', 'brand']):
                        logo_path = os.path.join(root, file)
                        break
            if logo_path:
                break
        
        # Determine project title
        project_title = "Project Documentation"
        
        # Try to get project name from directory structure
        try:
            top_level_dirs = [d for d in os.listdir(extract_dir) 
                            if os.path.isdir(os.path.join(extract_dir, d)) 
                            and not d.startswith('.')]
            if top_level_dirs:
                project_title = top_level_dirs[0].replace('_', ' ').replace('-', ' ').title()
        except:
            pass
        
        # Generate PDF output path
        pdf_filename = f"comprehensive_documentation_{session_id}.pdf"
        pdf_path = os.path.join(upload_dir, pdf_filename)
        
        print("📚 Generating comprehensive PDF documentation...")
        
        # Generate the enhanced documentation
        generate_enhanced_documentation_pdf(
            output_path=pdf_path,
            project_title=project_title,
            summary=final_summary,
            extract_dir=extract_dir,
            mcqs=mcqs,
            logo_path=logo_path
        )
        
        print(f"✅ Documentation generated successfully: {pdf_filename}")
        
        # Return the PDF file
        return FileResponse(
            pdf_path, 
            media_type="application/pdf", 
            filename=f"{project_title.replace(' ', '_')}_Documentation.pdf",
            headers={
                "Content-Disposition": f"attachment; filename={project_title.replace(' ', '_')}_Documentation.pdf"
            }
        )
        
    except Exception as e:
        print(f"❌ Error generating documentation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate documentation: {str(e)}"
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
