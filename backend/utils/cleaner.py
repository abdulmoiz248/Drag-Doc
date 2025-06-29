import os
import zipfile
import shutil

noiseDirs = [
    'node_modules', '__pycache__', '.venv', 'env', 'venv', '.git', '.next',
    'build', 'dist', 'out', 'target', '.gradle', '.terraform', '.scannerwork',
    '.expo', '.parcel-cache', '.idea', '.vscode', '.pytest_cache', '.mypy_cache',
    '.cache', '.github', '.circleci', '.husky', 'coverage', '__tests__', 'tests',
    'logs', 'log', '.history'
]

noiseFiles = [
    '.gitignore', '.dockerignore', '.env', '.env.local', '.editorconfig', 'README.md',
    'README', 'LICENSE', 'Makefile', 'Dockerfile', 'docker-compose.yml', 'yarn.lock',
    'package-lock.json', 'pnpm-lock.yaml', 'poetry.lock', 'Pipfile.lock', 'requirements.txt',
    'tsconfig.json', 'jsconfig.json', 'babel.config.js', 'webpack.config.js',
    'vite.config.js', 'CMakeLists.txt', 'setup.py', 'setup.cfg', 'pyproject.toml',
    '.prettierrc', '.eslintrc', '.stylelintrc', 'Procfile'
]

extensionsToDelete = [
    '.log', '.lock', '.tmp', '.bak', '.class', '.o', '.a', '.jar',
    '.exe', '.dll', '.so', '.dylib', '.iml', '.ipynb_checkpoints', '.csv'
]

def unzipAndClean(zipPath, extractTo="backend/extracted"):
    if os.path.exists(extractTo):
        shutil.rmtree(extractTo)
    with zipfile.ZipFile(zipPath, 'r') as zip_ref:
        zip_ref.extractall(extractTo)
    stripNoise(extractTo)
    return extractTo

def stripNoise(path):
    for root, dirs, files in os.walk(path, topdown=True):
        # Strip unwanted folders
        dirs[:] = [d for d in dirs if d not in noiseDirs]

        for d in noiseDirs:
            fullPath = os.path.join(root, d)
            if os.path.isdir(fullPath):
                shutil.rmtree(fullPath, ignore_errors=True)

        for f in files:
            fLower = f.lower()
            fullPath = os.path.join(root, f)

            if fLower in noiseFiles:
                os.remove(fullPath)
                continue

            if fLower.startswith('.') or any(fLower.endswith(ext) for ext in extensionsToDelete):
                try: os.remove(fullPath)
                except: pass
