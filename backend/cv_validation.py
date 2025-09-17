#!/usr/bin/env python3

import re
import json
from typing import Dict, Any, List, Tuple, Optional


class CVValidationError(Exception):
    """Custom exception for CV validation errors."""
    pass


class CVValidator:
    """Validates AI-generated CV structure against heuristics."""
    
    def __init__(self):
        self.dummy_indicators = [
            "n/a", "no information", "not available", "sample", "example",
            "placeholder", "dummy", "test", "lorem ipsum", "unknown", 
            "tbd", "to be determined", "no information available"
        ]
        
        self.min_content_length = 200
        self.min_skills_count = 1
        self.min_experience_count = 1
        self.min_education_count = 1
    
    def validate_ai_output(self, ai_data: Dict[str, Any], raw_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate AI output against strict schema and heuristics.
        
        Returns:
            Tuple of (is_valid, reason, validation_details)
        """
        validation_details = {
            "has_name": False,
            "has_meaningful_content": False,
            "has_skills_or_experience_or_education": False,
            "content_length_sufficient": False,
            "no_dummy_content": True,
            "overall_score": 0.0
        }
        
        try:
            # Check 1: Name is present
            name_present = self._check_name_present(ai_data)
            validation_details["has_name"] = name_present
            
            # Check 2: Content length is sufficient
            content_length_ok = self._check_content_length(ai_data, raw_text)
            validation_details["content_length_sufficient"] = content_length_ok
            
            # Check 3: Has meaningful content (not just empty structures)
            meaningful_content = self._check_meaningful_content(ai_data)
            validation_details["has_meaningful_content"] = meaningful_content
            
            # Check 4: Has at least one of skills, experience, or education
            has_required_sections = self._check_required_sections(ai_data)
            validation_details["has_skills_or_experience_or_education"] = has_required_sections
            
            # Check 5: No dummy/placeholder content
            no_dummy = self._check_no_dummy_content(ai_data)
            validation_details["no_dummy_content"] = no_dummy
            
            # Calculate overall score
            score = self._calculate_validation_score(validation_details)
            validation_details["overall_score"] = score
            
            # Determine if valid (score >= 0.7 and no dummy content)
            is_valid = score >= 0.7 and no_dummy
            
            if not is_valid:
                reason = self._generate_failure_reason(validation_details)
            else:
                reason = "AI output passed validation"
            
            return is_valid, reason, validation_details
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", validation_details
    
    def _check_name_present(self, data: Dict[str, Any]) -> bool:
        """Check if name is present in contact_info or professional_summary."""
        # Check contact_info.name
        contact_info = data.get("contact_info", {})
        if isinstance(contact_info, dict):
            name = contact_info.get("name", "").strip()
            if name and len(name) > 1 and not self._is_dummy_content(name):
                return True
        
        # Check professional_summary for name patterns
        summary = data.get("professional_summary", [])
        if isinstance(summary, list):
            for line in summary:
                if isinstance(line, str) and self._contains_name_pattern(line):
                    return True
        
        return False
    
    def _check_content_length(self, data: Dict[str, Any], raw_text: str) -> bool:
        """Check if structured content has sufficient length."""
        total_length = 0
        
        # Count content in all sections
        for section_name, section_data in data.items():
            if section_name == "contact_info" and isinstance(section_data, dict):
                for field, value in section_data.items():
                    if isinstance(value, str):
                        total_length += len(value)
                    elif isinstance(value, list):
                        total_length += sum(len(str(item)) for item in value)
            elif isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, str):
                        total_length += len(item)
                    elif isinstance(item, dict):
                        for field, value in item.items():
                            if isinstance(value, str):
                                total_length += len(value)
                            elif isinstance(value, list):
                                total_length += sum(len(str(subitem)) for subitem in value)
        
        return total_length >= self.min_content_length
    
    def _check_meaningful_content(self, data: Dict[str, Any]) -> bool:
        """Check if data contains meaningful content (not just empty structures)."""
        # Check if any section has substantial content
        for section_name, section_data in data.items():
            if section_name == "contact_info" and isinstance(section_data, dict):
                # Check if contact info has meaningful data
                for field, value in section_data.items():
                    if field in ["emails", "phones"] and isinstance(value, list) and len(value) > 0:
                        return True
                    elif field in ["name", "address"] and isinstance(value, str) and len(value.strip()) > 2:
                        return True
            elif isinstance(section_data, list) and len(section_data) > 0:
                # Check if list has meaningful items
                for item in section_data:
                    if isinstance(item, str) and len(item.strip()) > 10:
                        return True
                    elif isinstance(item, dict):
                        for field, value in item.items():
                            if isinstance(value, str) and len(value.strip()) > 5:
                                return True
                            elif isinstance(value, list) and len(value) > 0:
                                return True
        
        return False
    
    def _check_required_sections(self, data: Dict[str, Any]) -> bool:
        """Check if at least one of skills, experience, or education has content."""
        # Check skills
        skills = data.get("skills", [])
        if isinstance(skills, list) and len(skills) >= self.min_skills_count:
            return True
        
        # Check experience
        experience = data.get("experience", [])
        if isinstance(experience, list) and len(experience) >= self.min_experience_count:
            return True
        
        # Check education
        education = data.get("education", [])
        if isinstance(education, list) and len(education) >= self.min_education_count:
            return True
        
        return False
    
    def _check_no_dummy_content(self, data: Dict[str, Any]) -> bool:
        """Check if data contains dummy/placeholder content."""
        # Check all text fields for dummy indicators
        for section_name, section_data in data.items():
            if section_name == "contact_info" and isinstance(section_data, dict):
                for field, value in section_data.items():
                    if isinstance(value, str) and self._is_dummy_content(value):
                        return False
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and self._is_dummy_content(item):
                                return False
            elif isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, str) and self._is_dummy_content(item):
                        return False
                    elif isinstance(item, dict):
                        for field, value in item.items():
                            if isinstance(value, str) and self._is_dummy_content(value):
                                return False
                            elif isinstance(value, list):
                                for subitem in value:
                                    if isinstance(subitem, str) and self._is_dummy_content(subitem):
                                        return False
        
        return True
    
    def _is_dummy_content(self, text: str) -> bool:
        """Check if text contains dummy/placeholder indicators."""
        if not text or len(text.strip()) < 3:
            return True
        
        text_lower = text.lower().strip()
        
        # Check for dummy indicators (but be more specific)
        for indicator in self.dummy_indicators:
            if indicator in text_lower and len(text.strip()) < 20:  # Only flag if short
                return True
        
        # Check for very short responses
        if len(text.strip()) < 5:
            return True
        
        # Check for repetitive patterns
        if len(set(text.split())) < 3 and len(text.split()) > 5:
            return True
        
        # Check for empty JSON-like structures
        if text.strip() in ["{}", "[]", "null", ""]:
            return True
        
        return False
    
    def _contains_name_pattern(self, text: str) -> bool:
        """Check if text contains a name pattern."""
        # Look for patterns like "John Doe", "J. Smith", etc.
        name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b[A-Z]\. [A-Z][a-z]+\b',      # F. Last
            r'\b[A-Z][a-z]+ [A-Z]\.\b',      # First L.
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _calculate_validation_score(self, details: Dict[str, Any]) -> float:
        """Calculate overall validation score (0.0 to 1.0)."""
        weights = {
            "has_name": 0.2,
            "has_meaningful_content": 0.3,
            "has_skills_or_experience_or_education": 0.3,
            "content_length_sufficient": 0.1,
            "no_dummy_content": 0.1
        }
        
        score = 0.0
        for key, weight in weights.items():
            if details.get(key, False):
                score += weight
        
        return score
    
    def _generate_failure_reason(self, details: Dict[str, Any]) -> str:
        """Generate human-readable failure reason."""
        reasons = []
        
        if not details.get("has_name", False):
            reasons.append("missing name")
        
        if not details.get("has_meaningful_content", False):
            reasons.append("insufficient meaningful content")
        
        if not details.get("has_skills_or_experience_or_education", False):
            reasons.append("missing required sections (skills/experience/education)")
        
        if not details.get("content_length_sufficient", False):
            reasons.append("content too short")
        
        if not details.get("no_dummy_content", False):
            reasons.append("contains dummy/placeholder content")
        
        if reasons:
            return f"Validation failed: {', '.join(reasons)} (score: {details['overall_score']:.2f})"
        else:
            return "Validation failed: unknown reason"
    
    def detect_partial_output(self, ai_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Detect if AI output is partial (some sections missing).
        
        Returns:
            Tuple of (is_partial, missing_sections)
        """
        required_sections = [
            "contact_info", "professional_summary", "skills", 
            "languages", "education", "experience", "projects"
        ]
        
        missing_sections = []
        
        for section in required_sections:
            section_data = ai_data.get(section)
            
            if section == "contact_info":
                if not isinstance(section_data, dict) or not any(section_data.values()):
                    missing_sections.append(section)
            elif isinstance(section_data, list) and len(section_data) == 0:
                missing_sections.append(section)
            elif not section_data:
                missing_sections.append(section)
        
        is_partial = len(missing_sections) > 0
        return is_partial, missing_sections


def validate_cv_structure(ai_data: Dict[str, Any], raw_text: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Convenience function to validate CV structure.
    
    Returns:
        Tuple of (is_valid, reason, validation_details)
    """
    validator = CVValidator()
    return validator.validate_ai_output(ai_data, raw_text)


def detect_partial_cv(ai_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Convenience function to detect partial CV output.
    
    Returns:
        Tuple of (is_partial, missing_sections)
    """
    validator = CVValidator()
    return validator.detect_partial_output(ai_data)
