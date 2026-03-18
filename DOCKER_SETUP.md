# Docker & CI/CD Setup Guide

## � Related Documentation

- **[JENKINS_QUICKSTART.md](JENKINS_QUICKSTART.md)** - 5-minute Jenkins credentials setup
- **[JENKINS_SETUP.md](JENKINS_SETUP.md)** - Complete Jenkins pipeline configuration guide
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - PostgreSQL database setup for all environments

---

## �📦 Docker Files

### Files Created

1. **`backend/Dockerfile`** - Multi-stage Docker image for the backend
2. **`backend/.dockerignore`** - Excludes unnecessary files from Docker build
3. **`docker-compose.yml`** - Orchestrates backend + PostgreSQL database
4. **`Jenkinsfile`** - CI/CD pipeline configuration

---

## 🚀 Quick Start with Docker

### Option 1: Docker Compose (Recommended)

Run backend + database together:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Access:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

### Option 2: Docker Only (Backend)

Build and run backend container manually:

```bash
cd backend

# Build image
docker build -t ai-interview-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/db" \
  -e SECRET_KEY="your-secret-key" \
  --name backend \
  ai-interview-backend

# View logs
docker logs -f backend

# Stop container
docker stop backend
docker rm backend
```

---

## 🔧 Environment Variables

### Required Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://interview_user:interview_password@db:5432/interview_db

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Optional
SIMILARITY_THRESHOLD=0.6
NUM_QUESTIONS=3
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🔄 Jenkins CI/CD Pipeline

### Pipeline Stages

1. **Checkout** - Clone repository
2. **Setup Python** - Create virtual environment
3. **Lint & Code Quality** - Run flake8, black
4. **Run Tests** - Execute pytest with coverage
5. **Security Scan** - Check for vulnerabilities
6. **Build Docker Image** - Create Docker image
7. **Test Docker Image** - Verify container health
8. **Push Image** - Push to Docker registry (main branch)
9. **Deploy Staging** - Deploy to staging (develop branch)
10. **Deploy Production** - Deploy to prod (main branch, manual approval)

### Setting Up Jenkins

#### 1. Install Required Plugins

- Docker Pipeline
- Pipeline
- Git
- JUnit
- HTML Publisher
- Credentials Binding

#### 2. Configure Credentials

Add these credentials in Jenkins:

- **`test-database-url`** - Test database connection string
- **`test-secret-key`** - Test JWT secret key  
- **`docker-credentials`** - Docker registry credentials

Go to: **Jenkins → Manage Jenkins → Credentials → Add Credentials**

#### 3. Create Pipeline Job

1. New Item → Pipeline
2. Pipeline Definition: "Pipeline script from SCM"
3. SCM: Git
4. Repository URL: Your repo URL
5. Script Path: `Jenkinsfile`
6. Save

#### 4. Configure Webhooks (Optional)

Set up Git webhooks to trigger builds automatically:

- GitHub: Settings → Webhooks → Add webhook
- URL: `http://your-jenkins-url/github-webhook/`

---

## 🧪 Testing the Setup

### Test Docker Build

```bash
cd backend
docker build -t test-backend .
```

### Test Docker Compose

```bash
docker-compose up -d
docker-compose ps
curl http://localhost:8000/health
docker-compose logs backend
```

### Test Jenkins Pipeline Locally

Install Jenkins locally:

```bash
# Using Docker
docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins \
  jenkins/jenkins:lts
```

Access: http://localhost:8080

---

## 📊 Monitoring & Health Checks

### Docker Health Check

The backend container includes a health check:

```bash
docker inspect --format='{{.State.Health.Status}}' ai-interview-backend
```

### Manual Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-12T10:30:00",
  "version": "1.0.0"
}
```

---

## 🔒 Security Best Practices

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS/TLS
- [ ] Restrict CORS origins
- [ ] Use Docker secrets for sensitive data
- [ ] Enable database SSL connections
- [ ] Set up proper network security groups
- [ ] Regular security scans (safety, bandit)
- [ ] Keep dependencies updated

### Docker Secrets (Production)

```yaml
# docker-compose.prod.yml
services:
  backend:
    secrets:
      - db_password
      - secret_key
    environment:
      DATABASE_URL: postgresql://user:${db_password}@db:5432/db
      SECRET_KEY: ${secret_key}

secrets:
  db_password:
    external: true
  secret_key:
    external: true
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker logs ai-interview-backend

# Check health status
docker inspect ai-interview-backend | grep -A 10 Health

# Enter container
docker exec -it ai-interview-backend /bin/bash
```

### Database connection fails

```bash
# Test database connection
docker exec ai-interview-db psql -U interview_user -d interview_db -c "SELECT 1"

# Check if database is ready
docker-compose ps
```

### Jenkins pipeline fails

1. Check Jenkins console output
2. Verify credentials are configured
3. Ensure Docker is accessible from Jenkins
4. Check workspace permissions

---

## 📖 Additional Resources

- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)

---

## 🎯 Next Steps

1. **Local Testing**: Run `docker-compose up` and verify everything works
2. **Jenkins Setup**: Configure Jenkins server and credentials
3. **Registry Setup**: Set up Docker registry (Docker Hub, AWS ECR, etc.)
4. **Deployment**: Configure staging and production servers
5. **Monitoring**: Set up logging and monitoring (ELK, Prometheus, etc.)
