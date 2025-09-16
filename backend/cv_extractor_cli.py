#!/usr/bin/env python3isi

import os
import re
import json
import fitz  # PyMuPDF
from docx import Document
from typing import Dict, Any, List, Optional, Tuple, Set
import argparse


# ----------------------- Utility helpers -----------------------

def _dedupe_list(items: List[str]) -> List[str]:
    """Remove duplicate items while preserving order."""
    seen: Set[str] = set()
    out: List[str] = []
    for it in items:
        key = (it or "").strip()
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def _clean_text(text: str) -> str:
    """Clean text while preserving structure."""
    if not text:
        return ""
    
    # Remove excessive whitespace but preserve line breaks
    cleaned = re.sub(r"[ \t]+", " ", text)
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)
    
    # Remove null characters and other artifacts
    cleaned = cleaned.replace("\u0000", "")
    
    return cleaned.strip()


def _is_meaningful_text(text: str) -> bool:
    """Check if text contains meaningful content."""
    if not text or len(text.strip()) < 3:
        return False
    
    # Skip if it's just numbers, symbols, or very short fragments
    if re.match(r"^[\d\s\-_=*]+$", text):
        return False
    
    # Skip if it's just a single character
    if len(text.strip()) <= 1:
        return False
    
    return True


# ----------------------- Text extraction -----------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF with better formatting preservation."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
    
    pages: List[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            txt = page.get_text("text")
            txt = _clean_text(txt)
            if txt:
                pages.append(txt)
    
    return "\n\n".join(pages)


def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from DOCX with better formatting."""
    doc = Document(docx_path)
    lines: List[str] = []
    
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if t:
            lines.append(t)
    
    return "\n".join(lines)


def extract_text_from_txt(txt_path: str) -> str:
    """Extract text from TXT file."""
    with open(txt_path, "r", encoding="utf-8") as f:
        lines: List[str] = []
        for ln in f:
            s = (ln or "").strip()
            if s:
                lines.append(s)
    
    return "\n".join(lines)


def load_text(file_path: str) -> str:
    """Load text from various file formats."""
    print(f"DEBUG load_text: Attempting to load file: {file_path}")
    print(f"DEBUG load_text: File exists: {os.path.exists(file_path)}")
    print(f"DEBUG load_text: Current working directory: {os.getcwd()}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    print(f"DEBUG load_text: File extension: {ext}")
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


# ----------------------- Contact extraction -----------------------

def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract contact information using comprehensive regex patterns."""
    contact_info = {
        "emails": [],
        "phones": [],
        "linkedin": "",
        "address": ""
    }
    
    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    contact_info["emails"] = _dedupe_list(emails)
    
    # Extract phone numbers (multiple formats)
    phone_patterns = [
        r'\+?[\d\s\-\(\)]{10,}',  # International format
        r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # US/Canada format
        r'\b\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}\b',  # French format
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean phone number
            cleaned = re.sub(r'[^\d\s\+\(\)\-]', '', match)
            if len(cleaned.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 7:
                phones.append(cleaned.strip())
    
    contact_info["phones"] = _dedupe_list(phones)
    
    # Extract LinkedIn
    linkedin_pattern = r'linkedin\.com/[^\s\n]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info["linkedin"] = linkedin_match.group(0)
    
    # Extract address using dynamic extraction
    try:
        from address_extractor import extract_contact_address
        contact_info["address"] = extract_contact_address(text)
    except ImportError:
        # Fallback to simple pattern matching if address_extractor is not available
        address_patterns = [
            r'[A-Za-zÀ-ÿ\s]+\d{4,5}\s*[A-Za-zÀ-ÿ\s]*',  # French postal code
            r'[A-Za-zÀ-ÿ\s]+,\s*[A-Za-zÀ-ÿ\s]+',  # City, Country format
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, text)
            if address_match:
                address = address_match.group(0).strip()
                if len(address) > 10:  # Filter out very short matches
                    contact_info["address"] = address
                    break
    
    return contact_info


# ----------------------- Skills extraction -----------------------

def extract_skills(text: str) -> List[str]:
    """Extract skills using improved bullet point detection and Unicode handling."""
    skills = []
    
    # Find the skills section by looking for the section header and content
    lines = text.split('\n')
    in_skills = False
    skills_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering skills section (more flexible matching)
        if re.search(r'\b(?:TECHNICAL\s+SKILLS|COMPÉTENCES|SKILLS)\b', line, re.IGNORECASE):
            in_skills = True
            continue
        
        # Check if we're leaving skills section (more flexible matching)
        # Only leave if it's a standalone section header, not content
        if in_skills and re.match(r'^(?:LANGUAGES|LANGUES|EDUCATION|FORMATION|EXPERIENCE|PROJECTS|CERTIFICATIONS)$', line, re.IGNORECASE):
            in_skills = False
            continue
        
        if in_skills:
            skills_lines.append(line)
    
    # Parse skills from the collected lines
    current_category = ""
    current_skills = []
    
    for line in skills_lines:
        if not line:
            continue
        
        # Remove zero-width spaces and other invisible Unicode characters
        line = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', line)
        
        # Check for bullet points (including special Unicode characters)
        bullet_match = re.match(r'^[●○•\-\*]\s*', line)
        if bullet_match:
            # Process previous category if exists
            if current_skills:
                for skill in current_skills:
                    if skill and len(skill) >= 2:
                        skills.append(skill)
                current_skills = []
            
            # Extract content after bullet
            content = re.sub(r'^[●○•\-\*]\s*', '', line)
            if content:
                # Handle "Category: skill1, skill2, skill3" format
                if ':' in content:
                    parts = content.split(':', 1)
                    if len(parts) == 2:
                        current_category = parts[0].strip()
                        skill_list = parts[1].strip()
                        # Split by common separators
                        skill_items = re.split(r'[,;/|]', skill_list)
                        for skill in skill_items:
                            skill = skill.strip()
                            if skill and len(skill) >= 2:
                                # Don't include category names as skills
                                if skill.lower() not in ['programming languages', 'web technologies', 'databases', 'systems and networks', 'software and tools', 'system commands']:
                                    current_skills.append(skill)
                else:
                    # Single skill or comma-separated list
                    skill_items = re.split(r'[,;/|]', content)
                    for skill in skill_items:
                        skill = skill.strip()
                        if skill and len(skill) >= 2:
                            current_skills.append(skill)
        else:
            # This might be a continuation line (no bullet)
            # Check if it looks like skill content
            if line and not re.match(r'^[A-Z\s]+$', line):  # Not just uppercase words
                # Split by common separators
                skill_items = re.split(r'[,;/|]', line)
                for skill in skill_items:
                    skill = skill.strip()
                    if skill and len(skill) >= 2:
                        current_skills.append(skill)
    
    # Process final category
    if current_skills:
        for skill in current_skills:
            if skill and len(skill) >= 2:
                skills.append(skill)
    
    return _dedupe_list(skills)


# ----------------------- Languages extraction -----------------------

def extract_languages(text: str) -> List[Dict[str, str]]:
    """Extract languages using improved section detection and Unicode handling."""
    languages = []
    
    # Find the languages section by looking for the section header and content
    lines = text.split('\n')
    in_languages = False
    languages_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering languages section (exact match for section headers)
        if re.match(r'^(?:LANGUAGES|LANGUES)$', line, re.IGNORECASE):
            in_languages = True
            continue
        
        # Check if we're leaving languages section (more flexible matching)
        if in_languages and re.search(r'\b(?:CERTIFICATIONS|EDUCATION|FORMATION|EXPERIENCE|PROJECTS|SKILLS)\b', line, re.IGNORECASE):
            in_languages = False
            continue
        
        if in_languages:
            languages_lines.append(line)
    
    # Parse languages from the collected lines
    for line in languages_lines:
        if not line:
            continue
        
        # Remove zero-width spaces and other invisible Unicode characters
        line = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', line)
        
        # Check for bullet points
        if re.match(r'^[●○•\-\*]\s*', line):
            content = re.sub(r'^[●○•\-\*]\s*', '', line)
            if content:
                # Look for "Language: Level" pattern
                lang_match = re.match(r'^([A-Za-zÀ-ÿ]+)\s*[:\-–]\s*([A-Za-zÀ-ÿ\s]+)$', content)
                if lang_match:
                    language = lang_match.group(1).title()
                    level = lang_match.group(2).strip().title()
                    if language and level and len(language) > 1:
                        languages.append({"language": language, "level": level})
        else:
            # Check if it's a language line without bullet (continuation)
            # Look for "Language: Level" pattern
            lang_match = re.match(r'^([A-Za-zÀ-ÿ]+)\s*[:\-–]\s*([A-Za-zÀ-ÿ\s]+)$', line)
            if lang_match:
                language = lang_match.group(1).title()
                level = lang_match.group(2).strip().title()
                if language and level and len(language) > 1:
                    languages.append({"language": language, "level": level})
    
    return languages


# ----------------------- Education extraction -----------------------

def extract_education(text: str) -> List[Dict[str, Any]]:
    """Extract education information with improved structure detection."""
    education_entries = []
    
    # Find the education section by looking for the section header and content
    lines = text.split('\n')
    in_education = False
    education_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering education section (exact match for section headers)
        if re.match(r'^(?:EDUCATION|FORMATION|ÉDUCATION)$', line, re.IGNORECASE):
            in_education = True
            continue
        
        # Check if we're leaving education section (more flexible matching)
        if in_education and re.search(r'\b(?:Expérience Professionnelle|EXPERIENCE|PROJECTS|SKILLS|LANGUAGES)\b', line, re.IGNORECASE):
            in_education = False
            continue
        
        if in_education:
            education_lines.append(line)
    
    # Parse education from the collected lines
    current_entry = None
    
    for line in education_lines:
        if not line:
            continue
        
        # Remove zero-width spaces and other invisible Unicode characters
        line = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', line)
        
        # Check for date range pattern (e.g., "SEPT 2022- PRÉSENT :" or "SEPT 2020 - JUIN 2022 :")
        # Use Unicode-aware pattern for French month names
        date_range_match = re.match(r'^([A-ZÀ-ÿ]+\s+\d{4}[-–]\s*(?:PRÉSENT|\d{4}))\s*:\s*(.+)$', line, re.IGNORECASE)
        if date_range_match:
            # Start new entry
            if current_entry:
                education_entries.append(current_entry)
            
            date_range = date_range_match.group(1).strip()
            content = date_range_match.group(2).strip()
            
            current_entry = {
                "date_range": date_range,
                "details": []
            }
            
            # Try to extract institution and degree from content
            if content:
                # Look for institution patterns
                institution_match = re.search(r'\(([^)]+)\)', content)
                if institution_match:
                    current_entry["institution"] = institution_match.group(1).strip()
                    # Remove institution from content to get degree
                    degree_content = re.sub(r'\([^)]+\)', '', content).strip()
                    if degree_content:
                        current_entry["degree"] = degree_content
                else:
                    # If no institution in parentheses, treat as degree
                    current_entry["degree"] = content
        
        # Check for bullet points (coursework/details)
        elif re.match(r'^[●○•\-\*]\s*', line):
            content = re.sub(r'^[●○•\-\*]\s*', '', line)
            if content and current_entry:
                current_entry["details"].append(content.strip())
        
        # Check for continuation lines (no bullet, no date range)
        elif current_entry and _is_meaningful_text(line):
            # This might be a continuation of institution/degree or additional details
            if not re.match(r'^[A-Z\s]+$', line):  # Not just uppercase words
                current_entry["details"].append(line.strip())
            else:
                # Might be institution or degree continuation
                if "degree" not in current_entry or not current_entry["degree"]:
                    current_entry["degree"] = line.strip()
                elif "institution" not in current_entry or not current_entry["institution"]:
                    current_entry["institution"] = line.strip()
    
    # Add final entry
    if current_entry:
        education_entries.append(current_entry)
    
    return education_entries


# ----------------------- Experience extraction -----------------------

def extract_experience(text: str) -> List[Dict[str, Any]]:
    """Extract experience information with improved structure detection."""
    experience_entries = []
    
    # Find the experience section by looking for the section header and content
    lines = text.split('\n')
    in_experience = False
    experience_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering experience section (more flexible matching)
        if re.search(r'\b(?:Expérience Professionnelle|EXPERIENCE|EMPLOI|Professional Experience)\b', line, re.IGNORECASE):
            in_experience = True
            continue
        
        # Check if we're leaving experience section (more flexible matching)
        if in_experience and re.search(r'\b(?:PROJECTS|EDUCATION|FORMATION|SKILLS|LANGUAGES)\b', line, re.IGNORECASE):
            in_experience = False
            continue
        
        if in_experience:
            experience_lines.append(line)
    
    # Parse experience from the collected lines
    current_entry = None
    current_details = []
    
    for line in experience_lines:
        if not line:
            continue
        
        # Remove zero-width spaces and other invisible Unicode characters
        line = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', line)
        
        # Check for date range pattern (e.g., "JUIN 2024 - AOÛT 2024 :" or "Juin 2023 - Août 2023 :")
        # Use Unicode-aware pattern for French month names
        date_range_match = re.match(r'^([A-Za-zÀ-ÿ]+\s+\d{4}\s*[-–]\s*[A-Za-zÀ-ÿ]+\s+\d{4})\s*:\s*(.+)$', line, re.IGNORECASE)
        if not date_range_match:
            # Try alternative pattern without colon (e.g., "JUIN 2024 - AOÛT 2024 Progiciel System,")
            date_range_match = re.match(r'^([A-Za-zÀ-ÿ]+\s+\d{4}\s*[-–]\s*[A-Za-zÀ-ÿ]+\s+\d{4})\s+(.+)$', line, re.IGNORECASE)
        if not date_range_match:
            # Try pattern with space before colon (e.g., "JUIN 2024 - AOÛT 2024 : Progiciel System,")
            date_range_match = re.match(r'^([A-Za-zÀ-ÿ]+\s+\d{4}\s*[-–]\s*[A-Za-zÀ-ÿ]+\s+\d{4})\s+:\s*(.+)$', line, re.IGNORECASE)
        if date_range_match:
            # Finalize previous entry
            if current_entry:
                if current_details:
                    current_entry["details"] = _dedupe_list(current_details)
                experience_entries.append(current_entry)
            
            date_range = date_range_match.group(1).strip()
            content = date_range_match.group(2).strip()
            
            current_entry = {
                "date_range": date_range,
                "details": []
            }
            
            # Try to extract company and role from content
            if content:
                # Split by comma to separate company and role
                parts = content.split(',', 1)
                if len(parts) >= 2:
                    current_entry["company"] = parts[0].strip()
                    current_entry["role"] = parts[1].strip()
                else:
                    current_entry["company"] = content
        
        # Check for bullet points (details)
        elif re.match(r'^[●○•\-\*○]\s*', line):
            content = re.sub(r'^[●○•\-\*○]\s*', '', line)
            if content and current_entry and _is_meaningful_text(content):
                current_details.append(content.strip())
        
        # Check for continuation lines (no bullet, no date range)
        elif current_entry and _is_meaningful_text(line):
            # This might be a continuation of company/role or additional details
            if not re.match(r'^[A-Z\s]+$', line):  # Not just uppercase words
                current_details.append(line.strip())
            else:
                # Might be company or role continuation
                if "role" not in current_entry or not current_entry["role"]:
                    current_entry["role"] = line.strip()
                elif "company" not in current_entry or not current_entry["company"]:
                    current_entry["company"] = line.strip()
    
    # Add final entry
    if current_entry:
        if current_details:
            current_entry["details"] = _dedupe_list(current_details)
        experience_entries.append(current_entry)
    
    return experience_entries


# ----------------------- Projects extraction -----------------------

def extract_projects(text: str) -> List[Dict[str, Any]]:
    """Extract project information."""
    projects = []
    
    # Find the projects section by looking for the section header and content
    lines = text.split('\n')
    in_projects = False
    projects_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering projects section (exact match for section headers)
        if re.match(r'^(?:PROJECTS|PROJETS)$', line, re.IGNORECASE):
            in_projects = True
            continue
        
        # Check if we're leaving projects section (exact match for section headers)
        if in_projects and re.match(r'^(?:EDUCATION|FORMATION|EXPERIENCE|SKILLS|LANGUAGES)$', line, re.IGNORECASE):
            in_projects = False
            continue
        
        if in_projects:
            projects_lines.append(line)
    
    # Parse projects from the collected lines
    for line in projects_lines:
        if not line:
            continue
        
        # Check for bullet points
        if re.match(r'^[●○•\-\*]\s*', line):
            content = re.sub(r'^[●○•\-\*]\s*', '', line)
            if content:
                # Look for project description
                if ':' in content:
                    title, description = content.split(':', 1)
                    projects.append({
                        "title": title.strip(),
                        "description": description.strip()
                    })
                else:
                    projects.append({
                        "title": content,
                        "description": ""
                    })
    
    return projects


# ----------------------- Summary extraction -----------------------

def extract_summary(text: str) -> List[str]:
    """Extract professional summary with better content detection."""
    summary_lines = []
    
    # Find the summary section by looking for the section header and content
    lines = text.split('\n')
    in_summary = False
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering summary section (exact match for section headers)
        if re.match(r'^(?:SUMMARY|RÉSUMÉ|PROFILE)$', line, re.IGNORECASE):
            in_summary = True
            continue
        
        # Check if we're leaving summary section (exact match for section headers)
        if in_summary and re.match(r'^(?:TECHNICAL SKILLS|SKILLS|EDUCATION|FORMATION|EXPERIENCE|LANGUAGES|PROJECTS)$', line, re.IGNORECASE):
            in_summary = False
            continue
        
        if in_summary:
            summary_lines.append(line)
    
    # Parse summary from the collected lines
    summary_text = []
    
    for line in summary_lines:
        if not line:
            continue
        
        # Skip if it contains contact information
        if re.search(r'@', line) or re.search(r'\+?\d', line) or re.search(r'linkedin\.com|github\.com', line):
            continue
        
        # Skip if it's too short or looks like a fragment
        if len(line) < 20 and not line.endswith(('.', '!', '?')):
            continue
        
        # Clean up the text
        cleaned = _clean_text(line)
        if cleaned and _is_meaningful_text(cleaned):
            summary_text.append(cleaned)
    
    return _dedupe_list(summary_text)


# ----------------------- Main CV Extractor Class -----------------------

class CVExtractor:
    """Improved CV extractor with better parsing accuracy."""
    
    def extract_raw_text(self, file_path: str) -> str:
        """Extract raw text from CV file and save to data.txt."""
        text = load_text(file_path)
        
        # Save raw text to data.txt in the same directory as the CV file
        cv_dir = os.path.dirname(file_path)
        data_txt_path = os.path.join(cv_dir, "data.txt")
        
        with open(data_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"DEBUG: Raw text saved to: {data_txt_path}")
        return text
    
    def extract_cv_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured CV data with improved parsing."""
        text = load_text(file_path)
        
        # Extract all information
        data = {
            "contact_info": extract_contact_info(text),
            "professional_summary": extract_summary(text),
            "skills": extract_skills(text),
            "languages": extract_languages(text),
            "education": extract_education(text),
            "experience": extract_experience(text),
            "projects": extract_projects(text),
        }
        
        # Clean empty fields
        return {k: v for k, v in data.items() if v and (not isinstance(v, list) or len(v) > 0) and (not isinstance(v, dict) or any(v.values()))}


# ----------------------- CLI -----------------------

def main():
    parser = argparse.ArgumentParser(description="Improved CV parser with better section detection")
    parser.add_argument("input_dir", help="Directory containing CV files (pdf, docx, txt)")
    parser.add_argument("--output-dir", default="outputs", help="Directory for output JSON files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    files = [f for f in os.listdir(args.input_dir) if f.lower().endswith((".pdf", ".docx", ".doc", ".txt"))]
    print(f"Found {len(files)} file(s)")
    
    for i, name in enumerate(files, 1):
        in_path = os.path.join(args.input_dir, name)
        out_path = os.path.join(args.output_dir, f"{os.path.splitext(name)[0]}.json")
        print(f"[{i}/{len(files)}] Processing {name}")
        
        try:
            extractor = CVExtractor()
            data = extractor.extract_cv_data(in_path)
            
            # Save output
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Saved: {out_path}")
        except Exception as e:
            print(f"✗ Error processing {name}: {e}")

    print("\nExtraction complete!")


if __name__ == "__main__":
    main()


