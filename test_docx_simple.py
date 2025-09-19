#!/usr/bin/env python3
"""
Simple test to debug DOCX extraction issue.
"""

import os
import sys
from docx import Document

def test_docx_basic():
    """Test basic DOCX extraction."""
    print("🔍 Testing Basic DOCX Extraction")
    print("=" * 50)
    
    # Create a simple test DOCX file
    test_content = """
John Smith
Software Engineer
Email: john.smith@example.com
Phone: +1-555-123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in full-stack development.

SKILLS
- Python
- JavaScript
- React
- Node.js
- PostgreSQL

EXPERIENCE
Senior Software Engineer at TechCorp (2020-2024)
- Led development of microservices architecture
- Mentored junior developers

Software Engineer at StartupXYZ (2018-2020)
- Developed REST APIs
- Implemented CI/CD pipelines

EDUCATION
Bachelor of Computer Science
University of Technology (2014-2018)
"""
    
    # Create test DOCX file
    doc = Document()
    for line in test_content.strip().split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    test_docx_path = "test_cv.docx"
    doc.save(test_docx_path)
    print(f"✅ Created test DOCX file: {test_docx_path}")
    
    # Test extraction
    try:
        from backend.cv_extractor_cli import CVExtractor
        extractor = CVExtractor()
        
        print("\n1. Testing raw text extraction:")
        raw_text = extractor.extract_raw_text(test_docx_path)
        print(f"Raw text length: {len(raw_text)} characters")
        print(f"First 200 characters:")
        print(f"'{raw_text[:200]}'")
        
        print("\n2. Testing structured extraction:")
        structured_data = extractor.extract_cv_data(test_docx_path)
        print(f"Contact info: {structured_data.get('contact_info', {})}")
        print(f"Skills: {structured_data.get('skills', [])}")
        print(f"Experience: {structured_data.get('experience', [])}")
        
        print("\n3. Testing LLaMA service fallback:")
        # Test the CLI parser fallback directly
        sys.path.append('ai-service')
        
        # Import the fallback method directly
        from llama_service import LlamaService
        
        # Create a mock LlamaService without initializing torch
        class MockLlamaService:
            def _fallback_to_cli_parser(self, raw_text):
                from cv_extractor_cli import (
                    extract_contact_info, extract_summary, extract_skills, 
                    extract_languages, extract_education, extract_experience, 
                    extract_projects
                )
                
                contact_info = extract_contact_info(raw_text)
                candidate_name = self._extract_candidate_name(raw_text)
                if candidate_name:
                    contact_info["name"] = candidate_name
                
                return {
                    "contact_info": contact_info,
                    "professional_summary": extract_summary(raw_text),
                    "skills": extract_skills(raw_text),
                    "languages": extract_languages(raw_text),
                    "education": extract_education(raw_text),
                    "experience": extract_experience(raw_text),
                    "projects": extract_projects(raw_text),
                }
            
            def _extract_candidate_name(self, raw_text):
                import re
                lines = raw_text.split('\n')
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
                        return name_match.group(1)
                return ""
        
        mock_service = MockLlamaService()
        llama_result = mock_service._fallback_to_cli_parser(raw_text)
        print(f"LLaMA fallback contact info: {llama_result.get('contact_info', {})}")
        print(f"LLaMA fallback skills: {llama_result.get('skills', [])}")
        
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
    test_docx_basic()
