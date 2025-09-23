#!/usr/bin/env python3
"""
Test that simulates the actual upload process to find where John Doe comes from.
"""

import os
import sys
import json
from docx import Document

def test_upload_simulation():
    """Simulate the actual upload process."""
    print("🔍 Testing Upload Process Simulation")
    print("=" * 50)
    
    # Create a test DOCX file
    test_content = """
Alice Johnson
Data Scientist
Email: alice.johnson@example.com
Phone: +1-555-987-6543

PROFESSIONAL SUMMARY
Experienced data scientist with expertise in machine learning and analytics.

SKILLS
- Python
- R
- Machine Learning
- TensorFlow
- SQL

EXPERIENCE
Senior Data Scientist at DataCorp (2020-2024)
- Developed ML models for predictive analytics
- Led data science team

Data Scientist at AnalyticsInc (2018-2020)
- Built recommendation systems
- Analyzed customer behavior

EDUCATION
PhD in Data Science
MIT (2014-2018)
"""
    
    # Create test DOCX file
    doc = Document()
    for line in test_content.strip().split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    test_docx_path = "test_alice_cv.docx"
    doc.save(test_docx_path)
    print(f"✅ Created test DOCX file: {test_docx_path}")
    
    try:
        # Step 1: Test raw text extraction (like in main.py)
        print("\n1. Raw text extraction (main.py style):")
        from backend.cv_extractor_cli import CVExtractor
        cv_extractor = CVExtractor()
        
        raw_text = cv_extractor.extract_raw_text(test_docx_path)
        print(f"Raw text length: {len(raw_text)} characters")
        print(f"First 200 characters:")
        print(f"'{raw_text[:200]}'")
        
        # Step 2: Test LLaMA service (this might fail due to torch)
        print("\n2. LLaMA service test:")
        try:
            sys.path.append('ai-service')
            from llama_service import LlamaService
            
            llama_service = LlamaService()
            print(f"Provider: {llama_service.provider}")
            
            extracted_data = llama_service.structure_cv_text(raw_text)
            print(f"LLaMA result contact info: {extracted_data.get('contact_info', {})}")
            print(f"LLaMA result skills: {extracted_data.get('skills', [])}")
            
        except Exception as e:
            print(f"LLaMA service failed: {e}")
            print("This is expected if torch is not installed")
            
            # Test CLI parser fallback directly
            print("\n3. CLI parser fallback test:")
            from backend.cv_extractor_cli import (
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
        
        # Step 3: Test the name extraction logic from main.py
        print("\n4. Name extraction logic (main.py style):")
        contact_info = cli_result.get('contact_info', {}) if 'cli_result' in locals() else {}
        name = None
        if contact_info.get("emails"):
            email = contact_info["emails"][0]
            name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
            print(f"Name extracted from email: {name}")
        else:
            print("No email found for name extraction")
        
        print(f"Final contact info: {contact_info}")
        
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
    test_upload_simulation()


