#!/usr/bin/env python3

import re
from cv_extractor_cli import load_text

def debug_languages():
    """Debug languages extraction specifically."""
    text = load_text("cv_files/CV_ENG_DEV.pdf")
    lines = text.split('\n')
    
    print("=== DEBUGGING LANGUAGES EXTRACTION ===")
    
    # Find the languages section
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        if i >= 30 and i <= 45:  # Around languages section
            print(f"Line {i}: '{line}'")
            
            # Check if this is the languages section header
            if re.match(r'^(?:LANGUAGES|LANGUES)$', line, re.IGNORECASE):
                print(f"  -> LANGUAGES SECTION HEADER FOUND!")
                
                # Look at the next few lines
                print(f"  -> Next lines:")
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line:
                        print(f"    Line {j}: '{next_line}'")
                        # Check if it's a bullet point with language
                        if re.match(r'^[●○•\-\*]\s*', next_line):
                            print(f"      -> BULLET DETECTED")
                            content = re.sub(r'^[●○•\-\*]\s*', '', next_line)
                            print(f"      -> Content: '{content}'")
                            
                            # Remove Unicode characters
                            cleaned = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', content)
                            print(f"      -> Cleaned: '{cleaned}'")
                            
                            # Try to match language pattern
                            lang_match = re.match(r'^([A-Za-zÀ-ÿ]+)\s*[:\-–]\s*([A-Za-zÀ-ÿ\s]+)$', cleaned)
                            if lang_match:
                                language = lang_match.group(1).title()
                                level = lang_match.group(2).strip().title()
                                print(f"      -> MATCHED: Language='{language}', Level='{level}'")
                            else:
                                print(f"      -> NO MATCH")
                        elif re.match(r'^(?:CERTIFICATIONS|EDUCATION|FORMATION|EXPERIENCE|PROJECTS|SKILLS)$', next_line, re.IGNORECASE):
                            print(f"      -> END OF LANGUAGES SECTION")
                            break
            elif 'LANGUAGES' in line.upper():
                print(f"  -> CONTAINS 'LANGUAGES' but not exact match")
                print(f"  -> Line content: '{line}'")
                print(f"  -> Character codes: {[ord(c) for c in line]}")

if __name__ == "__main__":
    debug_languages()
