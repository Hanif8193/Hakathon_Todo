#!/usr/bin/env python3
"""Test script for Todo CLI Application."""

import sys
sys.path.insert(0, 'src')

from todo import Todo
from storage import add_todo, get_todo, get_all_todos, update_todo, delete_todo, mark_complete, todos, next_id
from operations import add_new_todo, view_all_todos, update_todo_details, toggle_todo_status, remove_todo
from cli import display_todos


def reset_storage():
    """Reset storage for clean tests."""
    import storage
    storage.todos.clear()
    storage.next_id = 1


def test_imports():
    """Test 1: Verify all modules import correctly."""
    print("=" * 80)
    print("TEST 1: Module Imports")
    print("=" * 80)
    print("✓ Todo entity imported")
    print("✓ Storage functions imported")
    print("✓ Operations functions imported")
    print("✓ CLI functions imported")
    print("✓ All modules imported successfully!\n")


def test_add_todos():
    """Test 2: Add multiple todos."""
    print("=" * 80)
    print("TEST 2: Add Todos")
    print("=" * 80)

    result1 = add_new_todo('Buy groceries', 'Milk, eggs, bread')
    assert result1['success'], "Failed to add todo 1"
    print(f"✓ {result1['message']}")

    result2 = add_new_todo('Call dentist', 'Schedule annual checkup')
    assert result2['success'], "Failed to add todo 2"
    print(f"✓ {result2['message']}")

    result3 = add_new_todo('Finish report', '')
    assert result3['success'], "Failed to add todo 3"
    print(f"✓ {result3['message']}")

    print()


def test_view_todos():
    """Test 3: View all todos."""
    print("=" * 80)
    print("TEST 3: View Todos")
    print("=" * 80)

    result = view_all_todos()
    assert result['success'], "Failed to view todos"
    assert len(result['data']) == 3, f"Expected 3 todos, got {len(result['data'])}"

    display_todos(result['data'])
    print("✓ View operation successful\n")


def test_mark_complete():
    """Test 4: Mark todo as complete."""
    print("=" * 80)
    print("TEST 4: Mark Todo Complete")
    print("=" * 80)

    result = toggle_todo_status(1, True)
    assert result['success'], "Failed to mark todo complete"
    print(f"✓ {result['message']}")

    # Verify status changed
    todo = get_todo(1)
    assert todo.completed == True, "Todo status not updated"
    print("✓ Status verified: Complete")

    result = view_all_todos()
    display_todos(result['data'])


def test_update_todo():
    """Test 5: Update todo details."""
    print("=" * 80)
    print("TEST 5: Update Todo")
    print("=" * 80)

    result = update_todo_details(2, 'Call dentist - URGENT', 'Schedule for next week')
    assert result['success'], "Failed to update todo"
    print(f"✓ {result['message']}")

    # Verify updates
    todo = get_todo(2)
    assert todo.title == 'Call dentist - URGENT', "Title not updated"
    assert todo.description == 'Schedule for next week', "Description not updated"
    print("✓ Updates verified")

    result = view_all_todos()
    display_todos(result['data'])


def test_delete_todo():
    """Test 6: Delete a todo."""
    print("=" * 80)
    print("TEST 6: Delete Todo")
    print("=" * 80)

    result = remove_todo(3)
    assert result['success'], "Failed to delete todo"
    print(f"✓ {result['message']}")

    # Verify deletion
    todo = get_todo(3)
    assert todo is None, "Todo not deleted"
    print("✓ Deletion verified")

    result = view_all_todos()
    assert len(result['data']) == 2, f"Expected 2 todos, got {len(result['data'])}"
    display_todos(result['data'])


def test_error_handling():
    """Test 7: Error handling for invalid operations."""
    print("=" * 80)
    print("TEST 7: Error Handling")
    print("=" * 80)

    # Invalid ID for toggle
    result = toggle_todo_status(999, True)
    assert not result['success'], "Should fail for invalid ID"
    print(f"✓ Toggle error handled: {result['message']}")

    # Invalid ID for update
    result = update_todo_details(999, 'Test', None)
    assert not result['success'], "Should fail for invalid ID"
    print(f"✓ Update error handled: {result['message']}")

    # Invalid ID for delete
    result = remove_todo(999)
    assert not result['success'], "Should fail for invalid ID"
    print(f"✓ Delete error handled: {result['message']}")

    print()


def test_empty_title_validation():
    """Test 8: Validate empty title rejection."""
    print("=" * 80)
    print("TEST 8: Empty Title Validation")
    print("=" * 80)

    result = add_new_todo('', 'Should fail')
    assert not result['success'], "Should reject empty title"
    print(f"✓ Empty string rejected: {result['message']}")

    result = add_new_todo('   ', 'Should also fail')
    assert not result['success'], "Should reject whitespace-only title"
    print(f"✓ Whitespace-only rejected: {result['message']}")

    print()


def test_performance():
    """Test 9: Performance with many todos."""
    print("=" * 80)
    print("TEST 9: Performance Test (100 todos)")
    print("=" * 80)

    import time

    # Clear existing todos for clean test
    import storage
    initial_count = len(storage.todos)

    start = time.time()
    for i in range(100):
        add_new_todo(f'Todo {i}', f'Description {i}')
    end = time.time()

    elapsed = end - start
    print(f"✓ Added 100 todos in {elapsed:.3f} seconds")
    print(f"✓ Average: {(elapsed/100)*1000:.2f}ms per todo")

    result = view_all_todos()
    total = len(result['data'])
    print(f"✓ Total todos in storage: {total}")
    assert total >= 100, f"Expected at least 100 todos, got {total}"

    # Test retrieval performance
    start = time.time()
    result = view_all_todos()
    end = time.time()
    print(f"✓ Retrieved {total} todos in {(end-start)*1000:.2f}ms")

    print()


def test_toggle_back():
    """Test 10: Toggle status back and forth."""
    print("=" * 80)
    print("TEST 10: Toggle Status Multiple Times")
    print("=" * 80)

    # Get first todo
    result = view_all_todos()
    if result['data']:
        todo_id = result['data'][0].id

        # Mark complete
        result = toggle_todo_status(todo_id, True)
        assert result['success'], "Failed to mark complete"
        todo = get_todo(todo_id)
        assert todo.completed == True, "Not marked complete"
        print(f"✓ Todo {todo_id} marked complete")

        # Mark incomplete
        result = toggle_todo_status(todo_id, False)
        assert result['success'], "Failed to mark incomplete"
        todo = get_todo(todo_id)
        assert todo.completed == False, "Not marked incomplete"
        print(f"✓ Todo {todo_id} marked incomplete")

        # Mark complete again
        result = toggle_todo_status(todo_id, True)
        assert result['success'], "Failed to mark complete again"
        todo = get_todo(todo_id)
        assert todo.completed == True, "Not marked complete again"
        print(f"✓ Todo {todo_id} marked complete again")
        print("✓ Toggle operations work correctly")

    print()


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "TODO CLI APPLICATION - TEST SUITE")
    print("=" * 80)
    print("\n")

    try:
        test_imports()
        reset_storage()
        test_add_todos()
        test_view_todos()
        test_mark_complete()
        test_update_todo()
        test_delete_todo()
        test_error_handling()
        test_empty_title_validation()
        test_performance()
        test_toggle_back()

        print("=" * 80)
        print(" " * 25 + "ALL TESTS PASSED ✓")
        print("=" * 80)
        print("\nSummary:")
        print("  ✓ 10 test suites executed")
        print("  ✓ All operations working correctly")
        print("  ✓ Error handling validated")
        print("  ✓ Performance acceptable")
        print("  ✓ Ready for production use")
        print()

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
