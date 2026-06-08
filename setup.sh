#!/bin/bash
# Setup script for local development

set -e

echo "🚀 RAG Backend Setup Script"

# Check Python version
python_version=$(python --version | cut -d' ' -f2)
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e ".[dev]"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
fi

# Create data directory
mkdir -p data logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: docker-compose up -d"
echo "3. Run: uvicorn src.api.main:app --reload"
echo ""
