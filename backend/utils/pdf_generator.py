from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.platypus.flowables import HRFlowable
import re
from datetime import datetime
import os

# Try to import Groq, but make it optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ Groq not installed. AI features will be disabled. Install with: pip install groq")

def create_ultimate_styles():
    """Create comprehensive custom paragraph styles"""
    return {
        'title': ParagraphStyle(
            name='CustomTitle',
            fontSize=36,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1a237e'),
            fontName='Helvetica-Bold',
            leading=42
        ),
        'subtitle': ParagraphStyle(
            name='CustomSubtitle',
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#424242'),
            fontName='Helvetica',
            leading=22
        ),
        'section_header': ParagraphStyle(
            name='SectionHeader',
            fontSize=22,
            alignment=TA_LEFT,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor('#1565c0'),
            fontName='Helvetica-Bold',
            borderWidth=3,
            borderColor=colors.HexColor('#1565c0'),
            borderPadding=10,
            backColor=colors.HexColor('#f8f9ff'),
            leading=26
        ),
        'subsection_header': ParagraphStyle(
            name='SubsectionHeader',
            fontSize=18,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2e7d32'),
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.HexColor('#2e7d32'),
            borderPadding=8,
            backColor=colors.HexColor('#f1f8e9'),
            leftIndent=5,
            leading=22
        ),
        'file_header': ParagraphStyle(
            name='FileHeader',
            fontSize=16,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#d84315'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#d84315'),
            borderPadding=6,
            backColor=colors.HexColor('#fff3e0'),
            leftIndent=10,
            leading=20
        ),
        'normal': ParagraphStyle(
            name='CustomNormal',
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            fontName='Helvetica',
            textColor=colors.HexColor('#333333'),
            leading=14,
            leftIndent=15,
            rightIndent=15
        ),
        'bullet': ParagraphStyle(
            name='CustomBullet',
            fontSize=11,
            leftIndent=30,
            bulletIndent=15,
            spaceAfter=8,
            fontName='Helvetica',
            textColor=colors.HexColor('#333333'),
            leading=14
        ),
        'code': ParagraphStyle(
            name='CustomCode',
            fontSize=9,
            fontName='Courier',
            backColor=colors.HexColor('#f5f5f5'),
            leftIndent=25,
            rightIndent=25,
            spaceAfter=12,
            spaceBefore=8,
            borderPadding=8,
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0'),
            leading=11
        ),
        'highlight': ParagraphStyle(
            name='Highlight',
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1976d2'),
            backColor=colors.HexColor('#e3f2fd'),
            borderPadding=6,
            leading=15
        )
    }

def detect_project_type(file_summaries):
    """Dynamically detect project type based on files"""
    files = list(file_summaries.keys())
    descriptions = ' '.join(file_summaries.values()).lower()
    
    if any('spam' in desc for desc in [descriptions]):
        return "Machine Learning - Spam Detection"
    elif any('ml' in f.lower() or 'model' in f.lower() for f in files):
        return "Machine Learning Project"
    elif any('api' in f.lower() or 'server' in f.lower() for f in files):
        return "Web API Application"
    elif any('data' in desc for desc in [descriptions]):
        return "Data Processing System"
    else:
        return "Software Development Project"

def detect_tech_stack(file_summaries):
    """Dynamically detect technology stack"""
    descriptions = ' '.join(file_summaries.values()).lower()
    tech_stack = []
    
    if 'pandas' in descriptions:
        tech_stack.append('Pandas')
    if 'scikit' in descriptions or 'sklearn' in descriptions:
        tech_stack.append('Scikit-learn')
    if 'numpy' in descriptions:
        tech_stack.append('NumPy')
    if 'flask' in descriptions:
        tech_stack.append('Flask')
    if 'django' in descriptions:
        tech_stack.append('Django')
    if 'tensorflow' in descriptions:
        tech_stack.append('TensorFlow')
    if 'pytorch' in descriptions:
        tech_stack.append('PyTorch')
    
    return ', '.join(tech_stack) if tech_stack else 'Python Standard Library'

def generate_ai_content(prompt, max_tokens=500, groq_api_key=None):
    """Generate content using Groq AI if available"""
    if not GROQ_AVAILABLE or not groq_api_key:
        return None
    
    try:
        client = Groq(api_key=groq_api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=max_tokens,
            temperature=0.7
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"AI generation failed: {str(e)}")
        return None

def add_logo_if_exists(story, logo_path):
    """Add logo to the document if it exists"""
    if logo_path and os.path.exists(logo_path):
        try:
            # Try to add the logo
            logo = Image(logo_path, width=1*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.2*inch))
            return True
        except Exception as e:
            print(f"⚠️ Could not load logo from {logo_path}: {str(e)}")
            return False
    return False

def add_ultimate_header_footer(canvas, doc, project_title="Project"):
    """Enhanced header and footer with project branding"""
    canvas.saveState()
    
    # Enhanced header
    canvas.setFillColor(colors.HexColor('#1565c0'))
    canvas.rect(doc.leftMargin, doc.height + doc.topMargin - 30, 
               doc.width, 25, fill=1, stroke=0)
    
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawString(doc.leftMargin + 10, doc.height + doc.topMargin - 20, 
                     f"📋 {project_title} - Documentation")
    
    # Enhanced footer
    canvas.setFillColor(colors.HexColor('#f5f5f5'))
    canvas.rect(doc.leftMargin, 20, doc.width, 30, fill=1, stroke=0)
    
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.setFont('Helvetica', 9)
    canvas.drawString(doc.leftMargin + 10, 35, 
                     f"Generated by Drag & Doc on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    canvas.drawRightString(doc.width + doc.leftMargin - 10, 35, 
                          f"Page {canvas.getPageNumber()}")
    
    # Decorative lines
    canvas.setStrokeColor(colors.HexColor('#1565c0'))
    canvas.setLineWidth(2)
    canvas.line(doc.leftMargin, doc.height + doc.topMargin - 35, 
               doc.width + doc.leftMargin, doc.height + doc.topMargin - 35)
    
    canvas.restoreState()

def add_ultimate_title_page(story, project_title, file_summaries, styles, logo_path=None):
    """Create dynamic title page based on project"""
    story.append(Spacer(1, 0.5*inch))
    
    # Add logo if available
    logo_added = add_logo_if_exists(story, logo_path)
    if not logo_added:
        story.append(Spacer(1, 0.5*inch))
    
    # Dynamic title
    title_data = [[project_title]]
    title_table = Table(title_data, colWidths=[7*inch])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 32),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 25),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
        ('GRID', (0, 0), (-1, -1), 3, colors.HexColor('#0d47a1'))
    ]))
    story.append(title_table)
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("📋 Comprehensive Technical Documentation", styles['subtitle']))
    story.append(Spacer(1, 0.5*inch))
    
    # Dynamic project metadata
    project_type = detect_project_type(file_summaries)
    tech_stack = detect_tech_stack(file_summaries)
    
    metadata = [
        ['🏷️ Project Type:', project_type],
        ['💻 Primary Language:', 'Python 3.x'],
        ['🔧 Technology Stack:', tech_stack],
        ['📊 Total Files:', str(len(file_summaries))],
        ['📅 Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
        ['🚀 Generated By:', 'Drag & Doc System']
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')])
    ]))
    story.append(metadata_table)
    story.append(PageBreak())

def add_comprehensive_toc(story, file_summaries, styles):
    """Create comprehensive table of contents"""
    story.append(Paragraph("📑 Table of Contents", styles['section_header']))
    story.append(Spacer(1, 0.3*inch))
    
    toc_sections = [
        ['📋 Section', '📄 Description', '📖 Page'],
        ['Executive Summary', 'Project overview and key insights', '3'],
        ['🏗️ System Architecture', 'Component design and data flow', '4'],
        ['📊 Technical Analysis', 'Requirements and specifications', '5'],
        ['🔧 File Documentation', 'Detailed file analysis', '6'],
    ]
    
    # Dynamic file entries
    current_page = 7
    files_per_page = 3
    for i, filename in enumerate(file_summaries.keys(), 1):
        page_num = current_page + ((i - 1) // files_per_page)
        toc_sections.append([f'  📄 {i}. {filename}', f'Implementation details', str(page_num)])
    
    # Calculate final page for additional sections
    final_file_page = current_page + (len(file_summaries) // files_per_page)
    
    additional_sections = [
        ['🔗 Dependencies Analysis', 'Library requirements and versions', str(final_file_page + 1)],
        ['🛡️ Security & Performance', 'Analysis and recommendations', str(final_file_page + 2)],
        ['🚀 Deployment Guide', 'Setup and deployment instructions', str(final_file_page + 3)],
        ['📈 System Diagrams', 'Architecture and flow diagrams', str(final_file_page + 4)],
        ['🔮 Future Roadmap', 'Enhancement recommendations', str(final_file_page + 5)]
    ]
    
    toc_sections.extend(additional_sections)
    
    toc_table = Table(toc_sections, colWidths=[3*inch, 3*inch, 0.8*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')])
    ]))
    story.append(toc_table)
    story.append(PageBreak())

def add_executive_summary(story, project_title, file_summaries, styles, groq_api_key=None):
    """Add dynamic executive summary"""
    story.append(Paragraph("📋 Executive Summary", styles['section_header']))
    
    # Try AI summary first
    ai_summary = None
    if GROQ_AVAILABLE and groq_api_key:
        files_list = ", ".join(file_summaries.keys())
        ai_prompt = f"""
        Create a professional executive summary for "{project_title}".
        Files: {files_list}
        
        Cover: 1) Project purpose 2) Technical approach 3) Key components 4) Expected outcomes
        Keep it professional and concise (250-300 words).
        """
        ai_summary = generate_ai_content(ai_prompt, 400, groq_api_key)
    
    # Use AI summary or fallback to dynamic summary
    if ai_summary:
        summary_text = ai_summary
    else:
        project_type = detect_project_type(file_summaries)
        tech_stack = detect_tech_stack(file_summaries)
        
        summary_text = f"""
        {project_title} represents a comprehensive {project_type.lower()} designed to address complex 
        technical challenges through innovative implementation and robust architecture. The system incorporates 
        {len(file_summaries)} specialized components working in harmony to deliver optimal performance and reliability.
        
        The technical approach leverages {tech_stack} and follows industry best practices to ensure scalability 
        and maintainability. Each component has been carefully designed to fulfill specific responsibilities 
        while maintaining loose coupling with other system elements.
        
        Key outcomes include improved efficiency, enhanced reliability, and streamlined operations that deliver 
        measurable value to stakeholders and end users. The modular architecture supports both current 
        requirements and future enhancements.
        """
    
    story.append(Paragraph(summary_text, styles['normal']))
    
    # Dynamic metrics table
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("📊 Project Metrics Dashboard", styles['subsection_header']))
    
    metrics_data = [
        ['Metric', 'Value', 'Status', 'Target'],
        ['Total Files', str(len(file_summaries)), '✅ Complete', f'{len(file_summaries)}'],
        ['Documentation Coverage', '100%', '✅ Excellent', '≥95%'],
        ['Code Quality', 'High', '✅ Good', 'High'],
        ['System Integration', 'Complete', '✅ Ready', 'Complete'],
        ['Performance Level', 'Optimized', '✅ Excellent', 'Optimized']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f8e9')])
    ]))
    story.append(metrics_table)
    story.append(PageBreak())

def generate_dynamic_architecture(file_summaries):
    """Generate architecture components based on actual files"""
    components = []
    
    for filename, description in file_summaries.items():
        desc_lower = description.lower()
        
        if 'merge' in filename.lower() or 'data' in desc_lower:
            components.append(['Data Layer', 'Data management & processing', 'Raw data', 'Processed data', 'Pandas, NumPy'])
        elif 'preprocess' in filename.lower() or 'clean' in desc_lower:
            components.append(['Processing Engine', 'Data transformation', 'Raw data', 'Clean features', 'Scikit-learn'])
        elif 'train' in filename.lower() or 'model' in desc_lower:
            components.append(['ML Pipeline', 'Model training & inference', 'Features', 'Predictions', 'ML Libraries'])
        elif 'predict' in filename.lower() or 'api' in desc_lower:
            components.append(['Prediction Service', 'Real-time inference', 'Input data', 'Predictions', 'Model, API'])
        elif 'test' in filename.lower():
            components.append(['Testing Framework', 'Quality assurance', 'Test cases', 'Results', 'Testing tools'])
        else:
            components.append(['Utility Module', 'Support functions', 'Various', 'Various', 'Standard Library'])
    
    return components

def add_system_architecture(story, file_summaries, styles):
    """Add dynamic system architecture section"""
    story.append(Paragraph("🏗️ System Architecture", styles['section_header']))
    
    story.append(Paragraph("📐 Architecture Overview", styles['subsection_header']))
    story.append(Paragraph(
        f"The system follows a modular architecture with {len(file_summaries)} main components. "
        "Each component is designed for optimal performance, maintainability, and extensibility. "
        "The architecture supports both batch processing and real-time operations based on the project requirements.",
        styles['normal']
    ))
    
    # Dynamic component diagram
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("🔧 System Components Matrix", styles['subsection_header']))
    
    components_data = [['Component', 'Primary Function', 'Input Type', 'Output Type', 'Dependencies']]
    components_data.extend(generate_dynamic_architecture(file_summaries))
    
    comp_table = Table(components_data, colWidths=[1.2*inch, 1.4*inch, 1.2*inch, 1.2*inch, 1.4*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')])
    ]))
    story.append(comp_table)
    story.append(PageBreak())

def add_file_documentation_with_smart_pagination(story, file_summaries, styles, groq_api_key=None):
    """Add file documentation with intelligent pagination"""
    story.append(Paragraph("🔧 Comprehensive File Documentation", styles['section_header']))
    
    files_per_page = 3  # Optimal files per page
    file_items = list(file_summaries.items())
    
    for i, (filename, description) in enumerate(file_items, 1):
        # Smart page break management
        if i > 1 and (i - 1) % files_per_page == 0:
            story.append(PageBreak())
        
        # Enhanced file header
        story.append(Paragraph(f"📄 {i}. {filename}", styles['file_header']))
        
        # AI-enhanced analysis if available
        if GROQ_AVAILABLE and groq_api_key:
            ai_prompt = f"""
            Analyze this file: {filename}
            Description: {description}
            
            Provide: 1) Summary 2) Key features 3) Complexity level 4) Dependencies
            Keep concise (150 words max).
            """
            ai_analysis = generate_ai_content(ai_prompt, 200, groq_api_key)
            if ai_analysis:
                story.append(Paragraph(ai_analysis, styles['normal']))
            else:
                story.append(Paragraph(description, styles['normal']))
        else:
            story.append(Paragraph(description, styles['normal']))
        
        # Dynamic file statistics
        file_ext = filename.split('.')[-1].upper() if '.' in filename else 'UNKNOWN'
        complexity = 'High' if any(word in description.lower() for word in ['train', 'model', 'algorithm']) else 'Medium' if 'function' in description.lower() else 'Low'
        
        stats_data = [
            ['Attribute', 'Value', 'Assessment'],
            ['File Type', file_ext, '📄 Source Code'],
            ['Complexity', complexity, '🔧 ' + ('Advanced' if complexity == 'High' else 'Standard')],
            ['Role', 'Core' if any(word in filename for word in ['train', 'predict', 'main']) else 'Support', '⚙️ Component'],
            ['Dependencies', 'External' if any(lib in description.lower() for lib in ['pandas', 'sklearn', 'numpy']) else 'Standard', '📦 Libraries']
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f57c00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8e1')])
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.2*inch))

def generate_dynamic_dependencies(file_summaries):
    """Generate dependencies based on file descriptions"""
    deps = []
    descriptions = ' '.join(file_summaries.values()).lower()
    
    if 'pandas' in descriptions:
        deps.append(['pandas', '≥1.3.0', 'Data manipulation', 'BSD-3', '✅', '🟢 Active'])
    if 'scikit' in descriptions or 'sklearn' in descriptions:
        deps.append(['scikit-learn', '≥1.0.0', 'Machine learning', 'BSD-3', '✅', '🟢 Active'])
    if 'numpy' in descriptions:
        deps.append(['numpy', '≥1.21.0', 'Numerical computing', 'BSD-3', '✅', '🟢 Active'])
    if 'joblib' in descriptions:
        deps.append(['joblib', '≥1.0.0', 'Model persistence', 'BSD-3', '✅', '🟢 Active'])
    if 'matplotlib' in descriptions:
        deps.append(['matplotlib', '≥3.3.0', 'Data visualization', 'PSF', '⚠️', '🟢 Active'])
    if 'flask' in descriptions:
        deps.append(['flask', '≥2.0.0', 'Web framework', 'BSD-3', '✅', '🟢 Active'])
    
    if not deps:  # Default dependencies
        deps.append(['python', '≥3.8.0', 'Runtime environment', 'PSF', '✅', '🟢 Active'])
    
    return deps

def add_comprehensive_additional_sections(story, file_summaries, styles):
    """Add all additional professional sections"""
    
    # Dynamic Dependencies Analysis
    story.append(PageBreak())
    story.append(Paragraph("🔗 Dependencies & Libraries Analysis", styles['section_header']))
    
    deps_data = [['Library', 'Version', 'Purpose', 'License', 'Critical', 'Status']]
    deps_data.extend(generate_dynamic_dependencies(file_summaries))
    
    deps_table = Table(deps_data, colWidths=[1*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.6*inch, 0.8*inch])
    deps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f8e9')])
    ]))
    story.append(deps_table)
    
    # Dynamic deployment guide
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("🚀 Deployment & Setup Guide", styles['section_header']))
    
    deployment_steps = [
        "1. 🔧 **Environment Setup**: Install Python 3.8+ and required dependencies",
        "2. 📦 **Package Installation**: Run `pip install -r requirements.txt`",
        "3. 🗃️ **Data Preparation**: Ensure all required data files are in place",
        "4. ⚙️ **Configuration**: Update configuration files as needed",
        "5. 🧪 **Testing**: Execute test suite to verify installation",
        "6. 🚀 **Launch**: Start the application using the main entry point",
        "7. 📊 **Monitoring**: Set up logging and monitoring as required"
    ]
    
    for step in deployment_steps:
        story.append(Paragraph(step, styles['bullet']))

# MAIN FUNCTION - This is what you'll call from your main code
def generate_enhanced_documentation_pdf(output_path, project_title, summary, extract_dir=None, mcqs=None, logo_path=None, groq_api_key=None):
    """
    Generate ultimate enhanced documentation PDF
    
    Args:
        output_path: Path where PDF will be saved
        project_title: Title of the project
        summary: Dictionary of {filename: description} - YOUR SUMMARIES FROM MAIN
        extract_dir: Optional directory path (not used but kept for compatibility)
        mcqs: Optional MCQs (not used but kept for compatibility)  
        logo_path: Path to logo file (default: backend/data/logo.png)
        groq_api_key: Optional Groq API key for AI features
    """
    
    # Set default logo path if not provided
    if logo_path is None:
        logo_path = "backend/data/logo.png"
    
    # Create document with professional settings
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=1.3*inch,
        bottomMargin=1.1*inch
    )
    
    # Create styles
    styles = create_ultimate_styles()
    
    # Build story
    story = []
    
    print(f"🚀 Generating documentation for '{project_title}' with {len(summary)} files...")
    
    # Add all sections with dynamic content
    add_ultimate_title_page(story, project_title, summary, styles, logo_path)
    add_comprehensive_toc(story, summary, styles)
    add_executive_summary(story, project_title, summary, styles, groq_api_key)
    add_system_architecture(story, summary, styles)
    add_file_documentation_with_smart_pagination(story, summary, styles, groq_api_key)
    add_comprehensive_additional_sections(story, summary, styles)
    
    # Build the ultimate PDF with project-specific header
    def header_footer_wrapper(canvas, doc):
        add_ultimate_header_footer(canvas, doc, project_title)
    
    doc.build(story, onFirstPage=header_footer_wrapper, onLaterPages=header_footer_wrapper)
    
    print(f"🎉 Documentation generated successfully!")
    print(f"📄 File: {output_path}")
    print(f"📊 Files documented: {len(summary)}")
    print(f"🤖 AI features: {'Enabled' if (GROQ_AVAILABLE and groq_api_key) else 'Disabled'}")
    print(f"🏆 Generated by: Drag & Doc System")
