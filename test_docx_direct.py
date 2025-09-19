#!/usr/bin/env python3
"""
Direct test of DOCX extraction without LLaMA service.
"""

import os
import sys
from docx import Document

def test_docx_direct():
    """Test DOCX extraction directly."""
    print("🔍 Testing Direct DOCX Extraction")
    print("=" * 50)
    
    # Create a test DOCX file with different content
    test_content = """
Marie Dubois
Développeuse Full Stack
Email: marie.dubois@example.fr
Téléphone: +33 1 23 45 67 89

PROFIL PROFESSIONNEL
Développeuse expérimentée avec 6 ans d'expérience en développement web.

COMPÉTENCES
- Python
- Django
- React
- PostgreSQL
- Docker

EXPÉRIENCE
Développeuse Senior chez TechCorp (2021-2024)
- Développement d'applications web complexes
- Encadrement d'équipe junior

Développeuse chez StartupXYZ (2019-2021)
- Création d'APIs REST
- Mise en place de pipelines CI/CD

FORMATION
Master en Informatique
Université de Paris (2017-2019)
"""
    
    # Create test DOCX file
    doc = Document()
    for line in test_content.strip().split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    
    test_docx_path = "test_cv_marie.docx"
    doc.save(test_docx_path)
    print(f"✅ Created test DOCX file: {test_docx_path}")
    
    try:
        # Test raw text extraction
        print("\n1. Raw text extraction:")
        from backend.cv_extractor_cli import load_text
        raw_text = load_text(test_docx_path)
        print(f"Raw text length: {len(raw_text)} characters")
        print(f"First 300 characters:")
        print(f"'{raw_text[:300]}'")
        
        # Test structured extraction
        print("\n2. Structured extraction:")
        from backend.cv_extractor_cli import (
            extract_contact_info, extract_summary, extract_skills, 
            extract_languages, extract_education, extract_experience, 
            extract_projects
        )
        
        contact_info = extract_contact_info(raw_text)
        print(f"Contact info: {contact_info}")
        
        skills = extract_skills(raw_text)
        print(f"Skills: {skills}")
        
        experience = extract_experience(raw_text)
        print(f"Experience: {experience}")
        
        # Test name extraction
        print("\n3. Name extraction:")
        import re
        lines = raw_text.split('\n')
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if not line:
                continue
            print(f"Line {i+1}: '{line}'")
            
            # Check if it looks like a name
            if not any(keyword in line.lower() for keyword in [
                'email', 'phone', 'téléphone', 'address', 'adresse', 'linkedin', 'summary', 'profil',
                'experience', 'expérience', 'education', 'formation', 'skills', 'compétences', 'languages', 'langues', 'projects', 'projets'
            ]):
                name_match = re.match(r'^([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+){1,2})$', line)
                if name_match:
                    print(f"  -> Potential name found: '{name_match.group(1)}'")
                else:
                    print(f"  -> Not a name pattern")
            else:
                print(f"  -> Skipped (contains keyword)")
        
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
    test_docx_direct()
