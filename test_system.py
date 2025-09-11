#!/usr/bin/env python3
"""
Test script for the CV Analysis system.
This script tests the basic functionality without requiring a full setup.
"""

import os
import json
import tempfile
from cv_extractor_cli import CVExtractor
from llama_service import LlamaService

def test_cv_extraction():
    """Test CV extraction functionality."""
    print("🧪 Testing CV Extraction...")
    
    # Check if we have any CV files to test with
    cv_files_dir = "cv_files"
    if not os.path.exists(cv_files_dir):
        print("✗ No cv_files directory found")
        return False
    
    cv_files = [f for f in os.listdir(cv_files_dir) if f.lower().endswith(('.pdf', '.docx', '.txt'))]
    if not cv_files:
        print("✗ No CV files found in cv_files directory")
        return False
    
    # Test extraction on the first CV file
    test_file = os.path.join(cv_files_dir, cv_files[0])
    print(f"📄 Testing with: {cv_files[0]}")
    
    try:
        extractor = CVExtractor()
        result = extractor.extract_cv_data(test_file)
        
        print("✓ CV extraction successful")
        print(f"  - Contact info: {len(result.get('contact_info', {}).get('emails', []))} emails")
        print(f"  - Skills: {len(result.get('skills', []))} skills")
        print(f"  - Education: {len(result.get('education', []))} entries")
        print(f"  - Experience: {len(result.get('experience', []))} entries")
        
        return True
    except Exception as e:
        print(f"✗ CV extraction failed: {e}")
        return False

def test_llama_service():
    """Test LLaMA service functionality."""
    print("\n🤖 Testing LLaMA Service...")
    
    try:
        llama_service = LlamaService()
        
        # Test with dummy data
        test_data = {
            "contact_info": {"emails": ["test@example.com"]},
            "skills": ["Python", "JavaScript", "React"],
            "education": [{"degree": "Computer Science", "institution": "University"}],
            "experience": [{"role": "Software Developer", "company": "Tech Corp"}]
        }
        
        recommendations = llama_service.generate_recommendations(test_data)
        
        print("✓ LLaMA service working")
        print(f"  - Generated {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations[:2], 1):
            print(f"    {i}. {rec['title']}: {rec['reason']}")
        
        return True
    except Exception as e:
        print(f"✗ LLaMA service failed: {e}")
        return False

def test_database_models():
    """Test database model imports."""
    print("\n🗄️ Testing Database Models...")
    
    try:
        from database import Candidate, JobRecommendation, create_tables
        print("✓ Database models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Database models import failed: {e}")
        return False

def test_api_models():
    """Test API model imports."""
    print("\n📋 Testing API Models...")
    
    try:
        from models import CandidateResponse, UploadResponse, JobRecommendationResponse
        print("✓ API models imported successfully")
        return True
    except Exception as e:
        print(f"✗ API models import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 CV Analysis System Test Suite")
    print("=" * 40)
    
    tests = [
        test_cv_extraction,
        test_llama_service,
        test_database_models,
        test_api_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results")
    print("=" * 20)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up PostgreSQL database")
        print("2. Create .env file with database credentials")
        print("3. Run: python start_backend.py")
        print("4. Start frontend: cd frontend && npm start")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("- Ensure all dependencies are installed: pip install -r requirements.txt")
        print("- Check that CV files exist in cv_files/ directory")
        print("- Verify Python environment is set up correctly")

if __name__ == "__main__":
    main()
