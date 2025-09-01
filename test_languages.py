#!/usr/bin/env python3

import re
from cv_extractor_cli import load_text, extract_languages

def test_languages_extraction():
    """Test languages extraction specifically."""
    text = load_text("cv_files/CV_ENG_DEV.pdf")
    
    print("=== TESTING LANGUAGES EXTRACTION ===")
    
    # Test the improved extract_languages function
    languages = extract_languages(text)
    print(f"Extracted languages: {languages}")
    
    print("\n=== DEBUGGING LANGUAGES SECTION DETECTION ===")
    
    lines = text.split('\n')
    in_languages = False
    languages_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Show character codes for debugging around languages section
        if i >= 30 and i <= 45:  # Around languages section
            print(f"Line {i}: '{line}' (codes: {[ord(c) for c in line[:10]]})")
        
        # Check if we're entering languages section (exact match for section headers)
        if re.match(r'^(?:LANGUAGES|LANGUES)$', line, re.IGNORECASE):
            print(f"ENTERING LANGUAGES at line {i}: '{line}'")
            in_languages = True
            continue
        
        # Check if we're leaving languages section (exact match for section headers)
        if in_languages and re.match(r'^(?:CERTIFICATIONS|EDUCATION|FORMATION|EXPERIENCE|PROJECTS|SKILLS)$', line, re.IGNORECASE):
            print(f"LEAVING LANGUAGES at line {i}: '{line}'")
            in_languages = False
            continue
        
        if in_languages:
            print(f"LANGUAGES LINE {i}: '{line}'")
            languages_lines.append(line)
    
    print(f"\nTotal languages lines collected: {len(languages_lines)}")
    print("Languages lines:")
    for line in languages_lines:
        print(f"  '{line}' (codes: {[ord(c) for c in line[:10]]})")
    
    print("\n=== DEBUGGING LANGUAGES PARSING ===")
    
    # Test languages parsing with Unicode handling
    for line in languages_lines:
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
                # Look for "Language: Level" pattern
                lang_match = re.match(r'^([A-Za-zÀ-ÿ]+)\s*[:\-–]\s*([A-Za-zÀ-ÿ\s]+)$', content)
                if lang_match:
                    language = lang_match.group(1).title()
                    level = lang_match.group(2).strip().title()
                    print(f"  -> Language: '{language}'")
                    print(f"  -> Level: '{level}'")
                else:
                    print(f"  -> NO LANGUAGE MATCH")
        else:
            print(f"  -> NO BULLET")

if __name__ == "__main__":
    test_languages_extraction()
