# Deployment Guide

This guide covers deploying the RAG Backend API to various cloud platforms.

## Prerequisites

- Docker installed locally
- GitHub account and repository
- API keys (OpenAI, Groq, Qdrant if using cloud)

## Local Development

### Using Docker Compose (Recommended)

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Start API server:**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access API:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health: http://localhost:8000/health

### Using Local Qdrant

If you don't want Docker, install Qdrant locally:

```bash
# macOS
brew install qdrant

# Or download from https://qdrant.tech/documentation/guides/installation/
```

Then configure `.env` to point to your local Qdrant instance.

## Cloud Deployment

### Option 1: Fly.io (Recommended for beginners)

**Pros:** Free tier, simple CLI, fast deployments
**Cons:** Limited free tier resources

1. **Install flyctl:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create Fly.io account:**
   ```bash
   flyctl auth signup
   ```

3. **Deploy:**
   ```bash
   # Set secrets
   flyctl secrets set OPENAI_API_KEY=<your-key>
   flyctl secrets set QDRANT_URL=<your-qdrant-url>
   flyctl secrets set QDRANT_API_KEY=<your-qdrant-key>

   # Deploy
   flyctl deploy
   ```

4. **Monitor:**
   ```bash
   flyctl logs --app rag-backend-api
   ```

**Using Qdrant Cloud with Fly.io:**
- Create account at https://cloud.qdrant.io
- Use Qdrant Cloud URL and API key in environment variables

### Option 2: Render

**Pros:** Generous free tier, GitHub integration, easy scaling
**Cons:** Slightly slower cold starts

1. **Connect GitHub repository:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure service:**
   - Name: `rag-backend-api`
   - Environment: `Docker`
   - Build Command: (leave empty, uses Dockerfile)
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

3. **Add environment variables:**
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `OPENAI_API_KEY=<secret>`
   - `QDRANT_URL=<your-url>`
   - `QDRANT_API_KEY=<secret>`

4. **Deploy:**
   - Click "Create Web Service"
   - Render will auto-deploy on git push

**Database considerations:**
- Use Qdrant Cloud (recommended)
- Or add a PostgreSQL service on Render for persistence

### Option 3: AWS App Runner

**Pros:** Scalable, pay-as-you-go, integrates with AWS ecosystem
**Cons:** More complex setup

1. **Build and push Docker image to ECR:**
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name rag-backend-api

   # Get login token
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build and push
   docker build -t rag-backend-api:latest .
   docker tag rag-backend-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend-api:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend-api:latest
   ```

2. **Create App Runner service:**
   ```bash
   aws apprunner create-service \
     --service-name rag-backend-api \
     --source-configuration ImageRepository={ImageIdentifier=<account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend-api:latest,ImageRepositoryType=ECR}
   ```

3. **Configure environment:**
   - Add environment variables in App Runner console
   - Set secrets in AWS Secrets Manager

### Option 4: Google Cloud Run

**Pros:** Excellent serverless platform, good free tier
**Cons:** Cold starts for long-running operations

1. **Build and push to GCR:**
   ```bash
   gcloud auth configure-docker
   docker build -t gcr.io/<project-id>/rag-backend-api:latest .
   docker push gcr.io/<project-id>/rag-backend-api:latest
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy rag-backend-api \
     --image gcr.io/<project-id>/rag-backend-api:latest \
     --region us-central1 \
     --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,QDRANT_URL=$QDRANT_URL \
     --memory 2Gi
   ```

## Database Options

### Qdrant Cloud (Recommended for production)

1. **Sign up:** https://cloud.qdrant.io
2. **Create cluster:** Choose region, size, API key
3. **Configure in .env:**
   ```
   QDRANT_URL=https://your-cluster.qdrant.io:6333
   QDRANT_API_KEY=your-api-key
   ```

### Self-hosted Qdrant

Option A: Docker container
```bash
docker run -p 6333:6333 qdrant/qdrant
```

Option B: Kubernetes
```bash
helm repo add qdrant https://qdrant.github.io/helm-charts
helm install qdrant-release qdrant/qdrant
```

## Monitoring & Logs

### Fly.io
```bash
flyctl logs --app rag-backend-api
```

### Render
- Logs available in Render dashboard under Service

### AWS App Runner
- CloudWatch logs in AWS console

### Google Cloud Run
- Cloud Logging in GCP console

## Scaling Considerations

1. **Horizontal scaling:**
   - Render: Increase instance count
   - Fly.io: Use `flyctl scale count <number>`
   - Cloud Run: Auto-scales automatically

2. **Database scaling:**
   - Qdrant Cloud: Upgrade cluster size
   - Self-hosted: Increase pod replicas

3. **Performance tuning:**
   - Increase `VECTOR_EMBEDDING_DIM` for better accuracy
   - Tune `TOP_K_RETRIEVAL` for speed vs recall tradeoff
   - Enable caching for repeated queries

## Security Best Practices

1. **Environment variables:**
   - Never commit `.env` files
   - Use platform secrets (Fly.io secrets, Render environment)
   - Rotate API keys regularly

2. **CORS:**
   - Configure `CORS_ORIGINS` for allowed domains
   - Disable in production if not needed

3. **Rate limiting:**
   - Consider using middleware for rate limiting
   - Monitor API usage

4. **Network:**
   - Use HTTPS/TLS (automatic on Render, Fly.io, Cloud Run)
   - Restrict Qdrant access with API keys
   - Consider VPN for internal services

## Troubleshooting

### API won't start
- Check Docker Compose is running: `docker-compose ps`
- Check logs: `docker-compose logs api`
- Verify API keys in `.env`

### No documents retrieved
- Ingest documents first: `python scripts/ingest_sample_data.py`
- Check Qdrant connection: `curl http://localhost:6333/health`

### Slow queries
- Check network latency to Qdrant
- Verify TOP_K_RETRIEVAL isn't too high
- Monitor API resource usage

### High costs
- Monitor Qdrant Cloud usage
- Consider batch operations
- Cache embedding results
