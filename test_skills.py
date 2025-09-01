#!/usr/bin/env python3

import re
from cv_extractor_cli import load_text, extract_skills

def test_skills_extraction():
    """Test skills extraction specifically."""
    text = load_text("cv_files/CV_ENG_DEV.pdf")
    lines = text.split('\n')
    
    print("=== TESTING SKILLS EXTRACTION ===")
    
    # Test the improved extract_skills function
    skills = extract_skills(text)
    print(f"Extracted skills: {skills}")
    
    print("\n=== DEBUGGING SECTION DETECTION ===")
    
    in_skills = False
    skills_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering skills section (more flexible matching)
        if re.search(r'\b(?:TECHNICAL\s+SKILLS|COMPÉTENCES|SKILLS)\b', line, re.IGNORECASE):
            print(f"ENTERING SKILLS at line {i}: '{line}'")
            in_skills = True
            continue
        
        # Check if we're leaving skills section (more flexible matching)
        if in_skills and re.search(r'\b(?:LANGUAGES|LANGUES|EDUCATION|FORMATION|EXPERIENCE|PROJECTS|CERTIFICATIONS)\b', line, re.IGNORECASE):
            print(f"LEAVING SKILLS at line {i}: '{line}'")
            in_skills = False
            continue
        
        if in_skills:
            print(f"SKILLS LINE {i}: '{line}'")
            skills_lines.append(line)
    
    print(f"\nTotal skills lines: {len(skills_lines)}")
    for line in skills_lines:
        print(f"  '{line}'")
    
    print("\n=== DEBUGGING UNICODE CHARACTERS ===")
    
    # Test skills parsing with Unicode handling
    for line in skills_lines:
        if not line:
            continue
        
        print(f"\nProcessing line: '{line}'")
        
        # Remove zero-width spaces and other invisible Unicode characters
        cleaned_line = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', line)
        print(f"  -> Cleaned line: '{cleaned_line}'")
        
        # Check for bullet points
        if re.match(r'^[●○•\-\*]\s*', cleaned_line):
            print(f"  -> BULLET DETECTED")
            content = re.sub(r'^[●○•\-\*]\s*', '', cleaned_line)
            print(f"  -> Content: '{content}'")
            
            if content:
                # Handle "Category: skill1, skill2, skill3" format
                if ':' in content:
                    parts = content.split(':', 1)
                    if len(parts) == 2:
                        category = parts[0].strip()
                        skill_list = parts[1].strip()
                        print(f"  -> Category: '{category}'")
                        print(f"  -> Skill list: '{skill_list}'")
                        # Split by common separators
                        skill_items = re.split(r'[,;/|]', skill_list)
                        for skill in skill_items:
                            skill = skill.strip()
                            if skill and len(skill) >= 2:
                                print(f"    -> Added skill: '{skill}'")
                else:
                    # Single skill or comma-separated list
                    skill_items = re.split(r'[,;/|]', content)
                    for skill in skill_items:
                        skill = skill.strip()
                        if skill and len(skill) >= 2:
                            print(f"    -> Added skill: '{skill}'")
        else:
            print(f"  -> NO BULLET")
            # Check if it's a continuation line
            if cleaned_line and not re.match(r'^[A-Z\s]+$', cleaned_line):
                print(f"  -> CONTINUATION LINE")
                skill_items = re.split(r'[,;/|]', cleaned_line)
                for skill in skill_items:
                    skill = skill.strip()
                    if skill and len(skill) >= 2:
                        print(f"    -> Added skill: '{skill}'")

if __name__ == "__main__":
    test_skills_extraction()
