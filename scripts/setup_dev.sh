#!/usr/bin/env bash
# ==============================================================================
# AgriVision AI - Local Development Environment Setup (Linux / macOS)
# ==============================================================================
set -euo pipefail

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}==========================================================${NC}"
echo -e "${GREEN}     AgriVision AI - Development Scaffolding Setup        ${NC}"
echo -e "${GREEN}==========================================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "Workspace Root: $ROOT_DIR"

# 1. Check Python
echo -e "\n${CYAN}>>> [1/5] Checking Python 3.10+...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH.${NC}"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}[OK] Detected Python $PY_VER${NC}"

# 2. Virtual Environment
echo -e "\n${CYAN}>>> [2/5] Setting up Virtual Environment (.venv)...${NC}"
if [ ! -d ".venv" ]; then
    echo "Creating .venv virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}[OK] Created virtual environment.${NC}"
else
    echo -e "${GREEN}[OK] .venv already exists.${NC}"
fi

source .venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend requirements..."
    pip install -r backend/requirements.txt
fi

if [ -f "ai/requirements.txt" ]; then
    echo "Installing AI service requirements..."
    pip install -r ai/requirements.txt
fi
echo -e "${GREEN}[OK] Python packages installed.${NC}"

# 3. Flutter Check
echo -e "\n${CYAN}>>> [3/5] Checking Flutter SDK...${NC}"
if command -v flutter &> /dev/null; then
    FLUTTER_VER=$(flutter --version | head -n 1)
    echo -e "${GREEN}[OK] Found: $FLUTTER_VER${NC}"
    if [ -d "apps/farmer_mobile" ]; then
        echo "Fetching Flutter dependencies for farmer_mobile..."
        (cd apps/farmer_mobile && flutter pub get)
    fi
else
    echo -e "${YELLOW}[WARN] Flutter SDK not found in PATH. Skipping mobile setup.${NC}"
fi

# 4. Docker & Compose
echo -e "\n${CYAN}>>> [4/5] Checking Docker & Docker Compose...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}[OK] Found Docker: $(docker --version)${NC}"
    if [ -f "infrastructure/docker/docker-compose.yml" ]; then
        echo "Starting backing containers (Postgres, Redis, MinIO, MLflow)..."
        docker compose -f infrastructure/docker/docker-compose.yml up -d postgres redis minio mlflow || true
    fi
else
    echo -e "${YELLOW}[WARN] Docker not installed or daemon not running.${NC}"
fi

# 5. Environment File
echo -e "\n${CYAN}>>> [5/5] Checking Environment Configuration...${NC}"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${GREEN}[OK] Created .env from .env.example.${NC}"
elif [ -f ".env" ]; then
    echo -e "${GREEN}[OK] .env exists.${NC}"
fi

echo -e "\n${GREEN}==========================================================${NC}"
echo -e "${GREEN}          AgriVision AI Setup Completed!                  ${NC}"
echo -e "${GREEN}==========================================================${NC}"
echo -e "Activate virtual environment:"
echo -e "  source .venv/bin/activate"
echo -e "Start Backend:"
echo -e "  uvicorn backend.main:app --reload --port 8000"
echo -e "Start AI Service:"
echo -e "  uvicorn ai.service.main:app --reload --port 8001\n"
