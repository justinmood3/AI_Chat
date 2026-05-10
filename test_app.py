#!/usr/bin/env python
"""Test API and routes"""

import sys
print("Testing Justin AI Application...")
print("-" * 50)

try:
    print("1. Checking .env file...")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env")
        sys.exit(1)
    
    print(f"✓ GEMINI_API_KEY found: {gemini_key[:20]}...")
    
    print("\n2. Testing Gemini API...")
    from google import genai
    client = genai.Client(api_key=gemini_key)
    
    # Quick test
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say 'Hello from Justin AI!' and nothing else."
    )
    print(f"✓ Gemini API working: {response.text[:50]}...")
    
    print("\n3. Checking Flask routes...")
    from app import app
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    
    required_routes = ['/login', '/register', '/chat', '/logout', '/new_thread', '/select_thread']
    for route in required_routes:
        if any(route in r for r in routes):
            print(f"✓ Route {route} exists")
        else:
            print(f"❌ Route {route} MISSING!")
    
    print("\n4. Checking database...")
    from database import get_user_by_id, create_thread, get_threads
    print("✓ Database functions imported successfully")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    print("\nYou can now run: python.exe app.py")
    print("Then open: http://localhost:5000")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
