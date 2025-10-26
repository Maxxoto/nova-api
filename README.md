# Nova Agent API

A powerful agent-based API service built with FastAPI and Hexagonal Architecture.

## Architecture Layers

This project follows Hexagonal Architecture with clear separation of concerns:

### Core Layer (Domain)
- **Entities**: `AgentState`, `Plan` - Pure business objects
- **Ports** - Interface definitions
- **Policies**: `SafetyPolicy` - Business rules and validation
- *No external dependencies*

### Application Layer (Use Cases)
- **Use Cases** - Business logic
- **Services** - Application logic and function
- *Depends only on Core ports*

### Adapters Layer (Infrastructure)
- **LLM Adapters**
- **Memory Adapters**
- **Tool Adapters**
- *Implements Core port interfaces*

### Infrastructure Layer (DI, Database, Cache, etc)
- **DependencyContainer** - Wires adapters to ports
- *Manages service lifecycle*

### Interfaces Layer (Agent Interface e.g: HTTP, SSE , WebSocket)
- **FastAPI Controllers** - HTTP endpoints
- **CLI For Testing**
- *Thin layer delegating to Application*

## Quick Start with uv

### Installation

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd nova-api
   uv sync
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate  # Unix/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

### Running the Application

**Start the Hexagonal Architecture API:**
```bash
uv run uvicorn src.interfaces.api.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

**Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Development Commands

```bash
# Run tests
uv run pytest

# Format code
uv run black src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```

## Architecture Flow

```
Interfaces → Application → Core ← Adapters ← Infrastructure
```

- **Dependencies flow inward** - Outer layers depend on inner layers
- **Core layer has no dependencies** on outer layers
- **Port interfaces define boundaries** between layers

## License

MIT License
