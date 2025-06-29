from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import os
import ast
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import seaborn as sns
from collections import defaultdict, Counter
import re
from pathlib import Path
import tempfile
import subprocess
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO

class EnhancedDocumentationGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for professional PDF design"""
        # Title page style
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=30,
            textColor=colors.HexColor('#1a237e'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section headers with modern design
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceBefore=25,
            spaceAfter=15,
            textColor=colors.white,
            backColor=colors.HexColor('#1a237e'),
            borderPadding=12,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))
        
        # Subsection headers
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#1a237e'),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#1a237e'),
            borderPadding=5
        ))
        
        # Code blocks with syntax highlighting appearance
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontSize=9,
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#dee2e6'),
            borderWidth=1,
            borderPadding=10,
            fontName='Courier',
            leftIndent=10,
            rightIndent=10
        ))
        
        # Info boxes
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=10,
            backColor=colors.HexColor('#e3f2fd'),
            borderColor=colors.HexColor('#2196f3'),
            borderWidth=1,
            borderPadding=10,
            leftIndent=10,
            rightIndent=10
        ))
        
        # Warning boxes
        self.styles.add(ParagraphStyle(
            name='WarningBox',
            parent=self.styles['Normal'],
            fontSize=10,
            backColor=colors.HexColor('#fff3e0'),
            borderColor=colors.HexColor('#ff9800'),
            borderWidth=1,
            borderPadding=10,
            leftIndent=10,
            rightIndent=10
        ))

    def analyze_project_structure(self, extract_dir: str) -> Dict[str, Any]:
        """Comprehensive project analysis"""
        analysis = {
            'project_info': self.extract_project_info(extract_dir),
            'tech_stack': self.analyze_tech_stack(extract_dir),
            'file_structure': self.analyze_file_structure(extract_dir),
            'dependencies': self.analyze_dependencies(extract_dir),
            'api_endpoints': self.extract_api_endpoints(extract_dir),
            'database_schema': self.analyze_database_schema(extract_dir),
            'environment_vars': self.extract_environment_variables(extract_dir),
            'testing_info': self.analyze_testing_setup(extract_dir),
            'deployment_info': self.analyze_deployment_config(extract_dir),
            'security_analysis': self.analyze_security_features(extract_dir),
            'performance_metrics': self.analyze_performance_aspects(extract_dir)
        }
        return analysis

    def extract_project_info(self, extract_dir: str) -> Dict[str, Any]:
        """Extract basic project information"""
        info = {
            'name': os.path.basename(extract_dir),
            'description': '',
            'version': '1.0.0',
            'author': '',
            'license': '',
            'repository': '',
            'main_language': '',
            'framework': ''
        }
        
        # Check for package.json
        package_json = os.path.join(extract_dir, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    info.update({
                        'name': data.get('name', info['name']),
                        'description': data.get('description', ''),
                        'version': data.get('version', '1.0.0'),
                        'author': data.get('author', ''),
                        'license': data.get('license', ''),
                        'repository': data.get('repository', {}).get('url', '') if isinstance(data.get('repository'), dict) else data.get('repository', ''),
                        'main_language': 'JavaScript/TypeScript'
                    })
            except:
                pass
        
        # Check for README files
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md']
        for readme in readme_files:
            readme_path = os.path.join(extract_dir, readme)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000]  # First 1000 chars
                        if not info['description']:
                            # Extract first paragraph as description
                            lines = content.split('\n')
                            for line in lines[1:]:  # Skip title
                                if line.strip() and not line.startswith('#'):
                                    info['description'] = line.strip()
                                    break
                except:
                    pass
                break
        
        return info

    def analyze_tech_stack(self, extract_dir: str) -> Dict[str, List[str]]:
        """Analyze technology stack"""
        tech_stack = {
            'languages': set(),
            'frameworks': set(),
            'databases': set(),
            'tools': set(),
            'cloud_services': set()
        }
        
        # Language detection by file extensions
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext == '.py':
                    tech_stack['languages'].add('Python')
                elif ext in ['.js', '.jsx']:
                    tech_stack['languages'].add('JavaScript')
                elif ext in ['.ts', '.tsx']:
                    tech_stack['languages'].add('TypeScript')
                elif ext == '.java':
                    tech_stack['languages'].add('Java')
                elif ext in ['.cpp', '.cc', '.cxx']:
                    tech_stack['languages'].add('C++')
                elif ext == '.c':
                    tech_stack['languages'].add('C')
                elif ext == '.cs':
                    tech_stack['languages'].add('C#')
                elif ext == '.go':
                    tech_stack['languages'].add('Go')
                elif ext == '.rs':
                    tech_stack['languages'].add('Rust')
                elif ext == '.php':
                    tech_stack['languages'].add('PHP')
                elif ext == '.rb':
                    tech_stack['languages'].add('Ruby')
        
        # Framework and library detection
        self._detect_frameworks_and_libraries(extract_dir, tech_stack)
        
        # Convert sets to lists for JSON serialization
        for key in tech_stack:
            tech_stack[key] = list(tech_stack[key])
        
        return tech_stack

    def _detect_frameworks_and_libraries(self, extract_dir: str, tech_stack: Dict[str, set]):
        """Detect frameworks and libraries from various config files"""
        # Python dependencies
        requirements_files = ['requirements.txt', 'Pipfile', 'pyproject.toml']
        for req_file in requirements_files:
            req_path = os.path.join(extract_dir, req_file)
            if os.path.exists(req_path):
                self._analyze_python_dependencies(req_path, tech_stack)
        
        # Node.js dependencies
        package_json = os.path.join(extract_dir, 'package.json')
        if os.path.exists(package_json):
            self._analyze_node_dependencies(package_json, tech_stack)

    def _analyze_python_dependencies(self, file_path: str, tech_stack: Dict[str, set]):
        """Analyze Python dependencies"""
        framework_map = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'tornado': 'Tornado',
            'pyramid': 'Pyramid',
            'numpy': 'NumPy',
            'pandas': 'Pandas',
            'matplotlib': 'Matplotlib',
            'seaborn': 'Seaborn',
            'scikit-learn': 'Scikit-learn',
            'tensorflow': 'TensorFlow',
            'torch': 'PyTorch',
            'keras': 'Keras'
        }
        
        db_map = {
            'psycopg2': 'PostgreSQL',
            'pymongo': 'MongoDB',
            'redis': 'Redis',
            'sqlalchemy': 'SQLAlchemy',
            'mysql': 'MySQL'
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read().lower()
                
            for lib, framework in framework_map.items():
                if lib in content:
                    tech_stack['frameworks'].add(framework)
            
            for lib, db in db_map.items():
                if lib in content:
                    tech_stack['databases'].add(db)
        except:
            pass

    def _analyze_node_dependencies(self, file_path: str, tech_stack: Dict[str, set]):
        """Analyze Node.js dependencies"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            framework_map = {
                'react': 'React',
                'vue': 'Vue.js',
                'angular': 'Angular',
                'express': 'Express.js',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js',
                'gatsby': 'Gatsby',
                'svelte': 'Svelte'
            }
            
            for dep in dependencies:
                for lib, framework in framework_map.items():
                    if lib in dep.lower():
                        tech_stack['frameworks'].add(framework)
        except:
            pass

    def analyze_file_structure(self, extract_dir: str) -> Dict[str, Any]:
        """Analyze project file structure"""
        structure = {
            'total_files': 0,
            'total_lines': 0,
            'file_types': Counter(),
            'directory_structure': {},
            'largest_files': [],
            'complexity_analysis': {}
        }
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, extract_dir)
                
                structure['total_files'] += 1
                
                # File type analysis
                ext = os.path.splitext(file)[1].lower()
                structure['file_types'][ext] += 1
                
                # Line count and size analysis
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        structure['total_lines'] += line_count
                        
                        file_size = os.path.getsize(file_path)
                        structure['largest_files'].append({
                            'path': rel_path,
                            'lines': line_count,
                            'size': file_size
                        })
                except:
                    pass
        
        # Sort largest files
        structure['largest_files'].sort(key=lambda x: x['size'], reverse=True)
        structure['largest_files'] = structure['largest_files'][:10]
        
        return structure

    def analyze_dependencies(self, extract_dir: str) -> Dict[str, List[str]]:
        """Analyze project dependencies"""
        dependencies = {}
        
        # Check for Python dependencies
        requirements_files = ['requirements.txt', 'Pipfile', 'pyproject.toml']
        for req_file in requirements_files:
            req_path = os.path.join(extract_dir, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        content = f.read()
                        # Extract package names (simplified)
                        lines = content.split('\n')
                        deps = []
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name before version specifier
                                pkg_name = re.split(r'[>=<!=]', line)[0].strip()
                                if pkg_name:
                                    deps.append(pkg_name)
                        dependencies[req_file] = deps
                except:
                    dependencies[req_file] = []
        
        # Check for Node.js dependencies
        package_json = os.path.join(extract_dir, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = list(data.get('dependencies', {}).keys())
                    dev_deps = list(data.get('devDependencies', {}).keys())
                    dependencies['package.json'] = deps + dev_deps
            except:
                dependencies['package.json'] = []
        
        return dependencies

    def extract_api_endpoints(self, extract_dir: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from code"""
        endpoints = []
        
        # FastAPI/Flask patterns
        api_patterns = [
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'app\.route\(["\']([^"\']+)["\'].*methods=\[([^\]]+)\]'
        ]
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in api_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if len(match) == 2:
                                    method, endpoint = match
                                    endpoints.append({
                                        'method': method.upper(),
                                        'endpoint': endpoint,
                                        'file': os.path.relpath(file_path, extract_dir)
                                    })
                    except:
                        pass
        
        return endpoints

    def analyze_database_schema(self, extract_dir: str) -> Dict[str, Any]:
        """Analyze database schema from models and SQL files"""
        schema_info = {
            'models': [],
            'tables': [],
            'relationships': []
        }
        
        # Look for SQL files
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.sql'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract CREATE TABLE statements
                        table_pattern = r'CREATE TABLE\s+(\w+)'
                        tables = re.findall(table_pattern, content, re.IGNORECASE)
                        schema_info['tables'].extend(tables)
                    except:
                        pass
        
        # Look for Python models (SQLAlchemy, Django)
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.py') and ('model' in file.lower() or 'schema' in file.lower()):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract class definitions that might be models
                        class_pattern = r'class\s+(\w+).*:'
                        classes = re.findall(class_pattern, content)
                        schema_info['models'].extend(classes)
                    except:
                        pass
        
        return schema_info

    def extract_environment_variables(self, extract_dir: str) -> List[str]:
        """Extract environment variables from various config files"""
        env_vars = set()
        
        # Check .env files
        env_files = ['.env', '.env.example', '.env.local', '.env.production']
        for env_file in env_files:
            env_path = os.path.join(extract_dir, env_file)
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            if '=' in line and not line.strip().startswith('#'):
                                var_name = line.split('=')[0].strip()
                                env_vars.add(var_name)
                except:
                    pass
        
        # Check for environment variable usage in code
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Python: os.environ.get('VAR') or os.getenv('VAR')
                        py_pattern = r'os\.(?:environ\.get|getenv)\(["\']([^"\']+)["\']'
                        # JavaScript: process.env.VAR
                        js_pattern = r'process\.env\.(\w+)'
                        
                        py_matches = re.findall(py_pattern, content)
                        js_matches = re.findall(js_pattern, content)
                        
                        env_vars.update(py_matches)
                        env_vars.update(js_matches)
                    except:
                        pass
        
        return sorted(list(env_vars))

    def analyze_testing_setup(self, extract_dir: str) -> Dict[str, Any]:
        """Analyze testing configuration and files"""
        testing_info = {
            'frameworks': [],
            'test_files': [],
            'coverage_config': False,
            'ci_config': False
        }
        
        # Check for test files
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if ('test' in file.lower() or file.startswith('test_') or 
                    file.endswith('.test.js') or file.endswith('.spec.js')):
                    rel_path = os.path.relpath(os.path.join(root, file), extract_dir)
                    testing_info['test_files'].append(rel_path)
        
        # Check for testing frameworks in dependencies
        package_json = os.path.join(extract_dir, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    test_frameworks = ['jest', 'mocha', 'jasmine', 'cypress', 'playwright']
                    for framework in test_frameworks:
                        if framework in deps:
                            testing_info['frameworks'].append(framework)
            except:
                pass
        
        # Check for Python testing
        requirements_files = ['requirements.txt', 'requirements-dev.txt']
        for req_file in requirements_files:
            req_path = os.path.join(extract_dir, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        content = f.read().lower()
                        if 'pytest' in content:
                            testing_info['frameworks'].append('pytest')
                        if 'unittest' in content:
                            testing_info['frameworks'].append('unittest')
                except:
                    pass
        
        # Check for CI configuration
        ci_files = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile']
        for ci_file in ci_files:
            if os.path.exists(os.path.join(extract_dir, ci_file)):
                testing_info['ci_config'] = True
                break
        
        return testing_info

    def analyze_deployment_config(self, extract_dir: str) -> Dict[str, Any]:
        """Analyze deployment configuration"""
        deployment_info = {
            'docker': False,
            'kubernetes': False,
            'cloud_config': [],
            'deployment_files': []
        }
        
        # Check for Docker
        if os.path.exists(os.path.join(extract_dir, 'Dockerfile')):
            deployment_info['docker'] = True
            deployment_info['deployment_files'].append('Dockerfile')
        
        if os.path.exists(os.path.join(extract_dir, 'docker-compose.yml')):
            deployment_info['deployment_files'].append('docker-compose.yml')
        
        # Check for Kubernetes
        k8s_files = ['deployment.yaml', 'service.yaml', 'ingress.yaml']
        for k8s_file in k8s_files:
            if os.path.exists(os.path.join(extract_dir, k8s_file)):
                deployment_info['kubernetes'] = True
                deployment_info['deployment_files'].append(k8s_file)
        
        # Check for cloud-specific configs
        cloud_configs = {
            'vercel.json': 'Vercel',
            'netlify.toml': 'Netlify',
            'app.yaml': 'Google Cloud',
            'Procfile': 'Heroku',
            'serverless.yml': 'Serverless Framework'
        }
        
        for config_file, platform in cloud_configs.items():
            if os.path.exists(os.path.join(extract_dir, config_file)):
                deployment_info['cloud_config'].append(platform)
                deployment_info['deployment_files'].append(config_file)
        
        return deployment_info

    def analyze_security_features(self, extract_dir: str) -> Dict[str, Any]:
        """Analyze security features and configurations"""
        security_info = {
            'authentication': [],
            'authorization': [],
            'security_headers': False,
            'input_validation': False,
            'encryption': []
        }
        
        # Look for authentication patterns
        auth_patterns = {
            'jwt': 'JWT Authentication',
            'oauth': 'OAuth',
            'passport': 'Passport.js',
            'auth0': 'Auth0',
            'firebase auth': 'Firebase Auth'
        }
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            
                        for pattern, auth_type in auth_patterns.items():
                            if pattern in content:
                                security_info['authentication'].append(auth_type)
                    except:
                        pass
        
        return security_info

    def analyze_performance_aspects(self, extract_dir: str) -> Dict[str, Any]:
        """Analyze performance-related configurations"""
        performance_info = {
            'caching': [],
            'database_optimization': [],
            'cdn_usage': False,
            'compression': False
        }
        
        # Check for caching solutions
        cache_patterns = {
            'redis': 'Redis',
            'memcached': 'Memcached',
            'cache': 'Generic Caching'
        }
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            
                        for pattern, cache_type in cache_patterns.items():
                            if pattern in content:
                                performance_info['caching'].append(cache_type)
                    except:
                        pass
        
        return performance_info

    def create_simple_architecture_diagram(self, analysis: Dict[str, Any]) -> str:
        """Create a simple architecture diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        # Simple boxes for different components
        components = [
            {'name': 'Frontend', 'pos': (2, 4), 'color': 'lightblue'},
            {'name': 'Backend API', 'pos': (2, 2), 'color': 'lightgreen'},
            {'name': 'Database', 'pos': (2, 0), 'color': 'lightcoral'}
        ]
        
        for comp in components:
            x, y = comp['pos']
            rect = plt.Rectangle((x-0.5, y-0.3), 1, 0.6, 
                               facecolor=comp['color'], 
                               edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            ax.text(x, y, comp['name'], ha='center', va='center', 
                   fontsize=12, fontweight='bold')
        
        # Simple arrows
        ax.arrow(2, 3.5, 0, -1, head_width=0.1, head_length=0.1, fc='black', ec='black')
        ax.arrow(2, 1.5, 0, -1, head_width=0.1, head_length=0.1, fc='black', ec='black')
        
        ax.set_xlim(0, 4)
        ax.set_ylim(-1, 5)
        ax.set_title('System Architecture', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        arch_path = os.path.join(self.temp_dir, 'architecture_diagram.png')
        plt.savefig(arch_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return arch_path

    def generate_enhanced_pdf(self, output_path: str, project_title: str, analysis: Dict[str, Any], 
                            summary: str, mcqs: List[Dict] = None, logo_path: str = None) -> str:
        """Generate enhanced PDF documentation"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title Page
        story.append(Paragraph(project_title, self.styles['MainTitle']))
        story.append(Spacer(1, 20))
        
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=2*inch)
                story.append(logo)
                story.append(Spacer(1, 20))
            except:
                pass
        
        story.append(Paragraph("Comprehensive Project Documentation", self.styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal']))
        story.append(PageBreak())
        
        # Project Overview
        story.append(Paragraph("Project Overview", self.styles['SectionHeader']))
        story.append(Paragraph(summary, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Project Statistics
        total_files = analysis['file_structure']['total_files']
        total_lines = analysis['file_structure']['total_lines']
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Files', str(total_files)],
            ['Total Lines of Code', str(total_lines)],
            ['Technologies Used', str(len(analysis['tech_stack']['languages'] + analysis['tech_stack']['frameworks']))]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(PageBreak())
        
        # Technology Stack
        story.append(Paragraph("Technology Stack", self.styles['SectionHeader']))
        
        if analysis['tech_stack']['languages']:
            story.append(Paragraph("Programming Languages", self.styles['SubsectionHeader']))
            lang_text = ", ".join(analysis['tech_stack']['languages'])
            story.append(Paragraph(lang_text, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        if analysis['tech_stack']['frameworks']:
            story.append(Paragraph("Frameworks & Libraries", self.styles['SubsectionHeader']))
            framework_text = ", ".join(analysis['tech_stack']['frameworks'])
            story.append(Paragraph(framework_text, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        story.append(PageBreak())
        
        # Architecture
        story.append(Paragraph("System Architecture", self.styles['SectionHeader']))
        
        try:
            arch_diagram_path = self.create_simple_architecture_diagram(analysis)
            if arch_diagram_path and os.path.exists(arch_diagram_path):
                story.append(Image(arch_diagram_path, width=6*inch, height=3.6*inch))
        except Exception as e:
            print(f"Warning: Could not create architecture diagram: {e}")
        
        story.append(PageBreak())
        
        # File Structure
        story.append(Paragraph("File Structure Analysis", self.styles['SectionHeader']))
        
        file_types = analysis['file_structure']['file_types']
        if file_types:
            type_data = [['File Type', 'Count']]
            for ext, count in file_types.most_common(10):
                type_data.append([ext or 'No extension', str(count)])
            
            type_table = Table(type_data)
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(type_table)
        
        story.append(PageBreak())
        
        # API Endpoints
        if analysis['api_endpoints']:
            story.append(Paragraph("API Endpoints", self.styles['SectionHeader']))
            
            api_data = [['Method', 'Endpoint', 'File']]
            for endpoint in analysis['api_endpoints'][:10]:
                api_data.append([
                    endpoint['method'],
                    endpoint['endpoint'],
                    os.path.basename(endpoint['file'])
                ])
            
            api_table = Table(api_data)
            api_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(api_table)
            story.append(PageBreak())
        
        # MCQs if provided
        if mcqs:
            story.append(Paragraph("Knowledge Assessment", self.styles['SectionHeader']))
            
            for i, mcq in enumerate(mcqs[:5], 1):  # Limit to 5 MCQs
                story.append(Paragraph(f"Q{i}: {mcq.get('question', '')}", self.styles['SubsectionHeader']))
                
                for j, option in enumerate(mcq.get('options', []), 1):
                    story.append(Paragraph(f"{chr(64+j)}. {option}", self.styles['Normal']))
                
                story.append(Paragraph(f"<b>Answer: {mcq.get('answer', '')}</b>", self.styles['InfoBox']))
                story.append(Spacer(1, 15))
        
        # Build PDF
        doc.build(story)
        return output_path


def generate_enhanced_documentation_pdf(
    output_path: str,
    project_title: str,
    summary: str,
    extract_dir: str,
    mcqs: List[Dict] = None,
    logo_path: str = None
) -> str:
    """Main function to generate enhanced documentation"""
    
    print("🔍 Starting comprehensive project analysis...")
    generator = EnhancedDocumentationGenerator()
    
    # Perform comprehensive analysis
    print("📊 Analyzing project structure...")
    project_analysis = generator.analyze_project_structure(extract_dir)
    
    # Update project title if found in analysis
    if project_analysis['project_info']['name'] != os.path.basename(extract_dir):
        project_title = project_analysis['project_info']['name']
    
    print("📄 Generating comprehensive PDF documentation...")
    
    # Generate the comprehensive PDF
    generator.generate_enhanced_pdf(
        output_path=output_path,
        project_title=project_title,
        analysis=project_analysis,
        summary=summary,
        mcqs=mcqs or [],
        logo_path=logo_path
    )
    
    print(f"✅ Enhanced documentation generated successfully: {output_path}")
    return output_path
