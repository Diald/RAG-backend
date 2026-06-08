# Architecture Documentation

## System Overview

The RAG Backend API is a modular, production-grade Retrieval-Augmented Generation system built with FastAPI, LlamaIndex, and Qdrant.

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────┐
│                   FastAPI Application                       │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Query Routes  │  │ Ingestion API  │  │ Admin Routes │  │
│  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘  │
└───────────┼─────────────────────┼──────────────────┼────────┘
            │                     │                  │
┌───────────▼─────────────────────▼──────────────────▼────────┐
│                    Core Services Layer                       │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Retrieval        │  │ Ingestion        │                │
│  │ - HybridRetriever│  │ - DocumentProc   │                │
│  │ - Reranker       │  │ - ParentChild    │                │
│  │ - EmbeddingService│  │   Splitter       │                │
│  │ - LLMService     │  │                  │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
└───────────┼─────────────────────┼─────────────────────────┘
            │                     │
┌───────────▼─────────────────────▼─────────────────────────┐
│                 External Services                         │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │  Vector Database │  │   LLM Providers              │  │
│  │  (Qdrant)        │  │   - OpenAI (gpt-4o-mini)    │  │
│  │  - Dense Search  │  │   - Groq (mixtral-8x7b)     │  │
│  │  - Hybrid Search │  │   - Embeddings (OAI)        │  │
│  └──────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`src/api/`)

**Responsibility:** HTTP interface and request/response handling

**Key Files:**
- `main.py`: FastAPI application with all routes
- `schemas.py`: Pydantic models for validation
- `evaluation_service.py`: Ragas integration for quality metrics

**Routes:**
- `GET /health` - Health check
- `POST /query` - Query with retrieval and generation
- `POST /query/stream` - Streaming responses
- `POST /ingest` - Document ingestion
- `POST /admin/evaluate` - Quality evaluation

### 2. Retrieval Layer (`src/retrieval/`)

**Responsibility:** Document retrieval, ranking, and response generation

**Components:**

#### HybridRetriever
- Combines dense vector search with optional sparse search
- Uses Qdrant for vector operations
- Integrates reranking for improved relevance

```python
# Flow
Query → Embedding → Dense Search → Reranking → Top-K Results
```

#### EmbeddingService
- Generates embeddings using OpenAI's text-embedding-3-small
- Supports batch operations for efficiency
- Caches embeddings for repeated queries

#### LLMService
- Abstract LLM interface (OpenAI or Groq)
- Supports both sync and streaming responses
- Incorporates retrieved context in prompts

#### LightweightReranker
- Hybrid scoring: BM25 + Vector similarity
- Configurable weighting (default: 30% BM25, 70% Vector)
- Optimized for production performance

### 3. Ingestion Layer (`src/ingestion/`)

**Responsibility:** Document processing and embedding generation

**Components:**

#### ParentChildSplitter
- Hierarchical chunking strategy
- Large parent chunks for context
- Small child chunks for precise retrieval
- Maintains parent-child relationships

```
Document
  ├── Parent Chunk 1 (2048 tokens)
  │   ├── Child 1 (512 tokens)
  │   └── Child 2 (512 tokens)
  └── Parent Chunk 2 (2048 tokens)
      ├── Child 3 (512 tokens)
      └── Child 4 (512 tokens)
```

#### DocumentProcessor
- Loads PDFs using LlamaIndex
- Applies hierarchical chunking
- Generates embeddings
- Upserts to Qdrant collection

### 4. Core Layer (`src/core/`)

**Responsibility:** Shared infrastructure

**Components:**

#### Settings (Pydantic v2)
- Environment-driven configuration
- Type-safe with full validation
- Singleton pattern with lru_cache

#### Logging
- Structured JSON logging for production
- Console logging for development
- Integrated with structlog

#### Utils
- Helper functions
- Async utilities

## Data Flow

### Query Flow
```
1. User submits query
   └─→ QueryRequest validated with Pydantic

2. Retrieval
   ├─→ Query text embedded (OpenAI)
   ├─→ Dense vector search (Qdrant)
   └─→ Reranking with BM25 + vector score

3. Context Assembly
   └─→ Top-K documents formatted with metadata

4. LLM Generation
   ├─→ Prompt constructed with context
   ├─→ LLM called (OpenAI or Groq)
   └─→ Response generated

5. Response
   └─→ QueryResponse with answer + sources
```

### Ingestion Flow
```
1. User uploads PDF/Markdown
   └─→ IngestDocumentsRequest validated

2. Document Loading
   ├─→ PDF parsed (PDFReader via LlamaIndex)
   └─→ Metadata extracted

3. Hierarchical Chunking
   ├─→ Large parent chunks created
   ├─→ Small child chunks created
   └─→ Parent-child relationships maintained

4. Embedding Generation
   ├─→ Each chunk embedded (batch)
   └─→ Embeddings normalized

5. Vector Storage
   ├─→ Points prepared with metadata
   └─→ Upserted to Qdrant collection

6. Response
   └─→ IngestDocumentsResponse with stats
```

## Database Schema

### Qdrant Collection: `rag_documents`

**Vector Configuration:**
- Dimension: 1536 (text-embedding-3-small)
- Distance: Cosine similarity
- Index: HNSW (Hierarchical Navigable Small World)

**Point Payload:**
```json
{
  "id": "<hash of content>",
  "vector": [float; 1536],
  "payload": {
    "text": "chunk content",
    "metadata": {
      "doc_id": "source_id",
      "is_parent": false,
      "source": "pdf_name"
    },
    "node_id": "unique_node_id"
  }
}
```

## Deployment Architecture

### Development
```
Docker Compose
├── FastAPI (src.api.main:app)
├── Qdrant (qdrant/qdrant:latest)
└── Volumes for persistence
```

### Production Options

#### Option 1: Fly.io
```
Fly.io VM
├── Multi-stage Docker build
├── Non-root user execution
└── Health checks
```

#### Option 2: Render
```
Render Web Service
├── GitHub-connected auto-deploy
├── Docker build on platform
└── Optional Render PostgreSQL
```

#### Option 3: Cloud Run / App Runner
```
Containerized Serverless
├── Auto-scaling
├── Pay-as-you-go
└── Managed infrastructure
```

## Scalability Considerations

### Horizontal Scaling

1. **Stateless API Servers**
   - Each instance independent
   - Load balanced across instances
   - No session affinity needed

2. **Qdrant Scaling**
   - Self-hosted: Kubernetes StatefulSet
   - Cloud: Qdrant Cloud with auto-scaling

3. **Cache Layer** (Future)
   - Redis for embedding cache
   - FastCache for recent queries

### Performance Optimization

1. **Batch Operations**
   - Batch embedding generation
   - Batch ingestion processing

2. **Caching**
   - LRU cache for embeddings
   - Query result caching

3. **Async Processing**
   - FastAPI background tasks
   - Non-blocking I/O throughout

4. **Reranking Optimization**
   - Lightweight BM25 + vector hybrid scoring
   - Configurable top-k for recall/latency tradeoff

## Security Architecture

### Authentication & Authorization
- TBD: API key authentication
- TBD: Role-based access control
- Environment-based admin endpoints

### Data Protection
- API keys in environment variables (never in code)
- HTTPS/TLS in production
- Qdrant API key authentication

### Network Security
- CORS configuration
- Rate limiting (configurable)
- Input validation (Pydantic)

## Monitoring & Observability

### Logging
- Structured JSON logging
- Log levels configurable
- Integrated with structlog

### Health Checks
- `/health` endpoint
- Database connectivity verification
- Service status reporting

### Future: Metrics & Tracing
- Prometheus metrics
- OpenTelemetry integration
- Response time tracking

## Error Handling

### Strategy
1. Validation errors → 400 Bad Request
2. Not found errors → 404 Not Found
3. Processing errors → 500 Internal Server Error
4. All errors logged with context

### Recovery
- Graceful degradation
- Fallback responses
- Circuit breaker pattern (future)

## Extension Points

### Adding New LLM Providers
1. Implement provider in `LLMService`
2. Update configuration
3. Add tests

### Custom Rerankers
1. Implement `BaseReranker` interface
2. Integrate into `HybridRetriever`
3. Configure weights

### Additional Document Types
1. Add loader in `DocumentProcessor`
2. Update `ParentChildSplitter` if needed
3. Add ingestion endpoint

## Technology Choices Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastAPI | Async-first, modern, excellent validation |
| Vector DB | Qdrant | Rust-based, production-ready, self-hosted option |
| Embeddings | OpenAI | Reliable, well-documented, excellent quality |
| LLM | OpenAI/Groq | Production-grade, diverse models, good APIs |
| Evaluation | Ragas | Specialized RAG evaluation, open-source |
| Chunking | Custom | Fine-grained control, parent-child relationships |
| Reranking | BM25 | Lightweight, proven, no extra dependencies |

## Future Enhancements

1. **Advanced Retrieval**
   - Multi-vector retrieval
   - Cross-encoder reranking
   - Query expansion

2. **Knowledge Graphs**
   - Entity extraction
   - Relationship mapping
   - Graph-based retrieval

3. **Fine-tuning**
   - Domain-specific embedding models
   - Specialized rerankers

4. **Distributed Processing**
   - Celery for async tasks
   - Distributed indexing
   - Multi-GPU processing

5. **Advanced Monitoring**
   - Prometheus metrics
   - OpenTelemetry tracing
   - Query analytics dashboard
