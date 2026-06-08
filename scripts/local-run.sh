#!/bin/bash
# Local development startup script

set -e

echo "🚀 Starting RAG Backend locally..."

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Start docker-compose services
echo "🐳 Starting Docker Compose services..."
docker-compose up -d

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
while ! curl -s http://localhost:6333/health > /dev/null; do
    sleep 1
done
echo "✓ Qdrant is ready"

# Start the API
echo "🚀 Starting API server..."
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
