@echo off
REM Setup script for local development on Windows

echo.
echo 🚀 RAG Backend Setup Script
echo.

REM Check Python
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found in PATH
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -e ".[dev]"

REM Create .env if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env with your API keys
)

REM Create directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env with your API keys
echo 2. Run: docker-compose up -d
echo 3. Run: uvicorn src.api.main:app --reload
echo.
