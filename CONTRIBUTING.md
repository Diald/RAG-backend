# Contributing Guide

## Development Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Quick Start

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd rag_backend
   ```

2. **Run setup script:**
   ```bash
   # macOS/Linux
   bash setup.sh

   # Windows
   setup.bat
   ```

3. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit with your API keys
   ```

4. **Start development environment:**
   ```bash
   docker-compose up -d
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Code Style

### Formatting

Use Black and Ruff:

```bash
# Format code
make format

# Or manually
black src/ tests/
ruff check src/ tests/ --fix
```

### Type Hints

All new code must include type hints:

```python
def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Retrieve documents."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Retrieve relevant documents.

    Args:
        query: Query text
        top_k: Number of documents to retrieve

    Returns:
        List of retrieved documents with metadata

    Raises:
        ValueError: If query is empty
    """
    pass
```

## Testing

### Run all tests:
```bash
make test
```

### Run specific test file:
```bash
pytest tests/test_api.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

### Test naming conventions:
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

## Project Structure

```
src/
├── api/              # FastAPI routes and schemas
├── ingestion/        # Document processing
├── retrieval/        # Hybrid search and reranking
└── core/            # Config, logging, utilities

tests/
├── test_api.py      # API endpoint tests
├── test_retrieval.py # Retrieval module tests
└── conftest.py      # pytest fixtures
```

## Adding New Features

### 1. Create Feature Branch
```bash
git checkout -b feature/my-feature
```

### 2. Implement with Tests
```bash
# Create test file
vim tests/test_my_feature.py

# Implement feature
vim src/module/my_feature.py

# Run tests
pytest tests/test_my_feature.py -v
```

### 3. Update Documentation
- Update README.md if user-facing
- Add docstrings to public APIs
- Update DEPLOYMENT.md if infrastructure changes

### 4. Commit and Push
```bash
git add .
git commit -m "feat: add my feature description"
git push origin feature/my-feature
```

### 5. Create Pull Request
- Add clear description
- Link related issues
- Ensure all tests pass

## Common Tasks

### Add a new dependency:
```bash
# Update pyproject.toml
vim pyproject.toml

# Install
pip install -e ".[dev]"
```

### Run linting:
```bash
make lint
```

### Fix type errors:
```bash
mypy src/ --ignore-missing-imports
```

### Test locally with docker-compose:
```bash
docker-compose up -d
# Make changes
docker-compose restart api
```

## Debugging

### Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Python debugger:
```python
import pdb; pdb.set_trace()
```

### Docker container logs:
```bash
docker-compose logs -f api
```

## Performance Tips

1. **Caching:** Use functools.lru_cache for expensive operations
2. **Async:** Use async/await for I/O operations
3. **Batching:** Process multiple items together when possible
4. **Vectorization:** Use batch embedding for multiple texts

## Reporting Issues

Include:
- Python version
- Full error traceback
- Steps to reproduce
- Expected vs actual behavior

Example:
```
Title: Queries timing out on large documents

Description:
When indexing PDFs > 100MB, queries timeout after 30s

Steps:
1. Ingest large PDF
2. Run /query endpoint
3. Times out

Expected: Should return results within timeout
Actual: Timeout error

Environment:
- Python 3.11
- Docker on M1 Mac
- Qdrant 2.7.0
```

## Questions?

- Check [README.md](README.md)
- Review [DEPLOYMENT.md](DEPLOYMENT.md)
- Open GitHub issue
