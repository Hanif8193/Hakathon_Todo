# Research Document: Todo Full-Stack Web Application

**Feature**: 002-todo-fullstack-web
**Date**: 2026-01-14
**Phase**: Phase 0 - Research & Discovery

## Purpose

This document consolidates all technical research findings to resolve "NEEDS CLARIFICATION" items from the planning phase. It establishes the technical foundation for designing the data model, API contracts, and implementation approach.

---

## Research Findings

### 1. Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with App Router for frontend
**Rationale**:
- App Router provides React Server Components for improved performance
- Built-in file-based routing reduces boilerplate
- Supports modern React 19 features
- Native TypeScript support with automatic type checking
- Excellent developer experience with Fast Refresh

**Best Practices**:
- Use App Router (`/app` directory) instead of Pages Router
- Implement Server Components by default, use Client Components only when needed
- Use Server Actions for form submissions
- Store JWT tokens in httpOnly cookies for security
- Implement middleware for route protection
- Use `loading.tsx` and `error.tsx` for better UX

**Key Patterns**:
```
/app
├── (auth)           # Auth route group
│   ├── login/
│   └── signup/
├── dashboard/       # Protected routes
├── layout.tsx       # Root layout
└── middleware.ts    # Auth middleware
```

**Alternatives Considered**:
- Vite + React Router: Less integrated, more manual setup required
- Remix: Strong contender but less ecosystem maturity than Next.js

---

### 2. FastAPI Backend Architecture

**Decision**: Use FastAPI with async/await for high-performance API
**Rationale**:
- Native async support for concurrent request handling
- Automatic OpenAPI documentation generation
- Pydantic integration for request/response validation
- Type hints improve code quality and IDE support
- Excellent performance characteristics (comparable to Node.js/Go)

**Best Practices**:
- Use dependency injection for database sessions and auth
- Implement JWT middleware for authentication
- Use Pydantic models for request/response validation
- Enable CORS for frontend-backend communication
- Structure routes with APIRouter for modularity
- Use async database drivers (asyncpg via SQLModel)

**Project Structure**:
```
backend/
├── main.py              # Application entry point
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # Authentication utilities
├── database.py          # Database connection and session
├── dependencies.py      # Dependency injection functions
└── routers/
    ├── auth.py          # Auth endpoints
    └── tasks.py         # Task CRUD endpoints
```

**Key Patterns**:
- Use `Depends()` for dependency injection
- Separate SQLModel models (database) from Pydantic schemas (API)
- Implement JWT bearer token authentication with `HTTPBearer`
- Use background tasks for non-blocking operations if needed

**Alternatives Considered**:
- Django REST Framework: More opinionated, heavier weight
- Flask: Less built-in functionality, more manual setup

---

### 3. SQLModel for Database ORM

**Decision**: Use SQLModel for type-safe database operations
**Rationale**:
- Combines SQLAlchemy and Pydantic for dual-purpose models
- Type hints enable static type checking
- Async support via SQLAlchemy 2.0+
- Simplified syntax compared to raw SQLAlchemy
- Built-in validation through Pydantic

**Best Practices**:
- Define models with SQLModel base class
- Use `Field()` for column constraints and metadata
- Implement relationships with `Relationship()` annotation
- Use async sessions for non-blocking database operations
- Create database tables with `SQLModel.metadata.create_all()`

**Model Design Pattern**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User = Relationship(back_populates="tasks")
```

**Alternatives Considered**:
- Raw SQLAlchemy: More verbose, less type safety
- Tortoise ORM: Good but less ecosystem support

---

### 4. Better Auth with JWT

**Decision**: Use Better Auth library with JWT plugin for authentication
**Rationale**:
- Next.js 16+ native integration
- Built-in JWT token generation and validation
- Secure password hashing (bcrypt)
- Configurable token expiration
- Session management out of the box

**Best Practices**:
- Store JWT tokens in httpOnly cookies (XSS protection)
- Include user_id in JWT payload for user-scoped queries
- Set appropriate token expiration (24 hours recommended)
- Implement token refresh strategy
- Validate tokens on every protected API request
- Use environment variables for JWT secret

**Authentication Flow**:
1. User submits credentials (email + password)
2. Backend validates credentials against hashed password
3. Backend generates JWT token with user_id claim
4. Frontend stores JWT in httpOnly cookie
5. Frontend attaches JWT to all API requests (Authorization header)
6. Backend middleware validates JWT and extracts user_id
7. Backend uses user_id to scope all database queries

**Token Structure**:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Security Considerations**:
- Use BETTER_AUTH_SECRET environment variable (min 32 characters)
- Never log JWT tokens
- Implement token rotation for long-lived sessions
- Return 401 Unauthorized for invalid/expired tokens

**Alternatives Considered**:
- NextAuth.js: More complex setup, heavier weight
- Custom JWT implementation: Reinventing the wheel, security risk

---

### 5. Neon Serverless PostgreSQL

**Decision**: Use Neon as managed PostgreSQL provider
**Rationale**:
- Serverless architecture with automatic scaling
- Generous free tier for development
- PostgreSQL compatibility (standard SQL)
- Built-in connection pooling
- Branching support for database versioning

**Best Practices**:
- Use connection pooling to handle concurrent requests
- Store connection string in DATABASE_URL environment variable
- Use asyncpg driver for async operations
- Implement proper error handling for connection failures
- Use transactions for multi-step operations

**Connection Pattern**:
```python
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

async def get_session():
    async with AsyncSession(engine) as session:
        yield session
```

**Schema Management**:
- Use SQLModel.metadata.create_all() for initial schema creation
- Implement migrations with Alembic for schema changes
- Use database constraints for data integrity (unique, foreign key, not null)

**Alternatives Considered**:
- Supabase: Good but adds unnecessary auth layer (we use Better Auth)
- PlanetScale: MySQL-based, less feature-rich than PostgreSQL

---

### 6. Tailwind CSS for Styling

**Decision**: Use Tailwind CSS for responsive styling
**Rationale**:
- Utility-first approach speeds up development
- Built-in responsive design utilities
- Excellent Next.js integration
- Small production bundle size (unused styles purged)
- Consistent design system out of the box

**Best Practices**:
- Use Tailwind's responsive prefixes (sm:, md:, lg:, xl:)
- Create component classes for repeated patterns
- Use dark mode support if needed
- Leverage Tailwind UI components for common patterns
- Configure custom colors/spacing in tailwind.config.js

**Responsive Breakpoints**:
- `sm`: 640px (mobile landscape)
- `md`: 768px (tablet)
- `lg`: 1024px (desktop)
- `xl`: 1280px (large desktop)

**Alternatives Considered**:
- CSS Modules: More manual work, less systematic
- Styled Components: Runtime cost, less performant

---

### 7. API Design: RESTful Conventions

**Decision**: Follow RESTful API design principles
**Rationale**:
- Industry standard, widely understood
- Predictable endpoint structure
- HTTP methods map to CRUD operations
- Stateless communication

**Endpoint Design**:
```
POST   /api/auth/signup              → Create user account
POST   /api/auth/login               → Authenticate user
GET    /api/tasks                    → List user's tasks
POST   /api/tasks                    → Create new task
GET    /api/tasks/{id}               → Get task details
PUT    /api/tasks/{id}               → Update task
PATCH  /api/tasks/{id}/complete      → Toggle completion
DELETE /api/tasks/{id}               → Delete task
```

**Response Format**:
```json
{
  "data": {...},          // Successful response payload
  "error": "message",     // Error message (if applicable)
  "status": 200           // HTTP status code
}
```

**HTTP Status Codes**:
- 200 OK: Successful GET/PUT/PATCH
- 201 Created: Successful POST
- 400 Bad Request: Validation error
- 401 Unauthorized: Missing/invalid JWT
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Server error

**Best Practices**:
- Use plural nouns for resource endpoints (/tasks not /task)
- Use HTTP methods correctly (GET is read-only, POST creates, PUT updates)
- Return appropriate status codes
- Include error messages in response body
- Use query parameters for filtering/pagination (future)

**Alternatives Considered**:
- GraphQL: Overkill for simple CRUD operations
- tRPC: Ties frontend tightly to backend

---

### 8. Development Environment

**Decision**: Develop on WSL 2 (Ubuntu 22.04) on Windows
**Rationale**:
- Native Linux environment on Windows
- Better compatibility with Python/Node.js tooling
- Consistent with production Linux servers
- Access to Windows filesystem via /mnt/c

**Setup Requirements**:
- Node.js 18+ (for Next.js)
- Python 3.11+ (for FastAPI)
- UV package manager (for Python dependencies)
- npm/pnpm (for JavaScript dependencies)

**Environment Variables**:
```bash
# .env file
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Alternatives Considered**:
- Native Windows: Worse Python/Node tooling support
- Docker: Adds complexity for Phase II (reserved for Phase IV)

---

### 9. Testing Strategy (Phase II Scope)

**Decision**: Manual testing for Phase II, automated testing deferred to Phase III
**Rationale**:
- Phase II focuses on core functionality delivery
- Manual testing sufficient for validating CRUD operations
- Automated testing infrastructure adds complexity
- Test automation planned for Phase III when agent integration occurs

**Manual Testing Checklist**:
- [ ] User signup with valid/invalid data
- [ ] User login with correct/incorrect credentials
- [ ] Create task with title only
- [ ] Create task with title and description
- [ ] View task list (empty and populated)
- [ ] Update task title and description
- [ ] Toggle task completion status
- [ ] Delete task with confirmation
- [ ] Access protected routes without authentication (should redirect)
- [ ] Data isolation (verify users only see their own tasks)

**Future Testing Strategy** (Phase III+):
- Backend: pytest for API endpoint testing
- Frontend: Jest + React Testing Library for component testing
- E2E: Playwright for end-to-end user flows

**Alternatives Considered**:
- Implement tests now: Out of scope for Phase II per constitution

---

### 10. Error Handling Strategy

**Decision**: Implement comprehensive error handling with user-friendly messages
**Rationale**:
- Improves user experience
- Prevents security information leakage
- Enables debugging without exposing internals

**Frontend Error Handling**:
- Display toast notifications for errors
- Show loading states during API calls
- Handle network failures gracefully
- Redirect to login on 401 responses
- Show user-friendly error messages (not stack traces)

**Backend Error Handling**:
- Catch database exceptions and return appropriate status codes
- Log errors server-side for debugging
- Never expose stack traces in API responses
- Validate request payloads and return clear validation errors

**Error Response Format**:
```json
{
  "error": "User-friendly error message",
  "status": 400,
  "details": {
    "field": "title",
    "issue": "Title is required"
  }
}
```

**Alternatives Considered**:
- Raw error exposure: Security risk
- Silent failures: Poor user experience

---

## Technology Decision Summary

| Component | Technology | Why Chosen |
|-----------|------------|------------|
| Frontend Framework | Next.js 16+ (App Router) | Modern React, server components, great DX |
| Backend Framework | FastAPI | High performance, async, auto docs |
| ORM | SQLModel | Type-safe, combines SQLAlchemy + Pydantic |
| Database | Neon PostgreSQL | Serverless, scalable, PostgreSQL compatible |
| Authentication | Better Auth (JWT) | Next.js native, secure, simple |
| Styling | Tailwind CSS | Utility-first, responsive, fast development |
| API Design | RESTful | Standard, predictable, stateless |
| Package Managers | UV (Python), npm (Node) | Fast, reliable dependency management |

---

## Open Questions (Resolved)

All technical questions from the planning phase have been resolved through this research. No outstanding clarifications needed.

---

## Next Steps

1. Proceed to Phase 1: Design data model based on User and Task entities
2. Generate API contracts based on RESTful design principles
3. Create quickstart guide for local development setup
4. Complete implementation plan (plan.md) with all research integrated

---

**Prepared by**: Claude Code
**Date**: 2026-01-14
**Status**: Complete
