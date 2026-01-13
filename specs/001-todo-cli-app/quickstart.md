# Quickstart Guide: Todo CLI Application

**Feature**: 001-todo-cli-app
**Phase**: Phase I
**Last Updated**: 2026-01-13

## Overview

This guide helps you quickly set up and use the Todo CLI application - a command-line todo manager that stores tasks in memory.

---

## Prerequisites

- **Python**: 3.13 or higher
- **UV**: Package and dependency manager
- **Operating System**: Linux, macOS, or Windows (WSL recommended on Windows)

---

## Installation

### 1. Verify Python Version

```bash
python --version
# Should show Python 3.13.x or higher
```

If Python 3.13+ is not installed:
- **Linux/WSL**: Use `apt`, `yum`, or your package manager
- **macOS**: Use `brew install python@3.13`
- **Windows**: Download from python.org or use WSL

### 2. Install UV

```bash
# On Linux/macOS/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

Verify UV installation:
```bash
uv --version
```

### 3. Clone Repository (or navigate to project)

```bash
cd /path/to/todo
```

### 4. Initialize Environment

```bash
# UV will create a virtual environment and install dependencies
uv sync
```

---

## Running the Application

### Start the Todo CLI

```bash
# Using UV
uv run python src/main.py

# Or activate the virtual environment first
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
python src/main.py
```

You should see the main menu:

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

---

## Usage Examples

### Example 1: Add Your First Todo

```
Select an option (1-6): 1

--- Add New Todo ---
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread

✓ Todo added successfully! (ID: 1)
```

### Example 2: View All Todos

```
Select an option (1-6): 2

================================================================================
                              TODO LIST
================================================================================
ID | Title                          | Description         | Status
--------------------------------------------------------------------------------
1  | Buy groceries                  | Milk, eggs, bread   | Incomplete
================================================================================
Total: 1 todo
```

### Example 3: Mark Todo Complete

```
Select an option (1-6): 4

--- Mark Todo Complete/Incomplete ---
Enter todo ID: 1
Is it complete? (y/n): y

✓ Todo 1 marked as complete!
```

### Example 4: Update Todo

```
Select an option (1-6): 3

--- Update Todo ---
Enter todo ID: 1
Update title? (y/n): y
Enter new title: Buy groceries and pharmacy items
Update description? (y/n): y
Enter new description: Milk, eggs, bread, aspirin

✓ Todo 1 updated successfully!
```

### Example 5: Delete Todo

```
Select an option (1-6): 5

--- Delete Todo ---
Enter todo ID: 1

✓ Todo 1 deleted successfully!
```

### Example 6: Exit Application

```
Select an option (1-6): 6

Thank you for using Todo CLI! Goodbye!
```

---

## Feature Overview

### What You Can Do

1. **Add Todos**: Create new tasks with titles and optional descriptions
2. **View Todos**: See all your tasks with ID, title, description, and status
3. **Update Todos**: Modify titles and descriptions of existing tasks
4. **Mark Complete/Incomplete**: Track your progress by toggling completion status
5. **Delete Todos**: Remove tasks you no longer need
6. **Exit**: Close the application gracefully

### Important Notes

- **In-Memory Only**: All data is stored in memory and lost when you exit
- **No Persistence**: This is a Phase I feature - no file or database storage
- **Single Session**: Each time you run the app, you start fresh
- **CLI Only**: No web interface or API in Phase I

---

## Common Workflows

### Workflow 1: Daily Task Management

```
1. Start application
2. Add todos for the day (option 1)
3. View all todos (option 2)
4. Work on tasks...
5. Mark completed tasks (option 4)
6. View updated list (option 2)
7. Exit when done (option 6)
```

### Workflow 2: Quick Note Taking

```
1. Start application
2. Add several quick todos (option 1)
3. View list to review (option 2)
4. Update details as needed (option 3)
5. Delete irrelevant items (option 5)
6. Exit (option 6)
```

### Workflow 3: Task Refinement

```
1. Start application
2. Add initial task ideas (option 1)
3. View and review (option 2)
4. Update with more details (option 3)
5. Mark some as done (option 4)
6. Delete obsolete tasks (option 5)
7. Exit (option 6)
```

---

## Troubleshooting

### Problem: "Python version too old"

**Solution**: Install Python 3.13 or higher
```bash
python --version
# If < 3.13, install newer version
```

### Problem: "uv command not found"

**Solution**: Install UV package manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or: pip install uv
```

### Problem: "Module not found" errors

**Solution**: Ensure you're in the correct directory and UV environment is synced
```bash
cd /path/to/todo
uv sync
uv run python src/main.py
```

### Problem: Application doesn't start

**Solution**: Check that all source files exist
```bash
ls src/
# Should show: main.py, todo.py, storage.py, operations.py, cli.py
```

### Problem: "Invalid option" when entering menu choice

**Solution**: Enter numbers 1-6 only
```
Valid: 1, 2, 3, 4, 5, 6
Invalid: a, 0, 7, todo, etc.
```

### Problem: "Todo ID not found"

**Solution**: View todos first to see valid IDs
```
1. Select option 2 (View Todos)
2. Note the ID numbers
3. Use those IDs for update/delete/complete operations
```

---

## Tips & Best Practices

### Tip 1: Start with Viewing

Always view todos (option 2) before updating or deleting to see current IDs and status.

### Tip 2: Use Descriptions Wisely

Add descriptions for tasks that need context. Leave empty for simple tasks.

### Tip 3: ID Numbers

ID numbers auto-increment and are never reused (even after deletion). Don't rely on specific IDs staying the same across sessions.

### Tip 4: Data Loss

Remember: exiting the app loses all data. This is by design for Phase I. Future phases will add persistence.

### Tip 5: Multiple Sessions

You can run multiple operations in one session. The app loops until you explicitly exit (option 6).

---

## Limitations (Phase I)

Current limitations (resolved in future phases):

- **No Persistence**: Data lost on exit (Phase II will add database)
- **No Authentication**: No user accounts (Phase II will add auth)
- **No Web Interface**: CLI only (Phase II will add web UI)
- **No API**: Direct CLI usage only (Phase II will add REST API)
- **No AI Features**: No intelligent assistance (Phase III will add AI agents)
- **Single User**: No multi-user support (Phase II+ will add)

---

## Performance Notes

- **Capacity**: Handles 100+ todos efficiently
- **Speed**: All operations are instant (in-memory)
- **Memory**: Minimal memory footprint
- **Responsiveness**: No noticeable lag for typical usage

---

## Next Steps

After mastering the CLI:

1. **Phase II Preview**: Future phases will add web interface and persistence
2. **Feedback**: Report issues or suggest improvements
3. **Documentation**: See `README.md` for development details

---

## Support & Resources

- **Specification**: `specs/001-todo-cli-app/spec.md`
- **Architecture Plan**: `specs/001-todo-cli-app/plan.md`
- **Data Model**: `specs/001-todo-cli-app/data-model.md`
- **README**: Root `README.md` for development setup

---

## Quick Reference Card

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

---

**Quickstart Guide Complete** ✅
**Ready to use the Todo CLI Application!**
