#!/usr/bin/env python3

import re
from cv_extractor_cli import load_text

def debug_education_experience():
    """Debug education and experience extraction issues."""
    text = load_text("cv_files/CV_Doha_Bouhali.pdf")
    lines = text.split('\n')
    
    print("=== DEBUGGING EDUCATION AND EXPERIENCE EXTRACTION ===")
    
    # Test section detection
    in_education = False
    in_experience = False
    education_lines = []
    experience_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Show lines around education and experience sections
        if i >= 50 and i <= 110:  # Around education/experience sections
            print(f"Line {i}: '{line}'")
            
            # Test different regex patterns for experience section
            if 'expérience' in line.lower() or 'experience' in line.lower():
                print(f"  -> CONTAINS 'expérience' or 'experience'")
                if re.match(r'^(?:Expérience Professionnelle|EXPERIENCE|EMPLOI|Professional Experience)$', line, re.IGNORECASE):
                    print(f"  -> MATCHES EXACT PATTERN")
                elif re.search(r'\b(?:Expérience Professionnelle|EXPERIENCE|EMPLOI|Professional Experience)\b', line, re.IGNORECASE):
                    print(f"  -> MATCHES FLEXIBLE PATTERN")
        
        # Check for education section
        if re.match(r'^(?:EDUCATION|FORMATION|ÉDUCATION)$', line, re.IGNORECASE):
            print(f"  -> ENTERING EDUCATION at line {i}: '{line}'")
            in_education = True
            in_experience = False
            continue
        
        # Check for experience section (more flexible)
        if re.search(r'\b(?:Expérience Professionnelle|EXPERIENCE|EMPLOI|Professional Experience)\b', line, re.IGNORECASE):
            print(f"  -> ENTERING EXPERIENCE at line {i}: '{line}'")
            in_experience = True
            in_education = False
            continue
        
        # Check for other section boundaries
        if re.match(r'^(?:PROJECTS|PROJETS|SKILLS|LANGUAGES|CERTIFICATIONS)$', line, re.IGNORECASE):
            print(f"  -> LEAVING SECTIONS at line {i}: '{line}'")
            in_education = False
            in_experience = False
            continue
        
        # Collect lines
        if in_education:
            education_lines.append(line)
            print(f"  -> EDUCATION LINE: '{line}'")
        elif in_experience:
            experience_lines.append(line)
            print(f"  -> EXPERIENCE LINE: '{line}'")
    
    print(f"\n=== EDUCATION LINES ({len(education_lines)}) ===")
    for line in education_lines:
        print(f"  '{line}'")
    
    print(f"\n=== EXPERIENCE LINES ({len(experience_lines)}) ===")
    for line in experience_lines:
        print(f"  '{line}'")
    
    print("\n=== TESTING DATE RANGE DETECTION ===")
    
    # Test date range detection
    date_pattern = r'\b(?:\w+\s+\d{4}|\d{4})\s*[-–]\s*(?:\w+\s+\d{4}|\d{4})\b'
    
    for line in education_lines + experience_lines:
        if re.search(date_pattern, line, re.IGNORECASE):
            print(f"DATE RANGE FOUND: '{line}'")
            matches = re.findall(date_pattern, line, re.IGNORECASE)
            for match in matches:
                print(f"  -> Match: '{match}'")

if __name__ == "__main__":
    debug_education_experience()
