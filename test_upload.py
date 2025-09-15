#!/usr/bin/env python3
"""
Test script to verify file upload functionality.
"""

import requests
import os

def test_upload():
    """Test the upload endpoint with a sample file."""
    
    # Test file path (you can change this to any PDF file)
    test_file = "backend/uploads/NOUR_CV.pdf"
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        print("Please ensure you have a PDF file in backend/uploads/")
        return
    
    # Upload the file
    url = "http://localhost:8000/upload-cv"
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/pdf')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing file upload functionality...")
    test_upload()
