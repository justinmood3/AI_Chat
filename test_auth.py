#!/usr/bin/env python
"""Test authentication functions"""

import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    from database import (
        save_user_email, get_user_by_email, get_user_by_id, 
        check_password, create_thread, save_chat
    )
    print("✓ Database imports successful")
    
    # Test 1: Create a new user
    print("\n--- Test 1: Creating new user ---")
    user_id = save_user_email("Test User", "test@example.com", "password123")
    print(f"✓ Created user with ID: {user_id}")
    
    # Test 2: Retrieve user by email
    print("\n--- Test 2: Retrieving user by email ---")
    user_data = get_user_by_email("test@example.com")
    print(f"✓ User data: ID={user_data[0]}, Name={user_data[1]}, Email={user_data[2]}")
    
    # Test 3: Retrieve user by ID
    print("\n--- Test 3: Retrieving user by ID ---")
    user_data = get_user_by_id(user_id)
    print(f"✓ User data: ID={user_data[0]}, Name={user_data[1]}, Email={user_data[2]}")
    
    # Test 4: Check password
    print("\n--- Test 4: Checking password ---")
    is_valid = check_password(user_id, "password123")
    print(f"✓ Password check (correct): {is_valid}")
    
    is_invalid = check_password(user_id, "wrongpassword")
    print(f"✓ Password check (incorrect): {is_invalid}")
    
    # Test 5: Create thread and chat
    print("\n--- Test 5: Creating thread and chat ---")
    thread_id = create_thread(user_id, "Test Chat")
    print(f"✓ Created thread with ID: {thread_id}")
    
    save_chat(thread_id, "Hello", "Hi there!")
    print(f"✓ Saved chat message")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
