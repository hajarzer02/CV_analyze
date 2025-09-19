#!/usr/bin/env python3
"""
Test the actual API upload process to find where John Doe comes from.
"""

import os
import sys
import requests
import json
from docx import Document

def test_api_upload():
    """Test the actual API upload process."""
    print("🔍 Testing API Upload Process")
    print("=" * 50)
    
    # Create a test DOCX file
    test_content = """
Michael Brown
Backend Developer
Email: michael.brown@example.com
Phone: +1-555-456-7890

PROFESSIONAL SUMMARY
Experienced backend developer specializing in API development and database design.

SKILLS
- Python
- Django
- FastAPI
- PostgreSQL
- Redis
- Docker

EXPERIENCE
Senior Backend Developer at DataFlow (2020-2024)
- Designed and implemented REST APIs
- Optimized database performance
- Led technical architecture decisions

Backend Developer at CloudTech (2018-2020)
- Developed microservices architecture
- Implemented caching strategies

EDUCATION
Master of Computer Science
Stanford University (2016-2018)
"""
    
    # Create test DOCX file
    doc = Document()
    for line in test_content.strip().split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    test_docx_path = "test_michael_cv.docx"
    doc.save(test_docx_path)
    print(f"✅ Created test DOCX file: {test_docx_path}")
    
    try:
        # Test the API upload endpoint
        print("\n1. Testing API upload endpoint:")
        
        # First, we need to login to get a token
        print("   Logging in...")
        login_data = {
            "email": "admin@test.com",  # You'll need to adjust this
            "password": "admin123"      # You'll need to adjust this
        }
        
        try:
            # Try to login
            login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                print("   ✅ Login successful")
                
                # Now test the upload
                print("   Testing file upload...")
                headers = {"Authorization": f"Bearer {token}"}
                
                with open(test_docx_path, "rb") as f:
                    files = {"file": (test_docx_path, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                    upload_response = requests.post("http://localhost:8000/api/upload-cv", headers=headers, files=files)
                
                if upload_response.status_code == 200:
                    result = upload_response.json()
                    print("   ✅ Upload successful")
                    print(f"   Candidate ID: {result.get('candidate_id')}")
                    
                    # Check the extracted data
                    extracted_data = result.get('extracted_data', {})
                    contact_info = extracted_data.get('contact_info', {})
                    print(f"   Contact info: {contact_info}")
                    
                    # Check if John Doe appears
                    result_str = json.dumps(extracted_data, indent=2)
                    if "John Doe" in result_str:
                        print("   ⚠️  WARNING: 'John Doe' found in API result!")
                        print("   This is the source of the issue!")
                    else:
                        print("   ✅ No 'John Doe' found in API result")
                        
                else:
                    print(f"   ❌ Upload failed: {upload_response.status_code}")
                    print(f"   Response: {upload_response.text}")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                print("   Note: You may need to create an admin user first")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to API server")
            print("   Make sure the backend server is running: python main.py")
        except Exception as e:
            print(f"   ❌ Error during API test: {e}")
        
        # Test direct processing without API
        print("\n2. Testing direct processing (bypassing API):")
        try:
            from cv_extractor_cli import CVExtractor
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-service'))
            from llama_service import LlamaService
            
            cv_extractor = CVExtractor()
            llama_service = LlamaService()
            
            # Extract raw text
            raw_text = cv_extractor.extract_raw_text(test_docx_path)
            print(f"   Raw text length: {len(raw_text)} characters")
            print(f"   First 200 characters: {raw_text[:200]}")
            
            # Process with LLaMA
            extracted_data = llama_service.structure_cv_text(raw_text)
            contact_info = extracted_data.get('contact_info', {})
            print(f"   Processed contact info: {contact_info}")
            
            # Check for John Doe
            result_str = json.dumps(extracted_data, indent=2)
            if "John Doe" in result_str:
                print("   ⚠️  WARNING: 'John Doe' found in direct processing!")
            else:
                print("   ✅ No 'John Doe' found in direct processing")
                
        except Exception as e:
            print(f"   ❌ Error in direct processing: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(test_docx_path):
            os.remove(test_docx_path)
            print(f"\n🧹 Cleaned up test file: {test_docx_path}")

if __name__ == "__main__":
    test_api_upload()
