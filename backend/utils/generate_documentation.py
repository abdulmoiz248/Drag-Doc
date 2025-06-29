from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile
import json
from pathlib import Path
from utils.pdf_generator import generate_enhanced_documentation_pdf
from utils.create_summary import createSummary, generateWithGemini

router = APIRouter()

@router.get("/generate-documentation/")
async def generate_comprehensive_documentation(session_id: str = Query(...)):
    """
    Generate comprehensive project documentation with enhanced design and analysis
    
    This endpoint creates a professional PDF documentation that includes:
    - Project Overview & Metadata
    - Technology Stack Analysis  
    - System Architecture Diagrams
    - API Documentation
    - Database Schema Analysis
    - File Structure Analysis
    - Security Analysis
    - Deployment Guide
    - Testing Strategy
    - Environment Configuration
    - Performance Analysis
    - Future Enhancements
    - Knowledge Assessment (MCQs)
    - Comprehensive Appendices
    """
    
    # Import session management from main app
    from main import session_dbs, get_session_dirs
    
    # Validate session
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
        
        # If no logo found, look for any image in root or assets directory
        if not logo_path:
            for root, dirs, files in os.walk(extract_dir):
                # Prioritize common asset directories
                if any(asset_dir in root.lower() for asset_dir in ['assets', 'images', 'img', 'static', 'public']):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in image_extensions):
                            logo_path = os.path.join(root, file)
                            break
                if logo_path:
                    break
        
        # Determine project title
        project_title = "Project Documentation"
        
        # Try to get project name from directory structure
        try:
            # Look for main project directory
            top_level_dirs = [d for d in os.listdir(extract_dir) 
                            if os.path.isdir(os.path.join(extract_dir, d)) 
                            and not d.startswith('.')]
            if top_level_dirs:
                project_title = top_level_dirs[0].replace('_', ' ').replace('-', ' ').title()
        except:
            pass
        
        # Try to get project name from package files
        package_files = ['package.json', 'setup.py', 'pyproject.toml', 'Cargo.toml']
        for package_file in package_files:
            package_path = os.path.join(extract_dir, package_file)
            if os.path.exists(package_path):
                try:
                    if package_file == 'package.json':
                        with open(package_path, 'r') as f:
                            data = json.load(f)
                            if 'name' in data:
                                project_title = data['name'].replace('-', ' ').replace('_', ' ').title()
                                break
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

@router.get("/documentation-status/{session_id}")
async def get_documentation_status(session_id: str):
    """Get the status of documentation generation for a session"""
    from main import session_dbs
    
    db = session_dbs.get(session_id)
    if db is None:
        return {"status": "error", "message": "Invalid session ID"}
    
    return {
        "status": "ready",
        "message": "Session is ready for documentation generation",
        "session_id": session_id
    }
