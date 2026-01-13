# Research: Todo In-Memory Python Console Application

**Feature**: 001-todo-cli-app
**Phase**: Phase 0 - Research & Technology Decisions
**Date**: 2026-01-13

## Purpose

This document resolves all technical unknowns and establishes technology decisions for the Phase I Todo CLI application. All decisions must align with constitutional requirements and specification constraints.

---

## Research Questions Resolved

### 1. Python Version & Environment Management

**Decision**: Python 3.13+ with UV for dependency management

**Rationale**:
- Python 3.13 specified in spec (TC-001)
- UV is mandated for environment and dependency management (TC-002)
- UV provides fast, reliable dependency resolution
- UV integrates well with modern Python tooling

**Alternatives Considered**:
- Poetry: Not specified in requirements, UV is mandated
- pip + venv: Less robust than UV for modern Python projects
- conda: Overkill for simple CLI application

**Implementation Notes**:
- Use `pyproject.toml` for project configuration
- UV handles virtual environment creation automatically
- No additional dependency managers needed

---

### 2. In-Memory Storage Structure

**Decision**: Python dictionary with integer keys for ID-based lookups

**Rationale**:
- Fast O(1) lookup by todo ID
- Simple to implement and reason about
- No persistence required (FR-010)
- Supports all required operations (add, update, delete, list)

**Alternatives Considered**:
- List with sequential access: O(n) lookups, slower for ID-based operations
- Class with list attribute: Unnecessary abstraction for Phase I
- dataclasses with storage: Over-engineered for in-memory needs

**Data Structure**:
```
todos = {
    1: Todo(id=1, title="...", description="...", completed=False),
    2: Todo(id=2, title="...", description="...", completed=True),
    ...
}
```

**ID Generation Strategy**: Auto-incrementing counter (global variable or class attribute)

---

### 3. Todo Data Model

**Decision**: Python dataclass with four fields

**Rationale**:
- Dataclasses provide automatic `__init__`, `__repr__`, and equality
- Type hints enforce field types
- Immutable by default if needed (frozen=True)
- Clear entity definition from spec

**Entity Definition** (from spec):
- ID: int (unique, auto-generated)
- Title: str (required, non-empty)
- Description: str (optional, defaults to empty string)
- Completed: bool (defaults to False)

**Implementation Approach**:
```python
from dataclasses import dataclass

@dataclass
class Todo:
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

**Validation**:
- Title cannot be empty (validated at input time)
- ID uniqueness enforced by storage structure
- Description can be empty (optional field)

---

### 4. Command-Line Interface Pattern

**Decision**: Menu-driven loop with numbered options

**Rationale**:
- Clear user experience (FR-011)
- Supports multiple operations per session (FR-013)
- Easy to implement with Python's `input()`
- Graceful exit option (FR-014)

**Alternatives Considered**:
- Click/Typer CLI frameworks: Overkill for simple menu
- argparse with subcommands: Less interactive than menu
- Natural language input: Too complex for Phase I

**Menu Structure**:
```
Todo Application
1. Add Todo
2. View Todos
3. Update Todo
4. Mark Complete/Incomplete
5. Delete Todo
6. Exit
```

**Implementation Pattern**:
- Main loop with `while True`
- Input validation for menu choices
- Clear prompts for each operation
- Error messages for invalid inputs

---

### 5. Error Handling Strategy

**Decision**: Try-except with custom error messages at operation level

**Rationale**:
- Graceful handling of invalid IDs (FR-012)
- Application must not crash
- Clear user feedback required

**Error Cases**:
1. Invalid todo ID: "Todo ID not found"
2. Empty title: "Title cannot be empty"
3. Invalid menu choice: "Invalid option, please try again"
4. Non-integer ID input: "Please enter a valid number"

**Implementation Approach**:
- Validate inputs before operations
- Use exceptions for control flow where appropriate
- Return early on validation failures
- Display error and return to menu (don't exit)

---

### 6. Code Organization

**Decision**: Modular structure with separation of concerns

**Rationale**:
- Business logic separate from UI (Phase I principle)
- Easy to test individual components
- Clean code principles
- Supports future phases

**Module Structure**:
```
src/
├── todo.py          # Todo dataclass
├── storage.py       # In-memory storage operations
├── operations.py    # Business logic (add, update, delete, etc.)
├── cli.py           # Command-line interface and menu
└── main.py          # Entry point
```

**Rationale for Each Module**:
- `todo.py`: Entity definition (single responsibility)
- `storage.py`: Storage abstraction (could swap implementations)
- `operations.py`: Pure business logic (testable)
- `cli.py`: User interaction (isolated from logic)
- `main.py`: Application entry point (minimal)

---

### 7. Display Formatting

**Decision**: Simple text-based table format with visual separators

**Rationale**:
- Clear visual distinction of completed vs incomplete (SC-002)
- Shows all required fields: ID, title, status (FR-004)
- Terminal-friendly (no external dependencies)

**Display Format**:
```
ID | Title              | Description         | Status
---+--------------------+---------------------+------------
1  | Buy groceries      | Milk, eggs, bread   | Incomplete
2  | Call dentist       |                     | Complete
3  | Finish report      | Q4 summary          | Incomplete
```

**Status Display**:
- Incomplete: "Incomplete" or "[ ]"
- Complete: "Complete" or "[✓]"
- Choose based on terminal compatibility

---

### 8. Testing Strategy (if applicable)

**Decision**: Manual testing via acceptance scenarios

**Rationale**:
- No automated tests explicitly requested in spec
- Acceptance scenarios (spec) serve as test cases
- Each user story has testable scenarios
- Focus on functional validation

**Testing Approach**:
- User Story 1: Test add and view operations
- User Story 2: Test mark complete/incomplete
- User Story 3: Test update operations
- User Story 4: Test delete operations
- Edge cases: Empty titles, invalid IDs, large datasets

**If tests requested later**:
- Use pytest (Python standard)
- Test operations.py functions (pure logic)
- Mock storage for unit tests

---

### 9. Dependencies

**Decision**: No external dependencies beyond Python standard library

**Rationale**:
- Spec explicitly forbids external libraries (EX-010)
- Python standard library sufficient for all requirements
- Keeps project simple and constitutional

**Standard Library Modules Used**:
- `dataclasses`: Todo entity
- `typing`: Type hints
- `sys`: Exit functionality

**UV Project Configuration**:
- Minimal `pyproject.toml`
- No external dependencies listed
- Python 3.13+ required

---

### 10. Performance Considerations

**Decision**: No special optimizations needed for Phase I

**Rationale**:
- Spec requires handling 100 todos (SC-007)
- In-memory dictionary easily handles this scale
- Python performance sufficient for console app
- No premature optimization

**Performance Notes**:
- Dictionary lookups: O(1)
- List all todos: O(n) acceptable for n ≤ 100
- Memory footprint negligible for 100 todos
- No performance testing needed for Phase I

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.13+ | Spec requirement (TC-001) |
| Dependency Mgmt | UV | Spec requirement (TC-002) |
| Data Model | Dataclass | Simple, type-safe, standard |
| Storage | Dictionary | Fast, simple, in-memory |
| CLI Framework | Native input/print | No external deps allowed |
| Testing | Manual | Not required in spec |
| Dependencies | None | Spec forbids external libs |

---

## Constitutional Compliance Check

- [x] **Agentic Implementation (I)**: All code generated by Claude Code
- [x] **Spec-Driven (II)**: All decisions traceable to spec requirements
- [x] **Plan-Before-Build (III)**: This research enables planning
- [x] **Phase I Requirements**: CLI-only, in-memory, no persistence
- [x] **No Forbidden Technologies**: No databases, files, web, auth, AI, containers
- [x] **Standard Library Only**: No external dependencies

---

## Risks & Mitigations

**Risk 1**: User force-quits application
- **Impact**: Data lost
- **Mitigation**: Acceptable per spec (AC-004), document in README

**Risk 2**: Extremely long titles (>1000 chars)
- **Impact**: Display formatting issues
- **Mitigation**: Truncate display, store full title

**Risk 3**: Rapid addition of 100+ todos
- **Impact**: Memory usage
- **Mitigation**: Acceptable, Python handles this scale

---

## Next Steps

With all research complete:
1. Generate `data-model.md` (Phase 1)
2. Generate contracts (Phase 1) - N/A for CLI (no APIs)
3. Generate `quickstart.md` (Phase 1)
4. Generate full `plan.md` with all sections filled

---

**Research Phase Complete**: All technical unknowns resolved ✅
**Ready for**: Phase 1 Design
