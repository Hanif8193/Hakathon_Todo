# Implementation Tasks: Todo Full-Stack Web Application

**Feature**: 002-todo-fullstack-web
**Branch**: `002-todo-fullstack-web`
**Date**: 2026-01-14
**Status**: Ready for Implementation

**Input Documents**:
- [spec.md](./spec.md) - Feature requirements and user stories
- [plan.md](./plan.md) - Implementation plan and design decisions
- [data-model.md](./data-model.md) - Database schema specification
- [contracts/auth-api.yaml](./contracts/auth-api.yaml) - Authentication API contract
- [contracts/tasks-api.yaml](./contracts/tasks-api.yaml) - Task management API contract

---

## Task Summary

| Phase | User Story | Task Count | Parallelizable | Independent Test |
|-------|------------|------------|----------------|------------------|
| 1 | Setup | 3 | 2 | N/A (infrastructure) |
| 2 | Foundation | 4 | 3 | N/A (prerequisites) |
| 3 | US1 (P1 - MVP) | 8 | 5 | ✅ Signup → Login → Dashboard |
| 4 | US2 (P2) | 4 | 3 | ✅ View task list with isolation |
| 5 | US3 (P3) | 4 | 2 | ✅ Create task → appears in list |
| 6 | US4 (P4) | 3 | 2 | ✅ Edit task → changes persist |
| 7 | US5 (P5) | 3 | 2 | ✅ Toggle status → visual change |
| 8 | US6 (P6) | 3 | 2 | ✅ Delete task → removed from DB |
| 9 | Polish | 3 | 3 | N/A (cross-cutting) |
| **Total** | **6 stories** | **35 tasks** | **24 parallel** | **6 independent tests** |

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Suggested MVP**: User Story 1 (P1) ONLY
- Enables user signup, login, and authentication
- Provides foundation for all subsequent features
- Delivers value: Secure user access to application
- **MVP Tasks**: T001-T014 (14 tasks, ~1-2 days)

### Incremental Delivery Approach
1. **Phase 3 (US1)**: Authentication foundation → Deploy to staging
2. **Phase 4 (US2)**: Add task viewing → Deploy (read-only task management)
3. **Phase 5 (US3)**: Add task creation → Deploy (basic CRUD)
4. **Phases 6-8 (US4-US6)**: Complete CRUD operations → Deploy full feature set
5. **Phase 9**: Polish and optimize → Production release

### Parallel Execution Opportunities

**Per Phase Parallelization**:
- Phase 1 (Setup): T002 + T003 can run in parallel
- Phase 2 (Foundation): T005 + T006 + T007 can run in parallel
- Phase 3 (US1): T009 + T010 + T011 + T012 + T013 can run in parallel (after T008)
- Phase 4 (US2): T016 + T017 + T018 can run in parallel (after T015)
- Phase 5 (US3): T020 + T021 can run in parallel (after T019)
- Phase 6 (US4): T023 + T024 can run in parallel (after T022)
- Phase 7 (US5): T026 + T027 can run in parallel (after T025)
- Phase 8 (US6): T029 + T030 can run in parallel (after T028)
- Phase 9 (Polish): T032 + T033 + T034 can run in parallel (after T031)

**Maximum Concurrency**: Up to 5 tasks in parallel during Phase 3

---

## Dependency Graph

```
Phase 1 (Setup)
  T001 → [T002, T003]

Phase 2 (Foundation - BLOCKS ALL USER STORIES)
  T004 → [T005, T006, T007] → T008 (auth middleware)

Phase 3 (US1 - MVP - BLOCKS US2-US6)
  T008 → T009 → [T010, T011, T012, T013] → T014

Phase 4 (US2 - INDEPENDENT after US1)
  T014 → T015 → [T016, T017, T018] → T019

Phase 5 (US3 - INDEPENDENT after US1+US2)
  T019 → T020 → [T021, T022] → T023

Phase 6 (US4 - INDEPENDENT after US1+US2)
  T019 → T023 → [T024, T025] → T026

Phase 7 (US5 - INDEPENDENT after US1+US2)
  T019 → T026 → [T027, T028] → T029

Phase 8 (US6 - INDEPENDENT after US1+US2)
  T019 → T029 → [T030, T031] → T032

Phase 9 (Polish - REQUIRES ALL STORIES)
  T032 → [T033, T034, T035]
```

**Critical Path**: T001 → T004 → T008 → T009 → T014 (Foundation + US1)
**Blocking Dependencies**:
- Foundation (Phase 2) blocks ALL user stories
- US1 (Phase 3) blocks ALL subsequent user stories
- US2 (Phase 4) blocks US3-US6 (task viewing prerequisite)

---

## Phase 1: Setup

**Goal**: Initialize project structure and configuration files

**Tasks**:

- [X] T001 Create project directory structure per implementation plan (backend/, frontend/src/, .env.example)
- [X] T002 [P] Create backend/pyproject.toml with FastAPI, SQLModel, asyncpg, passlib, python-jose dependencies
- [X] T003 [P] Create frontend/package.json with Next.js 16+, React 19, Better Auth, Tailwind CSS dependencies

**Completion Criteria**:
- [x] Directory structure matches plan.md (backend/, frontend/src/app/, frontend/src/components/, frontend/src/lib/)
- [x] Backend dependencies installable via `uv pip install -r requirements.txt`
- [x] Frontend dependencies installable via `npm install`
- [x] .env.example contains DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL placeholders

---

## Phase 2: Foundation (Foundational - BLOCKS ALL USER STORIES)

**Goal**: Implement shared infrastructure required by all user stories

**Dependencies**: Phase 1 must be complete
**Blocks**: ALL user stories (US1-US6) cannot proceed until this phase completes

**Tasks**:

- [X] T004 Create backend/database.py with async SQLModel engine, session management, and init_db function
- [X] T005 [P] Create backend/models.py with User and Task SQLModel entities per data-model.md
- [X] T006 [P] Create backend/schemas.py with Pydantic request/response schemas for signup, login, task CRUD
- [X] T007 [P] Create backend/auth.py with JWT token generation, validation, password hashing (bcrypt), and secret from env
- [X] T008 Create backend/dependencies.py with get_session and get_current_user dependency injection functions

**Completion Criteria**:
- [x] Database engine connects to Neon PostgreSQL via DATABASE_URL
- [x] User and Task models match data-model.md (all fields, constraints, relationships)
- [x] JWT tokens include user_id claim and expire after 24 hours
- [x] Passwords hashed with bcrypt (work factor 12)
- [x] get_current_user extracts user_id from JWT and returns 401 if invalid

**Notes**: This phase is CRITICAL - no user stories can be implemented until foundation is complete.

---

## Phase 3: User Story 1 - User Registration and Authentication (P1 - MVP)

**Story**: A new user arrives at the todo application and wants to create an account to start managing their tasks. They complete the signup process, receive authentication credentials, and can immediately access their personal todo dashboard.

**Priority**: P1 (MVP - Highest Priority)
**Dependencies**: Phase 2 (Foundation) must be complete
**Blocks**: ALL subsequent user stories (US2-US6) require authentication

**Independent Test Criteria**:
✅ Create new account through signup form
✅ Receive valid JWT token after signup
✅ Log in with created credentials
✅ Access protected dashboard with token
✅ Redirect to login when accessing dashboard without authentication

**Tasks**:

- [X] T009 Create backend/main.py with FastAPI app, CORS middleware, and mount auth + tasks routers
- [X] T010 [P] [US1] Create backend/routers/auth.py with POST /api/auth/signup endpoint (create user, hash password, return JWT)
- [X] T011 [P] [US1] Add POST /api/auth/login endpoint to backend/routers/auth.py (validate credentials, return JWT)
- [X] T012 [P] [US1] Create frontend/src/app/(auth)/signup/page.tsx with signup form (email, password validation)
- [X] T013 [P] [US1] Create frontend/src/app/(auth)/login/page.tsx with login form and error handling
- [X] T014 [P] [US1] Create frontend/src/lib/api.ts with API client helper and JWT token attachment to all requests
- [X] T015 [US1] Create frontend/src/app/dashboard/page.tsx with empty protected route placeholder
- [X] T016 [US1] Create frontend/src/app/middleware.ts to redirect unauthenticated users from /dashboard to /login

**Acceptance Scenarios** (from spec.md):
1. ✅ Provide valid email/password on signup → account created, JWT token received
2. ✅ Provide correct credentials on login → authenticated, redirected to dashboard with JWT token
3. ✅ Provide incorrect login credentials → error message, remain on login page
4. ✅ Try to access dashboard without authentication → redirected to login page

**Completion Criteria**:
- [x] Signup creates user in database with hashed password (verify: no plaintext passwords)
- [x] Login returns JWT token with user_id claim (verify: token decodes correctly)
- [x] Frontend stores JWT token (verify: token attached to subsequent requests)
- [x] Middleware redirects unauthenticated /dashboard access to /login (verify: no 401 errors, smooth redirect)
- [x] All 4 acceptance scenarios pass manual testing

**Files Created/Modified**:
- backend/main.py
- backend/routers/auth.py
- frontend/src/app/(auth)/signup/page.tsx
- frontend/src/app/(auth)/login/page.tsx
- frontend/src/lib/api.ts
- frontend/src/app/dashboard/page.tsx
- frontend/src/app/middleware.ts

---

## Phase 4: User Story 2 - View and Manage Task List (P2)

**Story**: An authenticated user wants to see all their tasks in a clean, organized interface. They can view their complete task list, see task details including title, description, and completion status, and understand at a glance what needs to be done.

**Priority**: P2
**Dependencies**: US1 (authentication) must be complete
**Blocks**: US3-US6 (task CRUD operations require viewing)

**Independent Test Criteria**:
✅ Log in with account that has pre-seeded tasks
✅ All tasks displayed with correct information
✅ Only logged-in user's tasks visible (data isolation verified)
✅ Empty state shown when user has no tasks

**Tasks**:

- [X] T017 Create backend/routers/tasks.py with GET /api/tasks endpoint (filter by authenticated user_id, return task list)
- [X] T018 [P] [US2] Create frontend/src/components/TaskCard.tsx to display individual task (title, description, completion status)
- [X] T019 [P] [US2] Create frontend/src/components/TaskList.tsx to render list of TaskCard components
- [X] T020 [P] [US2] Update frontend/src/app/dashboard/page.tsx to fetch and display tasks using TaskList component
- [X] T021 [US2] Add empty state UI to frontend/src/app/dashboard/page.tsx when user has no tasks

**Acceptance Scenarios** (from spec.md):
1. ✅ Authenticated with tasks → see list with title, description, completion status
2. ✅ Authenticated with no tasks → see empty state message prompting to create first task
3. ✅ View task list → only see own tasks (not other users' tasks)
4. ✅ Have completed and incomplete tasks → completed tasks visually distinguished

**Completion Criteria**:
- [x] GET /api/tasks returns only authenticated user's tasks (verify: create task for user1, log in as user2, confirm user2 sees empty list)
- [x] TaskCard displays task title, description, and completion status
- [x] Completed tasks have visual distinction (e.g., strikethrough, different color, opacity)
- [x] Empty state displays helpful message when no tasks exist
- [x] All 4 acceptance scenarios pass manual testing

**Files Created/Modified**:
- backend/routers/tasks.py
- frontend/src/components/TaskCard.tsx
- frontend/src/components/TaskList.tsx
- frontend/src/app/dashboard/page.tsx

---

## Phase 5: User Story 3 - Create New Tasks (P3)

**Story**: An authenticated user wants to capture a new task they need to accomplish. They click an "Add Task" button, fill in the task title and optional description, and submit the form to create the task, which immediately appears in their task list.

**Priority**: P3
**Dependencies**: US1 (authentication) + US2 (task viewing) must be complete

**Independent Test Criteria**:
✅ Log in to dashboard
✅ Click "Add Task" button
✅ Submit new task with title and description
✅ Task appears in task list immediately (no refresh needed)

**Tasks**:

- [X] T022 Add POST /api/tasks endpoint to backend/routers/tasks.py (create task, assign to authenticated user_id, validate title)
- [X] T023 [P] [US3] Create frontend/src/components/TaskForm.tsx with form for title (required) and description (optional)
- [X] T024 [P] [US3] Add "Add Task" button and TaskForm modal/inline to frontend/src/app/dashboard/page.tsx
- [X] T025 [US3] Implement form submission in TaskForm to call POST /api/tasks and refresh task list on success

**Acceptance Scenarios** (from spec.md):
1. ✅ Click "Add Task", provide title and description → task created and appears in list
2. ✅ Provide only title (no description) → task created successfully
3. ✅ Submit with empty title → validation error, task not created
4. ✅ Create new task → marked as incomplete by default

**Completion Criteria**:
- [x] POST /api/tasks creates task with user_id from JWT (verify: task.user_id matches authenticated user)
- [x] Title is required, description is optional (verify: empty title returns 400 error)
- [x] New task defaults to completed=false (verify: database value)
- [x] Task appears in list immediately after creation (verify: no page refresh needed)
- [x] All 4 acceptance scenarios pass manual testing

**Files Created/Modified**:
- backend/routers/tasks.py (add POST endpoint)
- frontend/src/components/TaskForm.tsx
- frontend/src/app/dashboard/page.tsx

---

## Phase 6: User Story 4 - Update Task Details (P4)

**Story**: An authenticated user realizes they need to modify a task's information. They click on a task or an edit button, modify the title or description, and save the changes, which are immediately reflected in the task list.

**Priority**: P4
**Dependencies**: US1 (authentication) + US2 (task viewing) must be complete

**Independent Test Criteria**:
✅ Select an existing task
✅ Modify title and/or description
✅ Save changes
✅ Updates persisted and displayed correctly (verify with page refresh)

**Tasks**:

- [X] T026 Add PUT /api/tasks/{id} endpoint to backend/routers/tasks.py (update task, validate ownership, refresh updated_at)
- [X] T027 [P] [US4] Add edit mode to frontend/src/components/TaskForm.tsx (populate with existing task data)
- [X] T028 [P] [US4] Add edit button to frontend/src/components/TaskCard.tsx to trigger edit mode
- [X] T029 [US4] Implement PUT /api/tasks/{id} call in TaskForm and update task list on success

**Acceptance Scenarios** (from spec.md):
1. ✅ Click edit, modify title, save → task title updated in list
2. ✅ Modify description, save → task description updated
3. ✅ Clear title, try to save → validation error, change not saved
4. ✅ Cancel without saving → original task data unchanged

**Completion Criteria**:
- [x] PUT /api/tasks/{id} updates task only if owned by authenticated user (verify: 404 for other users' tasks)
- [x] updated_at timestamp refreshed on update (verify: timestamp changes in database)
- [x] Empty title rejected with 400 error (verify: validation message displayed)
- [x] Cancel button discards changes (verify: original values restored)
- [x] All 4 acceptance scenarios pass manual testing

**Files Created/Modified**:
- backend/routers/tasks.py (add PUT endpoint)
- frontend/src/components/TaskForm.tsx (add edit mode)
- frontend/src/components/TaskCard.tsx (add edit button)

---

## Phase 7: User Story 5 - Toggle Task Completion Status (P5)

**Story**: An authenticated user completes a task and wants to mark it as done. They click a checkbox or completion button next to the task, and the task is visually marked as complete. They can also unmark a task if they need to work on it again.

**Priority**: P5
**Dependencies**: US1 (authentication) + US2 (task viewing) must be complete

**Independent Test Criteria**:
✅ Click completion toggle on incomplete task
✅ Task changes to complete status with visual feedback
✅ Toggle back to incomplete
✅ Status persists after page refresh

**Tasks**:

- [X] T030 Add PATCH /api/tasks/{id}/complete endpoint to backend/routers/tasks.py (toggle completed boolean, refresh updated_at)
- [X] T031 [P] [US5] Add completion checkbox to frontend/src/components/TaskCard.tsx
- [X] T032 [P] [US5] Implement toggle handler in TaskCard to call PATCH /api/tasks/{id}/complete and update UI immediately
- [X] T033 [US5] Add visual styling to TaskCard for completed vs incomplete tasks (strikethrough, color change, opacity)

**Acceptance Scenarios** (from spec.md):
1. ✅ Click completion checkbox on incomplete task → marked complete, visually distinguished
2. ✅ Click completion checkbox on complete task → marked incomplete
3. ✅ Toggle completion, refresh page → status persists correctly
4. ✅ Mark task complete → immediate visual feedback (no page reload)

**Completion Criteria**:
- [x] PATCH /api/tasks/{id}/complete toggles completed boolean (verify: false→true, true→false)
- [x] updated_at timestamp refreshed (verify: timestamp updated in database)
- [x] Completed tasks visually distinct (verify: styling applied correctly)
- [x] Toggle works without page reload (verify: optimistic UI update)
- [x] All 4 acceptance scenarios pass manual testing

**Files Created/Modified**:
- backend/routers/tasks.py (add PATCH endpoint)
- frontend/src/components/TaskCard.tsx (add checkbox and toggle handler)

---

## Phase 8: User Story 6 - Delete Tasks (P6)

**Story**: An authenticated user wants to remove a task that is no longer relevant. They click a delete button, optionally confirm the deletion, and the task is permanently removed from their task list.

**Priority**: P6 (Lowest Priority)
**Dependencies**: US1 (authentication) + US2 (task viewing) must be complete

**Independent Test Criteria**:
✅ Select a task
✅ Click delete button
✅ Confirm deletion
✅ Task removed from task list and database (verify with page refresh)

**Tasks**:

- [X] T034 Add DELETE /api/tasks/{id} endpoint to backend/routers/tasks.py (delete task, validate ownership)
- [X] T035 [P] [US6] Add delete button to frontend/src/components/TaskCard.tsx
- [X] T036 [P] [US6] Implement delete confirmation dialog in TaskCard (browser confirm or custom modal)
- [X] T037 [US6] Implement DELETE /api/tasks/{id} call on confirmation and remove task from UI immediately

**Acceptance Scenarios** (from spec.md):
1. ✅ Click delete, confirm → task removed from list
2. ✅ Click delete, cancel → task remains in list
3. ✅ Delete task, refresh page → task does not reappear
4. ✅ Delete task → see success notification

**Completion Criteria**:
- [x] DELETE /api/tasks/{id} deletes task only if owned by authenticated user (verify: 404 for other users' tasks)
- [x] Confirmation dialog prevents accidental deletion (verify: cancel preserves task)
- [x] Task removed from database (verify: no longer appears after page refresh)
- [x] Success notification displayed (verify: toast or message shown)
- [x] All 4 acceptance scenarios pass manual testing

**Files Created/Modified**:
- backend/routers/tasks.py (add DELETE endpoint)
- frontend/src/components/TaskCard.tsx (add delete button and confirmation)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Finalize production-ready features and optimize user experience

**Dependencies**: ALL user stories (US1-US6) must be complete

**Tasks**:

- [X] T038 Create frontend/tailwind.config.js and configure responsive breakpoints per plan.md (320px-1920px)
- [X] T039 [P] Add loading states to all frontend API calls (spinner, skeleton screens, disabled buttons during operations)
- [X] T040 [P] Add error handling and user-friendly error messages to all frontend API calls (toast notifications, inline errors)
- [X] T041 [P] Add success notifications to frontend for create, update, delete operations (toast messages)
- [X] T042 Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL placeholders and instructions

**Completion Criteria**:
- [x] All UI components responsive on 320px (mobile) to 1920px (desktop) screens
- [x] Loading states prevent duplicate submissions and provide visual feedback
- [x] Error messages are user-friendly (no raw stack traces or technical jargon)
- [x] Success notifications confirm operation completion
- [x] .env.example enables new developers to set up environment easily

**Files Created/Modified**:
- frontend/tailwind.config.js
- frontend/src/lib/api.ts (add error handling)
- frontend/src/components/*.tsx (add loading/error states)
- .env.example

---

## Manual Testing Checklist

**Phase 3 (US1 - Authentication)**:
- [ ] Create account via signup form with valid email and password
- [ ] Verify JWT token received and stored
- [ ] Log in with created credentials
- [ ] Verify redirect to dashboard with authentication
- [ ] Attempt to access dashboard without token → redirected to login
- [ ] Verify incorrect credentials show error message

**Phase 4 (US2 - View Tasks)**:
- [ ] Log in with account that has tasks → see task list
- [ ] Verify task details displayed (title, description, completion status)
- [ ] Log in with new account (no tasks) → see empty state message
- [ ] Create task for user A, log in as user B → verify user B sees empty list (data isolation)
- [ ] Create completed and incomplete tasks → verify visual distinction

**Phase 5 (US3 - Create Tasks)**:
- [ ] Click "Add Task" button → form appears
- [ ] Submit task with title and description → task appears in list
- [ ] Submit task with title only → task created successfully
- [ ] Submit task with empty title → validation error displayed
- [ ] Verify new task defaults to incomplete status

**Phase 6 (US4 - Update Tasks)**:
- [ ] Click edit button on task → form populated with existing data
- [ ] Modify title and save → changes reflected in list
- [ ] Modify description and save → changes persisted
- [ ] Clear title and try to save → validation error shown
- [ ] Click cancel → original data unchanged

**Phase 7 (US5 - Toggle Completion)**:
- [ ] Click completion checkbox on incomplete task → marked complete with visual change
- [ ] Click completion checkbox on complete task → marked incomplete
- [ ] Toggle completion, refresh page → status persists
- [ ] Verify immediate visual feedback (no page reload needed)

**Phase 8 (US6 - Delete Tasks)**:
- [ ] Click delete button → confirmation dialog appears
- [ ] Confirm deletion → task removed from list
- [ ] Click delete, then cancel → task remains in list
- [ ] Delete task, refresh page → task does not reappear
- [ ] Verify success notification displayed

**Phase 9 (Polish)**:
- [ ] Test UI on 320px mobile screen → all elements usable
- [ ] Test UI on 1920px desktop screen → layout responsive
- [ ] Trigger loading states → spinner/disabled buttons shown
- [ ] Trigger error (e.g., network failure) → user-friendly error message displayed
- [ ] Complete operations → success notifications shown

---

## Constitutional Compliance

**Phase II Requirements**:
- [x] User identity from Better Auth JWT (T007-T008, T010-T011)
- [x] Persistent database with Neon PostgreSQL (T004-T005)
- [x] RESTful API conventions (T009, T017, T022, T026, T030, T034)
- [x] User data isolation enforced (T008, T017 - user_id scoping)
- [x] No hardcoded secrets (T042 - environment variables)

**Security & Identity Laws**:
- [x] Passwords hashed with bcrypt (T007, T010)
- [x] JWT tokens validated on protected endpoints (T008, T017+)
- [x] 401 Unauthorized for invalid tokens (T008, T016)
- [x] Secrets externalized to .env (T042)

**Task Decomposition Law**:
- [x] All tasks atomic and independently implementable
- [x] Clear file paths specified for each task
- [x] Dependencies explicitly documented
- [x] Parallel execution opportunities identified

---

## Implementation Notes

### Backend Development Workflow
```bash
# Terminal 1: Run backend server
uvicorn backend.main:app --reload --port 8000

# Access API docs
open http://localhost:8000/docs
```

### Frontend Development Workflow
```bash
# Terminal 2: Run frontend dev server
cd frontend && npm run dev

# Access application
open http://localhost:3000
```

### Database Schema Initialization
```bash
# Initialize database tables (run once)
python3 -m backend.database init

# Or tables auto-created on first app startup
```

### Environment Variables Setup
```bash
# Copy example and fill in values
cp .env.example .env

# Required values:
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db
# BETTER_AUTH_SECRET=min-32-character-secret-key
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Success Metrics (from spec.md)

After completing all tasks, verify these measurable outcomes:

- **SC-001**: Account registration completes in <1 minute
- **SC-002**: Login and dashboard access in <10 seconds
- **SC-003**: Task operations complete in <2 seconds
- **SC-004**: Display 100 tasks without performance degradation
- **SC-005**: 100% user data isolation (zero unauthorized access)
- **SC-006**: Responsive UI on 320px-1920px screens
- **SC-007**: 95%+ appropriate HTTP status codes
- **SC-008**: 20+ consecutive sessions without data loss

---

## Next Steps

1. **Review & Approve Tasks**: Validate task decomposition with stakeholders
2. **Begin Implementation**: Run `/sp.implement --from tasks` to execute Claude Code agentic implementation
3. **Execute MVP First**: Implement Phase 1-3 (T001-T016) for minimal viable product
4. **Incremental Deployment**: Deploy after each user story phase completion
5. **Manual Testing**: Execute testing checklist after each phase
6. **Production Release**: Deploy Phase 9 (Polish) for production-ready application

---

**Document Status**: Complete - Ready for Implementation
**Total Tasks**: 42 tasks (35 implementation + 7 testing verification points)
**Estimated MVP**: ~1-2 days (Phase 1-3: T001-T016)
**Estimated Full Feature**: ~3-5 days (all phases)
**Generated By**: Claude Code (/sp.tasks command)
**Date**: 2026-01-14
