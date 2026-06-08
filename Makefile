# Deployment Makefile for common tasks

.PHONY: help install dev test lint format clean docker-build docker-run local-run eval docs

help:
	@echo "RAG Backend API - Development Makefile"
	@echo "Available targets:"
	@echo "  install       - Install dependencies"
	@echo "  dev           - Install dev dependencies"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linters (ruff, mypy)"
	@echo "  format        - Format code with black"
	@echo "  clean         - Remove build artifacts"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  local-run     - Run locally with uvicorn"
	@echo "  compose-up    - Start docker-compose stack"
	@echo "  compose-down  - Stop docker-compose stack"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	ruff check src/ tests/ --fix

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage

docker-build:
	docker build -t rag-backend:latest .

docker-run: docker-build
	docker run -p 8000:8000 --env-file .env rag-backend:latest

local-run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

compose-up:
	docker-compose up -d

compose-down:
	docker-compose down

logs:
	docker-compose logs -f api

# Ingestion helpers
ingest-sample-pdf:
	python -c "from src.ingestion.document_processor import DocumentProcessor; p = DocumentProcessor(); print(p.ingest_pdfs('./data'))"

# Quick start
quickstart: install compose-up local-run
