# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key (https://platform.openai.com/api-keys)
- Git

### Step 1: Clone & Setup
```bash
git clone <your-repo>
cd rag_backend
cp .env.example .env
```

### Step 2: Configure API Keys
Edit `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
ENVIRONMENT=development
DEBUG=true
```

### Step 3: Start Services
```bash
docker-compose up -d
```

Wait for Qdrant to be ready (check `docker-compose logs qdrant`).

### Step 4: Start API
```bash
pip install -e .
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Try It Out

**In another terminal:**

```bash
# Ingest sample data
python scripts/ingest_sample_data.py

# Test a query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'

# View docs
# Open: http://localhost:8000/docs
```

## What's Next?

### 1. **Ingest Your Documents**
```python
from src.ingestion.document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.ingest_pdfs("./path/to/pdfs/")
print(f"Ingested {result['total_chunks']} chunks")
```

### 2. **Query the System**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "temperature": 0.7
  }'
```

### 3. **Deploy to Production**
- See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud options
- Recommended: Fly.io for quick start

### 4. **Evaluate Quality**
```bash
curl -X POST http://localhost:8000/admin/evaluate
```

## Project Structure at a Glance

```
rag_backend/
├── src/
│   ├── api/              # FastAPI routes
│   ├── ingestion/        # Document processing
│   ├── retrieval/        # Search & ranking
│   └── core/            # Config & logging
├── scripts/             # Helper scripts
├── tests/               # Test suite
├── Dockerfile           # Production image
├── docker-compose.yml   # Local dev stack
└── README.md            # Full documentation
```

## Common Commands

```bash
# Development
make dev          # Install dev dependencies
make local-run    # Start local dev server
make test         # Run tests
make lint         # Check code quality

# Docker
docker-compose up -d      # Start services
docker-compose logs -f    # View logs
docker-compose down       # Stop services

# Ingestion
python scripts/ingest_sample_data.py

# Query
python scripts/test_query.py
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/query` | POST | Query RAG system |
| `/query/stream` | POST | Streaming query |
| `/ingest` | POST | Ingest documents |
| `/admin/evaluate` | POST | Run evaluation |
| `/docs` | GET | Interactive API docs |

## Troubleshooting

### "Connection refused" errors
```bash
# Check if Qdrant is running
docker-compose ps
docker-compose logs qdrant
```

### "API key not found" 
```bash
# Verify .env file
cat .env | grep OPENAI_API_KEY
```

### Port already in use
```bash
# Change port in .env or:
uvicorn src.api.main:app --port 8001
```

## Documentation

- **[README.md](README.md)** - Project overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guide

## Support

- Create GitHub issues for bugs
- Check existing issues for FAQ
- See CONTRIBUTING.md for development questions
