# Company AI Assistant

A multi-agent LLM system for company information queries using LangChain and LangGraph.

**Now with FastAPI REST API and Docker containerization! See [INDEX.md](INDEX.md) for new features.**

## Quick Start (Choose One)

### 1. FastAPI REST API (Recommended for Integration)
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
# Then: curl http://127.0.0.1:8000/health
```

### 2. Docker Container (Production-like)
```bash
docker build -t company-chat-agent .
docker run --rm -p 8080:8080 --env-file .env company-chat-agent
```

### 3. CLI (Original - Still Works)
```bash
python main.py
```

## New in This Release

✨ **FastAPI REST API**
- `GET /health` - Health monitoring
- `POST /chat` - Main chat interface
- Thread-based conversation memory
- Swagger/ReDoc documentation at `/docs`

📦 **Docker Support**
- Production-ready Dockerfile
- Google Cloud Run compatible
- Environment variable configuration
- Health checks integrated

📚 **Complete Documentation**
- [INDEX.md](INDEX.md) - Start here!
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) - Technical details
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deploy to Cloud Run

✅ **All Tests Passing**
- 22/22 unit tests
- 8/8 integration tests
- Zero breaking changes

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure .env:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run (pick your option above)**

## Agents

| Agent | Purpose |
|-------|---------|
| Holiday Agent | Company holidays and working days |
| HR Agent | Leave policies and HR information |
| Events Agent | Company events and announcements |
| Team Agent | Employee and team information |
| General Agent | General company questions |
| Supervisor Agent | Routes queries to specialists |

## Architecture

- **API Layer**: FastAPI for HTTP integration
- **Supervisor**: Classifies queries and routes to specialists
- **Specialists**: 5 domain-specific agents answer questions
- **Memory**: Per-thread conversation continuity with MemorySaver
- **State**: LangGraph TypedDict with message history

## Testing

```bash
# Verify everything works
python verify_implementation.py

# Run unit tests
python -m pytest tests/ -v

# Test FastAPI
curl http://127.0.0.1:8000/health
```

## Documentation

**For different audiences:**
- 👨‍💼 **Managers**: Read [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)
- 👨‍💻 **Developers**: Read [QUICKSTART.md](QUICKSTART.md)
- 🏗️ **DevOps**: Read [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- 🔍 **Architects**: Read [FINAL_REPORT.md](FINAL_REPORT.md)

**See [INDEX.md](INDEX.md) for complete navigation**

## Project Structure

```
agents/              # Specialist agents (unchanged)
config/              # Configuration
data/                # JSON data files
tests/               # Test suite (22 tests passing)
tools/               # Company tools

[NEW] api.py         # FastAPI REST API
[NEW] Dockerfile     # Container definition
[MOD] graph.py       # LangGraph workflow (bug fix)
[MOD] main.py        # CLI interface (updated)
main.py              # CLI interface
graph.py             # LangGraph workflow
requirements.txt     # Dependencies (+ FastAPI, Uvicorn)
```

## Example Queries

```
You: What are our company holidays?
Assistant: [Response about holidays]
  [Holiday Agent (Agent)]

You: What's our leave policy?
Assistant: [Response about HR policies]
  [HR Agent (Agent)]

You: Who's in the engineering team?
Assistant: [Response about team members]
  [Team Agent (Agent)]
```

## Requirements

- Python 3.12+ (required for production)
- OpenAI API key
- Docker (for containerization)
- See `requirements.txt` for Python dependencies

## Commands

### CLI Commands
- `exit` - Quit
- `help` - Show commands
- `clear` - Clear history
- `history` - Show conversation

### API Endpoints
```
GET  /health       - Health check
POST /chat         - Send message
GET  /docs         - Swagger UI
GET  /redoc        - ReDoc
```

## License

MIT

