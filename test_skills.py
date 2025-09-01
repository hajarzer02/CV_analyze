#!/usr/bin/env python3

import re
from cv_extractor_cli import load_text

def test_skills_extraction():
    """Test skills extraction specifically."""
    text = load_text("cv_files/CV_ENG_DEV.pdf")
    lines = text.split('\n')
    
    print("=== TESTING SKILLS EXTRACTION ===")
    
    in_skills = False
    skills_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering skills section
        if re.match(r'^(?:TECHNICAL SKILLS|COMPÉTENCES|SKILLS)$', line, re.IGNORECASE):
            print(f"ENTERING SKILLS at line {i}: '{line}'")
            in_skills = True
            continue
        
        # Check if we're leaving skills section
        if in_skills and re.match(r'^(?:LANGUAGES|LANGUES|EDUCATION|FORMATION|EXPERIENCE|PROJECTS)$', line, re.IGNORECASE):
            print(f"LEAVING SKILLS at line {i}: '{line}'")
            in_skills = False
            continue
        
        if in_skills:
            print(f"SKILLS LINE {i}: '{line}'")
            skills_lines.append(line)
    
    print(f"\nTotal skills lines: {len(skills_lines)}")
    for line in skills_lines:
        print(f"  '{line}'")
    
    # Test skills parsing
    skills = []
    for line in skills_lines:
        if not line:
            continue
        
        print(f"\nProcessing line: '{line}'")
        
        # Check for bullet points
        if re.match(r'^[●○•\-\*]\s*', line):
            print(f"  -> BULLET DETECTED")
            content = re.sub(r'^[●○•\-\*]\s*', '', line)
            print(f"  -> Raw content: '{content}'")
            
            # Remove zero-width spaces and other invisible characters
            content = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', content)
            print(f"  -> Cleaned content: '{content}'")
            
            if content:
                # Handle "Category: skill1, skill2, skill3" format
                if ':' in content:
                    parts = content.split(':', 1)
                    if len(parts) == 2:
                        skill_list = parts[1].strip()
                        print(f"  -> Skill list: '{skill_list}'")
                        # Split by common separators
                        skill_items = re.split(r'[,;/|]', skill_list)
                        for skill in skill_items:
                            skill = skill.strip()
                            if skill and len(skill) >= 2:
                                skills.append(skill)
                                print(f"    -> Added skill: '{skill}'")
                else:
                    # Single skill or comma-separated list
                    skill_items = re.split(r'[,;/|]', content)
                    for skill in skill_items:
                        skill = skill.strip()
                        if skill and len(skill) >= 2:
                            skills.append(skill)
                            print(f"    -> Added skill: '{skill}'")
        else:
            print(f"  -> NO BULLET")
    
    print(f"\nFinal skills: {skills}")

if __name__ == "__main__":
    test_skills_extraction()
