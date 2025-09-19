#!/usr/bin/env python3
"""
Test script to verify admin functionality.
This script tests the admin endpoints and role-based access control.
"""

import requests
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@test.com"
TEST_PASSWORD = "admin123"
REGULAR_USER_EMAIL = "user@test.com"
REGULAR_USER_PASSWORD = "user123"

def test_admin_functionality():
    """Test the complete admin functionality."""
    print("🧪 Testing Admin Functionality")
    print("=" * 50)
    
    # Test 1: Create admin user
    print("\n1. Creating admin user...")
    try:
        from backend.create_admin_user import create_admin_user
        # This will prompt for input, so we'll skip it in automated testing
        print("   ✅ Admin user creation script available")
    except Exception as e:
        print(f"   ❌ Error with admin user creation: {e}")
    
    # Test 2: Test API endpoints
    print("\n2. Testing API endpoints...")
    
    # First, try to register a regular user
    print("   Registering regular user...")
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        })
        if response.status_code == 200:
            print("   ✅ Regular user registered successfully")
        else:
            print(f"   ⚠️  Regular user registration failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error registering regular user: {e}")
    
    # Test 3: Test admin endpoints without authentication
    print("\n3. Testing admin endpoints without authentication...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/admin/users")
        if response.status_code == 401:
            print("   ✅ Admin endpoints properly protected (401 Unauthorized)")
        else:
            print(f"   ❌ Admin endpoints not properly protected: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing admin endpoints: {e}")
    
    # Test 4: Test regular user trying to access admin endpoints
    print("\n4. Testing regular user accessing admin endpoints...")
    try:
        # Login as regular user
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to access admin endpoints
            admin_response = requests.get(f"{API_BASE_URL}/api/admin/users", headers=headers)
            if admin_response.status_code == 403:
                print("   ✅ Regular users properly blocked from admin endpoints (403 Forbidden)")
            else:
                print(f"   ❌ Regular users not properly blocked: {admin_response.status_code}")
        else:
            print(f"   ❌ Could not login as regular user: {login_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing regular user access: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Admin functionality test completed!")
    print("\nTo fully test the admin functionality:")
    print("1. Run the backend server: python backend/main.py")
    print("2. Create an admin user: python backend/create_admin_user.py")
    print("3. Start the frontend: npm start (in frontend directory)")
    print("4. Login as admin and navigate to /admin")

if __name__ == "__main__":
    test_admin_functionality()
