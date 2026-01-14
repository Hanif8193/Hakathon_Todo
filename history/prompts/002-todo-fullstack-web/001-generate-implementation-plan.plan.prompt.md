---
id: 001
title: Generate Implementation Plan
stage: plan
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-todo-fullstack-web
branch: 002-todo-fullstack-web
user: hanif
command: /sp.plan
labels: ["plan", "architecture", "phase-ii", "web-application"]
links:
  spec: specs/002-todo-fullstack-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-fullstack-web/plan.md
  - specs/002-todo-fullstack-web/data-model.md
  - specs/002-todo-fullstack-web/contracts/auth-api.yaml
  - specs/002-todo-fullstack-web/contracts/tasks-api.yaml
  - specs/002-todo-fullstack-web/quickstart.md
tests:
  - No tests created (planning phase)
---

## Prompt

```text
# Phase II Plan: Todo Full-Stack Web Application

## Objective
Transform the Phase I in-memory CLI Todo app into a fully functional multi-user web application with persistent storage, responsive UI, and authentication.

---

## Step 1: Project Setup
1. Initialize monorepo (if not already done)
   - `/frontend` for Next.js app
   - `/backend` for FastAPI API
   - `/specs` for specifications
2. Set up Claude Code and Spec-Kit Plus configuration
3. Ensure environment variables for database and JWT:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`

---

## Step 2: Backend API Development
1. Create FastAPI server
   - Project structure:
     ```
     /backend
     ├─ main.py
     ├─ models.py
     ├─ routes/
     └─ db.py
     ```
2. Implement SQLModel database models
   - `User` (from Better Auth)
   - `Task` (id, user_id, title, description, completed, created_at, updated_at)
3. Create REST API endpoints:
   - GET `/api/{user_id}/tasks` → list tasks
   - POST `/api/{user_id}/tasks` → create task
   - GET `/api/{user_id}/tasks/{id}` → task details
   - PUT `/api/{user_id}/tasks/{id}` → update task
   - DELETE `/api/{user_id}/tasks/{id}` → delete task
   - PATCH `/api/{user_id}/tasks/{id}/complete` → toggle completion
4. Implement JWT authentication middleware
5. Filter all requests by authenticated user ID

---

## Step 3: Frontend Development
1. Initialize Next.js 16+ app with App Router
2. Set up Tailwind CSS for styling
3. Create pages and components:
   - `/app/dashboard` → list tasks
   - `/app/task/[id]` → task details
   - `/components/TaskCard.tsx` → reusable task component
   - `/components/TaskForm.tsx` → add/update task form
4. Integrate API client:
   - Use JWT token for every request
   - Implement CRUD calls using `/lib/api.ts`
5. Implement authentication:
   - Signup and login pages
   - Store JWT in cookies or localStorage

---

## Step 4: Testing
1. Backend:
   - Unit tests for API endpoints
   - Validate JWT authentication
2. Frontend:
   - Component and page testing
   - CRUD operation flows
3. Integration:
   - Ensure frontend and backend communicate properly
   - Verify that tasks are user-specific

---

## Step 5: Deployment & Documentation
1. Create README.md with setup instructions
2. Document all specs and CLAUDE.md instructions
3. Ensure repository has `/specs` folder with updated specifications
4. Run app locally:
   - Backend: `uvicorn main:app --reload --port 8000`
   - Frontend: `cd frontend && npm run dev`
5. Verify:
   - Task CRUD works
   - Authentication works
   - JWT tokens enforce user isolation
   - Responsive UI

---

## Timeline & Milestones
| Step | Task | Estimated Time |
|------|------|----------------|
| 1    | Project Setup | 1-2 hours |
| 2    | Backend API | 1-2 days |
| 3    | Frontend | 2-3 days |
| 4    | Testing | 1 day |
| 5    | Deployment & Docs | 0.5 day |

---

## Success Criteria
- All CRUD operations functional
- Only authenticated users can access their tasks
- JWT tokens enforce access control
- Responsive web interface
- Full integration with database
- Clean code and proper project structure
```

## Response snapshot

Successfully generated comprehensive implementation plan with Phase 1 design artifacts:

**1. Implementation Plan (plan.md)**:
- Complete technical context (Python 3.11+, FastAPI, SQLModel, Next.js 16+, Neon PostgreSQL)
- Constitutional compliance check (all Phase II requirements satisfied)
- 7 design decisions with rationale and alternatives (JWT auth, PostgreSQL, REST API, App Router, Tailwind)
- Risk analysis with mitigation strategies
- Implementation phases (0: Research ✅, 1: Design, 2: Tasks, 3: Implementation)
- Validation criteria mapped to spec acceptance scenarios

**2. Data Model (data-model.md)**:
- Complete SQLModel entity definitions (User, Task)
- ERD showing one-to-many relationship
- Database schema SQL with constraints and indexes
- 5 data access patterns with performance analysis
- Migration strategy with Alembic roadmap
- Security considerations (SQL injection prevention, password hashing, data isolation)

**3. API Contracts (OpenAPI 3.1.0)**:
- **auth-api.yaml**: Signup/login endpoints with JWT token generation
- **tasks-api.yaml**: Full CRUD endpoints (list, create, get, update, delete, toggle completion)
- Request/response schemas with validation rules
- HTTP status codes (200, 201, 400, 401, 404, 500)
- Bearer token security scheme

**4. Quickstart Guide (quickstart.md)**:
- Prerequisites checklist (WSL 2, Python 3.11+, Node.js 18+, UV, npm)
- Step-by-step setup (clone repo, configure .env, install dependencies)
- Database initialization instructions
- Running backend (uvicorn) and frontend (npm run dev)
- End-to-end verification flow (signup → login → create task → CRUD operations)
- Troubleshooting common issues

**Key Architectural Decisions**:
1. JWT-based stateless authentication (enables horizontal scaling, user data isolation)
2. Neon PostgreSQL with async SQLModel (ACID guarantees, type safety, serverless scaling)
3. RESTful API design (industry standard, predictable, auto-documented)
4. Next.js App Router (server components, improved performance, modern React)
5. Tailwind CSS (rapid development, responsive utilities, small bundle)

**Constitutional Compliance**:
- Phase II Web Application requirements: ✅ All satisfied
- Security & Identity Laws: ✅ No hardcoded secrets, JWT authentication, user data isolation
- Immutable Global Laws: ✅ Spec-driven, plan-before-build, agentic implementation

**Next Action**: Await stakeholder plan approval, then generate tasks with `/sp.tasks --from plan`

## Outcome

- ✅ Impact: Complete Phase 1 design artifacts generated (plan, data model, API contracts, quickstart)
- 🧪 Tests: No tests created (planning phase, testing deferred to implementation)
- 📁 Files: 5 files created (plan.md, data-model.md, auth-api.yaml, tasks-api.yaml, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks --from plan` to decompose into atomic tasks
- 🧠 Reflection: Research phase (Phase 0) was previously completed, enabling direct Phase 1 execution. All NEEDS CLARIFICATION items resolved via research.md.

## Evaluation notes (flywheel)

- Failure modes observed: None - all Phase 1 deliverables completed successfully
- Graders run and results (PASS/FAIL): Manual validation - PASS (all required sections present, constitutional compliance verified)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided outline
- Next experiment (smallest change to try): None needed - workflow executed as designed
