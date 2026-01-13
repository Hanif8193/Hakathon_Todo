"""Command-line interface for Todo CLI Application.

This module provides the user-facing menu and display functions.
"""

try:
    from .todo import Todo
    from . import operations
except ImportError:
    from todo import Todo
    import operations


def display_menu():
    """Display the main menu options."""
    print("=" * 80)
    print(" " * 26 + "TODO CLI APPLICATION")
    print("=" * 80)
    print()
    print("1. Add Todo")
    print("2. View Todos")
    print("3. Update Todo")
    print("4. Mark Complete/Incomplete")
    print("5. Delete Todo")
    print("6. Exit")
    print()


def display_todos(todos: list[Todo]):
    """
    Display todos in a formatted table.

    Args:
        todos: List of Todo objects to display
    """
    print()
    print("=" * 80)
    print(" " * 32 + "TODO LIST")
    print("=" * 80)

    if not todos:
        print("No todos found. Add your first todo to get started!")
        print("=" * 80)
        return

    # Table header
    print(f"{'ID':<4} | {'Title':<30} | {'Description':<20} | {'Status':<12}")
    print("-" * 80)

    # Table rows
    for todo in todos:
        # Truncate long strings for display
        title_display = todo.title[:28] + "..." if len(todo.title) > 30 else todo.title
        desc_display = todo.description[:18] + "..." if len(todo.description) > 20 else todo.description
        status_display = "Complete" if todo.completed else "Incomplete"

        print(f"{todo.id:<4} | {title_display:<30} | {desc_display:<20} | {status_display:<12}")

    print("=" * 80)
    print(f"Total: {len(todos)} todo{'s' if len(todos) != 1 else ''}")
    print()


def get_menu_choice() -> int:
    """
    Get and validate menu choice from user.

    Returns:
        Valid menu choice (1-6)
    """
    while True:
        try:
            choice = input("Select an option (1-6): ")
            choice_int = int(choice)

            if 1 <= choice_int <= 6:
                return choice_int
            else:
                print("Invalid option. Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            return 6  # Exit


def handle_add_todo():
    """Handle the 'Add Todo' operation."""
    print()
    print("--- Add New Todo ---")

    try:
        title = input("Enter title: ")
        description = input("Enter description (optional): ")

        result = operations.add_new_todo(title, description)

        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['message']}")

    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")


def handle_view_todos():
    """Handle the 'View Todos' operation."""
    result = operations.view_all_todos()
    display_todos(result["data"])


def handle_update_todo():
    """Handle the 'Update Todo' operation."""
    print()
    print("--- Update Todo ---")

    try:
        todo_id_str = input("Enter todo ID: ")

        try:
            todo_id = int(todo_id_str)
        except ValueError:
            print("✗ Error: Please enter a valid number")
            return

        # Ask which fields to update
        update_title_input = input("Update title? (y/n): ").strip().lower()
        new_title = None
        if update_title_input == 'y':
            new_title = input("Enter new title: ")

        update_desc_input = input("Update description? (y/n): ").strip().lower()
        new_description = None
        if update_desc_input == 'y':
            new_description = input("Enter new description: ")

        # Perform update
        result = operations.update_todo_details(todo_id, new_title, new_description)

        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['message']}")

    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")


def handle_mark_complete():
    """Handle the 'Mark Complete/Incomplete' operation."""
    print()
    print("--- Mark Todo Complete/Incomplete ---")

    try:
        todo_id_str = input("Enter todo ID: ")

        try:
            todo_id = int(todo_id_str)
        except ValueError:
            print("✗ Error: Please enter a valid number")
            return

        complete_input = input("Is it complete? (y/n): ").strip().lower()
        complete = complete_input == 'y'

        result = operations.toggle_todo_status(todo_id, complete)

        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['message']}")

    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")


def handle_delete_todo():
    """Handle the 'Delete Todo' operation."""
    print()
    print("--- Delete Todo ---")

    try:
        todo_id_str = input("Enter todo ID: ")

        try:
            todo_id = int(todo_id_str)
        except ValueError:
            print("✗ Error: Please enter a valid number")
            return

        result = operations.remove_todo(todo_id)

        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['message']}")

    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")


def run_cli():
    """
    Main CLI loop.

    Displays menu, gets user choice, and executes corresponding handler.
    Loops until user selects Exit (option 6).
    """
    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_todo()
        elif choice == 2:
            handle_view_todos()
        elif choice == 3:
            handle_update_todo()
        elif choice == 4:
            handle_mark_complete()
        elif choice == 5:
            handle_delete_todo()
        elif choice == 6:
            print("\nThank you for using Todo CLI! Goodbye!")
            break

        # Pause before showing menu again (except on exit)
        if choice != 6:
            input("\nPress Enter to continue...")
