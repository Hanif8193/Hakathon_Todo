# Todo CLI Application

**Phase I: In-Memory Python Console Application**

A command-line todo manager that stores tasks in memory. Build using spec-driven development principles with Claude Code.

## Features

- ✅ **Add Todos**: Create tasks with titles and optional descriptions
- ✅ **View Todos**: Display all tasks in a formatted table
- ✅ **Update Todos**: Modify titles and descriptions
- ✅ **Mark Complete/Incomplete**: Track completion status
- ✅ **Delete Todos**: Remove tasks from the list
- ✅ **CLI Interface**: Menu-driven console interaction

## Requirements

- **Python**: 3.13 or higher
- **UV**: Package and dependency manager

## Installation

### 1. Install Python 3.13+

**Linux/WSL**:
```bash
# Using apt (Ubuntu/Debian)
sudo apt update
sudo apt install python3.13

# Verify installation
python3.13 --version
```

**macOS**:
```bash
brew install python@3.13
python3.13 --version
```

**Windows**:
Download from [python.org](https://python.org) or use WSL (recommended).

### 2. Install UV

```bash
# Linux/macOS/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Verify installation
uv --version
```

### 3. Clone/Navigate to Project

```bash
cd /path/to/todo
```

### 4. Initialize Environment

```bash
# UV will create a virtual environment and install dependencies
uv sync
```

## Usage

### Start the Application

```bash
# Using UV (recommended)
uv run python src/main.py

# Or activate virtual environment first
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
python src/main.py
```

### Main Menu

```
================================================================================
                          TODO CLI APPLICATION
================================================================================

1. Add Todo
2. View Todos
3. Update Todo
4. Mark Complete/Incomplete
5. Delete Todo
6. Exit

Select an option (1-6):
```

### Quick Examples

**Add a todo**:
```
Select option: 1
Enter title: Buy groceries
Enter description: Milk, eggs, bread
✓ Todo added successfully! (ID: 1)
```

**View todos**:
```
Select option: 2

================================================================================
                              TODO LIST
================================================================================
ID   | Title                          | Description          | Status
--------------------------------------------------------------------------------
1    | Buy groceries                  | Milk, eggs, bread    | Incomplete
================================================================================
Total: 1 todo
```

**Mark complete**:
```
Select option: 4
Enter todo ID: 1
Is it complete? (y/n): y
✓ Todo 1 marked as complete!
```

**Update todo**:
```
Select option: 3
Enter todo ID: 1
Update title? (y/n): y
Enter new title: Buy groceries and pharmacy items
Update description? (y/n): n
✓ Todo 1 updated successfully!
```

**Delete todo**:
```
Select option: 5
Enter todo ID: 1
✓ Todo 1 deleted successfully!
```

**Exit**:
```
Select option: 6
Thank you for using Todo CLI! Goodbye!
```

## Project Structure

```
todo/
├── src/
│   ├── __init__.py       # Package marker
│   ├── todo.py           # Todo dataclass entity
│   ├── storage.py        # In-memory storage layer
│   ├── operations.py     # Business logic
│   ├── cli.py            # Command-line interface
│   └── main.py           # Application entry point
├── specs/
│   └── 001-todo-cli-app/ # Feature specifications and design
├── .gitignore            # Git ignore file
├── pyproject.toml        # UV project configuration
├── README.md             # This file
└── CLAUDE.md             # Claude Code operating rules
```

## Architecture

**Modular Design** (Bottom-Up):
```
main.py (Entry Point)
  └── cli.py (UI Layer)
       └── operations.py (Business Logic)
            └── storage.py (Data Layer)
                 └── todo.py (Entity)
```

**Storage**: In-memory Python dictionary (`dict[int, Todo]`)
**ID Generation**: Auto-incrementing counter (starts at 1)
**Persistence**: None (data lost on exit - Phase I design)

## Phase I Limitations

- **No Persistence**: All data is stored in memory and lost when you exit
- **No Authentication**: Single-user, no user accounts
- **No Web Interface**: CLI only
- **No API**: Direct command-line usage only
- **No AI Features**: No intelligent assistance

These limitations will be addressed in future phases:
- **Phase II**: Web app, database persistence, REST APIs, authentication
- **Phase III**: AI agents, MCP tools, chat interface
- **Phase IV**: Containers, Kubernetes deployment
- **Phase V**: Cloud-native, event-driven architecture

## Development

### Spec-Driven Development

This project follows strict spec-driven development:

1. **Specification** (`specs/001-todo-cli-app/spec.md`): Requirements and acceptance criteria
2. **Plan** (`specs/001-todo-cli-app/plan.md`): Architecture and design decisions
3. **Tasks** (`specs/001-todo-cli-app/tasks.md`): Atomic implementation tasks
4. **Implementation**: All code generated by Claude Code

### Constitutional Governance

Governed by `.specify/memory/constitution.md`:
- All implementation by Claude Code
- No manual coding by humans
- Spec-driven workflow enforced
- Phase I requirements: CLI-only, in-memory, no persistence

## Troubleshooting

### "Python version too old"
Install Python 3.13 or higher.

### "uv command not found"
Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### "Module not found" errors
Run `uv sync` to initialize the environment.

### Application doesn't start
Verify all source files exist: `ls src/`

### "Invalid option" error
Enter numbers 1-6 only.

### "Todo ID not found"
View todos first (option 2) to see valid IDs.

## Quick Reference

```
┌─────────────────────────────────────────┐
│         TODO CLI QUICK REFERENCE        │
├─────────────────────────────────────────┤
│ 1 - Add Todo                            │
│ 2 - View Todos                          │
│ 3 - Update Todo                         │
│ 4 - Mark Complete/Incomplete            │
│ 5 - Delete Todo                         │
│ 6 - Exit                                │
└─────────────────────────────────────────┘

Start: uv run python src/main.py
Stop:  Select option 6 or Ctrl+C
```

## Documentation

- **Specification**: `specs/001-todo-cli-app/spec.md`
- **Implementation Plan**: `specs/001-todo-cli-app/plan.md`
- **Data Model**: `specs/001-todo-cli-app/data-model.md`
- **Quickstart Guide**: `specs/001-todo-cli-app/quickstart.md`
- **Task List**: `specs/001-todo-cli-app/tasks.md`

## License

MIT License

## Version

**Phase I**: Version 0.1.0
**Status**: Complete
**Date**: 2026-01-13
