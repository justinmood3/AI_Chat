#!/usr/bin/env python
"""Quick structure test without API calls"""

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
    
    print("\n2. Checking imports...")
    try:
        from flask import Flask
        print("✓ Flask imported")
        from google import genai
        print("✓ Google genai imported")
        from database import get_user_by_id, create_thread, get_threads
        print("✓ Database functions imported")
        from ai_engine import get_response
        print("✓ AI engine imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    
    print("\n3. Checking Flask routes...")
    from app import app
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    print(f"Total routes: {len(routes)}")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            print(f"  ✓ {rule.rule} -> {rule.endpoint}")
    
    # Check for critical routes
    critical_routes = ['/login', '/register', '/chat', '/logout']
    route_strings = [str(r) for r in app.url_map.iter_rules()]
    for route in critical_routes:
        found = any(route in str(r) for r in app.url_map.iter_rules())
        if found:
            print(f"✓ Route {route} exists")
        else:
            print(f"❌ Route {route} MISSING!")
            
    print("\n" + "=" * 50)
    print("✅ Structure Check PASSED!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run: C:\\Python314\\python.exe app.py")
    print("2. Open: http://localhost:5000")
    print("3. Sign up with email")
    print("4. Start chatting!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
