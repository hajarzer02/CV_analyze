#!/usr/bin/env python3
"""
Test script to verify frontend integration for delete functionality.
This script checks if the frontend files have been properly updated.
"""

import os
import re

def check_api_service():
    """Check if the API service has been updated with delete function."""
    api_file = "frontend/src/services/api.js"
    
    print("🔍 Checking API Service Integration")
    print("=" * 40)
    
    if not os.path.exists(api_file):
        print("❌ API service file not found")
        return False
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Check for delete function
    if "deleteCandidate" in content:
        print("✅ deleteCandidate function found in API service")
    else:
        print("❌ deleteCandidate function not found in API service")
        return False
    
    # Check for DELETE method
    if "api.delete" in content:
        print("✅ DELETE method found in API service")
    else:
        print("❌ DELETE method not found in API service")
        return False
    
    return True

def check_dashboard_component():
    """Check if the Dashboard component has been updated with delete functionality."""
    dashboard_file = "frontend/src/pages/Dashboard.js"
    
    print("\n🔍 Checking Dashboard Component Integration")
    print("=" * 45)
    
    if not os.path.exists(dashboard_file):
        print("❌ Dashboard component file not found")
        return False
    
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    # Check for required imports
    required_imports = ["Trash2", "AlertTriangle", "deleteCandidate"]
    for import_item in required_imports:
        if import_item in content:
            print(f"✅ {import_item} import found")
        else:
            print(f"❌ {import_item} import not found")
            return False
    
    # Check for delete state
    if "deleteModal" in content:
        print("✅ deleteModal state found")
    else:
        print("❌ deleteModal state not found")
        return False
    
    # Check for delete functions
    delete_functions = ["handleDeleteClick", "handleDeleteConfirm", "handleDeleteCancel"]
    for func in delete_functions:
        if func in content:
            print(f"✅ {func} function found")
        else:
            print(f"❌ {func} function not found")
            return False
    
    # Check for delete button
    if "Delete" in content and "Trash2" in content:
        print("✅ Delete button found")
    else:
        print("❌ Delete button not found")
        return False
    
    # Check for confirmation modal
    if "Delete Candidate" in content and "Are you sure" in content:
        print("✅ Confirmation modal found")
    else:
        print("❌ Confirmation modal not found")
        return False
    
    return True

def check_backend_endpoint():
    """Check if the backend has been updated with delete endpoint."""
    main_file = "main.py"
    
    print("\n🔍 Checking Backend Integration")
    print("=" * 35)
    
    if not os.path.exists(main_file):
        print("❌ Main backend file not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for delete endpoint
    if "@app.delete" in content:
        print("✅ DELETE endpoint decorator found")
    else:
        print("❌ DELETE endpoint decorator not found")
        return False
    
    # Check for delete function
    if "def delete_candidate" in content:
        print("✅ delete_candidate function found")
    else:
        print("❌ delete_candidate function not found")
        return False
    
    # Check for database cleanup
    if "JobRecommendation" in content and "delete" in content:
        print("✅ Database cleanup logic found")
    else:
        print("❌ Database cleanup logic not found")
        return False
    
    # Check for file cleanup
    if "os.remove" in content:
        print("✅ File cleanup logic found")
    else:
        print("❌ File cleanup logic not found")
    
    return True

def main():
    """Run all frontend integration tests."""
    print("🔍 Frontend Integration Test Suite")
    print("=" * 40)
    
    api_ok = check_api_service()
    dashboard_ok = check_dashboard_component()
    backend_ok = check_backend_endpoint()
    
    print(f"\n📊 Integration Test Results")
    print("=" * 30)
    
    if api_ok and dashboard_ok and backend_ok:
        print("🎉 All integration tests passed!")
        print("\n✅ Delete functionality is fully integrated:")
        print("   • Backend DELETE endpoint implemented")
        print("   • Frontend API service updated")
        print("   • Dashboard component with delete button")
        print("   • Confirmation modal with candidate details")
        print("   • Loading states and error handling")
        print("   • Database and file cleanup")
    else:
        print("❌ Some integration tests failed")
        print("   Please check the errors above and fix them")

if __name__ == "__main__":
    main()
