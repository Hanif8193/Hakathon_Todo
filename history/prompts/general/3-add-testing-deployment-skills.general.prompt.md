---
id: 3
title: Add Testing and Deployment Skills
stage: general
date: 2026-01-12
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: PMLS
command: add testing and deployment skills next
labels: ["skills", "testing", "pytest", "deployment", "docker", "ci-cd", "github-actions"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/testing.md
  - .claude/skills/deployment.md
tests:
  - null
---

## Prompt

```text
add testing and deployment skills next
```

## Response snapshot

Created 2 new skills to complete the backend development skill suite:

1. **testing.md** - Comprehensive testing skill covering:
   - pytest configuration and project structure
   - Shared fixtures (database, client, factories)
   - Unit testing with mocks
   - Integration testing with real database
   - API endpoint testing
   - Parametrized tests for validation
   - Test coverage reporting

2. **deployment.md** - Production deployment skill covering:
   - Multi-stage Dockerfile (builder/production)
   - Docker Compose for dev and production
   - GitHub Actions CI/CD pipelines
   - Nginx reverse proxy with SSL
   - Health check endpoints
   - Environment management
   - Makefile commands
   - Zero-downtime deployment scripts

## Outcome

- ✅ Impact: Backend development skill suite now complete (8 skills total)
- 🧪 Tests: No tests required (documentation/skill files)
- 📁 Files: Created testing.md and deployment.md in .claude/skills/
- 🔁 Next prompts: Skills ready for use in FastAPI/backend projects
- 🧠 Reflection: The skill set now covers the complete development lifecycle from code to production

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation task)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding monitoring/observability skills or frontend integration skills
