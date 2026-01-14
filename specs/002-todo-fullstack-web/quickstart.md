# Quickstart Guide: Todo Full-Stack Web Application

**Feature**: 002-todo-fullstack-web
**Date**: 2026-01-14
**Target**: New developers setting up local development environment

## Purpose

This guide enables a new developer to set up and run the Todo Full-Stack Web Application locally within 15 minutes.

---

## Prerequisites

Ensure the following software is installed on your system:

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| **WSL 2** | Ubuntu 22.04+ | Linux environment on Windows | [WSL Install Guide](https://learn.microsoft.com/en-us/windows/wsl/install) |
| **Python** | 3.11+ | Backend runtime | `sudo apt install python3.11 python3.11-venv` |
| **UV** | Latest | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node.js** | 18+ | Frontend runtime | `curl -fsSL https://deb.nodesource.com/setup_18.x \| sudo -E bash - && sudo apt install -y nodejs` |
| **npm** | 9+ | Node package manager | Installed with Node.js |
| **Git** | 2.0+ | Version control | `sudo apt install git` |
| **PostgreSQL Client** | 15+ | Database CLI (optional) | `sudo apt install postgresql-client` |

**Verification**:
```bash
python3 --version    # Should show 3.11+
uv --version         # Should show latest version
node --version       # Should show v18+
npm --version        # Should show 9+
git --version        # Should show 2.0+
```

---

## Step 1: Clone Repository

```bash
# Navigate to your projects directory
cd ~/projects  # Or your preferred location

# Clone the repository
git clone <repository-url> todo
cd todo

# Checkout Phase II branch
git checkout 002-todo-fullstack-web

# Verify you're on the correct branch
git branch --show-current  # Should show: 002-todo-fullstack-web
```

---

## Step 2: Set Up Environment Variables

Create a `.env` file in the repository root with the following configuration:

```bash
# Create .env file from example
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

**Required Environment Variables**:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Authentication Secret
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Obtaining Database URL (Neon PostgreSQL)

**Option 1: Use Existing Neon Database** (Recommended)
1. Log in to [Neon Console](https://console.neon.tech)
2. Navigate to your project
3. Click "Connection Details"
4. Copy the **Connection String** for Node.js/Python
5. Replace `postgresql://` with `postgresql+asyncpg://` (for async driver)
6. Paste into `.env` as `DATABASE_URL`

**Option 2: Create New Neon Database**
1. Sign up at [Neon](https://neon.tech) (free tier available)
2. Create a new project named `todo-app`
3. Create a database named `todo`
4. Copy connection string (format: `postgresql+asyncpg://user:pass@host/db`)
5. Add to `.env` as `DATABASE_URL`

**Option 3: Use Local PostgreSQL** (Advanced)
```bash
# Install PostgreSQL locally
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb todo

# Create user
sudo -u postgres createuser -P todouser  # Enter password when prompted

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE todo TO todouser;"

# Connection string
DATABASE_URL=postgresql+asyncpg://todouser:password@localhost:5432/todo
```

### Generating Auth Secret

```bash
# Generate a secure random secret (32+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy output to .env as BETTER_AUTH_SECRET
```

**Example `.env` file**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@ep-example.us-east-2.aws.neon.tech/todo
BETTER_AUTH_SECRET=abc123xyz789randomsecretkeythatis32charslong
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 3: Set Up Backend (FastAPI)

### Install Python Dependencies

```bash
# Navigate to repository root
cd /path/to/todo

# Install dependencies with UV
uv pip install -r requirements.txt

# Or manually install core dependencies
uv pip install fastapi uvicorn sqlmodel asyncpg passlib[bcrypt] python-jose[cryptography]
```

**Expected `requirements.txt`** (will be created during implementation):
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
```

### Initialize Database Schema

```bash
# Run database initialization script (creates tables)
python3 -m backend.database init

# Or run via FastAPI startup (automatic on first run)
# Tables are created automatically when the app starts
```

**Verify Database Schema**:
```bash
# Connect to database
psql "$DATABASE_URL"

# List tables (should show 'user' and 'task')
\dt

# Describe user table
\d user

# Describe task table
\d task

# Exit psql
\q
```

---

## Step 4: Set Up Frontend (Next.js)

### Install Node Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies with npm
npm install

# Or use pnpm for faster installs (optional)
pnpm install
```

**Expected `package.json` dependencies** (will be created during implementation):
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "^0.5.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.3.0"
  }
}
```

### Configure Tailwind CSS

Tailwind configuration is auto-generated by `create-next-app`, but verify the following:

**`tailwind.config.js`**:
```javascript
module.exports = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## Step 5: Run the Application

### Terminal 1: Start Backend Server

```bash
# Navigate to repository root
cd /path/to/todo

# Run FastAPI with auto-reload
uvicorn backend.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using StatReload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Verify Backend**:
- Open browser: http://localhost:8000/docs
- You should see the FastAPI automatic documentation (Swagger UI)
- API endpoints listed: `/api/auth/signup`, `/api/auth/login`, `/api/tasks`, etc.

### Terminal 2: Start Frontend Server

```bash
# Navigate to frontend directory
cd /path/to/todo/frontend

# Run Next.js development server
npm run dev

# Expected output:
# ▲ Next.js 16.0.0
# - Local:        http://localhost:3000
# - Ready in 1.2s
```

**Verify Frontend**:
- Open browser: http://localhost:3000
- You should see the login/signup page
- No errors in browser console

---

## Step 6: Verify End-to-End Flow

### Test User Signup

1. **Navigate to signup page**: http://localhost:3000/signup
2. **Fill in signup form**:
   - Email: `test@example.com`
   - Password: `SecurePass123`
3. **Submit form**: Click "Sign Up"
4. **Expected result**: Redirected to dashboard with empty task list

### Test User Login

1. **Navigate to login page**: http://localhost:3000/login
2. **Fill in login form**:
   - Email: `test@example.com`
   - Password: `SecurePass123`
3. **Submit form**: Click "Log In"
4. **Expected result**: Redirected to dashboard

### Test Task Creation

1. **On dashboard**: Click "Add Task" button
2. **Fill in task form**:
   - Title: `Test Task`
   - Description: `This is a test task`
3. **Submit form**: Click "Create"
4. **Expected result**: New task appears in task list

### Test Task Operations

1. **Toggle completion**: Click checkbox next to task → task marked complete with visual change
2. **Edit task**: Click "Edit" → modify title/description → save → changes reflected
3. **Delete task**: Click "Delete" → confirm → task removed from list

### Test Data Isolation

1. **Create second user**:
   - Log out (if logout implemented) or open incognito window
   - Sign up with `test2@example.com` / `SecurePass456`
2. **Verify isolation**:
   - Dashboard should be empty (no tasks from first user)
   - Create a task for second user
3. **Switch back to first user**:
   - Log in as `test@example.com`
   - Verify only first user's tasks are visible

---

## Step 7: Verify Database Persistence

### Check Database Manually

```bash
# Connect to database
psql "$DATABASE_URL"

# List all users
SELECT id, email, created_at FROM "user";

# List all tasks
SELECT id, title, completed, user_id, created_at FROM task;

# Verify referential integrity (tasks belong to users)
SELECT u.email, t.title, t.completed
FROM "user" u
JOIN task t ON t.user_id = u.id;

# Exit
\q
```

### Test Persistence Across Restarts

1. **Create a task** in the web UI
2. **Stop both servers** (Ctrl+C in both terminals)
3. **Restart both servers**:
   - Backend: `uvicorn backend.main:app --reload --port 8000`
   - Frontend: `cd frontend && npm run dev`
4. **Refresh browser**: Task should still be present (persisted in database)

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Install dependencies: `uv pip install -r requirements.txt`

**Issue**: `sqlalchemy.exc.OperationalError: connection refused`
**Solution**: Verify `DATABASE_URL` in `.env` is correct and database is accessible

**Issue**: `jose.exceptions.JWTError: Invalid token`
**Solution**: Regenerate `BETTER_AUTH_SECRET` with at least 32 characters

**Issue**: Port 8000 already in use
**Solution**: Kill existing process: `lsof -ti:8000 | xargs kill -9` or use different port: `--port 8001`

### Frontend Issues

**Issue**: `Error: ENOENT: no such file or directory, open '.env.local'`
**Solution**: Ensure `.env` file exists in repository root with `NEXT_PUBLIC_API_URL`

**Issue**: `Failed to fetch` or CORS errors
**Solution**: Verify backend is running on port 8000 and CORS is enabled in `backend/main.py`

**Issue**: 401 Unauthorized on all API requests
**Solution**: Check JWT token is being attached to requests in `frontend/src/lib/api.ts`

**Issue**: Port 3000 already in use
**Solution**: Kill existing process: `lsof -ti:3000 | xargs kill -9` or set different port: `PORT=3001 npm run dev`

### Database Issues

**Issue**: `relation "user" does not exist`
**Solution**: Run database initialization: `python3 -m backend.database init`

**Issue**: `duplicate key value violates unique constraint "user_email_key"`
**Solution**: User with that email already exists; use a different email or delete existing user

**Issue**: Connection timeout to Neon
**Solution**: Check internet connection, verify Neon project is active (free tier may suspend after inactivity)

---

## Development Workflow

### Hot Reload

Both backend and frontend support hot reload:

- **Backend**: FastAPI auto-reloads when Python files change (`.py`)
- **Frontend**: Next.js Fast Refresh updates UI when React files change (`.tsx`, `.ts`)

**No server restart needed** for code changes during development.

### Making Changes

1. **Backend changes**: Edit files in `backend/` directory
   - Modify models: `backend/models.py`
   - Add routes: `backend/routers/`
   - Update auth: `backend/auth.py`
   - Server auto-reloads

2. **Frontend changes**: Edit files in `frontend/src/` directory
   - Add components: `frontend/src/components/`
   - Modify pages: `frontend/src/app/`
   - Update API client: `frontend/src/lib/api.ts`
   - Browser auto-refreshes

### Viewing Logs

**Backend logs** (Terminal 1):
- Request logs: `INFO: 127.0.0.1:xxxxx - "GET /api/tasks HTTP/1.1" 200 OK`
- Error logs: `ERROR: <error message and stack trace>`

**Frontend logs** (Terminal 2 + Browser Console):
- Build logs in terminal
- Runtime logs in browser DevTools console (F12)

---

## API Documentation

### Swagger UI (Interactive Docs)

- **URL**: http://localhost:8000/docs
- **Features**: Try out API endpoints, view request/response schemas
- **Authentication**: Click "Authorize" → paste JWT token from login response

### ReDoc (Alternative Docs)

- **URL**: http://localhost:8000/redoc
- **Features**: Cleaner, read-only documentation

### OpenAPI Spec

- **URL**: http://localhost:8000/openapi.json
- **Use case**: Import into Postman, Insomnia, or other API clients

---

## Next Steps

After successfully running the application locally:

1. **Review Implementation Plan**: [specs/002-todo-fullstack-web/plan.md](./plan.md)
2. **Understand Data Model**: [specs/002-todo-fullstack-web/data-model.md](./data-model.md)
3. **Study API Contracts**:
   - [contracts/auth-api.yaml](./contracts/auth-api.yaml)
   - [contracts/tasks-api.yaml](./contracts/tasks-api.yaml)
4. **Run Task Decomposition**: Execute `/sp.tasks --from plan` to generate atomic tasks
5. **Begin Implementation**: Execute `/sp.implement --from tasks` for Claude Code agentic development

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **Neon Documentation**: https://neon.tech/docs
- **Better Auth Documentation**: https://better-auth.com/docs

---

## Support

**Issues**: Report bugs or ask questions in the project repository's issue tracker

**Constitutional Reference**: This quickstart follows Phase II Web Application requirements defined in `.specify/memory/constitution.md`

---

**Document Status**: Complete
**Estimated Setup Time**: 15 minutes (assuming prerequisites installed)
**Last Updated**: 2026-01-14
