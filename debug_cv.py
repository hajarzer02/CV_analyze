#!/usr/bin/env python3

import re
from cv_extractor_cli import load_text

def debug_cv_parsing(file_path):
    """Debug CV parsing to see what's happening."""
    text = load_text(file_path)
    print("=== DEBUGGING SKILLS EXTRACTION ===")
    
    # Test the skills extraction logic
    lines = text.split('\n')
    in_skills = False
    skills_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering skills section
        if re.search(r'\b(?:TECHNICAL SKILLS|COMPÉTENCES|SKILLS)\b', line, re.IGNORECASE):
            print(f"ENTERING SKILLS at line {i}: '{line}'")
            in_skills = True
            continue
        
        # Check if we're leaving skills section
        if in_skills and re.search(r'\b(?:LANGUAGES|LANGUES|EDUCATION|FORMATION|EXPERIENCE|PROJECTS)\b', line, re.IGNORECASE):
            print(f"LEAVING SKILLS at line {i}: '{line}'")
            in_skills = False
            continue
        
        if in_skills:
            print(f"SKILLS LINE {i}: '{line}'")
            skills_lines.append(line)
    
    print(f"\nTotal skills lines collected: {len(skills_lines)}")
    print("Skills lines:")
    for line in skills_lines:
        print(f"  '{line}'")
    
    print("\n=== DEBUGGING LANGUAGES EXTRACTION ===")
    
    # Test the languages extraction logic
    in_languages = False
    languages_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering languages section
        if re.search(r'\b(?:LANGUAGES|LANGUES)\b', line, re.IGNORECASE):
            print(f"ENTERING LANGUAGES at line {i}: '{line}'")
            in_languages = True
            continue
        
        # Check if we're leaving languages section
        if in_languages and re.search(r'\b(?:CERTIFICATIONS|EDUCATION|FORMATION|EXPERIENCE|PROJECTS)\b', line, re.IGNORECASE):
            print(f"LEAVING LANGUAGES at line {i}: '{line}'")
            in_languages = False
            continue
        
        if in_languages:
            print(f"LANGUAGES LINE {i}: '{line}'")
            languages_lines.append(line)
    
    print(f"\nTotal languages lines collected: {len(languages_lines)}")
    print("Languages lines:")
    for line in languages_lines:
        print(f"  '{line}'")

if __name__ == "__main__":
    debug_cv_parsing("cv_files/CV_ENG_DEV.pdf")
