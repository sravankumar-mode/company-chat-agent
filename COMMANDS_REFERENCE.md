# Command Reference Card

## Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Verify Python modules
python -m py_compile api.py graph.py main.py
```

## Running the Application

### Option 1: FastAPI Server (Local Development)
```bash
# Start development server with auto-reload
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload

# Swagger API docs: http://127.0.0.1:8000/docs
# ReDoc: http://127.0.0.1:8000/redoc
```

### Option 2: CLI (Original)
```bash
# Interactive chat interface
python main.py

# Commands in chat:
#   exit    - Quit
#   help    - Show commands
#   clear   - Clear conversation history
#   history - View conversation
```

### Option 3: Docker Container
```bash
# Build image
docker build -t company-chat-agent .

# Run container
docker run --rm -p 8080:8080 --env-file .env company-chat-agent

# Or with explicit environment variables
docker run --rm -p 8080:8080 \
  -e OPENAI_API_KEY=sk-... \
  -e OPENAI_MODEL=gpt-3.5-turbo \
  company-chat-agent
```

## Testing API Endpoints

### Health Check
```bash
# Local (port 8000)
curl http://127.0.0.1:8000/health

# Docker (port 8080)
curl http://localhost:8080/health
```

### Chat Endpoint - Basic Query
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are our company holidays?",
    "thread_id": "user-1"
  }'
```

### Chat Endpoint - Follow-up (Same Thread)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about sick leave?",
    "thread_id": "user-1"
  }'
```

### Chat Endpoint - Different Thread
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about holidays",
    "thread_id": "user-2"
  }'
```

### Error Test - Empty Message
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "",
    "thread_id": "user-1"
  }'
# Expected: 400 Bad Request
```

## Testing & Verification

### Run Existing Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_routing.py -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html

# Quiet mode (summary only)
python -m pytest tests/ -q
```

### Run Comprehensive Verification
```bash
python verify_implementation.py
# Tests: syntax, pytest, Docker build, FastAPI endpoints
```

### Check Python Syntax
```bash
python -m py_compile api.py graph.py main.py config/settings.py
```

### Verify Imports
```bash
python -c "from api import app; from graph import company_assistant; print('OK')"
```

## Docker Commands

### Build
```bash
# Build with tag
docker build -t company-chat-agent .

# Build with multiple tags
docker build -t company-chat-agent:latest -t company-chat-agent:v1.0 .

# Build without cache
docker build --no-cache -t company-chat-agent .
```

### Run
```bash
# Basic run
docker run --rm -p 8080:8080 --env-file .env company-chat-agent

# Run with specific env vars
docker run --rm -p 8080:8080 \
  -e OPENAI_API_KEY=sk-... \
  -e OPENAI_MODEL=gpt-3.5-turbo \
  company-chat-agent

# Run in background
docker run -d -p 8080:8080 --env-file .env --name chat-agent company-chat-agent

# View logs
docker logs chat-agent

# Stop container
docker stop chat-agent
```

### Container Management
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs <container-id>

# View logs in real-time
docker logs -f <container-id>

# Remove container
docker rm <container-id>

# Remove image
docker rmi company-chat-agent

# Clean up all
docker system prune -a
```

### Container Inspection
```bash
# Container info
docker inspect <container-id>

# View running processes
docker top <container-id>

# View resource usage
docker stats <container-id>

# Execute command in running container
docker exec -it <container-id> bash
```

## Environment Configuration

### View Current Configuration
```bash
# Check if .env file exists
ls -la .env

# View environment variables (without exposing secrets)
grep -E "^[A-Z_]+" .env | cut -d= -f1
```

### Set Environment Variables

#### For Local Development (.env file)
```bash
# Create or edit .env
echo "OPENAI_API_KEY=sk-..." > .env
echo "OPENAI_MODEL=gpt-3.5-turbo" >> .env
```

#### For CLI/Local Testing
```bash
# Linux/Mac
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-3.5-turbo
python main.py

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_MODEL = "gpt-3.5-turbo"
python main.py
```

#### For Docker
```bash
# Use .env file
docker run --rm -p 8080:8080 --env-file .env company-chat-agent

# Use -e flags
docker run --rm -p 8080:8080 \
  -e OPENAI_API_KEY=sk-... \
  company-chat-agent
```

#### For Google Cloud Run
```bash
gcloud run deploy company-chat-agent \
  --image gcr.io/PROJECT-ID/company-chat-agent \
  --set-env-vars OPENAI_API_KEY=sk-... \
  --region us-central1
```

## Debugging

### FastAPI Debug Mode
```bash
# Run with debug logging
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --log-level debug

# With detailed stack traces
PYTHONTRACEBACK=1 python -m uvicorn api:app --port 8000
```

### Python Debug
```bash
# Run script with pdb debugger
python -m pdb api.py

# Or add breakpoint in code:
breakpoint()  # Will drop to pdb when executed
```

### Docker Debug
```bash
# Run interactive bash in container
docker run -it --rm -p 8080:8080 --env-file .env company-chat-agent /bin/bash

# View Python environment in container
docker run -it --rm company-chat-agent python -c "import sys; print(sys.path)"
```

### API Request Debugging
```bash
# Verbose curl output
curl -v -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "thread_id": "t1"}'

# Save response to file
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "thread_id": "t1"}' \
  -o response.json

# Pretty-print JSON response
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

## Performance & Monitoring

### Check Container Health
```bash
# Health check
docker exec <container-id> curl -s http://127.0.0.1:8080/health

# Check running processes
docker exec <container-id> ps aux

# Check disk usage
docker exec <container-id> du -sh /app
```

### Monitor Performance
```bash
# Real-time stats
watch 'docker stats --no-stream company-chat-agent'

# Memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"

# CPU usage
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}"
```

### View Logs
```bash
# Last 50 lines
docker logs --tail 50 <container-id>

# Follow logs in real-time
docker logs -f <container-id>

# Last 5 minutes of logs
docker logs --since 5m <container-id>

# Specific time range
docker logs --since 2026-11-11T10:00:00 <container-id>
```

## Cloud Deployment (Google Cloud Run)

### Build and Push to Container Registry
```bash
# Configure Docker to use gcloud
gcloud auth configure-docker

# Build
docker build -t gcr.io/PROJECT-ID/company-chat-agent:latest .

# Push
docker push gcr.io/PROJECT-ID/company-chat-agent:latest
```

### Deploy to Cloud Run
```bash
# Deploy with environment variables
gcloud run deploy company-chat-agent \
  --image gcr.io/PROJECT-ID/company-chat-agent:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=sk-...,OPENAI_MODEL=gpt-3.5-turbo \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300

# View service details
gcloud run describe company-chat-agent --region us-central1

# View logs
gcloud run logs read company-chat-agent --region us-central1 --limit 50

# Test deployed service
curl $(gcloud run services describe company-chat-agent \
  --region us-central1 --format='value(status.url)')/health
```

## Cleanup

### Clean Python Cache
```bash
# Remove __pycache__
find . -type d -name __pycache__ -exec rm -r {} +

# Remove .pyc files
find . -type f -name "*.pyc" -delete

# Remove pytest cache
rm -rf .pytest_cache
```

### Clean Docker
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -f

# Remove unused volumes
docker volume prune -f

# Full cleanup
docker system prune -af --volumes
```

## Useful Aliases (add to ~/.bashrc or ~/.zshrc)

```bash
# FastAPI
alias api-run="python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload"
alias api-test="curl http://127.0.0.1:8000/health"
alias api-chat='curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d'

# Docker
alias docker-build="docker build -t company-chat-agent ."
alias docker-run="docker run --rm -p 8080:8080 --env-file .env company-chat-agent"
alias docker-logs="docker logs -f $(docker ps -q)"

# Tests
alias test-all="python -m pytest tests/ -v"
alias test-verify="python verify_implementation.py"
```

---

**Last Updated:** 2026-11-11  
**For more details:** See QUICKSTART.md and IMPLEMENTATION_REPORT.md
