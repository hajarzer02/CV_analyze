#!/usr/bin/env python3
"""
Test script to verify the authentication system works correctly.
Run this after starting the backend server.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test User"

def test_authentication():
    """Test the complete authentication flow."""
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        "name": TEST_NAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}")
            print(f"   Name: {user_data['name']}")
            print(f"   Email: {user_data['email']}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8000.")
        return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Test 2: Login with the new user
    print("\n2. Testing user login...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "remember_me": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"   Token type: {token_data['token_type']}")
            print(f"   Access token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Access protected endpoint
    print("\n3. Testing protected endpoint access...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            user_info = response.json()
            print(f"   Current user: {user_info['name']} ({user_info['email']})")
        else:
            print(f"❌ Protected endpoint access failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return
    
    # Test 4: Access protected CV endpoint
    print("\n4. Testing protected CV endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/candidates", headers=headers)
        if response.status_code == 200:
            print("✅ Protected CV endpoint access successful")
            candidates = response.json()
            print(f"   Found {len(candidates)} candidates")
        else:
            print(f"❌ Protected CV endpoint access failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Protected CV endpoint error: {e}")
    
    # Test 5: Test without token (should fail)
    print("\n5. Testing access without token (should fail)...")
    try:
        response = requests.get(f"{BASE_URL}/candidates")
        if response.status_code == 401:
            print("✅ Correctly rejected request without token")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing without token: {e}")
    
    # Test 6: Logout
    print("\n6. Testing user logout...")
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        if response.status_code == 200:
            print("✅ User logout successful")
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Logout error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")
    print("\nTo test the frontend:")
    print("1. Start the frontend: cd frontend && npm start")
    print("2. Go to http://localhost:3000")
    print("3. Try to register/login with the test user")
    print(f"   Email: {TEST_EMAIL}")
    print(f"   Password: {TEST_PASSWORD}")

if __name__ == "__main__":
    test_authentication()
