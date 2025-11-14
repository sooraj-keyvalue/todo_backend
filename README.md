# Todo Backend API

A production-ready RESTful API for task management built with FastAPI, PostgreSQL, and SQLAlchemy 2.0.

## Features

- 🚀 **FastAPI** - Modern, fast web framework with automatic OpenAPI documentation
- 🗄️ **PostgreSQL** - Robust relational database with async support
- 🔄 **Alembic** - Database migrations with autogenerate
- 🔐 **JWT Authentication** - Secure token-based authentication
- ✅ **TDD Approach** - Test-driven development with pytest
- 📦 **Docker** - Containerized PostgreSQL for easy setup
- 🎯 **Vertical Slice Architecture** - Feature-based organization
- 🔍 **Type Safety** - Full type hints with mypy validation

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Docker & Docker Compose (for PostgreSQL)
- Make (optional, for shorthand commands)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd todo_backend
   ```

2. **Install dependencies**

   ```bash
   make install
   # or
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start PostgreSQL**

   ```bash
   make db-up
   # or
   docker compose up -d postgres
   ```

5. **Run migrations**

   ```bash
   make migrate
   # or
   uv run alembic upgrade head
   ```

6. **Start the development server**

   ```bash
   make run
   # or
   uv run uvicorn src.main:app --reload
   ```

7. **Access the API**
   - API: [http://localhost:8000](http://localhost:8000)
   - Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Alternative docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Development Commands

The project includes a Makefile with convenient shortcuts:

### Setup

```bash
make install          # Install all dependencies
make dev              # Setup development environment
```

### Database

```bash
make db-up            # Start PostgreSQL
make db-down          # Stop PostgreSQL
make db-reset         # Reset database (drop & recreate)
make db-test          # Test database connection
```

### Migrations

```bash
make migrate          # Apply pending migrations
make migrate-auto     # Create new migration (autogenerate)
make migrate-down     # Rollback last migration
make migrate-history  # Show migration history
make migrate-current  # Show current version
```

### Testing

```bash
make test             # Run all tests
make test-cov         # Run tests with coverage
make test-watch       # Run tests in watch mode
```

### Code Quality

```bash
make lint             # Run linter (ruff)
make format           # Format code
make type-check       # Run type checker (mypy)
make check            # Run all checks
```

### Development

```bash
make run              # Start dev server
make shell            # Open Python shell
make clean            # Remove cache files
```

### View all commands

```bash
make help
```

## Project Structure

```text
todo_backend/
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── core/                        # Core infrastructure
│   │   ├── config.py                # Configuration management
│   │   ├── database/
│   │   │   ├── session.py           # Database session & engine
│   │   │   ├── base_repository.py  # Generic CRUD repository
│   │   │   ├── query_helper.py     # Filtering & pagination
│   │   │   └── pagination.py       # Pagination utilities
│   │   ├── middleware/
│   │   │   ├── request_tracking.py # Request ID tracking
│   │   │   └── error_handling.py   # Centralized error handling
│   │   ├── exceptions.py            # Custom exceptions
│   │   └── dependencies.py          # FastAPI dependencies
│   ├── shared/                      # Shared utilities
│   │   ├── enums.py
│   │   ├── constants.py
│   │   └── utils.py
│   └── features/                    # Feature modules (vertical slices)
│       ├── users/                   # User & auth feature
│       └── tasks/                   # Tasks feature
├── tests/                           # Test suite
│   ├── conftest.py                  # Pytest configuration
│   └── core/                        # Core tests
├── alembic/                         # Database migrations
│   ├── versions/                    # Migration files
│   └── env.py                       # Alembic configuration
├── ai/                              # AI-assisted development docs
│   ├── prd.md                       # Product requirements
│   ├── hld.md                       # High-level design
│   └── plan.md                      # Implementation plan
├── docker-compose.yml               # Docker services
├── pyproject.toml                   # Project dependencies
├── Makefile                         # Development shortcuts
└── README.md                        # This file
```

## Configuration

Key environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todo_db

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
DEBUG=True
ENVIRONMENT=development
```

## Testing

Run tests with coverage:

```bash
make test-cov
```

Expected output:

```text
✓ All tests passing
✓ Coverage >= 80%
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Architecture

This project follows **Vertical Slice Architecture**:

- Each feature is self-contained with its own models, schemas, services, and tests
- Core infrastructure is shared across features
- Clear separation of concerns: API → Service → Repository → Database

### Key Patterns

- **Repository Pattern**: Generic CRUD with filtering and pagination
- **Dependency Injection**: FastAPI's built-in DI system
- **Async/Await**: Full async support with asyncpg
- **Type Safety**: Comprehensive type hints validated by mypy

## Contributing

1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Run quality checks: `make check`
5. Ensure tests pass: `make test-cov`
6. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open a GitHub issue.
