#!/usr/bin/env python3
"""
Test DOCX extraction in virtual environment to debug the John Doe issue.
"""

import os
import sys
import json
from docx import Document

def test_docx_in_venv():
    """Test DOCX extraction in virtual environment."""
    print("🔍 Testing DOCX Extraction in Virtual Environment")
    print("=" * 60)
    
    # Create a test DOCX file with real content
    test_content = """
Sarah Wilson
Frontend Developer
Email: sarah.wilson@example.com
Phone: +1-555-123-4567

PROFESSIONAL SUMMARY
Creative frontend developer with 4 years of experience building responsive web applications.

SKILLS
- React
- Vue.js
- TypeScript
- CSS3
- HTML5
- Node.js

EXPERIENCE
Senior Frontend Developer at WebCorp (2021-2024)
- Led development of company's main web application
- Implemented responsive design patterns
- Mentored junior developers

Frontend Developer at DigitalAgency (2019-2021)
- Built client websites using React and Vue.js
- Collaborated with design team on UI/UX

EDUCATION
Bachelor of Computer Science
University of California (2015-2019)
"""
    
    # Create test DOCX file
    doc = Document()
    for line in test_content.strip().split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    test_docx_path = "test_sarah_cv.docx"
    doc.save(test_docx_path)
    print(f"✅ Created test DOCX file: {test_docx_path}")
    
    try:
        # Test 1: Raw text extraction
        print("\n1. Raw text extraction:")
        from cv_extractor_cli import CVExtractor
        cv_extractor = CVExtractor()
        
        raw_text = cv_extractor.extract_raw_text(test_docx_path)
        print(f"Raw text length: {len(raw_text)} characters")
        print(f"First 300 characters:")
        print(f"'{raw_text[:300]}'")
        
        # Test 2: LLaMA service
        print("\n2. LLaMA service test:")
        try:
            # Add ai-service to path
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-service'))
            from llama_service import LlamaService
            
            llama_service = LlamaService()
            print(f"Provider: {llama_service.provider}")
            
            extracted_data = llama_service.structure_cv_text(raw_text)
            print(f"LLaMA result contact info: {extracted_data.get('contact_info', {})}")
            print(f"LLaMA result skills: {extracted_data.get('skills', [])}")
            
            # Check if John Doe appears anywhere
            result_str = json.dumps(extracted_data, indent=2)
            if "John Doe" in result_str:
                print("⚠️  WARNING: 'John Doe' found in LLaMA result!")
                print("This is the source of the issue!")
            else:
                print("✅ No 'John Doe' found in LLaMA result")
            
        except Exception as e:
            print(f"LLaMA service error: {e}")
            print("This might be the source of the issue if it's falling back to test data")
            
            # Test CLI parser fallback
            print("\n3. CLI parser fallback test:")
            from cv_extractor_cli import (
                extract_contact_info, extract_summary, extract_skills, 
                extract_languages, extract_education, extract_experience, 
                extract_projects
            )
            
            contact_info = extract_contact_info(raw_text)
            
            # Extract candidate name
            import re
            lines = raw_text.split('\n')
            candidate_name = ""
            for line in lines[:10]:
                line = line.strip()
                if not line:
                    continue
                if any(keyword in line.lower() for keyword in [
                    'email', 'phone', 'address', 'linkedin', 'summary', 'profile',
                    'experience', 'education', 'skills', 'languages', 'projects'
                ]):
                    continue
                name_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})$', line)
                if name_match:
                    candidate_name = name_match.group(1)
                    break
            
            if candidate_name:
                contact_info["name"] = candidate_name
            
            cli_result = {
                "contact_info": contact_info,
                "professional_summary": extract_summary(raw_text),
                "skills": extract_skills(raw_text),
                "languages": extract_languages(raw_text),
                "education": extract_education(raw_text),
                "experience": extract_experience(raw_text),
                "projects": extract_projects(raw_text),
            }
            
            print(f"CLI result contact info: {cli_result.get('contact_info', {})}")
            print(f"CLI result skills: {cli_result.get('skills', [])}")
            
            # Check if John Doe appears in CLI result
            cli_str = json.dumps(cli_result, indent=2)
            if "John Doe" in cli_str:
                print("⚠️  WARNING: 'John Doe' found in CLI result!")
            else:
                print("✅ No 'John Doe' found in CLI result")
        
        # Test 3: Simulate the main.py upload process
        print("\n4. Simulating main.py upload process:")
        try:
            # This is the exact logic from main.py
            contact_info = extracted_data.get("contact_info", {}) if 'extracted_data' in locals() else cli_result.get('contact_info', {})
            name = None
            if contact_info.get("emails"):
                email = contact_info["emails"][0]
                name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
                print(f"Name extracted from email: {name}")
            
            print(f"Final contact info: {contact_info}")
            
            if "John Doe" in str(contact_info):
                print("⚠️  WARNING: 'John Doe' found in final contact info!")
            else:
                print("✅ No 'John Doe' found in final contact info")
                
        except Exception as e:
            print(f"Error in upload simulation: {e}")
        
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
    test_docx_in_venv()


