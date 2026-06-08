#!/bin/bash
# Deploy to Render

set -e

echo "🚀 Deploying to Render..."

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "ℹ️  Install Render CLI from: https://render.com/docs/deploy-an-app"
fi

# Use git to deploy (recommended method for Render)
echo "📤 Pushing to Git repository..."
git add .
git commit -m "Deploy RAG backend" || true
git push

echo "✅ Deployment initiated!"
echo "Monitor at: https://dashboard.render.com"
