# ==============================================================================
# AgriVision AI - Local Development Environment Setup (Windows PowerShell)
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$SkipDocker,
    [switch]$SkipFlutter,
    [switch]$SkipVenv
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n>>> [AgriVision Dev Setup] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host " [OK] $Message" -ForegroundColor Green
}

function Write-WarnMsg {
    param([string]$Message)
    Write-Host " [WARN] $Message" -ForegroundColor Yellow
}

function Write-Failure {
    param([string]$Message)
    Write-Host " [ERROR] $Message" -ForegroundColor Red
}

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "     AgriVision AI - Development Scaffolding Setup        " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Workspace Root: $RootDir"

# 1. Check Python Version
Write-Step "Checking Python Installation..."
try {
    $pythonVerOutput = python --version 2>&1
    Write-Success "Found: $pythonVerOutput"
    
    # Check Python version >= 3.10
    $match = [regex]::Match($pythonVerOutput, 'Python\s+(\d+)\.(\d+)')
    if ($match.Success) {
        $major = [int]$match.Groups[1].Value
        $minor = [int]$match.Groups[2].Value
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-WarnMsg "Python version $major.$minor detected. AgriVision AI recommends Python 3.10+."
        }
    }
} catch {
    Write-Failure "Python was not found in PATH. Please install Python 3.10+ and re-run."
    exit 1
}

# 2. Virtual Environment Setup
if (-not $SkipVenv) {
    Write-Step "Configuring Python Virtual Environment (.venv)..."
    $venvPath = Join-Path $RootDir ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtual environment at $venvPath..."
        python -m venv $venvPath
        Write-Success "Virtual environment created."
    } else {
        Write-Success "Virtual environment already exists."
    }

    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    $venvPip = Join-Path $venvPath "Scripts\pip.exe"

    if (Test-Path $venvPip) {
        Write-Step "Upgrading pip and installing Python dependencies..."
        & $venvPython -m pip install --upgrade pip setuptools wheel
        
        $backendReq = Join-Path $RootDir "backend\requirements.txt"
        if (Test-Path $backendReq) {
            Write-Host "Installing backend requirements..."
            & $venvPip install -r $backendReq
        }

        $aiReq = Join-Path $RootDir "ai\requirements.txt"
        if (Test-Path $aiReq) {
            Write-Host "Installing AI service requirements..."
            & $venvPip install -r $aiReq
        }
        Write-Success "Python dependencies installed successfully."
    }
}

# 3. Check Flutter & Mobile App Setup
if (-not $SkipFlutter) {
    Write-Step "Checking Flutter SDK..."
    try {
        $flutterVer = flutter --version 2>&1 | Select-Object -First 1
        Write-Success "Found Flutter: $flutterVer"
        
        $farmerAppDir = Join-Path $RootDir "apps\farmer_mobile"
        if (Test-Path $farmerAppDir) {
            Write-Host "Fetching Flutter packages for apps/farmer_mobile..."
            Push-Location $farmerAppDir
            flutter pub get
            Pop-Location
            Write-Success "Flutter dependencies installed."
        }
    } catch {
        Write-WarnMsg "Flutter SDK not found in PATH. Skipping Flutter package resolution."
    }
}

# 4. Check Docker & Docker-Compose
if (-not $SkipDocker) {
    Write-Step "Checking Docker Engine & Compose..."
    try {
        $dockerVer = docker --version 2>&1
        Write-Success "Found Docker: $dockerVer"
        
        $composeFile = Join-Path $RootDir "infrastructure\docker\docker-compose.yml"
        if (Test-Path $composeFile) {
            Write-Host "Starting core services (PostgreSQL, Redis, MinIO, MLflow)..."
            docker compose -f $composeFile up -d postgres redis minio mlflow
            Write-Success "Docker backing services started."
        }
    } catch {
        Write-WarnMsg "Docker is either not running or not in PATH. Backing services were not started automatically."
    }
}

# 5. Environment File Verification
Write-Step "Checking Environment Variables..."
$envFile = Join-Path $RootDir ".env"
$envExample = Join-Path $RootDir ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Success "Created .env from .env.example."
    }
} else {
    Write-Success ".env configuration file is present."
}

# 6. Setup Summary
Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "          AgriVision AI Setup Completed Successfully!     " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Quick Start Commands:" -ForegroundColor Cyan
Write-Host "  1. Activate Virtual Environment:"
Write-Host "     .venv\Scripts\Activate.ps1"
Write-Host "  2. Run Backend (FastAPI):"
Write-Host "     uvicorn backend.main:app --reload --port 8000"
Write-Host "  3. Run AI Service (PyTorch Inference):"
Write-Host "     uvicorn ai.service.main:app --reload --port 8001"
Write-Host "  4. Run Farmer Mobile App (Flutter):"
Write-Host "     cd apps/farmer_mobile && flutter run"
Write-Host "==========================================================`n"
