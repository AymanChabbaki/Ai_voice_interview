# Makefile for AI Voice Interview Project
# Simple commands for Docker and development tasks

.PHONY: help build up down restart logs test clean deploy

# Default target
help:
	@echo "AI Voice Interview - Available Commands:"
	@echo ""
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services (detached)"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View backend logs"
	@echo "  make logs-db        - View database logs"
	@echo "  make test           - Run backend tests"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make shell          - Open backend container shell"
	@echo "  make db-shell       - Open database shell"
	@echo "  make clean          - Stop services and remove volumes"
	@echo "  make deploy-prod    - Build and deploy to production"
	@echo ""

# Build Docker images
build:
	docker-compose build

# Start services in detached mode
up:
	docker-compose up -d
	@echo "Services started! Backend: http://localhost:8000"

# Stop services
down:
	docker-compose down

# Restart services
restart: down up

# View backend logs
logs:
	docker-compose logs -f backend

# View database logs
logs-db:
	docker-compose logs -f db

# Run tests in backend container
test:
	docker-compose exec backend pytest -v

# Run tests with coverage
test-cov:
	docker-compose exec backend pytest -v --cov=. --cov-report=html --cov-report=term

# Open shell in backend container
shell:
	docker-compose exec backend /bin/bash

# Open PostgreSQL shell
db-shell:
	docker-compose exec db psql -U interview_user -d interview_db

# Clean up everything (including volumes)
clean:
	docker-compose down -v
	@echo "All services stopped and volumes removed"

# Production deployment
deploy-prod:
	@echo "Building production image..."
	cd backend && docker build -t ai-interview-backend:latest .
	@echo "Build complete! Push to registry:"
	@echo "  docker tag ai-interview-backend:latest your-registry/ai-interview-backend:latest"
	@echo "  docker push your-registry/ai-interview-backend:latest"

# Development mode with live reload
dev:
	docker-compose -f docker-compose.yml up

# Check service health
health:
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/health && echo "\n✓ Backend is healthy" || echo "\n✗ Backend is not responding"
	@echo "Checking database..."
	@docker-compose exec db pg_isready -U interview_user && echo "✓ Database is ready" || echo "✗ Database is not ready"

# Initialize database
db-init:
	docker-compose exec backend python -c "from database import init_db; init_db()"
	@echo "Database initialized"

# Backup database
db-backup:
	@mkdir -p backups
	docker-compose exec db pg_dump -U interview_user interview_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backups/"

# Restore database from backup
db-restore:
	@if [ -z "$(file)" ]; then echo "Usage: make db-restore file=backups/backup_YYYYMMDD_HHMMSS.sql"; exit 1; fi
	docker-compose exec -T db psql -U interview_user interview_db < $(file)
	@echo "Database restored from $(file)"
