#!/usr/bin/env python3

from cv_extractor_cli import load_text, extract_languages, extract_skills

def simple_test():
    """Simple test of the extraction functions."""
    text = load_text("cv_files/CV_ENG_DEV.pdf")
    
    print("=== TESTING EXTRACTION FUNCTIONS ===")
    
    # Test skills extraction
    skills = extract_skills(text)
    print(f"Skills: {skills}")
    print(f"Number of skills: {len(skills)}")
    
    # Test languages extraction
    languages = extract_languages(text)
    print(f"Languages: {languages}")
    print(f"Number of languages: {len(languages)}")
    
    # Test the main extractor
    from cv_extractor_cli import CVExtractor
    extractor = CVExtractor()
    data = extractor.extract_cv_data("cv_files/CV_ENG_DEV.pdf")
    
    print(f"\n=== MAIN EXTRACTOR RESULTS ===")
    print(f"Keys in data: {list(data.keys())}")
    if 'languages' in data:
        print(f"Languages from main extractor: {data['languages']}")
    else:
        print("Languages key not found in main extractor output")

if __name__ == "__main__":
    simple_test()
