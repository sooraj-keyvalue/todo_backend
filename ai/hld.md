# High-Level Design (HLD) - Todo Backend API

**Version:** 1.0
**Date:** 2024-11-14
**Reference:** See `ai/prd.md` for requirements, `CLAUDE.md` for architecture patterns

---

## 1. System Overview

The Todo Backend API is a RESTful service built with FastAPI and PostgreSQL, designed using **Vertical Slice Architecture** with a focus on modularity, testability, and maintainability.

### 1.1 Key Characteristics

- **Architecture:** Vertical Slice (feature-based organization)
- **API Style:** RESTful with JSON
- **Authentication:** JWT-based (stateless)
- **Database:** PostgreSQL with async SQLAlchemy
- **Deployment:** Containerized (Docker)
- **Development:** Test-Driven Development (TDD)

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Client]
        Mobile[Mobile Client]
        API_Client[API Client]
    end

    subgraph "API Gateway / Load Balancer"
        LB[Load Balancer<br/>HTTPS/CORS]
    end

    subgraph "Application Layer"
        FastAPI[FastAPI Application]

        subgraph "Middleware Stack"
            ErrorMW[Error Handling<br/>Middleware]
            TrackMW[Request Tracking<br/>Middleware]
        end

        subgraph "Core Infrastructure"
            Config[Configuration]
            Schemas[Response Schemas]
            Exceptions[Exception Classes]
            BaseRepo[Base Repository]
            QueryHelper[Query Helper]
            Pagination[Pagination Helper]
        end

        subgraph "Features (Vertical Slices)"
            Auth[Authentication<br/>Feature]
            Tasks[Tasks<br/>Feature]
            Subtasks[Subtasks<br/>Feature]
            Tags[Tags<br/>Feature]
        end
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Database)]
        Migrations[Alembic<br/>Migrations]
    end

    subgraph "External Services (Future)"
        Email[Email Service]
        Queue[Message Queue]
    end

    Web --> LB
    Mobile --> LB
    API_Client --> LB

    LB --> FastAPI

    FastAPI --> ErrorMW
    ErrorMW --> TrackMW
    TrackMW --> Auth
    TrackMW --> Tasks
    TrackMW --> Subtasks
    TrackMW --> Tags

    Auth --> BaseRepo
    Tasks --> BaseRepo
    Subtasks --> BaseRepo
    Tags --> BaseRepo

    BaseRepo --> DB
    QueryHelper --> DB
    Migrations --> DB

    Auth -.Future.-> Email
    Tasks -.Future.-> Queue

    style FastAPI fill:#e1f5ff
    style DB fill:#ffe1e1
    style Auth fill:#e8f5e9
    style Tasks fill:#e8f5e9
    style Subtasks fill:#e8f5e9
    style Tags fill:#e8f5e9
```

### 2.2 Vertical Slice Architecture

```mermaid
graph LR
    subgraph "Feature: Tasks"
        API_Tasks[API Layer<br/>api.py]
        Service_Tasks[Service Layer<br/>service.py]
        Repo_Tasks[Repository Layer<br/>repository.py]
        Model_Tasks[Model Layer<br/>models.py]
        Schema_Tasks[Schemas<br/>schemas.py]
        Tests_Tasks[Tests<br/>tests/]
    end

    subgraph "Core Components (Shared)"
        BaseRepo[BaseRepository]
        QueryHelper[QueryHelper]
        Middleware[Middleware]
        Exceptions[Exceptions]
    end

    API_Tasks --> Service_Tasks
    Service_Tasks --> Repo_Tasks
    Repo_Tasks --> Model_Tasks
    API_Tasks --> Schema_Tasks

    Repo_Tasks --> BaseRepo
    Repo_Tasks --> QueryHelper
    API_Tasks --> Middleware
    Service_Tasks --> Exceptions

    style API_Tasks fill:#bbdefb
    style Service_Tasks fill:#c8e6c9
    style Repo_Tasks fill:#fff9c4
    style Model_Tasks fill:#ffccbc
```

---

## 3. Request Flow

### 3.1 Complete Request Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant LB as Load Balancer
    participant MW1 as Error Middleware
    participant MW2 as Request Tracking
    participant API as API Endpoint
    participant Auth as Auth Dependency
    participant Service
    participant Repository
    participant DB as Database

    Client->>LB: HTTPS Request
    LB->>MW1: Forward Request
    MW1->>MW2: Pass Through

    MW2->>MW2: Generate UUID<br/>Store request_id, timestamp
    MW2->>API: Request with tracking

    API->>Auth: Verify JWT Token
    Auth->>Auth: Decode & Validate
    Auth-->>API: User Object

    API->>Service: Call Business Logic
    Service->>Service: Validate Business Rules
    Service->>Repository: Query Data
    Repository->>DB: SQL Query (async)
    DB-->>Repository: Results
    Repository-->>Service: Domain Objects
    Service-->>API: Response Data

    API->>API: Wrap in APIResponse<br/>with meta
    API-->>MW2: Response
    MW2->>MW2: Add X-Request-ID header
    MW2-->>MW1: Response
    MW1-->>LB: Response
    LB-->>Client: JSON Response

    Note over Client,DB: Happy Path - Success Flow

    API->>Service: Call with invalid data
    Service->>Service: Validation fails
    Service-->>MW1: Raise ValidationException
    MW1->>MW1: Catch Exception<br/>Map to 422<br/>Format ErrorResponse
    MW1-->>Client: Error Response

    Note over Client,DB: Error Path - Exception Flow
```

### 3.2 Layer Responsibilities

```mermaid
graph TD
    subgraph "Responsibilities by Layer"
        direction TB

        API_Layer["API Layer (api.py)<br/>------------------------<br/>• Route definition<br/>• Request parsing<br/>• Response formatting<br/>• Dependency injection<br/>• OpenAPI documentation"]

        Service_Layer["Service Layer (service.py)<br/>------------------------<br/>• Business logic<br/>• Validation rules<br/>• Orchestration<br/>• Multi-repository coordination<br/>• Exception handling"]

        Repo_Layer["Repository Layer (repository.py)<br/>------------------------<br/>• Data access<br/>• Query construction<br/>• Filtering & sorting<br/>• Pagination<br/>• Database operations"]

        Model_Layer["Model Layer (models.py)<br/>------------------------<br/>• Database schema<br/>• Relationships<br/>• Constraints<br/>• Indexes<br/>• SQLAlchemy mappings"]
    end

    API_Layer --> Service_Layer
    Service_Layer --> Repo_Layer
    Repo_Layer --> Model_Layer

    style API_Layer fill:#e3f2fd
    style Service_Layer fill:#f1f8e9
    style Repo_Layer fill:#fff3e0
    style Model_Layer fill:#fce4ec
```

---

## 4. Database Design

### 4.1 Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Task : owns
    User ||--o{ Tag : creates
    Task ||--o{ Subtask : contains
    Task }o--o{ Tag : tagged_with

    User {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
        datetime last_login_at
    }

    Task {
        uuid id PK
        uuid user_id FK
        string title
        string description
        datetime due_date
        boolean is_completed
        enum priority
        datetime completed_at
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }

    Subtask {
        uuid id PK
        uuid task_id FK
        string title
        boolean is_completed
        int position
        datetime created_at
        datetime updated_at
    }

    Tag {
        uuid id PK
        uuid user_id FK
        string name
        string color
        datetime created_at
    }

    TaskTag {
        uuid task_id FK
        uuid tag_id FK
        datetime created_at
    }
```

### 4.2 Database Constraints & Indexes

```mermaid
graph TB
    subgraph "Users Table"
        U1["PRIMARY KEY: id"]
        U2["UNIQUE: email"]
        U3["INDEX: is_active"]
        U4["CHECK: email format"]
    end

    subgraph "Tasks Table"
        T1["PRIMARY KEY: id"]
        T2["FOREIGN KEY: user_id → users.id<br/>ON DELETE CASCADE"]
        T3["UNIQUE: user_id, LOWER(title)<br/>WHERE deleted_at IS NULL"]
        T4["INDEX: user_id, deleted_at"]
        T5["INDEX: user_id, is_completed"]
        T6["INDEX: due_date"]
        T7["CHECK: due_date > created_at"]
    end

    subgraph "Subtasks Table"
        S1["PRIMARY KEY: id"]
        S2["FOREIGN KEY: task_id → tasks.id<br/>ON DELETE CASCADE"]
        S3["INDEX: task_id, position"]
        S4["CHECK: position >= 0"]
    end

    subgraph "Tags Table"
        TG1["PRIMARY KEY: id"]
        TG2["FOREIGN KEY: user_id → users.id<br/>ON DELETE CASCADE"]
        TG3["UNIQUE: user_id, LOWER(name)"]
        TG4["CHECK: color ~ '^#[0-9A-Fa-f]{6}$'"]
    end

    subgraph "TaskTags Table"
        TT1["PRIMARY KEY: task_id, tag_id"]
        TT2["FOREIGN KEY: task_id → tasks.id<br/>ON DELETE CASCADE"]
        TT3["FOREIGN KEY: tag_id → tags.id<br/>ON DELETE CASCADE"]
        TT4["INDEX: tag_id"]
    end

    style U1 fill:#e8f5e9
    style T1 fill:#e8f5e9
    style S1 fill:#e8f5e9
    style TG1 fill:#e8f5e9
    style TT1 fill:#e8f5e9
```

---

## 5. Authentication & Authorization

### 5.1 JWT Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Endpoint
    participant Auth as Auth Service
    participant UserRepo as User Repository
    participant DB as Database
    participant JWT as JWT Utils

    Note over Client,DB: Registration Flow
    Client->>API: POST /auth/register<br/>{email, password}
    API->>Auth: register(data)
    Auth->>Auth: Validate password strength
    Auth->>UserRepo: email_exists(email)
    UserRepo->>DB: SELECT * FROM users WHERE email = ?
    DB-->>UserRepo: No results
    UserRepo-->>Auth: False
    Auth->>Auth: Hash password (Argon2)
    Auth->>UserRepo: create(user)
    UserRepo->>DB: INSERT INTO users
    DB-->>UserRepo: User created
    UserRepo-->>Auth: User object
    Auth-->>API: UserResponse
    API-->>Client: 201 Created

    Note over Client,DB: Login Flow
    Client->>API: POST /auth/login<br/>{email, password}
    API->>Auth: login(data)
    Auth->>UserRepo: get_by_email(email)
    UserRepo->>DB: SELECT * FROM users WHERE email = ?
    DB-->>UserRepo: User record
    UserRepo-->>Auth: User object
    Auth->>Auth: Verify password<br/>(Argon2)
    Auth->>JWT: create_access_token(user)
    JWT->>JWT: Generate JWT<br/>Expiry: 15 min
    JWT-->>Auth: access_token
    Auth->>JWT: create_refresh_token(user)
    JWT->>JWT: Generate JWT<br/>Expiry: 7 days
    JWT-->>Auth: refresh_token
    Auth->>UserRepo: update_last_login(user_id)
    Auth-->>API: TokenResponse
    API-->>Client: 200 OK<br/>{access_token, refresh_token}

    Note over Client,DB: Authenticated Request Flow
    Client->>API: GET /tasks<br/>Authorization: Bearer {token}
    API->>Auth: get_current_user(token)
    Auth->>JWT: verify_access_token(token)
    JWT->>JWT: Decode & validate<br/>Check expiry
    JWT-->>Auth: user_id
    Auth->>UserRepo: get_or_404(user_id)
    UserRepo->>DB: SELECT * FROM users WHERE id = ?
    DB-->>UserRepo: User record
    UserRepo-->>Auth: User object
    Auth-->>API: UserResponse
    API->>API: Process request<br/>with user context
    API-->>Client: 200 OK
```

### 5.2 Token Structure

```mermaid
graph LR
    subgraph "Access Token Payload"
        AT1["sub: user_id (UUID)"]
        AT2["email: user@example.com"]
        AT3["is_verified: true/false"]
        AT4["exp: timestamp (15 min)"]
        AT5["iat: issued_at timestamp"]
    end

    subgraph "Refresh Token Payload"
        RT1["sub: user_id (UUID)"]
        RT2["type: 'refresh'"]
        RT3["exp: timestamp (7 days)"]
        RT4["iat: issued_at timestamp"]
    end

    subgraph "Security"
        SEC1["Algorithm: HS256"]
        SEC2["Secret: from env"]
        SEC3["Signature: HMAC-SHA256"]
    end

    AT1 --> SEC1
    AT2 --> SEC1
    AT3 --> SEC1
    AT4 --> SEC1
    AT5 --> SEC1

    RT1 --> SEC2
    RT2 --> SEC2
    RT3 --> SEC2
    RT4 --> SEC2

    style AT1 fill:#e3f2fd
    style AT2 fill:#e3f2fd
    style AT3 fill:#e3f2fd
    style AT4 fill:#e3f2fd
    style AT5 fill:#e3f2fd
    style RT1 fill:#fff3e0
    style RT2 fill:#fff3e0
    style RT3 fill:#fff3e0
    style RT4 fill:#fff3e0
```

---

## 6. API Endpoint Organization

### 6.1 API Endpoint Tree

```mermaid
graph TD
    Root["/api/v1"]

    Root --> Auth["/auth"]
    Root --> Me["/me"]
    Root --> Tasks["/tasks"]
    Root --> Subtasks["/subtasks"]
    Root --> Tags["/tags"]
    Root --> Health["/health"]

    Auth --> AuthReg["POST /register"]
    Auth --> AuthLogin["POST /login"]
    Auth --> AuthRefresh["POST /refresh"]
    Auth --> AuthLogout["POST /logout"]

    Me --> MeGet["GET /"]
    Me --> MePatch["PATCH /"]
    Me --> MeDelete["DELETE /"]

    Tasks --> TasksList["GET /<br/>Query: filters, sort, page"]
    Tasks --> TasksCreate["POST /"]
    Tasks --> TasksID["{task_id}"]
    Tasks --> TasksDeleted["GET /deleted"]
    Tasks --> TasksOverdue["GET /overdue"]
    Tasks --> TasksToday["GET /today"]
    Tasks --> TasksUpcoming["GET /upcoming"]

    TasksID --> TaskGet["GET /"]
    TasksID --> TaskPatch["PATCH /"]
    TasksID --> TaskDelete["DELETE /"]
    TasksID --> TaskComplete["POST /complete"]
    TasksID --> TaskUncomplete["POST /uncomplete"]
    TasksID --> TaskRestore["POST /restore"]
    TasksID --> TaskSubtasks["POST /subtasks"]
    TasksID --> TaskTagsAdd["POST /tags/{tag_id}"]
    TasksID --> TaskTagsRemove["DELETE /tags/{tag_id}"]

    Subtasks --> SubtaskID["{subtask_id}"]
    SubtaskID --> SubtaskPatch["PATCH /"]
    SubtaskID --> SubtaskDelete["DELETE /"]

    Tags --> TagsList["GET /"]
    Tags --> TagsCreate["POST /"]
    Tags --> TagID["{tag_id}"]
    TagID --> TagPatch["PATCH /"]
    TagID --> TagDelete["DELETE /"]

    Health --> HealthLive["GET /live"]
    Health --> HealthReady["GET /ready"]

    style Root fill:#e1f5ff
    style Auth fill:#e8f5e9
    style Me fill:#e8f5e9
    style Tasks fill:#e8f5e9
    style Subtasks fill:#e8f5e9
    style Tags fill:#e8f5e9
    style Health fill:#fff9c4
```

### 6.2 Common Query Parameters

```mermaid
graph LR
    subgraph "Filtering"
        F1["field__eq<br/>field__ne"]
        F2["field__gt, field__gte<br/>field__lt, field__lte"]
        F3["field__like<br/>field__ilike"]
        F4["field__in<br/>field__not_in"]
        F5["field__is_null"]
    end

    subgraph "Sorting"
        S1["sort_by=field_name"]
        S2["sort_order=asc/desc"]
    end

    subgraph "Pagination"
        P1["page=1 (default)"]
        P2["page_size=20 (default)<br/>max=100"]
    end

    subgraph "Example Query"
        EX["GET /tasks?<br/>is_completed__eq=false&<br/>priority__in=high,medium&<br/>due_date__gte=2024-01-01&<br/>sort_by=due_date&<br/>sort_order=asc&<br/>page=1&<br/>page_size=20"]
    end

    F1 --> EX
    F2 --> EX
    F3 --> EX
    F4 --> EX
    F5 --> EX
    S1 --> EX
    S2 --> EX
    P1 --> EX
    P2 --> EX

    style EX fill:#ffe0b2
```

---

## 7. Core Patterns & Components

### 7.1 Repository Pattern with QueryHelper

```mermaid
classDiagram
    class BaseRepository~T~ {
        <<abstract>>
        +model: Type[T]
        +db: AsyncSession
        +get(id: UUID) Optional[T]
        +get_or_404(id: UUID) T
        +create(obj: T) T
        +update(id: UUID, data: dict) T
        +delete(id: UUID) None
        +count() int
        +exists(id: UUID) bool
    }

    class QueryHelper {
        <<static>>
        +ALLOWED_OPERATIONS: dict
        +apply_filters(query, model, filters, allowed_fields) Select
        +apply_sorting(query, model, sort_by, order, allowed_fields) Select
        +apply_pagination(query, page, page_size, max_size) Select
    }

    class TaskRepository {
        +FILTERABLE_FIELDS: set
        +SORTABLE_FIELDS: set
        +search(filters, sort_by, order, page, page_size) PaginatedResponse
        +get_by_title(user_id, title) Task
        +get_overdue(user_id) list~Task~
        +get_today(user_id) list~Task~
        +get_upcoming(user_id) list~Task~
    }

    class PaginationHelper {
        +create_pagination_metadata(page, page_size, total) PaginationMetadata
    }

    BaseRepository <|-- TaskRepository : inherits
    TaskRepository ..> QueryHelper : uses
    TaskRepository ..> PaginationHelper : uses

    class Task {
        +id: UUID
        +user_id: UUID
        +title: str
        +description: str
        +due_date: datetime
        +is_completed: bool
        +priority: enum
    }

    TaskRepository --> Task : manages
```

### 7.2 Service Layer Pattern

```mermaid
classDiagram
    class TaskService {
        -db: AsyncSession
        -repo: TaskRepository
        +create_task(user_id, data) TaskResponse
        +update_task(user_id, task_id, data) TaskResponse
        +delete_task(user_id, task_id) None
        +get_task(user_id, task_id) TaskResponse
        +search_tasks(user_id, filters, sort, page, page_size) PaginatedResponse
        +mark_completed(user_id, task_id) TaskResponse
        +mark_uncompleted(user_id, task_id) TaskResponse
        +restore_task(user_id, task_id) TaskResponse
        -validate_ownership(user_id, task) None
        -validate_title_unique(user_id, title) None
        -check_max_tasks(user_id) None
    }

    class TaskRepository {
        +get(id) Task
        +create(task) Task
        +update(id, data) Task
        +search(...) PaginatedResponse
    }

    class ValidationException {
        +message: str
        +details: dict
    }

    class NotFoundException {
        +message: str
    }

    TaskService --> TaskRepository : uses
    TaskService ..> ValidationException : raises
    TaskService ..> NotFoundException : raises

    note for TaskService "Business Logic Layer:\n- Validates business rules\n- Checks ownership\n- Orchestrates repositories\n- Handles exceptions"
```

### 7.3 Middleware Stack

```mermaid
graph TB
    subgraph "Request Flow Through Middleware"
        Client[Client Request]

        Client --> ErrorMW

        subgraph "Error Handling Middleware"
            ErrorMW[Catch All Exceptions]
            ErrorMap[Map to HTTP Status]
            ErrorFormat[Format ErrorResponse]
            ErrorLog[Log with Context]
        end

        ErrorMW --> TrackMW

        subgraph "Request Tracking Middleware"
            TrackMW[Generate UUID]
            TrackStore[Store in request.state]
            TrackHeader[Add X-Request-ID Header]
        end

        TrackMW --> Endpoint[API Endpoint]
        Endpoint --> Response[Response]

        Response --> TrackHeader
        TrackHeader --> ErrorFormat
        ErrorFormat --> ErrorMW
        ErrorMW --> ClientResp[Client Response]
    end

    style ErrorMW fill:#ffcdd2
    style TrackMW fill:#c8e6c9
    style Endpoint fill:#bbdefb
```

---

## 8. Data Flow Diagrams

### 8.1 Create Task Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Task API
    participant Auth as Auth Dependency
    participant Service as Task Service
    participant Repo as Task Repository
    participant DB

    Client->>API: POST /tasks<br/>{title, description, due_date, priority}
    API->>Auth: Verify JWT
    Auth-->>API: User (user_id)
    API->>Service: create_task(user_id, data)

    Service->>Service: Validate title (1-200 chars, trimmed)
    Service->>Service: Validate due_date (future)
    Service->>Service: Validate priority (enum)

    Service->>Repo: get_by_title(user_id, title)
    Repo->>DB: SELECT WHERE user_id=? AND title=?
    DB-->>Repo: null
    Repo-->>Service: None

    Service->>Repo: count() WHERE user_id=?
    Repo->>DB: SELECT COUNT(*)
    DB-->>Repo: 42
    Repo-->>Service: 42
    Service->>Service: Check < 500 ✓

    Service->>Service: Create Task object
    Service->>Repo: create(task)
    Repo->>DB: INSERT INTO tasks
    DB-->>Repo: Task created
    Repo-->>Service: Task

    Service->>Service: Convert to TaskResponse
    Service-->>API: TaskResponse
    API->>API: Wrap in APIResponse
    API-->>Client: 201 Created<br/>{data: {...}, meta: {...}}
```

### 8.2 Search Tasks with Filtering Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Repo
    participant QueryHelper as Query Helper
    participant DB

    Client->>API: GET /tasks?<br/>is_completed__eq=false&<br/>priority__in=high,medium&<br/>sort_by=due_date&<br/>page=1&page_size=20
    API->>Auth: Verify JWT
    Auth-->>API: User

    API->>API: Parse query params
    API->>API: Build filters dict:<br/>{is_completed__eq: false,<br/>priority__in: [high, medium]}

    API->>Service: search_tasks(user_id, filters, sort, page, size)
    Service->>Repo: search(user_id, filters, sort, page, size)

    Repo->>Repo: Build base query:<br/>SELECT * FROM tasks<br/>WHERE user_id=? AND deleted_at IS NULL

    Repo->>QueryHelper: apply_filters(query, Task, filters, FILTERABLE_FIELDS)
    QueryHelper->>QueryHelper: Check field in whitelist ✓
    QueryHelper->>QueryHelper: Apply is_completed = false
    QueryHelper->>QueryHelper: Apply priority IN (high, medium)
    QueryHelper-->>Repo: Filtered query

    Repo->>DB: SELECT COUNT(*) FROM (filtered_query)
    DB-->>Repo: total = 42

    Repo->>QueryHelper: apply_sorting(query, Task, due_date, asc)
    QueryHelper->>QueryHelper: Check field in whitelist ✓
    QueryHelper-->>Repo: Sorted query

    Repo->>QueryHelper: apply_pagination(query, 1, 20)
    QueryHelper->>QueryHelper: Calculate offset = 0
    QueryHelper->>QueryHelper: LIMIT 20 OFFSET 0
    QueryHelper-->>Repo: Paginated query

    Repo->>DB: Execute final query
    DB-->>Repo: 20 Task records

    Repo->>Repo: Create pagination metadata:<br/>page=1, page_size=20,<br/>total=42, total_pages=3
    Repo-->>Service: PaginatedResponse
    Service-->>API: PaginatedResponse
    API->>API: Wrap in APIResponse
    API-->>Client: 200 OK<br/>{data: {items: [...], pagination: {...}}}
```

---

## 9. Error Handling Strategy

### 9.1 Exception Hierarchy

```mermaid
graph TD
    BaseException[Python BaseException]
    Exception[Python Exception]
    BaseAPIException[BaseAPIException]

    NotFoundException[NotFoundException<br/>→ 404]
    ValidationException[ValidationException<br/>→ 422]
    AuthenticationException[AuthenticationException<br/>→ 401]
    AuthorizationException[AuthorizationException<br/>→ 403]

    IntegrityError[SQLAlchemy IntegrityError<br/>→ 409]
    GenericError[Generic Exception<br/>→ 500]

    BaseException --> Exception
    Exception --> BaseAPIException
    Exception --> IntegrityError
    Exception --> GenericError

    BaseAPIException --> NotFoundException
    BaseAPIException --> ValidationException
    BaseAPIException --> AuthenticationException
    BaseAPIException --> AuthorizationException

    style BaseAPIException fill:#bbdefb
    style NotFoundException fill:#ffcdd2
    style ValidationException fill:#fff9c4
    style AuthenticationException fill:#f8bbd0
    style AuthorizationException fill:#f8bbd0
```

### 9.2 Error Response Flow

```mermaid
graph TB
    Start[Exception Raised]
    Catch[Error Middleware Catches]

    Start --> Catch

    Catch --> Check{Exception Type?}

    Check -->|NotFoundException| NF[404 NOT_FOUND]
    Check -->|ValidationException| VE[422 VALIDATION_ERROR]
    Check -->|AuthenticationException| AE[401 UNAUTHORIZED]
    Check -->|AuthorizationException| AZ[403 FORBIDDEN]
    Check -->|IntegrityError| IE[409 CONFLICT]
    Check -->|Other Exception| GE[500 INTERNAL_SERVER_ERROR]

    NF --> Format
    VE --> Format
    AE --> Format
    AZ --> Format
    IE --> Format
    GE --> Format

    Format[Format ErrorResponse]
    Format --> Log[Log Error with Context]
    Log --> Return[Return JSON Response]

    Return --> Client[Client receives:<br/>{error: {code, message, details}, meta: {...}}]

    style Check fill:#fff9c4
    style Format fill:#c8e6c9
    style Log fill:#ffccbc
```

---

## 10. Deployment Architecture

### 10.1 Container Architecture

```mermaid
graph TB
    subgraph "Docker Compose (Local)"
        API_Container[FastAPI Container<br/>Port: 8000]
        DB_Container[PostgreSQL Container<br/>Port: 5432]

        API_Container --> DB_Container
    end

    subgraph "Production (Future - Kubernetes)"
        LB_Prod[Load Balancer]

        subgraph "API Pods"
            API1[API Pod 1]
            API2[API Pod 2]
            API3[API Pod 3]
        end

        subgraph "Database"
            DB_Prod[(Managed PostgreSQL<br/>RDS/Cloud SQL)]
        end

        LB_Prod --> API1
        LB_Prod --> API2
        LB_Prod --> API3

        API1 --> DB_Prod
        API2 --> DB_Prod
        API3 --> DB_Prod
    end

    style API_Container fill:#e3f2fd
    style DB_Container fill:#ffebee
    style LB_Prod fill:#f3e5f5
```

### 10.2 CI/CD Pipeline

```mermaid
graph LR
    Code[Code Push]

    Code --> Lint[Lint<br/>ruff check]
    Lint --> Format[Format Check<br/>ruff format]
    Format --> Type[Type Check<br/>mypy]
    Type --> Test[Tests<br/>pytest + coverage]

    Test --> Build[Build Docker Image]
    Build --> Push[Push to Registry]

    Push --> Deploy{Branch?}

    Deploy -->|main| Staging[Deploy to Staging<br/>Auto]
    Deploy -->|tag| Prod[Deploy to Production<br/>Manual Approval]

    Staging --> Verify[Smoke Tests]
    Verify --> Monitor[Monitor]

    style Lint fill:#ffccbc
    style Format fill:#ffccbc
    style Type fill:#ffccbc
    style Test fill:#c8e6c9
    style Build fill:#bbdefb
    style Deploy fill:#fff9c4
```

---

## 11. Security Architecture

### 11.1 Security Layers

```mermaid
graph TB
    subgraph "Security Layers"
        TLS[TLS/HTTPS<br/>Encryption in Transit]
        CORS[CORS Policy<br/>Origin Validation]
        RateLimit[Rate Limiting<br/>DDoS Protection]

        JWT_Auth[JWT Authentication<br/>Token Validation]
        Ownership[Ownership Validation<br/>User Isolation]

        InputVal[Input Validation<br/>Pydantic Schemas]
        SQLInj[SQL Injection Prevention<br/>SQLAlchemy ORM]
        PasswordHash[Password Hashing<br/>Argon2]

        Logging[Security Logging<br/>Audit Trail]
        Monitoring[Monitoring & Alerts<br/>Anomaly Detection]
    end

    Internet[Internet] --> TLS
    TLS --> CORS
    CORS --> RateLimit
    RateLimit --> JWT_Auth
    JWT_Auth --> Ownership
    Ownership --> InputVal
    InputVal --> SQLInj
    SQLInj --> PasswordHash
    PasswordHash --> Logging
    Logging --> Monitoring

    style TLS fill:#c8e6c9
    style JWT_Auth fill:#bbdefb
    style InputVal fill:#fff9c4
    style PasswordHash fill:#ffccbc
```

### 11.2 Data Access Control

```mermaid
graph LR
    subgraph "User A"
        UserA_Req[Request]
        UserA_JWT[JWT: user_id=A]
    end

    subgraph "User B"
        UserB_Req[Request]
        UserB_JWT[JWT: user_id=B]
    end

    subgraph "Service Layer"
        Service[Task Service]
        Check{user_id matches<br/>resource owner?}
    end

    subgraph "Database"
        TasksA[(Tasks<br/>user_id=A)]
        TasksB[(Tasks<br/>user_id=B)]
    end

    UserA_Req --> UserA_JWT
    UserA_JWT --> Service
    Service --> Check
    Check -->|Yes| TasksA
    Check -->|No| Error[403 Forbidden]

    UserB_Req --> UserB_JWT
    UserB_JWT --> Service
    Check -->|Yes| TasksB

    style Check fill:#fff9c4
    style Error fill:#ffcdd2
    style TasksA fill:#c8e6c9
    style TasksB fill:#c8e6c9
```

---

## 12. Performance Considerations

### 12.1 Database Optimization

```mermaid
graph TB
    subgraph "Query Optimization"
        Index[Proper Indexing<br/>Foreign keys, filters]
        NoN1[No N+1 Queries<br/>Use joinedload]
        Pool[Connection Pooling<br/>Size: 10, Overflow: 20]
        Async[Async Queries<br/>Non-blocking I/O]
    end

    subgraph "Application Optimization"
        Pagination[Mandatory Pagination<br/>Max 100 items]
        Whitelist[Field Whitelisting<br/>Prevent query injection]
        Cache[Caching Strategy<br/>Future: Redis]
    end

    subgraph "Monitoring"
        SlowQuery[Slow Query Logging]
        Metrics[Query Metrics<br/>Latency tracking]
    end

    Index --> NoN1
    NoN1 --> Pool
    Pool --> Async

    Pagination --> Whitelist
    Whitelist --> Cache

    Async --> SlowQuery
    Cache --> Metrics

    style Index fill:#c8e6c9
    style NoN1 fill:#c8e6c9
    style Pagination fill:#bbdefb
    style Cache fill:#fff9c4
```

### 12.2 Preventing N+1 Queries

```mermaid
graph LR
    subgraph "Bad: N+1 Query Pattern"
        Bad1[Query 1: Get all tasks]
        Bad2[Query 2: Get subtasks for task 1]
        Bad3[Query 3: Get subtasks for task 2]
        Bad4[Query N: Get subtasks for task N]

        Bad1 --> Bad2
        Bad2 --> Bad3
        Bad3 --> Bad4
    end

    subgraph "Good: Single Query with Join"
        Good1[Query 1: Get tasks with subtasks<br/>Using joinedload]
        Good2[All data loaded in 1-2 queries]

        Good1 --> Good2
    end

    style Bad1 fill:#ffcdd2
    style Bad2 fill:#ffcdd2
    style Bad3 fill:#ffcdd2
    style Bad4 fill:#ffcdd2
    style Good1 fill:#c8e6c9
    style Good2 fill:#c8e6c9
```

---

## 13. Testing Strategy

### 13.1 Test Pyramid

```mermaid
graph TB
    subgraph "Test Pyramid"
        E2E[End-to-End Tests<br/>Few, Critical Flows]
        Integration[Integration Tests<br/>API Endpoints + DB]
        Unit[Unit Tests<br/>Services, Repositories, Utils]
    end

    Unit --> Integration
    Integration --> E2E

    style E2E fill:#ffccbc
    style Integration fill:#fff9c4
    style Unit fill:#c8e6c9

    Note[Target: 80% Coverage<br/>TDD: Write tests first]
```

### 13.2 Test Isolation

```mermaid
sequenceDiagram
    participant Test
    participant Fixture as Test Fixture
    participant DB as Test Database
    participant App as FastAPI App

    Test->>Fixture: Request db_session
    Fixture->>DB: Create all tables
    Fixture->>DB: Begin transaction
    Fixture-->>Test: Session

    Test->>App: Make API request
    App->>DB: Execute queries
    DB-->>App: Results
    App-->>Test: Response

    Test->>Test: Assert results

    Test->>Fixture: Test complete
    Fixture->>DB: Rollback transaction
    Fixture->>DB: Drop all tables
    Fixture-->>Test: Cleanup done

    Note over Test,DB: Each test isolated<br/>No data persists
```

---

## 14. Key Design Decisions

### 14.1 Architectural Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Architecture Pattern** | Vertical Slice | Feature isolation, easier to scale teams, clear boundaries |
| **ID Type** | UUID | Distributed-friendly, non-guessable, future-proof |
| **Pagination** | Page-based | User-friendly, common pattern, easier than offset |
| **Authentication** | JWT (stateless) | Scalable, no server-side session storage required |
| **Async/Sync** | Async (asyncio) | Better performance under load, non-blocking I/O |
| **Soft Delete** | Timestamp (deleted_at) | Data recovery, audit trail, user safety |
| **Error Handling** | Centralized Middleware | Consistent responses, separation of concerns |
| **Testing** | TDD | Quality assurance, regression prevention, living documentation |

### 14.2 Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Web Framework** | FastAPI | Auto OpenAPI docs, async support, type hints, fast |
| **Database** | PostgreSQL | ACID compliance, mature, rich feature set, JSON support |
| **ORM** | SQLAlchemy 2.0 | Industry standard, async support, type safety with Mapped |
| **Password Hashing** | Argon2 | OWASP recommended, memory-hard, resistant to GPU attacks |
| **JWT Library** | python-jose | Lightweight, widely used, good documentation |
| **Validation** | Pydantic | FastAPI native, type safety, clear error messages |
| **Migrations** | Alembic | SQLAlchemy companion, autogenerate, version control |
| **Testing** | pytest | Fixtures, async support, parametrization, plugins |
| **Linting** | ruff | Fast (Rust-based), combines multiple tools, configurable |

---

## 15. Future Enhancements

### 15.1 Phase 2 Architecture Additions

```mermaid
graph TB
    subgraph "Phase 2 Additions"
        Queue[Message Queue<br/>Celery + Redis]
        Worker[Background Workers<br/>Reminders, Notifications]
        Email[Email Service<br/>SendGrid/SES]
        Search[Full-Text Search<br/>PostgreSQL FTS]
        Cache[Redis Cache<br/>User profiles, Tags]
        Metrics[Prometheus Metrics<br/>+ Grafana Dashboards]
    end

    API[FastAPI Application]
    DB[(PostgreSQL)]

    API --> Queue
    Queue --> Worker
    Worker --> Email
    Worker --> DB

    API --> Search
    Search --> DB

    API --> Cache

    API --> Metrics

    style Queue fill:#ffe0b2
    style Worker fill:#ffe0b2
    style Email fill:#ffe0b2
    style Search fill:#ffe0b2
    style Cache fill:#ffe0b2
    style Metrics fill:#ffe0b2
```

### 15.2 Phase 3 Architecture Additions

```mermaid
graph TB
    subgraph "Phase 3 Additions"
        WebSocket[WebSocket Server<br/>Real-time updates]
        Storage[Object Storage<br/>File attachments]
        Analytics[Analytics Service<br/>User behavior]
        AI[AI Service<br/>Task suggestions]
    end

    API[FastAPI Application]

    API --> WebSocket
    API --> Storage
    API --> Analytics
    API --> AI

    style WebSocket fill:#f3e5f5
    style Storage fill:#f3e5f5
    style Analytics fill:#f3e5f5
    style AI fill:#f3e5f5
```

---

## Appendix: Quick Reference

### Component Responsibilities

| Component | Primary Responsibility |
|-----------|----------------------|
| **API Layer** | HTTP interface, request/response handling, OpenAPI docs |
| **Service Layer** | Business logic, validation, orchestration, exception handling |
| **Repository Layer** | Data access, query construction, database operations |
| **Model Layer** | Database schema, relationships, constraints |
| **Middleware** | Cross-cutting concerns (logging, error handling, tracking) |
| **Schemas** | Data validation, serialization, API contracts |

### Critical Flows to Understand

1. **Authentication Flow** - Registration → Login → JWT → Authenticated requests
2. **Task Creation** - Validation → Ownership → Uniqueness → DB insert
3. **Task Search** - Auth → Filters → QueryHelper → Pagination → Response
4. **Error Handling** - Exception → Middleware → Status mapping → ErrorResponse
5. **Request Tracking** - UUID generation → Store in state → Return in response

### Key Files by Feature

- **Core**: `session.py`, `base_repository.py`, `query_helper.py`, `pagination.py`
- **Middleware**: `request_tracking.py`, `error_handling.py`
- **Auth**: `models.py`, `service.py`, `jwt.py`, `security.py`, `api.py`
- **Tasks**: `models.py`, `repository.py`, `service.py`, `api.py`

---

**End of High-Level Design Document**

This HLD serves as a comprehensive reference for understanding the system architecture, data flows, and design decisions. Use this in conjunction with the PRD (`ai/prd.md`) and architecture patterns (`CLAUDE.md`) for complete context.
