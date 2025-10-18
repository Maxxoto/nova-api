# Nova Agent API

A powerful agent-based API service built with FastAPI and domain-driven design architecture.

## Project Structure

```
nova-api/
├── .github/                 # GitHub workflows and configurations
├── notebooks/               # Jupyter notebooks for data analysis
├── data/                    # Data files and datasets
├── src/                     # Source code
│   └── nova_agent/          # Main package
│       ├── __init__.py      # Package initialization
│       ├── config.py        # Application configuration
│       ├── main.py          # FastAPI application
│       ├── domain/          # Domain layer
│       │   ├── entities/    # Domain entities
│       │   ├── value_objects/ # Value objects
│       │   ├── events/      # Domain events
│       │   └── exceptions/  # Domain exceptions
│       ├── application/     # Application layer
│       │   ├── use_cases/   # Business use cases
│       │   ├── services/    # Application services
│       │   └── dto/         # Data transfer objects
│       └── infrastructure/  # Infrastructure layer
│           ├── database/    # Database implementations
│           ├── api/         # API endpoints
│           └── events/      # Event handlers
├── static/                  # Static files (CSS, JS, images)
├── tests/                   # Test files
├── Makefile                 # Build and development commands
├── docker-compose.yaml      # Docker services configuration
├── Dockerfile               # Container definition
└── pyproject.toml          # Python project configuration
```

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- PostgreSQL (for production)
- Redis (for caching and sessions)

## Installation

### Method 1: Using uv (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd nova-api
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

### Method 2: Using pip (Alternative)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd nova-api
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

### Method 2: Using Docker (Recommended)

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - API server on port 8000
   - PostgreSQL on port 5432
   - Redis on port 6379

## Running the Application

### Development Mode

1. **Start the development server with uv:**
   ```bash
   uv run uvicorn src.nova_agent.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or use the Makefile:
   ```bash
   make run-dev
   ```

2. **Using uvx for one-off commands:**
   ```bash
   uvx uvicorn src.nova_agent.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Production Mode

1. **Using Docker:**
   ```bash
   docker-compose -f docker-compose.prod.yaml up -d
   ```

2. **Using the Makefile:**
   ```bash
   make run-prod
   ```

## Available Commands

### Makefile Commands

```bash
make install      # Install dependencies
make test         # Run tests
make lint         # Run linting
make format       # Format code
make clean        # Clean build artifacts
make run-dev      # Run development server
make run-prod     # Run production server
```

### Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run tests in container
docker-compose run api pytest
```

## API Endpoints

### Agents Management

- `POST /agents` - Create a new agent
- `GET /agents` - List all agents
- `GET /agents/{agent_id}` - Get agent by ID
- `PUT /agents/{agent_id}` - Update agent

### Health and Info

- `GET /` - Root endpoint with API info
- `GET /health` - Health check

## Configuration

Environment variables can be set in a `.env` file:

```env
# API Settings
API_TITLE=Nova Agent API
API_VERSION=0.1.0
API_DESCRIPTION=A powerful agent-based API service

# Server Settings
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Database Settings
DATABASE_URL=postgresql://nova_user:nova_password@localhost:5432/nova_api

# Redis Settings
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing

### Run Tests

```bash
# Run all tests with uv
uv run pytest

# Run tests with coverage
uv run pytest --cov=src.nova_agent

# Run specific test file
uv run pytest tests/test_example_agent_api.py

# Run tests in Docker
docker-compose run api pytest
```

### Test Structure

- `tests/` - Contains all test files
- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_example_agent_api.py` - Example tests for domain entities

## Development

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

## Deployment

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t nova-agent-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 nova-agent-api
   ```

### Cloud Deployment

The project includes Docker configuration for easy deployment to cloud platforms like:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- Heroku

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.