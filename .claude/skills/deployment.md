---
description: Deployment with Docker, Docker Compose, CI/CD pipelines, environment management, and production best practices
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Deployment Expert Skill

You are an expert in deploying Python/FastAPI applications using Docker, CI/CD pipelines, and cloud platforms with production-grade configurations.

### Deployment Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                           │
├─────────────────────────────────────────────────────────────┤
│  Code Push → Build → Test → Lint → Build Image → Deploy     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Container Registry                        │
│              (Docker Hub / GitHub / AWS ECR)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Production Environment                        │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer → App Containers → Database → Cache          │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```text
project/
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline
│       ├── cd.yml           # CD pipeline
│       └── pr.yml           # PR checks
├── docker/
│   ├── Dockerfile           # Production image
│   ├── Dockerfile.dev       # Development image
│   └── entrypoint.sh        # Container entrypoint
├── docker-compose.yml       # Local development
├── docker-compose.prod.yml  # Production compose
├── .dockerignore
├── .env.example
├── scripts/
│   ├── start.sh
│   ├── healthcheck.sh
│   └── migrate.sh
└── k8s/                     # Kubernetes manifests (optional)
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

### Production Dockerfile

```dockerfile
# docker/Dockerfile

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser docker/entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Development Dockerfile

```dockerfile
# docker/Dockerfile.dev

FROM python:3.12-slim

WORKDIR /app

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application (will be overridden by volume mount)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Entrypoint Script

```bash
#!/bin/bash
# docker/entrypoint.sh

set -e

echo "Starting application..."

# Wait for database to be ready
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        sleep 1
    done
    echo "Database is ready!"
fi

# Run database migrations
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Execute the main command
exec "$@"
```

### Docker Compose - Development

```yaml
# docker-compose.yml

version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /app/__pycache__
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

  pgadmin:
    image: dpage/pgadmin4
    ports:
      - "5050:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    depends_on:
      - db
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### Docker Compose - Production

```yaml
# docker-compose.prod.yml

version: '3.8'

services:
  app:
    image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG:-latest}
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - RUN_MIGRATIONS=true
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### .dockerignore

```text
# .dockerignore

# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.venv
venv/
ENV/

# Testing
.pytest_cache
.coverage
htmlcov/
.tox

# IDE
.idea/
.vscode/
*.swp
*.swo

# Docker
Dockerfile*
docker-compose*
.docker

# Documentation
docs/
*.md
!README.md

# Local files
.env
.env.*
!.env.example
*.log
*.sqlite

# CI/CD
.github/
.gitlab-ci.yml
```

### GitHub Actions - CI Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: '3.12'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install ruff mypy

      - name: Run Ruff linter
        run: ruff check .

      - name: Run Ruff formatter check
        run: ruff format --check .

      - name: Run MyPy
        run: mypy app/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: test-secret-key
          ENVIRONMENT: testing
        run: |
          pytest --cov=app --cov-report=xml --cov-report=html

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: pip install bandit safety

      - name: Run Bandit security scan
        run: bandit -r app/ -ll

      - name: Check dependencies for vulnerabilities
        run: safety check -r requirements.txt

  build:
    runs-on: ubuntu-latest
    needs: [lint, test, security]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: false
          tags: app:test
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### GitHub Actions - CD Pipeline

```yaml
# .github/workflows/cd.yml

name: CD

on:
  push:
    tags:
      - 'v*'

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging..."
          # Add deployment commands here
          # e.g., kubectl, docker-compose, SSH, etc.

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add production deployment commands
```

### Nginx Configuration

```nginx
# nginx/nginx.conf

upstream app {
    least_conn;
    server app:8000;
}

server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_types application/json text/plain application/javascript;
    gzip_min_length 1000;

    location / {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }

    location /health {
        proxy_pass http://app/health;
        access_log off;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://app;
    }
}
```

### Health Check Endpoint

```python
# app/api/v1/endpoints/health.py

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check including database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ready" if db_status == "healthy" else "not_ready",
        "checks": {
            "database": db_status,
        },
    }


@router.get("/health/live")
async def liveness_check():
    """Liveness check for container orchestration."""
    return {"status": "alive"}
```

### Environment Management

```bash
# .env.example

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=change-this-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO

# Docker
DOCKER_REGISTRY=ghcr.io
IMAGE_NAME=myorg/myapp
IMAGE_TAG=latest
```

### Makefile Commands

```makefile
# Makefile

.PHONY: help build up down logs test lint clean deploy

help:
	@echo "Available commands:"
	@echo "  build    - Build Docker images"
	@echo "  up       - Start development environment"
	@echo "  down     - Stop all containers"
	@echo "  logs     - View container logs"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linters"
	@echo "  clean    - Remove containers and volumes"
	@echo "  deploy   - Deploy to production"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec app pytest

lint:
	docker-compose exec app ruff check .
	docker-compose exec app ruff format --check .

clean:
	docker-compose down -v --rmi local
	docker system prune -f

migrate:
	docker-compose exec app alembic upgrade head

shell:
	docker-compose exec app bash

# Production commands
deploy-staging:
	docker-compose -f docker-compose.prod.yml up -d

deploy-prod:
	./scripts/deploy.sh production
```

### Deployment Script

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
REGISTRY=${DOCKER_REGISTRY:-ghcr.io}
IMAGE=${IMAGE_NAME:-myorg/myapp}
TAG=${IMAGE_TAG:-latest}

echo "Deploying to $ENVIRONMENT..."

# Pull latest image
docker pull $REGISTRY/$IMAGE:$TAG

# Run database migrations
docker run --rm \
    --env-file .env.$ENVIRONMENT \
    $REGISTRY/$IMAGE:$TAG \
    alembic upgrade head

# Deploy with zero downtime
docker-compose -f docker-compose.prod.yml up -d --no-deps --scale app=3 app

# Wait for health check
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment to $ENVIRONMENT complete!"
```

### Deployment Checklist

- [ ] Create optimized multi-stage Dockerfile
- [ ] Configure docker-compose for development and production
- [ ] Set up CI pipeline (lint, test, security scan, build)
- [ ] Set up CD pipeline (build, push, deploy)
- [ ] Configure environment-specific settings
- [ ] Add health check endpoints
- [ ] Set up reverse proxy (Nginx) with SSL
- [ ] Configure logging and monitoring
- [ ] Implement zero-downtime deployment
- [ ] Create deployment scripts and Makefile

---

When deploying, always use multi-stage builds, non-root users, health checks, and proper secret management. Never commit secrets to version control.
