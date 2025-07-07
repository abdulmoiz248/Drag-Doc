import os
import zipfile
import shutil

noiseDirs = [
    'node_modules', '__pycache__', '.venv', 'env', 'venv', '.git', '.next',
    'build', 'dist', 'out', 'target', '.gradle', '.terraform', '.scannerwork',
    '.expo', '.parcel-cache', '.idea', '.vscode', '.pytest_cache', '.mypy_cache',
    '.cache', '.github', '.circleci', '.husky', 'coverage', '__tests__', 'tests',
    'logs', 'log', '.history', 'ui'
]

noiseFiles = [
    '.gitignore', '.dockerignore', '.env', '.env.local', '.editorconfig', 'README.md',
    'README', 'LICENSE', 'Makefile', 'Dockerfile', 'docker-compose.yml', 'yarn.lock','package.json',
    'package-lock.json', 'pnpm-lock.yaml', 'poetry.lock', 'Pipfile.lock', 'requirements.txt',
    'tsconfig.json', 'jsconfig.json', 'babel.config.js', 'webpack.config.js',
    'vite.config.js', 'CMakeLists.txt', 'setup.py', 'setup.cfg', 'pyproject.toml',
    '.prettierrc', '.eslintrc', '.stylelintrc', 'Procfile', '.ngrok.yml', '.env.example' 
]

extensionsToDelete = [
    '.png', '.jpeg', '.jpg', '.gif', '.svg', '.ico', '.webp',
    '.mp4', '.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.m4v', '.mov',
    '.avi', '.wmv', '.webm', '.mkv', '.flv', '.vob', '.ogv', '.m3u8', '.ts',
    '.log', '.lock', '.tmp', '.bak', '.class', '.o', '.a', '.jar',
    '.exe', '.dll', '.so', '.dylib', '.iml', '.ipynb_checkpoints', '.csv' , '.pptx' ,'.txt', '.docx','.pdf'
]

def unzipAndClean(zipPath, extractTo="backend/extracted"):
    if os.path.exists(extractTo):
        shutil.rmtree(extractTo)
    with zipfile.ZipFile(zipPath, 'r') as zip_ref:
        zip_ref.extractall(extractTo)
    stripNoise(extractTo)
    return extractTo

def stripNoise(path):
    for root, dirs, files in os.walk(path, topdown=False):
        # remove noise directories
        for d in dirs:
            dPath = os.path.join(root, d)
            if d in noiseDirs:
                try:
                    shutil.rmtree(dPath, ignore_errors=True)
                    print(f"🗑️ Removed directory: {dPath}")
                except:
                    pass

        # remove noise files
        for f in files:
            fLower = f.lower()
            fPath = os.path.join(root, f)

            if fLower in noiseFiles or fLower.startswith('.') or any(fLower.endswith(ext) for ext in extensionsToDelete):
                try:
                    os.remove(fPath)
                    print(f"🗑️ Removed file: {fPath}")
                except:
                    pass
