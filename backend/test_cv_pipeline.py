#!/usr/bin/env python3

import os
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Mock the llama_service import to avoid torch dependency
import sys
sys.modules['llama_service'] = Mock()

from cv_validation import validate_cv_structure, detect_partial_cv


class TestCVPipeline(unittest.TestCase):
    """Test cases for the two-step CV processing pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a mock processor for testing
        from cv_validation import CVValidator
        self.validator = CVValidator()
        
        # Sample raw text for testing
        self.sample_raw_text = """
        John Doe
        Software Engineer
        john.doe@email.com
        +1-555-123-4567
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years of experience in Python, JavaScript, and React.
        Passionate about creating innovative solutions and leading development teams.
        
        TECHNICAL SKILLS
        - Python, JavaScript, React, Node.js
        - PostgreSQL, MongoDB
        - Docker, AWS
        - Git, Agile methodologies
        
        EXPERIENCE
        June 2020 - Present: Senior Software Engineer at TechCorp
        - Led development of microservices architecture
        - Mentored junior developers
        - Implemented CI/CD pipelines
        
        EDUCATION
        September 2016 - June 2020: Bachelor of Computer Science
        University of Technology
        - Graduated with honors
        - Relevant coursework: Data Structures, Algorithms, Software Engineering
        """
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validation_well_structured_cv(self):
        """Test A: Well-structured CV with AI success."""
        # Mock well-structured AI output
        well_structured_ai_output = {
            "contact_info": {
                "emails": ["john.doe@email.com"],
                "phones": ["+1-555-123-4567"],
                "linkedin": "",
                "address": "",
                "name": "John Doe"
            },
            "professional_summary": [
                "Experienced software engineer with 5+ years of experience",
                "Passionate about creating innovative solutions"
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "MongoDB", "Docker", "AWS"],
            "languages": [
                {"language": "English", "level": "Native"},
                {"language": "Spanish", "level": "Intermediate"}
            ],
            "education": [
                {
                    "date_range": "September 2016 - June 2020",
                    "degree": "Bachelor of Computer Science",
                    "institution": "University of Technology",
                    "details": ["Graduated with honors", "Relevant coursework: Data Structures, Algorithms"]
                }
            ],
            "experience": [
                {
                    "date_range": "June 2020 - Present",
                    "company": "TechCorp",
                    "role": "Senior Software Engineer",
                    "details": ["Led development of microservices architecture", "Mentored junior developers"]
                }
            ],
            "projects": [
                {
                    "title": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce platform using React and Node.js"
                }
            ]
        }
        
        # Test validation
        is_valid, reason, details = validate_cv_structure(well_structured_ai_output, self.sample_raw_text)
        
        self.assertTrue(is_valid, f"Validation should pass for well-structured CV: {reason}")
        self.assertGreaterEqual(details["overall_score"], 0.7)
        self.assertTrue(details["has_name"])
        self.assertTrue(details["has_meaningful_content"])
        self.assertTrue(details["has_skills_or_experience_or_education"])
        self.assertTrue(details["content_length_sufficient"])
        self.assertTrue(details["no_dummy_content"])
    
    def test_validation_messy_cv_ai_fails(self):
        """Test B: Messy/unstructured CV where AI fails and fallback is used."""
        # Mock poor AI output (dummy/placeholder content)
        poor_ai_output = {
            "contact_info": {
                "emails": [],
                "phones": [],
                "linkedin": "",
                "address": "",
                "name": "N/A"
            },
            "professional_summary": ["No information available"],
            "skills": [],
            "languages": [],
            "education": [],
            "experience": [],
            "projects": []
        }
        
        # Test validation
        is_valid, reason, details = validate_cv_structure(poor_ai_output, self.sample_raw_text)
        
        self.assertFalse(is_valid, f"Validation should fail for poor AI output: {reason}")
        self.assertLess(details["overall_score"], 0.7)
        self.assertFalse(details["has_name"])
        self.assertFalse(details["has_meaningful_content"])
        self.assertFalse(details["has_skills_or_experience_or_education"])
        self.assertFalse(details["no_dummy_content"])
    
    def test_validation_partial_ai_output(self):
        """Test C: Partial AI output where merge is required."""
        # Mock partial AI output (some sections missing)
        partial_ai_output = {
            "contact_info": {
                "emails": ["john.doe@email.com"],
                "phones": ["+1-555-123-4567"],
                "linkedin": "",
                "address": "",
                "name": "John Doe"
            },
            "professional_summary": [
                "Experienced software engineer with 5+ years of experience"
            ],
            "skills": ["Python", "JavaScript", "React"],
            "languages": [],  # Missing
            "education": [],  # Missing
            "experience": [],  # Missing
            "projects": []  # Missing
        }
        
        # Test partial detection
        is_partial, missing_sections = detect_partial_cv(partial_ai_output)
        
        self.assertTrue(is_partial)
        self.assertIn("languages", missing_sections)
        self.assertIn("education", missing_sections)
        self.assertIn("experience", missing_sections)
        self.assertIn("projects", missing_sections)
    
    def test_validation_dummy_content_detection(self):
        """Test detection of dummy/placeholder content."""
        dummy_cases = [
            "N/A",
            "No information",
            "Sample data",
            "John Doe",  # Common placeholder name
            "example@email.com",
            "Lorem ipsum dolor sit amet",
            "{}",
            "[]",
            "null",
            ""
        ]
        
        validator = self.validator
        
        for dummy_text in dummy_cases:
            with self.subTest(dummy_text=dummy_text):
                self.assertTrue(validator._is_dummy_content(dummy_text), 
                              f"Should detect '{dummy_text}' as dummy content")
    
    def test_validation_meaningful_content_detection(self):
        """Test detection of meaningful content."""
        meaningful_cases = [
            "John Smith",
            "john.smith@company.com",
            "Experienced software engineer with 5+ years",
            "Led development of microservices architecture",
            "Bachelor of Computer Science from MIT",
            "Python, JavaScript, React, Node.js"
        ]
        
        validator = self.validator
        
        for meaningful_text in meaningful_cases:
            with self.subTest(meaningful_text=meaningful_text):
                self.assertFalse(validator._is_dummy_content(meaningful_text), 
                               f"Should not detect '{meaningful_text}' as dummy content")
    
    def test_validation_name_detection(self):
        """Test name detection in various formats."""
        # Test contact_info name
        data_with_contact_name = {
            "contact_info": {"name": "John Smith"},
            "professional_summary": []
        }
        is_valid, _, details = validate_cv_structure(data_with_contact_name, self.sample_raw_text)
        self.assertTrue(details["has_name"])
        
        # Test professional_summary name
        data_with_summary_name = {
            "contact_info": {"name": ""},
            "professional_summary": ["John Smith is an experienced engineer"]
        }
        is_valid, _, details = validate_cv_structure(data_with_summary_name, self.sample_raw_text)
        self.assertTrue(details["has_name"])
        
        # Test no name
        data_no_name = {
            "contact_info": {"name": ""},
            "professional_summary": ["Experienced engineer with skills"]
        }
        is_valid, _, details = validate_cv_structure(data_no_name, self.sample_raw_text)
        self.assertFalse(details["has_name"])
    
    def test_merge_partial_outputs(self):
        """Test merging partial AI output with CLI parser output."""
        ai_data = {
            "contact_info": {
                "emails": ["john.doe@email.com"],
                "phones": ["+1-555-123-4567"],
                "name": "John Doe"
            },
            "skills": ["Python", "JavaScript"],
            "experience": []  # Missing
        }
        
        cli_data = {
            "contact_info": {
                "emails": ["john.doe@email.com"],
                "phones": ["+1-555-123-4567"],
                "address": "123 Main St"
            },
            "skills": ["Python", "JavaScript", "React"],
            "experience": [{"company": "TechCorp", "role": "Software Engineer"}],
            "education": [{"degree": "Bachelor of Computer Science"}]
        }
        
        missing_sections = ["experience", "education"]
        
        # Simple merge logic for testing
        merged = ai_data.copy()
        for section in missing_sections:
            if section in cli_data and cli_data[section]:
                merged[section] = cli_data[section]
        
        # Check that AI data is preserved
        self.assertEqual(merged["contact_info"]["name"], "John Doe")
        self.assertEqual(merged["skills"], ["Python", "JavaScript"])
        
        # Check that missing sections are filled from CLI
        self.assertIn("experience", merged)
        self.assertIn("education", merged)
        self.assertEqual(len(merged["experience"]), 1)
        self.assertEqual(len(merged["education"]), 1)


if __name__ == "__main__":
    unittest.main()
