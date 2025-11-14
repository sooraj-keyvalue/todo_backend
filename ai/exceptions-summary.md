# Custom Exceptions Implementation Summary

**Date:** 2025-11-14  
**Task:** Task 2.2 - Custom Exception Classes  
**Status:** ✅ Completed

---

## Overview

Implemented a comprehensive exception hierarchy for structured error handling throughout the application. All exceptions inherit from a base class and include HTTP status codes, error codes, and optional details.

## What Was Implemented

### 1. Exception Hierarchy

Created `/src/core/exceptions.py` with the following structure:

```
Exception
└── BaseAPIException
    ├── BadRequestException (400)
    ├── AuthenticationException (401)
    ├── AuthorizationException (403)
    ├── NotFoundException (404)
    ├── ConflictException (409)
    ├── ValidationException (422)
    └── InternalServerException (500)
```

### 2. BaseAPIException

Base class for all API exceptions with consistent attributes:

```python
class BaseAPIException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
```

**Attributes:**
- `message: str` - Human-readable error message
- `code: str` - Machine-readable error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
- `status_code: int` - HTTP status code
- `details: dict | None` - Optional additional error details

**Methods:**
- `__str__()` - Returns `"{code}: {message}"`
- `__repr__()` - Developer-friendly representation with all attributes

### 3. Specific Exception Classes

#### NotFoundException (404)
```python
raise NotFoundException(
    message="Task with id 123 not found",
    code="TASK_NOT_FOUND"
)
```

**Default Values:**
- message: "Resource not found"
- code: "NOT_FOUND"
- status_code: 404

#### AuthenticationException (401)
```python
raise AuthenticationException(
    message="Invalid credentials",
    code="INVALID_CREDENTIALS"
)
```

**Default Values:**
- message: "Authentication failed"
- code: "AUTHENTICATION_FAILED"
- status_code: 401

#### AuthorizationException (403)
```python
raise AuthorizationException(
    message="You don't have permission to delete this task",
    code="PERMISSION_DENIED"
)
```

**Default Values:**
- message: "Permission denied"
- code: "PERMISSION_DENIED"
- status_code: 403

#### ValidationException (422)
```python
raise ValidationException(
    message="Invalid input data",
    code="VALIDATION_ERROR",
    details={
        "email": "Invalid email format",
        "password": "Password too short"
    }
)
```

**Default Values:**
- message: "Validation failed"
- code: "VALIDATION_ERROR"
- status_code: 422

**Special Feature:** Supports field-level validation errors via `details` dict

#### ConflictException (409)
```python
raise ConflictException(
    message="User with this email already exists",
    code="USER_ALREADY_EXISTS"
)
```

**Default Values:**
- message: "Resource conflict"
- code: "CONFLICT"
- status_code: 409

#### BadRequestException (400)
```python
raise BadRequestException(
    message="Invalid request format",
    code="BAD_REQUEST"
)
```

**Default Values:**
- message: "Bad request"
- code: "BAD_REQUEST"
- status_code: 400

#### InternalServerException (500)
```python
raise InternalServerException(
    message="Database connection failed",
    code="DB_CONNECTION_ERROR"
)
```

**Default Values:**
- message: "Internal server error"
- code: "INTERNAL_ERROR"
- status_code: 500

## Test Coverage

Created `/tests/core/test_exceptions.py` with 20 comprehensive tests:

### Test Categories

1. **Base Exception Tests**
   - Creation and attributes
   - String representation (`__str__` and `__repr__`)

2. **Individual Exception Tests**
   - Default values for each exception type
   - Custom values for each exception type
   - ValidationException with field-level details

3. **Hierarchy Tests**
   - All exceptions inherit from BaseAPIException
   - Can be caught as base class
   - Can be raised and caught individually

4. **Status Code Tests**
   - Each exception has correct HTTP status code
   - Status codes match REST conventions

### Test Results

```bash
make test
```

**Output:**
```
collected 33 items

tests/core/test_exceptions.py (20 tests) - ALL PASSED
tests/core/test_schemas.py (10 tests) - ALL PASSED
tests/test_health.py (3 tests) - ALL PASSED

===== 33 passed in 0.08s ======
```

## Usage Patterns

### In Service Layer

```python
async def get_task_by_id(task_id: str) -> Task:
    """Get a task by ID."""
    task = await repository.get(task_id)
    
    if not task:
        raise NotFoundException(
            message=f"Task with id {task_id} not found",
            code="TASK_NOT_FOUND"
        )
    
    return task
```

### In Repository Layer

```python
async def create_user(email: str) -> User:
    """Create a new user."""
    existing = await self.get_by_email(email)
    
    if existing:
        raise ConflictException(
            message=f"User with email {email} already exists",
            code="USER_ALREADY_EXISTS"
        )
    
    return await self.create(User(email=email))
```

### With Validation

```python
def validate_user_input(data: dict) -> None:
    """Validate user input data."""
    errors = {}
    
    if not is_valid_email(data.get("email")):
        errors["email"] = "Invalid email format"
    
    if len(data.get("password", "")) < 8:
        errors["password"] = "Password must be at least 8 characters"
    
    if errors:
        raise ValidationException(
            message="Invalid input data",
            details=errors
        )
```

### Exception Handling

```python
try:
    user = await service.create_user(email)
except ConflictException as e:
    # Handle duplicate user
    logger.warning(f"Duplicate user: {e.message}")
    return {"error": e.message}
except ValidationException as e:
    # Handle validation errors
    logger.info(f"Validation failed: {e.details}")
    return {"errors": e.details}
except BaseAPIException as e:
    # Catch all API exceptions
    logger.error(f"API error: {e.code} - {e.message}")
    return {"error": e.message}
```

## Integration with Response Schemas

The exceptions are designed to work seamlessly with the `ErrorResponse` schema:

```python
from src.core.exceptions import NotFoundException
from src.core.schemas import ErrorResponse, ErrorDetail, ResponseMetadata

try:
    task = await service.get_task(task_id)
except NotFoundException as e:
    # Convert exception to ErrorResponse
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=e.code,
            message=e.message,
            details=e.details
        ),
        meta=ResponseMetadata(
            request_id=request.state.request_id,
            timestamp=datetime.now(timezone.utc),
            path=request.url.path,
            method=request.method
        )
    )
    return JSONResponse(
        status_code=e.status_code,
        content=error_response.model_dump()
    )
```

## Design Decisions

### 1. Single Base Class
All exceptions inherit from `BaseAPIException` for:
- Consistent error structure
- Easy to catch all API errors
- Type safety with isinstance checks

### 2. HTTP Status Codes Built-In
Each exception has its status code:
- No need to map exceptions to status codes elsewhere
- Follows REST conventions
- Clear intent in code

### 3. Optional Details Dictionary
The `details` field allows:
- Field-level validation errors
- Additional context
- Structured error information
- Flexibility for different use cases

### 4. Default Values
Each exception has sensible defaults:
- Quick to use without parameters
- Can be customized when needed
- Consistent error codes

### 5. Descriptive Error Codes
Machine-readable codes like:
- `TASK_NOT_FOUND` instead of just `NOT_FOUND`
- `USER_ALREADY_EXISTS` instead of just `CONFLICT`
- Makes debugging easier
- Better for API consumers

## Benefits

### For Developers
- **Type Safety**: Proper exception hierarchy with type hints
- **Consistency**: All exceptions follow the same pattern
- **Easy to Use**: Sensible defaults, customizable when needed
- **Self-Documenting**: Clear exception names and error codes

### For API Consumers
- **Predictable**: Consistent error format
- **Informative**: Clear error codes and messages
- **Actionable**: Field-level validation details
- **Standard**: HTTP status codes follow REST conventions

### For Debugging
- **Traceable**: Request tracking integration ready
- **Detailed**: Optional details field for context
- **Clear**: Descriptive error codes and messages
- **Structured**: Consistent format across all errors

## Next Steps

The exception classes are ready for integration with:

1. **Error Handling Middleware** (Task 2.4)
   - Catch exceptions globally
   - Convert to ErrorResponse
   - Add request tracking metadata

2. **Service Layer** (Phase 3+)
   - Use in business logic
   - Validate inputs
   - Handle domain errors

3. **Repository Layer** (Phase 3+)
   - Database errors
   - Constraint violations
   - Not found scenarios

## Files Created

- `/src/core/exceptions.py` - Exception classes (310 lines)
- `/tests/core/test_exceptions.py` - Comprehensive tests (240 lines)

## Related Documents

- `/ai/prd.md` - Error response format specification
- `/ai/hld.md` - Error handling architecture
- `/src/core/schemas.py` - ErrorResponse and ErrorDetail schemas
- `/ai/makefile-summary.md` - Development commands

---

**Deliverable:** ✅ Can raise and catch exceptions (verified by 20 passing tests)

**Test Coverage:** 100% of exception classes and methods

**Integration:** Ready for middleware and service layer usage
