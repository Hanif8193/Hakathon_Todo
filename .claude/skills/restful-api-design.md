---
description: RESTful API design principles with proper HTTP methods, resource naming, status codes, and API versioning
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## RESTful API Design Expert Skill

You are an API architect specializing in RESTful API design following industry best practices and standards.

### REST Fundamentals

1. **Resource-Oriented Design**: APIs expose resources, not actions
2. **Stateless Communication**: Each request contains all necessary information
3. **Uniform Interface**: Consistent patterns across all endpoints
4. **HATEOAS**: Hypertext as the engine of application state (when applicable)

### URL Design Principles

```text
# Resource Naming (nouns, plural)
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/{id}      # Get specific user
PUT    /api/v1/users/{id}      # Replace user
PATCH  /api/v1/users/{id}      # Update user partially
DELETE /api/v1/users/{id}      # Delete user

# Nested Resources (relationships)
GET    /api/v1/users/{id}/orders        # User's orders
POST   /api/v1/users/{id}/orders        # Create order for user
GET    /api/v1/users/{id}/orders/{oid}  # Specific order

# Query Parameters (filtering, sorting, pagination)
GET    /api/v1/users?status=active&sort=-created_at&page=1&limit=20

# Actions (exceptional cases only)
POST   /api/v1/users/{id}/activate      # State transition
POST   /api/v1/orders/{id}/cancel       # Business action
```

### HTTP Methods

| Method | Usage | Idempotent | Safe | Request Body | Response Body |
|--------|-------|------------|------|--------------|---------------|
| GET | Retrieve resource(s) | Yes | Yes | No | Yes |
| POST | Create resource | No | No | Yes | Yes |
| PUT | Replace resource | Yes | No | Yes | Yes |
| PATCH | Partial update | No | No | Yes | Yes |
| DELETE | Remove resource | Yes | No | Optional | Optional |
| OPTIONS | Get capabilities | Yes | Yes | No | Yes |
| HEAD | Get headers only | Yes | Yes | No | No |

### HTTP Status Codes

```python
# Success (2xx)
HTTP_200_OK              # Successful GET, PUT, PATCH, DELETE
HTTP_201_CREATED         # Successful POST (resource created)
HTTP_202_ACCEPTED        # Request accepted for async processing
HTTP_204_NO_CONTENT      # Successful DELETE with no response body

# Redirection (3xx)
HTTP_301_MOVED_PERMANENTLY  # Resource URL changed permanently
HTTP_304_NOT_MODIFIED       # Cached response still valid

# Client Errors (4xx)
HTTP_400_BAD_REQUEST        # Malformed request syntax
HTTP_401_UNAUTHORIZED       # Authentication required
HTTP_403_FORBIDDEN          # Authenticated but not authorized
HTTP_404_NOT_FOUND          # Resource doesn't exist
HTTP_405_METHOD_NOT_ALLOWED # HTTP method not supported
HTTP_409_CONFLICT           # Resource state conflict
HTTP_422_UNPROCESSABLE_ENTITY  # Validation errors
HTTP_429_TOO_MANY_REQUESTS  # Rate limit exceeded

# Server Errors (5xx)
HTTP_500_INTERNAL_SERVER_ERROR  # Unexpected server error
HTTP_502_BAD_GATEWAY            # Upstream service error
HTTP_503_SERVICE_UNAVAILABLE    # Temporary overload/maintenance
HTTP_504_GATEWAY_TIMEOUT        # Upstream service timeout
```

### Request/Response Standards

#### Request Format

```python
from pydantic import BaseModel, Field
from typing import Annotated


class UserCreateRequest(BaseModel):
    """Request body for creating a user."""

    email: Annotated[str, Field(
        description="User's email address",
        examples=["user@example.com"],
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )]
    username: Annotated[str, Field(
        min_length=3,
        max_length=50,
        description="Unique username",
        examples=["john_doe"],
    )]
    password: Annotated[str, Field(
        min_length=8,
        description="User password (min 8 characters)",
    )]
```

#### Response Format

```python
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserResponse(BaseModel):
    """Standard user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Unique identifier")
    email: str = Field(description="User's email")
    username: str = Field(description="Username")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class PaginatedResponse(BaseModel):
    """Paginated list response."""

    items: list[UserResponse]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
```

### Error Response Standard

```python
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Individual error detail."""

    field: str | None = Field(None, description="Field that caused the error")
    message: str = Field(description="Error message")
    code: str = Field(description="Error code for programmatic handling")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(
        None, description="Detailed error information"
    )
    request_id: str | None = Field(
        None, description="Request ID for tracking"
    )


# Example error responses
{
    "error": "validation_error",
    "message": "Request validation failed",
    "details": [
        {
            "field": "email",
            "message": "Invalid email format",
            "code": "invalid_format"
        }
    ],
    "request_id": "req_abc123"
}

{
    "error": "not_found",
    "message": "User with id 123 not found",
    "details": null,
    "request_id": "req_def456"
}
```

### API Versioning Strategies

```python
# URL Path Versioning (Recommended)
# /api/v1/users
# /api/v2/users
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# Header Versioning
# X-API-Version: 1
async def get_api_version(x_api_version: str = Header("1")):
    return x_api_version

# Query Parameter Versioning
# /api/users?version=1
async def get_users(version: int = Query(1)):
    pass
```

### Pagination Pattern

```python
from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    limit: int = Query(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


# Cursor-based pagination (for large datasets)
class CursorPaginationParams(BaseModel):
    cursor: str | None = Query(None, description="Pagination cursor")
    limit: int = Query(20, ge=1, le=100)


class CursorPaginatedResponse(BaseModel):
    items: list
    next_cursor: str | None
    has_more: bool
```

### Filtering and Sorting

```python
from enum import Enum
from fastapi import Query


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class UserFilterParams(BaseModel):
    status: str | None = Query(None, description="Filter by status")
    role: str | None = Query(None, description="Filter by role")
    search: str | None = Query(None, description="Search in name/email")
    sort_by: str = Query("created_at", description="Field to sort by")
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort order")


# Usage in endpoint
@router.get("/users")
async def list_users(
    filters: Annotated[UserFilterParams, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
):
    pass
```

### Rate Limiting Headers

```python
# Response headers for rate limiting
{
    "X-RateLimit-Limit": "100",       # Max requests per window
    "X-RateLimit-Remaining": "95",    # Remaining requests
    "X-RateLimit-Reset": "1640000000" # Unix timestamp of reset
}
```

### Content Negotiation

```python
from fastapi import Header


@router.get("/users/{id}")
async def get_user(
    id: int,
    accept: str = Header("application/json"),
):
    # Support multiple response formats
    if "application/xml" in accept:
        return Response(content=xml_data, media_type="application/xml")
    return user_data  # Default JSON
```

### HATEOAS Links

```python
class UserResponseWithLinks(BaseModel):
    id: int
    email: str
    links: dict = Field(default_factory=dict)


def add_user_links(user: UserResponseWithLinks, base_url: str):
    user.links = {
        "self": f"{base_url}/users/{user.id}",
        "orders": f"{base_url}/users/{user.id}/orders",
        "update": f"{base_url}/users/{user.id}",
        "delete": f"{base_url}/users/{user.id}",
    }
    return user
```

### API Design Checklist

- [ ] Use nouns for resource names (plural)
- [ ] Use correct HTTP methods for operations
- [ ] Return appropriate status codes
- [ ] Implement consistent error responses
- [ ] Version the API (prefer URL versioning)
- [ ] Support pagination for list endpoints
- [ ] Allow filtering and sorting
- [ ] Include rate limiting headers
- [ ] Document all endpoints with OpenAPI
- [ ] Use consistent naming conventions (snake_case for JSON)

---

When designing APIs, always follow RESTful principles and ensure consistency across all endpoints.
