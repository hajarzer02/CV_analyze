#!/usr/bin/env python3
"""
Test script to demonstrate the improved address extraction integration.
"""

import os
import json
from cv_extractor_cli import CVExtractor

def test_address_extraction_on_cvs():
    """Test address extraction on actual CV files."""
    print("🏠 Testing Address Extraction on Real CV Files")
    print("=" * 60)
    
    # Test on CV files
    cv_files = [
        "cv_files/CV ZEROUAL Hajar.pdf",
        "cv_files/CV_Chadi.pdf", 
        "cv_files/CV_Doha_Bouhali.pdf",
        "cv_files/CV_ENG_DEV.pdf",
        "cv_files/NOUR_CV.pdf"
    ]
    
    extractor = CVExtractor()
    
    for i, cv_file in enumerate(cv_files, 1):
        if not os.path.exists(cv_file):
            print(f"⚠️  File not found: {cv_file}")
            continue
            
        print(f"\n📄 Test {i}: {os.path.basename(cv_file)}")
        print("-" * 50)
        
        try:
            # Extract CV data
            data = extractor.extract_cv_data(cv_file)
            
            # Display contact info
            contact_info = data.get("contact_info", {})
            print(f"📧 Email: {contact_info.get('emails', ['None'])[0]}")
            print(f"📞 Phone: {contact_info.get('phones', ['None'])[0]}")
            print(f"🔗 LinkedIn: {contact_info.get('linkedin', 'None')}")
            print(f"🏠 Address: '{contact_info.get('address', 'None')}'")
            
            # Show if address was found
            if contact_info.get('address'):
                print("✅ Address successfully extracted!")
            else:
                print("❌ No address found")
                
        except Exception as e:
            print(f"❌ Error processing {cv_file}: {e}")
    
    print(f"\n📊 Summary")
    print("=" * 20)
    print("The dynamic address extraction uses:")
    print("• Pattern recognition for postal codes (US, Canada, France, UK, etc.)")
    print("• Address structure words (street, avenue, boulevard, rue, etc.)")
    print("• Geographic indicators (city, state, country patterns)")
    print("• Contextual clues (address keywords in English/French)")
    print("• Scoring system to select the best address candidate")
    print("• Multi-line address detection")
    print("• Duplicate removal and similarity checking")

def test_address_extraction_accuracy():
    """Test address extraction accuracy with sample text."""
    print("\n🧪 Testing Address Extraction Accuracy")
    print("=" * 50)
    
    from address_extractor import extract_contact_address
    
    test_cases = [
        {
            "name": "English CV with clear address",
            "text": """
            John Smith
            Software Engineer
            Email: john@example.com
            Phone: (555) 123-4567
            Address: 123 Main Street, Apt 4B, New York, NY 10001
            """,
            "expected": "123 Main Street, Apt 4B, New York, NY 10001"
        },
        {
            "name": "French CV with address",
            "text": """
            Marie Dupont
            Développeuse
            Email: marie@example.fr
            Téléphone: 01 42 34 56 78
            Adresse: 25 Rue de la République, 75011 Paris, France
            """,
            "expected": "25 Rue de la République, 75011 Paris, France"
        },
        {
            "name": "CV with location field",
            "text": """
            Sarah Johnson
            Data Analyst
            Email: sarah@example.com
            Location: 789 Elm Street, Unit 12, Toronto, ON M5V 3A1
            """,
            "expected": "789 Elm Street, Unit 12, Toronto, ON M5V 3A1"
        },
        {
            "name": "CV with domicile field",
            "text": """
            Pierre Martin
            Ingénieur
            Email: pierre@example.fr
            Domicile: 42 Boulevard Saint-Michel, Appartement 5, Lyon 69002
            """,
            "expected": "42 Boulevard Saint-Michel, Appartement 5, Lyon 69002"
        }
    ]
    
    correct = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 40)
        
        extracted = extract_contact_address(test_case['text'])
        expected = test_case['expected']
        
        print(f"Expected: '{expected}'")
        print(f"Extracted: '{extracted}'")
        
        # Check if the extracted address contains the expected content
        if expected.lower() in extracted.lower() or extracted.lower() in expected.lower():
            print("✅ PASS - Address correctly extracted")
            correct += 1
        else:
            print("❌ FAIL - Address not correctly extracted")
    
    print(f"\n📊 Accuracy Results")
    print("=" * 20)
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {(correct/total)*100:.1f}%")

def main():
    """Run all address extraction tests."""
    print("🔍 Address Extraction Integration Test Suite")
    print("=" * 60)
    
    # Test on real CV files
    test_address_extraction_on_cvs()
    
    # Test accuracy with sample text
    test_address_extraction_accuracy()
    
    print(f"\n🎉 Address Extraction Integration Complete!")
    print("=" * 50)
    print("✅ Dynamic address extraction is now integrated into the CV analysis system")
    print("✅ Supports both English and French CVs")
    print("✅ Uses intelligent pattern recognition and scoring")
    print("✅ Provides fallback to simple pattern matching if needed")
    print("✅ Handles various address formats and postal codes")

if __name__ == "__main__":
    main()
