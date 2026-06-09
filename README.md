# RAG Backend API

A production-grade Retrieval-Augmented Generation (RAG) backend API built with FastAPI, LlamaIndex, and Qdrant.

## Architecture

- **Ingestion Module** (`src/ingestion/`): Parse documents, apply parent-child chunking, generate embeddings
- **Retrieval Module** (`src/retrieval/`): Hybrid search with reranking
- **API Module** (`src/api/`): FastAPI routes for querying and evaluation
- **Core Module** (`src/core/`): Shared configurations, logging, and utilities

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API key (or Groq key)

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repo>
   cd rag_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Run the API:**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **API will be available at:** `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`

### Ingestion

To ingest documents:

```python
from src.ingestion.document_processor import DocumentProcessor

processor = DocumentProcessor()
processor.ingest_pdfs(pdf_dir="./documents", chunk_size=1024, chunk_overlap=128)
```

## API Endpoints

- `POST /query` - Query the RAG system
- `POST /admin/evaluate` - Run Ragas evaluation
- `GET /health` - Health check

## Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

### Using Render

Push to Render:

```bash
render deploy
```

Configuration in `render.yaml`.

### Using Fly.io

```bash
flyctl deploy
```

Configuration in `fly.toml`.

## Project Structure

```
rag_backend/
├── src/
│   ├── ingestion/          # Document processing & embedding
│   ├── retrieval/          # Search and reranking
│   ├── api/                # FastAPI application
│   └── core/               # Shared config, logging, utils
├── tests/                  # Test suite
├── data/                   # Document storage
├── Dockerfile              # Container image
├── docker-compose.yml      # Local development stack
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Configuration

All environment variables are in `.env`. Key variables:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication |
| `QDRANT_URL` | Qdrant vector DB endpoint |
| `QDRANT_API_KEY` | Qdrant authentication (optional) |
| `VECTOR_EMBEDDING_DIM` | Embedding dimension (default: 1536) |
| `TOP_K_RETRIEVAL` | Number of documents to retrieve |
| `RERANKER_TOP_K` | Number of docs after reranking |

## Development

Run tests:

```bash
pytest tests/ -v --cov=src
```

Format code:

```bash
black src/ tests/
ruff check src/ tests/ --fix
```
