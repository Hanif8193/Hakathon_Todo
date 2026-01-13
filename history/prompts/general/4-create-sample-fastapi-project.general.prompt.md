---
id: 4
title: Create Sample FastAPI Project
stage: general
date: 2026-01-12
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: PMLS
command: create a sample fastapi project using these skills
labels: ["fastapi", "project", "sample", "crud", "auth", "testing", "docker", "ci-cd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - sample-fastapi-project/app/main.py
  - sample-fastapi-project/app/config.py
  - sample-fastapi-project/app/db/base.py
  - sample-fastapi-project/app/db/session.py
  - sample-fastapi-project/app/models/user.py
  - sample-fastapi-project/app/models/item.py
  - sample-fastapi-project/app/schemas/user.py
  - sample-fastapi-project/app/schemas/item.py
  - sample-fastapi-project/app/schemas/auth.py
  - sample-fastapi-project/app/schemas/common.py
  - sample-fastapi-project/app/core/security.py
  - sample-fastapi-project/app/core/exceptions.py
  - sample-fastapi-project/app/repositories/base.py
  - sample-fastapi-project/app/repositories/user.py
  - sample-fastapi-project/app/repositories/item.py
  - sample-fastapi-project/app/services/user.py
  - sample-fastapi-project/app/services/item.py
  - sample-fastapi-project/app/services/auth.py
  - sample-fastapi-project/app/api/deps.py
  - sample-fastapi-project/app/api/v1/router.py
  - sample-fastapi-project/app/api/v1/endpoints/auth.py
  - sample-fastapi-project/app/api/v1/endpoints/users.py
  - sample-fastapi-project/app/api/v1/endpoints/items.py
  - sample-fastapi-project/tests/conftest.py
  - sample-fastapi-project/tests/unit/test_security.py
  - sample-fastapi-project/tests/integration/test_repositories.py
  - sample-fastapi-project/tests/api/test_auth.py
  - sample-fastapi-project/tests/api/test_users.py
  - sample-fastapi-project/tests/api/test_items.py
  - sample-fastapi-project/docker/Dockerfile
  - sample-fastapi-project/docker/Dockerfile.dev
  - sample-fastapi-project/docker-compose.yml
  - sample-fastapi-project/.github/workflows/ci.yml
  - sample-fastapi-project/Makefile
  - sample-fastapi-project/README.md
tests:
  - tests/unit/test_security.py
  - tests/integration/test_repositories.py
  - tests/api/test_auth.py
  - tests/api/test_users.py
  - tests/api/test_items.py
---

## Prompt

```text
create a sample fastapi project using these skills
```

## Response snapshot

Created a complete production-ready FastAPI project demonstrating all 8 skills:

**Skills Applied:**
1. **FastAPI Development** - Async app with lifespan, CORS, dependency injection
2. **RESTful API Design** - Proper endpoints, HTTP methods, status codes, pagination
3. **Pydantic Validation** - Request/response schemas with comprehensive validation
4. **CRUD Operations** - Repository pattern, service layer, generic base repository
5. **Auth & Authorization** - JWT tokens, password hashing, OAuth2 flow
6. **Database Integration** - SQLAlchemy async, SQLite/PostgreSQL support
7. **Testing** - pytest fixtures, unit/integration/API tests
8. **Deployment** - Docker, docker-compose, GitHub Actions CI/CD

**Project Statistics:**
- 50+ files created
- Complete project structure following clean architecture
- Ready to run with `make run` or `docker-compose up`

## Outcome

- ✅ Impact: Created a fully functional FastAPI project as a reference implementation
- 🧪 Tests: Unit tests for security, integration tests for repositories, API tests for endpoints
- 📁 Files: 50+ files across app/, tests/, docker/, .github/workflows/
- 🔁 Next prompts: User can run `cd sample-fastapi-project && make dev && make run`
- 🧠 Reflection: The project demonstrates all 8 skills working together in a cohesive application

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (project template creation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add Alembic migration setup, add more endpoints, or add frontend integration
