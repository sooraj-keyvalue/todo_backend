# Implementation Plan - Todo Backend API

**Strategy:** Core-First, Then Vertical Slices
**Approach:** Test-Driven Development (TDD)
**References:** `ai/prd.md` (requirements), `CLAUDE.md` (architecture), `ai/hld.md` (design)

---

## Plan Style Rationale

This plan uses a **Phase-Based with Task Cards** approach:

### Why This Style?

✅ **Clear Progression** - Phases show the big picture, logical order
✅ **Self-Contained Tasks** - Each task has all info LLM needs
✅ **TDD-Friendly** - Test requirements in every task
✅ **Actionable** - Specific files, specific code, specific outcomes
✅ **Not Verbose** - Concise but complete
✅ **Easy Navigation** - Find what you need quickly

### Structure

Each task follows this format:
- **Objective:** What we're building
- **Files:** What to create/modify
- **Implementation:** Key points (not full code)
- **Tests:** What to test
- **Deliverable:** Success criteria

---

## Phase 1: Foundation (Setup)

### Task 1.1: Project Structure [x]

**Objective:** Create directory structure and basic files

**Actions:**
```bash
mkdir -p src/{core/{database,middleware},shared,features}
mkdir -p tests/core
touch src/{__init__,core/__init__,shared/__init__,features/__init__}.py
touch tests/{__init__,core/__init__}.py
```

**Deliverable:**
- [x] Directory structure matches `ai/hld.md`

---

### Task 1.2: Dependencies [X]

**Objective:** Install all packages

**Update:** `pyproject.toml`

**Add:**
```toml
dependencies = [
    "fastapi>=0.108.0",
    "uvicorn[standard]>=0.25.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "pydantic[email]>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[argon2]>=1.7.4",
    "python-multipart>=0.0.6",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "faker>=20.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

**Run:** `uv sync`

**Deliverable:**

- [X] All packages installed

---

### Task 1.3: Configuration [X]

**Objective:** Environment-based configuration

**Create:** `src/core/config.py`

**Implementation:**
- Use `pydantic-settings` BaseSettings
- Fields: DATABASE_URL, SECRET_KEY, JWT settings, CORS, pool settings
- Load from `.env` file

**Create:** `.env.example` with all variables

**Deliverable:**

- [X] Settings load from `.env`

---

### Task 1.4: Database Setup [X]

**Objective:** Async SQLAlchemy connection

**Create:** `src/core/database/session.py`

**Implementation:**
- `create_async_engine` with pool settings
- `async_sessionmaker`
- `Base = declarative_base()`
- `get_db()` dependency (yield session, commit/rollback)

**Deliverable:**

- [X] Can connect to PostgreSQL

---

### Task 1.5: Alembic [X]

**Objective:** Database migrations

**Run:** `alembic init alembic`

**Update:** `alembic/env.py`
- Import Base from session.py
- Set sqlalchemy.url from settings
- Configure for async

**Deliverable:**

- [X] `alembic upgrade head` works

---

### Task 1.6: Test Infrastructure [X]

**Objective:** pytest with async support

**Create:** `tests/conftest.py`

**Implementation:**
- `event_loop` fixture (session scope)
- `db_session` fixture (creates test DB, yields session, drops DB)
- `client` fixture (AsyncClient with overridden get_db)

**Deliverable:**

- [X] `pytest` runs (3 tests pass)

---

## Phase 2: Core Infrastructure

### Task 2.1: Response Schemas [X]

**Objective:** Standard API response format

**Create:** `src/core/schemas.py`

**Implementation:**
- `ResponseMetadata` - request_id, timestamp, path, method
- `APIResponse[T]` - Generic with data + meta
- `ErrorDetail` - code, message, details
- `ErrorResponse` - error + meta

**Deliverable:**

- [X] Can instantiate `APIResponse[dict]`

---

### Task 2.2: Exceptions [X]

**Objective:** Custom exception classes

**Create:** `src/core/exceptions.py`

**Implementation:**
- `BaseAPIException(Exception)`
- `NotFoundException`, `AuthenticationException`, `AuthorizationException`
- `ValidationException` with optional details dict

**Deliverable:**

- [X] Can raise and catch exceptions

---

### Task 2.3: Request Tracking Middleware []

**Objective:** Add UUID to every request

**Create:** `src/core/middleware/request_tracking.py`

**Implementation:**
- Generate UUID
- Store in `request.state` (request_id, timestamp, path, method)
- Add `X-Request-ID` response header

**Test:** `tests/core/test_request_tracking.py`
- UUID in response headers
- request.state populated

**Deliverable:**

- [ ] Tests pass

---

### Task 2.4: Error Handling Middleware []

**Objective:** Catch all exceptions, return ErrorResponse

**Create:** `src/core/middleware/error_handling.py`

**Implementation:**
- Catch all exceptions in dispatch
- Map exception types to HTTP status (see `ai/prd.md` Section 7)
- Return ErrorResponse with meta
- Log errors with request context

**Test:** `tests/core/test_error_handling.py`
- Each exception type returns correct status
- ErrorResponse format correct

**Deliverable:**

- [ ] Tests pass

---

### Task 2.5: Main App []

**Objective:** FastAPI app with middleware

**Update:** `src/main.py`

**Implementation:**
```python
app = FastAPI(title="Todo API", version="1.0.0")
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(CORSMiddleware, ...)

@app.get("/health/live")
@app.get("/health/ready")
```

**Deliverable:**

- [ ] Server starts, health checks work

---

### Task 2.6: BaseRepository []

**Objective:** Generic CRUD repository

**Create:** `src/core/database/base_repository.py`

**Implementation:**
- `BaseRepository[T]` generic class
- Methods: get, get_or_404, create, update, delete, count, exists
- See `CLAUDE.md` for complete implementation

**Test:** `tests/core/test_base_repository.py`
- All CRUD methods with mock model

**Deliverable:**

- [ ] Tests pass

---

### Task 2.7: QueryHelper []

**Objective:** Dynamic filtering, sorting, pagination

**Create:** `src/core/database/query_helper.py`

**Implementation:**
- `ALLOWED_OPERATIONS` dict with 11 operations
- `apply_filters()` with field whitelisting
- `apply_sorting()` with field whitelisting
- `apply_pagination()` with max cap (100)

**Test:** `tests/core/test_query_helper.py`
- Each filter operation
- Field whitelisting enforced

**Deliverable:**

- [ ] Tests pass

---

### Task 2.8: Pagination Helper []

**Objective:** Pagination utilities

**Create:** `src/core/database/pagination.py`

**Implementation:**
- `PaginationMetadata` schema
- `PaginatedResponse[T]` generic
- `create_pagination_metadata()` function

**Test:** `tests/core/test_pagination.py`
- total_pages calculation (edge cases)

**Deliverable:**

- [ ] Tests pass

---

### Task 2.9: Dependencies []

**Objective:** Dependency injection helpers

**Create:** `src/core/dependencies.py`

**Implementation:**
```python
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
```

**Deliverable:**

- [ ] Type alias works

---

## Phase 3: Authentication Feature

### Task 3.1: User Model []

**Objective:** User database table

**Create:** `src/features/users/models.py`

**Implementation:**
- `User(Base)` with all fields (see `ai/prd.md` Section 4.1)
- UUID primary key
- email unique index
- timestamps

**Migration:**
```bash
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

**Deliverable:**

- [ ] Table created in DB

---

### Task 3.2: User Schemas []

**Objective:** Pydantic models for API

**Create:** `src/features/users/schemas.py`

**Implementation:**
- `UserCreate` - email, password (8-128 chars), full_name
- `UserLogin` - email, password
- `UserResponse` - all fields except password_hash
- `TokenResponse` - access_token, refresh_token, expires_in, user

**Deliverable:**

- [ ] Schemas validate correctly

---

### Task 3.3: Password Security []

**Objective:** Argon2 hashing and validation

**Create:** `src/features/users/security.py`

**Implementation:**
- `hash_password()` - Argon2
- `verify_password()`
- `validate_password_strength()` - check complexity (see `ai/prd.md` Section 5.2)

**Test:** `tests/features/users/test_security.py`
- Hashing and verification
- Each password rule

**Deliverable:**

- [ ] Tests pass

---

### Task 3.4: JWT Utilities []

**Objective:** Token creation and verification

**Create:** `src/features/users/jwt.py`

**Implementation:**
- `create_access_token()` - 15 min expiry
- `create_refresh_token()` - 7 day expiry
- `decode_token()`
- `verify_access_token()` - returns user_id

**Test:** `tests/features/users/test_jwt.py`
- Token creation and decoding
- Expiry enforcement

**Deliverable:**

- [ ] Tests pass

---

### Task 3.5: User Repository []

**Objective:** Data access for users

**Create:** `src/features/users/repository.py`

**Implementation:**
- Inherit from `BaseRepository[User]`
- `get_by_email()` - case-insensitive
- `email_exists()`
- `update_last_login()`

**Test:** `tests/features/users/test_repository.py`
- Email lookup (case-insensitive)

**Deliverable:**

- [ ] Tests pass

---

### Task 3.6: User Service (TDD) []

**Objective:** Authentication business logic

**Test First:** `tests/features/users/test_service.py`
- Register success
- Register duplicate email fails
- Register weak password fails
- Login success
- Login wrong password fails
- Get current user with valid token

**Then Create:** `src/features/users/service.py`

**Implementation:**
- `register()` - validate password, check uniqueness, hash, create
- `login()` - verify credentials, update last_login, return tokens
- `get_current_user()` - decode token, fetch user

**Deliverable:**

- [ ] All tests pass

---

### Task 3.7: Auth Dependency []

**Objective:** Extract and verify JWT from header

**Update:** `src/core/dependencies.py`

**Implementation:**
- `get_current_user(authorization: str = Header(...), db: DatabaseSession)`
- Extract "Bearer {token}"
- Use UserService.get_current_user()
- `CurrentUser = Annotated[UserResponse, Depends(get_current_user)]`

**Deliverable:**

- [ ] Dependency works in routes

---

### Task 3.8: Auth API (TDD) []

**Objective:** Authentication endpoints

**Test First:** `tests/features/users/test_api.py`
- POST /register returns 201
- POST /register with duplicate email returns 409
- POST /login returns 200 with tokens
- POST /login with wrong password returns 401
- GET /me authenticated returns 200
- GET /me unauthenticated returns 401

**Then Create:** `src/features/users/api.py`

**Implementation:**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- All return `APIResponse` wrapper

**Update:** `src/main.py` - register router

**Deliverable:**

- [ ] All integration tests pass

---

## Phase 4: Tasks Feature

### Task 4.1: Task Model []

**Objective:** Task database table

**Create:** `src/features/tasks/models.py`

**Implementation:**
- All fields from `ai/prd.md` Section 4.1
- UNIQUE constraint on (user_id, LOWER(title)) WHERE deleted_at IS NULL
- CHECK constraint on due_date
- FK to User with CASCADE DELETE

**Migration:** Create and apply

**Deliverable:**

- [ ] Constraints enforced

---

### Task 4.2: Task Schemas []

**Objective:** Pydantic models

**Create:** `src/features/tasks/schemas.py`

**Implementation:**
- `TaskCreate` - title (1-200), description, due_date, priority
- `TaskUpdate` - all optional
- `TaskResponse` - complete task data

**Deliverable:**

- [ ] Validation works

---

### Task 4.3: Task Repository (TDD) []

**Objective:** Data access with filtering

**Test First:** `tests/features/tasks/test_repository.py`
- search() with filters, pagination
- get_by_title() case-insensitive
- Field whitelisting

**Then Create:** `src/features/tasks/repository.py`

**Implementation:**
- Define FILTERABLE_FIELDS and SORTABLE_FIELDS
- `search()` using QueryHelper and PaginationHelper
- Get total count before pagination
- Custom queries: get_overdue, get_today, get_upcoming

**Deliverable:**

- [ ] Tests pass

---

### Task 4.4: Task Service (TDD) []

**Objective:** Business logic

**Test First:** `tests/features/tasks/test_service.py`
- Create with valid data
- Create with duplicate title fails
- Create exceeding 500 tasks fails
- Update with ownership validation
- Delete (soft delete)
- Mark completed
- Restore deleted

**Then Create:** `src/features/tasks/service.py`

**Implementation:**
- All CRUD methods with ownership validation
- Validate title (trimmed, 1-200 chars, unique per user)
- Check max 500 tasks
- Validate due_date is future
- Soft delete implementation

**Deliverable:**

- [ ] All tests pass

---

### Task 4.5: Task API (TDD) []

**Objective:** Task management endpoints

**Test First:** `tests/features/tasks/test_api.py`
- All CRUD operations
- Filtering with multiple operations
- Pagination
- Special queries (overdue, today, upcoming)
- Ownership enforcement

**Then Create:** `src/features/tasks/api.py`

**Endpoints:** (see `ai/prd.md` Section 6.3)
- POST /tasks
- GET /tasks (with filters)
- GET /tasks/{id}
- PATCH /tasks/{id}
- DELETE /tasks/{id}
- POST /tasks/{id}/complete
- POST /tasks/{id}/uncomplete
- POST /tasks/{id}/restore
- GET /tasks/deleted
- GET /tasks/overdue
- GET /tasks/today
- GET /tasks/upcoming

**Register router in main.py**

**Deliverable:**

- [ ] All integration tests pass

---

## Phase 5: Subtasks Feature

### Task 5.1: Subtask Model []

**Objective:** Subtask table with cascade delete

**Create:** `src/features/subtasks/models.py`

**Implementation:**
- FK to Task with ON DELETE CASCADE
- position field for ordering

**Migration:** Create and apply

**Deliverable:**

- [ ] Cascade delete works

---

### Task 5.2: Subtasks Complete (TDD) []

**Objective:** Full subtask feature

**Test First:**
- Max 50 subtasks per task
- Cannot add to completed task
- Ownership via task validation

**Then Create:**
- `schemas.py`
- `repository.py` (inherit BaseRepository)
- `service.py` (enforce rules)
- `api.py` (3 endpoints)

**Endpoints:**
- POST /tasks/{task_id}/subtasks
- PATCH /subtasks/{id}
- DELETE /subtasks/{id}

**Deliverable:**

- [ ] All tests pass

---

## Phase 6: Tags Feature

### Task 6.1: Tag Models []

**Objective:** Tag and TaskTag tables

**Create:** `src/features/tags/models.py`

**Implementation:**
- Tag model (user_id, name, color)
- TaskTag junction (composite PK)
- Many-to-many relationships

**Migration:** Create and apply

**Deliverable:**

- [ ] Associations work

---

### Task 6.2: Tags Complete (TDD) []

**Objective:** Full tag feature

**Test First:**
- Tag name unique per user
- Color hex format validation
- Max 10 tags per task
- Ownership validation

**Then Create:** All layers

**Endpoints:**
- POST /tags
- GET /tags
- PATCH /tags/{id}
- DELETE /tags/{id}
- POST /tasks/{task_id}/tags/{tag_id}
- DELETE /tasks/{task_id}/tags/{tag_id}

**Deliverable:**

- [ ] All tests pass

---

## Phase 7: Production Ready

### Task 7.1: Eager Loading []

**Objective:** Prevent N+1 queries

**Update:** TaskRepository.get() and search()

**Implementation:**
- Use `joinedload(Task.subtasks)` and `joinedload(Task.tags)`

**Deliverable:**

- [ ] No N+1 queries

---

### Task 7.2: API Documentation []

**Objective:** Professional OpenAPI docs

**Update:** All files

**Actions:**
- Add descriptions to all endpoints
- Add examples to all schemas
- Configure FastAPI metadata
- Test /docs

**Deliverable:**

- [ ] Clear, helpful documentation

---

### Task 7.3: README []

**Objective:** Setup documentation

**Update:** `README.md`

**Include:**
- Project description
- Setup instructions
- Environment variables
- Run commands
- Test commands
- Link to API docs

**Deliverable:**

- [ ] New dev can setup project

---

### Task 7.4: Docker []

**Objective:** Containerization

**Create:** `Dockerfile`, `docker-compose.yml`

**Implementation:**
- Multi-stage Dockerfile with uv
- docker-compose with PostgreSQL
- Migrations run on startup

**Test:** `docker-compose up`

**Deliverable:**

- [ ] App runs in Docker

---

### Task 7.5: CI/CD []

**Objective:** Automated testing

**Create:** `.github/workflows/ci.yml`

**Pipeline:**
1. Lint (ruff check)
2. Format (ruff format --check)
3. Type check (mypy)
4. Tests (pytest --cov --cov-fail-under=80)

**Deliverable:**

- [ ] Pipeline runs on push

---

### Task 7.6: Pre-commit Hooks []

**Objective:** Local quality checks

**Create:** `.pre-commit-config.yaml`

**Hooks:** ruff, mypy, pytest

**Install:** `pre-commit install`

**Deliverable:**

- [ ] Hooks run before commits

---

### Task 7.7: Final Verification []

**Objective:** Complete validation

**Checklist:**
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Linting passes
- [ ] Format passes
- [ ] Type check passes
- [ ] Server starts
- [ ] Health checks work
- [ ] OpenAPI docs accessible
- [ ] Can register/login
- [ ] Can CRUD tasks
- [ ] Filtering works
- [ ] Pagination works
- [ ] Soft delete works
- [ ] Subtasks work
- [ ] Tags work
- [ ] Docker works
- [ ] CI passes

**Deliverable:**

- [ ] Production-ready MVP

---

## Success Criteria

### Functional (from PRD)
✅ Authentication with JWT
✅ Task CRUD with soft delete
✅ Subtask CRUD
✅ Tag CRUD and associations
✅ 11 filter operations
✅ Page-based pagination
✅ Special queries (overdue, today, upcoming)

### Technical (from PRD)
✅ Test coverage >= 80%
✅ TDD followed
✅ All business rules enforced
✅ Request tracking (UUID)
✅ API documentation
✅ Dockerized
✅ CI/CD pipeline

### Quality (from CLAUDE.md)
✅ Vertical slice architecture
✅ Type hints everywhere
✅ Consistent code style
✅ No N+1 queries
✅ Separation of concerns

---

## Quick Commands

```bash
# Development
uv sync                          # Install
uvicorn src.main:app --reload    # Run
pytest                           # Test
pytest --cov=src                 # Coverage
ruff check .                     # Lint
ruff format .                    # Format
mypy src                         # Type check

# Database
alembic revision --autogenerate -m "msg"
alembic upgrade head
alembic downgrade -1

# Docker
docker-compose up
docker-compose down
```

---

## Notes for LLM Assistants

1. **Always TDD** - Write tests before implementation
2. **One task at a time** - Complete each task fully before moving on
3. **Check deliverables** - Ensure success criteria met
4. **Reference docs** - Use PRD for requirements, CLAUDE.md for patterns, HLD for design
5. **Type hints** - Required on all functions
6. **Ownership** - Always validate user owns resource
7. **Field whitelisting** - Required for filtering and sorting
8. **Pagination** - Get total count before applying pagination
9. **Error handling** - Use custom exceptions, middleware catches all
10. **Soft delete** - Use deleted_at timestamp, exclude from queries

---

**End of Plan**

This plan provides clear, actionable steps for building the Todo Backend API. Each task is self-contained with specific deliverables. Follow phases in order for proper dependency management.
