# Data Model Specification: Todo Full-Stack Web Application

**Feature**: 002-todo-fullstack-web
**Date**: 2026-01-14
**Phase**: Phase 1 - Design Artifacts
**Status**: Complete

## Purpose

This document defines the complete database schema for the Todo Full-Stack Web Application, including entity definitions, relationships, constraints, indexes, and migration strategy.

## Database Technology

**DBMS**: PostgreSQL 15+ (Neon Serverless)
**ORM**: SQLModel 0.0.14+ (combines SQLAlchemy 2.0+ and Pydantic)
**Driver**: asyncpg (async PostgreSQL driver)
**Connection Pooling**: Managed by Neon (serverless)

## Entity Definitions

### Entity: User

**Purpose**: Represents an authenticated user account with login credentials

**Table Name**: `user`

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    """User account with authentication credentials"""

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key"
    )

    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (unique identifier)"
    )

    password_hash: str = Field(
        max_length=255,
        description="Bcrypt hashed password (never store plaintext)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp (UTC)"
    )

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Columns**:

| Column        | Type      | Constraints                  | Description                           |
|---------------|-----------|------------------------------|---------------------------------------|
| id            | INTEGER   | PRIMARY KEY, AUTO_INCREMENT  | Unique user identifier                |
| email         | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED | User email (login identifier)         |
| password_hash | VARCHAR(255) | NOT NULL                  | Bcrypt hashed password                |
| created_at    | TIMESTAMP | NOT NULL, DEFAULT NOW()      | Account creation timestamp (UTC)      |

**Constraints**:
- **PRIMARY KEY**: `id` (auto-incrementing integer)
- **UNIQUE**: `email` (no duplicate email addresses)
- **NOT NULL**: All columns except `id` (id is auto-generated)
- **CHECK**: Email format validation (handled by application layer)
- **CASCADE DELETE**: Deleting a user deletes all their tasks (orphan prevention)

**Indexes**:
- **Primary Index**: `id` (automatic with PRIMARY KEY)
- **Unique Index**: `email` (for fast lookup during login, enforces uniqueness)

**Validation Rules** (enforced by Pydantic in schemas.py):
- Email: Must match regex pattern `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Password: Minimum 8 characters (validated before hashing)
- Password hash: Bcrypt format `$2b$12$...` (60 characters)

**Relationships**:
- **One-to-Many**: User → Tasks (one user owns many tasks)

---

### Entity: Task

**Purpose**: Represents a todo item owned by a specific user

**Table Name**: `task`

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Todo task owned by a user"""

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key"
    )

    title: str = Field(
        max_length=200,
        description="Task title (required, max 200 chars)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 chars)"
    )

    completed: bool = Field(
        default=False,
        description="Task completion status (default: incomplete)"
    )

    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        description="Owner user ID (foreign key to user.id)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task last modification timestamp (UTC)"
    )

    # Relationships
    owner: User = Relationship(back_populates="tasks")
```

**Columns**:

| Column      | Type         | Constraints                     | Description                          |
|-------------|--------------|--------------------------------|--------------------------------------|
| id          | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique task identifier               |
| title       | VARCHAR(200) | NOT NULL                       | Task title (required)                |
| description | VARCHAR(2000)| NULL                           | Task description (optional)          |
| completed   | BOOLEAN      | NOT NULL, DEFAULT FALSE        | Completion status                    |
| user_id     | INTEGER      | FOREIGN KEY(user.id), INDEXED  | Task owner (references user.id)      |
| created_at  | TIMESTAMP    | NOT NULL, DEFAULT NOW()        | Task creation timestamp (UTC)        |
| updated_at  | TIMESTAMP    | NOT NULL, DEFAULT NOW()        | Last modification timestamp (UTC)    |

**Constraints**:
- **PRIMARY KEY**: `id` (auto-incrementing integer)
- **FOREIGN KEY**: `user_id` REFERENCES `user(id)` ON DELETE CASCADE
- **NOT NULL**: `id`, `title`, `completed`, `user_id`, `created_at`, `updated_at`
- **CHECK**: `title` length 1-200 characters (enforced by SQLModel max_length)
- **CHECK**: `description` length 0-2000 characters if provided
- **ON DELETE CASCADE**: Deleting a user deletes all their tasks

**Indexes**:
- **Primary Index**: `id` (automatic with PRIMARY KEY)
- **Foreign Key Index**: `user_id` (for fast filtering by user, JOIN operations)
- **Composite Index** (future optimization): `(user_id, completed)` for filtered task lists

**Validation Rules** (enforced by Pydantic in schemas.py):
- Title: Required, 1-200 characters, non-empty after stripping whitespace
- Description: Optional, 0-2000 characters if provided
- Completed: Boolean (true/false), defaults to false
- User ID: Must reference an existing user (referential integrity enforced by FK)

**Relationships**:
- **Many-to-One**: Task → User (many tasks belong to one user)

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────┐
│          User               │
├─────────────────────────────┤
│ id (PK)            INTEGER  │
│ email (UQ, IDX)    VARCHAR  │
│ password_hash      VARCHAR  │
│ created_at         TIMESTAMP│
└─────────────────────────────┘
              │
              │ 1
              │
              │ owns
              │
              │ *
              ▼
┌─────────────────────────────┐
│          Task               │
├─────────────────────────────┤
│ id (PK)            INTEGER  │
│ title              VARCHAR  │
│ description        VARCHAR  │
│ completed          BOOLEAN  │
│ user_id (FK, IDX)  INTEGER  │
│ created_at         TIMESTAMP│
│ updated_at         TIMESTAMP│
└─────────────────────────────┘

Legend:
PK  = Primary Key
FK  = Foreign Key
UQ  = Unique Constraint
IDX = Indexed Column
*   = Zero or more
1   = Exactly one
```

**Relationship Cardinality**:
- User : Task = 1 : N (one user, many tasks)
- Task : User = N : 1 (many tasks, one owner)

**Referential Integrity**:
- Task.user_id MUST reference an existing User.id
- Deleting a User cascades deletion to all owned Tasks
- Updating User.id is prohibited (primary key immutability)

---

## Database Schema SQL (Generated by SQLModel)

```sql
-- User table
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON user(email);

-- Task table
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_user_id ON task(user_id);

-- Optional composite index for performance (add if needed)
-- CREATE INDEX idx_task_user_completed ON task(user_id, completed);
```

**Note**: SQLModel automatically generates this schema via `SQLModel.metadata.create_all(engine)`. The SQL above is provided for reference and manual database inspection.

---

## Data Access Patterns

### Pattern 1: User Authentication (Login)

**Query**: Find user by email
```python
async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    return result.first()
```

**Index Used**: `idx_user_email` (unique index on email column)
**Performance**: O(log n) lookup via B-tree index

### Pattern 2: List User's Tasks

**Query**: Get all tasks for authenticated user
```python
async def get_user_tasks(session: AsyncSession, user_id: int) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    result = await session.exec(statement)
    return result.all()
```

**Index Used**: `idx_task_user_id` (foreign key index on user_id)
**Performance**: O(log n) index scan + O(m) result retrieval (m = user's task count)

### Pattern 3: Get Task by ID (with Authorization)

**Query**: Get task if owned by user
```python
async def get_task_by_id(session: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.exec(statement)
    return result.first()
```

**Index Used**: Primary key index on `id` + foreign key index on `user_id`
**Performance**: O(log n) lookup

### Pattern 4: Update Task

**Query**: Update task title/description/completion status
```python
async def update_task(session: AsyncSession, task: Task) -> Task:
    task.updated_at = datetime.utcnow()  # Refresh timestamp
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

**Index Used**: Primary key index on `id`
**Performance**: O(log n) lookup + O(1) update

### Pattern 5: Delete Task

**Query**: Delete task if owned by user
```python
async def delete_task(session: AsyncSession, task: Task) -> None:
    await session.delete(task)
    await session.commit()
```

**Index Used**: Primary key index on `id`
**Performance**: O(log n) lookup + O(1) delete

---

## Migration Strategy

### Initial Schema Creation

**Method**: SQLModel.metadata.create_all()

**Implementation** (backend/database.py):
```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

async def init_db():
    """Initialize database schema (create tables if not exist)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Invocation**: Run once during application startup or via CLI command

### Future Schema Changes (Phase III+)

**Migration Tool**: Alembic (SQLAlchemy migration framework)

**Migration Process**:
1. Define schema changes in models.py
2. Generate migration script: `alembic revision --autogenerate -m "description"`
3. Review generated migration SQL
4. Apply migration: `alembic upgrade head`
5. Rollback if needed: `alembic downgrade -1`

**Example Migration** (add task priority field):
```python
# alembic/versions/xxx_add_task_priority.py
def upgrade():
    op.add_column('task', sa.Column('priority', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('task', 'priority')
```

**Not Implemented in Phase II**: Manual schema changes acceptable, Alembic deferred to Phase III

---

## Data Integrity Rules

### Rule 1: Email Uniqueness

**Enforcement**: Database UNIQUE constraint + application validation
**Violation**: 409 Conflict response during signup
**Business Rule**: One account per email address

### Rule 2: Task Ownership

**Enforcement**: Foreign key constraint + application-level authorization
**Violation**: 404 Not Found (hiding existence of tasks owned by other users)
**Business Rule**: Users can only access their own tasks

### Rule 3: Referential Integrity

**Enforcement**: Foreign key constraint with ON DELETE CASCADE
**Violation**: Prevented by database (cannot create task with non-existent user_id)
**Business Rule**: Tasks must belong to a valid user; deleting user deletes tasks

### Rule 4: Password Security

**Enforcement**: Application layer (bcrypt hashing before storage)
**Violation**: Never store plaintext passwords (constitutional violation)
**Business Rule**: Passwords hashed with bcrypt (work factor 12)

### Rule 5: Non-Empty Task Title

**Enforcement**: Application validation (Pydantic schema) + SQLModel max_length
**Violation**: 400 Bad Request with validation error message
**Business Rule**: Task must have a meaningful title (1-200 characters)

---

## Performance Considerations

### Index Strategy

**Current Indexes**:
1. `user.id` (primary key) - Clustered index for user lookups
2. `user.email` (unique) - Fast login authentication queries
3. `task.id` (primary key) - Clustered index for task lookups
4. `task.user_id` (foreign key) - Fast user-scoped task filtering

**Future Optimization** (if performance degrades):
- Composite index on `(user_id, completed)` for filtered task lists
- Partial index on `completed = FALSE` for active tasks view

### Query Optimization

**Best Practices**:
- Use async database operations to avoid blocking event loop
- Eager loading with `selectinload()` for user->tasks relationships (if needed)
- Pagination for task lists (deferred to Phase III)
- Connection pooling managed by Neon (automatic)

**Anti-Patterns to Avoid**:
- N+1 queries (loading tasks one-by-one instead of batch)
- SELECT * queries (only select needed columns)
- Missing WHERE clause on user_id (exposing other users' data)

### Scalability Limits (Phase II)

**Expected Scale**:
- Users: 10-100 concurrent users
- Tasks: Up to 100 tasks per user (no pagination)
- Database: Single Neon instance (serverless auto-scaling)

**Performance Targets**:
- User authentication: <500ms p95
- Task list retrieval: <200ms p95 for 100 tasks
- Task CRUD operations: <100ms p95

**Bottleneck**: Task list retrieval without pagination (100+ tasks)
**Mitigation**: Deferred to Phase III (implement pagination, filtering)

---

## Security Considerations

### SQL Injection Prevention

**Method**: Parameterized queries via SQLModel/SQLAlchemy
**Example**:
```python
# SAFE: Parameterized query
statement = select(User).where(User.email == email)  # Parameterized
result = await session.exec(statement)

# UNSAFE: String concatenation (NEVER DO THIS)
# query = f"SELECT * FROM user WHERE email = '{email}'"  # SQL injection risk!
```

**Constitutional Compliance**: SQLModel ORM prevents SQL injection by design

### Password Storage

**Method**: Bcrypt hashing with salt (work factor 12)
**Library**: `passlib` with bcrypt backend
**Example**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing
password_hash = pwd_context.hash(password)  # $2b$12$...

# Verification
is_valid = pwd_context.verify(password, password_hash)  # True/False
```

**Constitutional Compliance**: No plaintext passwords (Security Law)

### Data Isolation

**Method**: User-scoped queries via JWT user_id extraction
**Example**:
```python
# CORRECT: Scoped to authenticated user
tasks = await session.exec(
    select(Task).where(Task.user_id == current_user.id)
)

# INCORRECT: Exposes all users' tasks (constitutional violation!)
# tasks = await session.exec(select(Task))  # NO USER FILTER!
```

**Constitutional Compliance**: User data isolation (Phase II requirement)

---

## Validation & Acceptance

### Schema Validation Checklist

- [x] All entities from spec defined (User, Task)
- [x] All columns from spec included (FR-001 through FR-036)
- [x] Primary keys defined (auto-incrementing integers)
- [x] Foreign keys enforce referential integrity (user_id -> user.id)
- [x] Unique constraints prevent duplicates (user.email)
- [x] Indexes optimize query patterns (email, user_id)
- [x] Timestamps track creation/modification (created_at, updated_at)
- [x] Cascade deletes prevent orphaned tasks
- [x] Length constraints match spec (title: 200, description: 2000)

### Constitutional Compliance Checklist

- [x] No hardcoded data (schema only, no seed data)
- [x] User data isolation enabled (foreign key structure)
- [x] Password security enforced (password_hash column, bcrypt)
- [x] SQL injection prevented (SQLModel parameterized queries)
- [x] Secrets externalized (DATABASE_URL in environment variables)

---

## References

- **Feature Specification**: [specs/002-todo-fullstack-web/spec.md](./spec.md)
- **Implementation Plan**: [specs/002-todo-fullstack-web/plan.md](./plan.md)
- **Research Document**: [specs/002-todo-fullstack-web/research.md](./research.md)
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/15/

---

**Document Status**: Complete
**Next Action**: Generate API contracts (contracts/auth-api.yaml, contracts/tasks-api.yaml)
**Prepared by**: Claude Code
**Date**: 2026-01-14
