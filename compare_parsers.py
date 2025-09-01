#!/usr/bin/env python3
"""
Compare old vs dynamic CV parser outputs.
"""

import json
import os
import re
from cv_extractor_cli import CVExtractor

def load_old_output():
    """Load the old parser output for comparison."""
    try:
        with open("outputs/CV_ENG_DEV.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_new_output():
    """Generate new dynamic parser output for comparison."""
    try:
        extractor = CVExtractor()
        return extractor.extract_cv_data("cv_files/CV_ENG_DEV.pdf")
    except Exception as e:
        print(f"Error generating new output: {e}")
        return None

def compare_outputs():
    """Compare old vs new dynamic parser outputs."""
    print("COMPARING OLD vs DYNAMIC CV PARSER")
    print("=" * 70)
    
    old_data = load_old_output()
    new_data = load_new_output()
    
    if not old_data or not new_data:
        print("Could not load data for comparison")
        return
    
    # Compare name detection
    print("\n1. NAME DETECTION:")
    print("-" * 40)
    old_name = old_data.get('name', 'Unknown')
    new_name = new_data.get('name', 'Unknown')
    print(f"OLD: {old_name}")
    print(f"NEW: {new_name}")
    print(f"✓ Name extraction improved: {old_name != new_name}")
    
    # Compare professional summary
    print("\n2. PROFESSIONAL SUMMARY COMPARISON:")
    print("-" * 40)
    
    old_summary = old_data.get('professional_summary', [])
    new_summary = new_data.get('professional_summary', [])
    
    print(f"OLD: {len(old_summary)} entries")
    for i, entry in enumerate(old_summary[:3], 1):
        print(f"  {i}. {entry[:80]}{'...' if len(entry) > 80 else ''}")
    
    print(f"\nNEW: {len(new_summary)} entries")
    for i, entry in enumerate(new_summary[:3], 1):
        print(f"  {i}. {entry[:80]}{'...' if len(entry) > 80 else ''}")
    
    # Check for improvements
    print("\n3. IMPROVEMENTS DETECTED:")
    print("-" * 40)
    
    # Contact info leakage
    old_contact_leak = any('@' in s or 'http' in s for s in old_summary)
    new_contact_leak = any('@' in s or 'http' in s for s in new_summary)
    print(f"✓ Contact info removed from summary: {old_contact_leak} → {new_contact_leak}")
    
    # Date patterns
    old_dates = sum(1 for s in old_summary if _detect_date_patterns(s))
    new_dates = sum(1 for s in new_summary if _detect_date_patterns(s))
    print(f"✓ Date patterns removed from summary: {old_dates} → {new_dates}")
    
    # Phone numbers
    old_phones = sum(1 for s in old_summary if _detect_phone_numbers(s))
    new_phones = sum(1 for s in new_summary if _detect_phone_numbers(s))
    print(f"✓ Phone numbers removed from summary: {old_phones} → {new_phones}")
    
    # Address patterns
    old_addresses = sum(1 for s in old_summary if _detect_address_patterns(s))
    new_addresses = sum(1 for s in new_summary if _detect_address_patterns(s))
    print(f"✓ Address patterns removed from summary: {old_addresses} → {new_addresses}")
    
    # Broken fragments
    old_broken = sum(1 for s in old_summary if len(s) < 20 and not s.endswith(('.', '!', '?')))
    new_broken = sum(1 for s in new_summary if len(s) < 20 and not s.endswith(('.', '!', '?')))
    print(f"✓ Broken fragments removed: {old_broken} → {new_broken}")
    
    # Skills comparison
    print("\n4. SKILLS EXTRACTION:")
    print("-" * 40)
    old_skills = old_data.get('skills', [])
    new_skills = new_data.get('skills', [])
    print(f"OLD: {len(old_skills)} skills")
    print(f"NEW: {len(new_skills)} skills")
    
    # Languages comparison
    print("\n5. LANGUAGES EXTRACTION:")
    print("-" * 40)
    old_langs = old_data.get('languages', [])
    new_langs = new_data.get('languages', [])
    print(f"OLD: {len(old_langs)} languages")
    print(f"NEW: {len(new_langs)} languages")
    
    # Education comparison
    print("\n6. EDUCATION EXTRACTION:")
    print("-" * 40)
    old_edu = old_data.get('education', [])
    new_edu = new_data.get('education', [])
    print(f"OLD: {len(old_edu)} education entries")
    print(f"NEW: {len(new_edu)} education entries")
    
    # Experience comparison
    print("\n7. EXPERIENCE EXTRACTION:")
    print("-" * 40)
    old_exp = old_data.get('experience', [])
    new_exp = new_data.get('experience', [])
    print(f"OLD: {len(old_exp)} experience entries")
    print(f"NEW: {len(new_exp)} experience entries")
    
    # Projects comparison
    print("\n8. PROJECTS EXTRACTION:")
    print("-" * 40)
    old_proj = old_data.get('projects', [])
    new_proj = new_data.get('projects', [])
    print(f"OLD: {len(old_proj)} project entries")
    print(f"NEW: {len(new_proj)} project entries")
    
    # Save comparison
    comparison = {
        "old_output": old_data,
        "new_output": new_data,
        "improvements": {
            "name_extraction_improved": old_name != new_name,
            "contact_leakage_removed": old_contact_leak and not new_contact_leak,
            "date_patterns_removed": old_dates > new_dates,
            "phone_numbers_removed": old_phones > new_phones,
            "address_patterns_removed": old_addresses > new_addresses,
            "broken_fragments_removed": old_broken > new_broken,
            "summary_entries": len(new_summary),
            "skills_extracted": len(new_skills),
            "languages_detected": len(new_langs),
            "education_entries": len(new_edu),
            "experience_entries": len(new_exp),
            "project_entries": len(new_proj)
        }
    }
    
    with open("dynamic_parser_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    
    print(f"\nComparison saved to: dynamic_parser_comparison.json")

def _detect_phone_numbers(text):
    """Helper function to detect phone numbers."""
    phone_patterns = [
        r"\+?\d[\d\s\-/()]{7,}",
        r"\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b",
        r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}\b",
        r"\b\d{4}[\s\-]?\d{4}\b",
    ]
    return any(re.search(pattern, text) for pattern in phone_patterns)

def _detect_date_patterns(text):
    """Helper function to detect date patterns."""
    date_patterns = [
        r"\b(?:19|20)\d{2}\b",
        r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
        r"\b\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+(?:19|20)\d{2}\b",
        r"\b[A-Za-zÀ-ÿ]+\s+(?:19|20)\d{2}\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|janv|févr|mars|avr|mai|juin|juil|aoû|sept|oct|nov|déc)\s*(?:19|20)\d{2}\b",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns)

def _detect_address_patterns(text):
    """Helper function to detect address patterns."""
    address_indicators = [
        r"\b\d+\s+[A-Za-zÀ-ÿ\s]+(?:street|st\.|avenue|av\.|road|rd\.|boulevard|blvd|drive|dr\.|lane|ln\.|way|place|pl\.|court|ct\.|circle|cir\.|square|sq\.)\b",
        r"\b[A-Za-zÀ-ÿ\s]+(?:street|st\.|avenue|av\.|road|rd\.|boulevard|blvd|drive|dr\.|lane|ln\.|way|place|pl\.|court|ct\.|circle|cir\.|square|sq\.)\s+\d+\b",
        r"\b\d{5}\b",
        r"\b[A-Za-zÀ-ÿ\s]+\s+\d{4,5}\s+[A-Za-zÀ-ÿ\s]+\b",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in address_indicators)

if __name__ == "__main__":
    compare_outputs()
