"""Main entry point for Todo CLI Application.

Phase I: In-Memory Python Console Application
"""

import sys
try:
    from .cli import run_cli
except ImportError:
    from cli import run_cli


def main():
    """Application entry point."""
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {e}")
        print("Please report this issue if it persists.")
        sys.exit(1)


if __name__ == "__main__":
    main()
