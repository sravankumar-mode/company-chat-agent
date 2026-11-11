# Quick Start Guide - FastAPI & Docker

## Prerequisites
- Python 3.12+
- Docker (optional, for containerized deployment)
- OpenAI API key in `.env` file

## Option 1: FastAPI Local Development

### Setup
```bash
cd holiday-agent
pip install -r requirements.txt
```

### Start Server
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

### Test
```bash
# Terminal 1: Server running ↑

# Terminal 2: Test endpoints
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are our holidays?", "thread_id": "user-1"}'
```

### Access API Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Option 2: Docker Local Testing

### Build
```bash
docker build -t company-chat-agent .
```

### Run
```bash
docker run --rm -p 8080:8080 --env-file .env company-chat-agent
```

### Test
```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about holidays", "thread_id": "user-1"}'
```

## Option 3: CLI (Original)

### Run
```bash
python main.py
```

## API Endpoints

### Health Check
```
GET /health
```
Returns: `{"status": "healthy", "service": "company-chat-agent", "timestamp": "..."}`

### Chat
```
POST /chat
Content-Type: application/json

{
  "message": "Your question here",
  "thread_id": "unique-user-id"
}
```

Returns:
```json
{
  "response": "Agent's response",
  "thread_id": "unique-user-id",
  "agent_name": "Holiday Agent (Agent)",
  "timestamp": "2026-11-11T15:56:28.266738"
}
```

## Conversation Continuity

### Same User - Same Thread
```bash
# First message
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What holidays do we have?", "thread_id": "user-1"}'

# Follow-up - same thread_id preserves context
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What about sick leave?", "thread_id": "user-1"}'
```

### Different User - Different Thread
```bash
# User 1
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Holidays?", "thread_id": "user-1"}'

# User 2 - separate conversation
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Holidays?", "thread_id": "user-2"}'
```

## Environment Variables

### Required
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional
- `OPENAI_MODEL` - LLM model (default: `gpt-3.5-turbo`)

### .env File Example
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

## Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Verification Script
```bash
python verify_implementation.py
```

## Troubleshooting

### "No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not set"
Ensure `.env` file exists with `OPENAI_API_KEY=sk-...`

### Docker build fails
```bash
# Clear Docker cache
docker system prune -a
# Rebuild
docker build -t company-chat-agent .
```

### Docker connection refused
```bash
# Check if container is running
docker ps

# Check logs
docker logs <container-id>
```

## Files Overview

| File | Purpose |
|------|---------|
| `api.py` | FastAPI application |
| `Dockerfile` | Container definition |
| `.dockerignore` | Files to exclude from image |
| `graph.py` | LangGraph state machine (unchanged) |
| `main.py` | CLI interface (minor update) |
| `requirements.txt` | Python dependencies (updated) |
| `config/settings.py` | Configuration management |
| `agents/*.py` | Specialist agents (unchanged) |

## Architecture

```
Client → FastAPI (port 8000/8080) → LangGraph → Supervisor → Specialists
                                          ↓
                                    MemorySaver (thread-based state)
```

## Next Steps

1. ✓ Review implementation
2. ✓ Test locally (CLI, FastAPI, Docker)
3. ✓ Verify all tests pass
4. → Deploy to Google Cloud Run (when approved)

---

For detailed information, see `IMPLEMENTATION_REPORT.md`
