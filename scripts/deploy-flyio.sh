#!/bin/bash
# Deploy to Fly.io

set -e

echo "🚀 Deploying to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed"
    echo "Install from: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Login to Fly.io
flyctl auth login

# Create app if it doesn't exist
if [ -z "$(flyctl apps list | grep rag-backend)" ]; then
    echo "📝 Creating Fly.io app..."
    flyctl apps create --name rag-backend-api
fi

# Set secrets
echo "🔐 Setting environment secrets..."
flyctl secrets set \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    QDRANT_URL=$QDRANT_URL \
    QDRANT_API_KEY=$QDRANT_API_KEY \
    --app rag-backend-api

# Deploy
echo "📤 Deploying application..."
flyctl deploy --app rag-backend-api

echo "✅ Deployment complete!"
echo "Your app is available at: https://rag-backend-api.fly.dev"
