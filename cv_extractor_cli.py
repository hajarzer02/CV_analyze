#!/usr/bin/env python3

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
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


# ----------------------- Improved section detection -----------------------

def _is_header_line(line: str) -> bool:
    """Determine if a line looks like a section header."""
    s = (line or "").strip()
    if not s:
        return False
    
    # Ends with colon and is short
    if s.endswith(":") and len(s.split()) <= 8:
        return True
    
    # All caps short line (common in many languages)
    letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", s)
    if len(letters) >= 2 and s == s.upper() and len(s.split()) <= 8:
        return True
    
    # Title case short line - but be more restrictive for names
    words = s.split()
    if 1 <= len(words) <= 6 and all(w[:1].isupper() for w in words if w):
        # Skip if it's just a single word that could be a name
        if len(words) == 1 and len(s) <= 20:
            return False
        # Skip if it's just two words that could be a name
        if len(words) == 2 and len(s) <= 30:
            return False
        return True
    
    # Check for common section indicators
    section_indicators = [
        r"^(?:summary|resume|profile|about|overview|introduction|presentation|présentation|résumé|profil|aperçu|introduction)$",
        r"^(?:experience|work|employment|emploi|travail|expérience|carrière|career|professional\s+experience)$",
        r"^(?:education|formation|études|academic|académique|diplômes|diplomas)$",
        r"^(?:skills|compétences|competences|aptitudes|capacités|capabilities|technical\s+skills)$",
        r"^(?:languages|langues|idiomas|sprachen|lingue)$",
        r"^(?:projects|projets|proyectos|projekte|progetti)$",
        r"^(?:contact|coordonnées|contacto|kontakt|contatto)$",
        r"^(?:certifications|certificaciones|zertifikate|certificazioni)$",
    ]
    
    return any(re.search(pattern, s, re.IGNORECASE) for pattern in section_indicators)


def _detect_bullet_line(line: str) -> bool:
    """Detect if a line starts with a bullet point."""
    if not line:
        return False
    
    stripped = line.strip()
    bullet_patterns = [
        r"^[\u2022\u25E6\u2023\u2043\u2219•○●]",  # Unicode bullets
        r"^[\-\*]",  # Dash/asterisk
        r"^\d+[\.\)]\s+",  # Numbered lists
        r"^[a-z][\.\)]\s+",  # Letter lists
    ]
    
    return any(re.match(pattern, stripped) for pattern in bullet_patterns)


def _extract_bullet_content(line: str) -> str:
    """Extract content from a bullet line."""
    if not line:
        return ""
    
    # Remove bullet markers
    cleaned = re.sub(r"^[\u2022\u25E6\u2023\u2043\u2219•○●\-\*\s]+", "", line.strip())
    cleaned = re.sub(r"^\d+[\.\)]\s+", "", cleaned)
    cleaned = re.sub(r"^[a-z][\.\)]\s+", "", cleaned)
    
    return cleaned.strip()


def split_sections_improved(text: str) -> Dict[str, List[str]]:
    """Split text into sections with improved detection."""
    sections: Dict[str, List[str]] = {}
    current_header = "header"  # Default section for top content
    sections[current_header] = []
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a header line
        if _is_header_line(line):
            # Clean header name
            header_name = line.strip().rstrip(":")
            # Normalize header names
            header_name = re.sub(r'\s+', ' ', header_name).strip()
            current_header = header_name
            if current_header not in sections:
                sections[current_header] = []
            continue
        
        # Skip separator lines
        if re.fullmatch(r"[\-\_=\*\s]+", line):
            continue
        
        # Add line to current section
        if current_header not in sections:
            sections[current_header] = []
        sections[current_header].append(line)
    
    return sections


# ----------------------- Improved field extractors -----------------------

def extract_name_improved(text: str) -> str:
    """Extract name from CV header more reliably."""
    lines = text.split('\n')
    
    # Look for the first meaningful line that could be a name
    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        line = line.strip()
        if not line or len(line) < 2:
            continue
        
        # Skip if it looks like a section header
        if _is_header_line(line):
            continue
        
        # Skip if it contains contact information
        if re.search(r'@', line) or re.search(r'\+?\d', line) or re.search(r'linkedin\.com|github\.com', line):
            continue
        
        # Skip if it's too long (likely not a name)
        if len(line) > 50:
            continue
        
        # Skip if it contains numbers or special characters typical of non-name content
        if re.search(r'\d{4,}', line):  # Skip if contains 4+ digit numbers
            continue
        
        # Check if this could be part of a two-line name
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip()
            if next_line and not _is_header_line(next_line) and not re.search(r'@|\+?\d|linkedin\.com|github\.com', next_line):
                # This could be a two-line name
                combined_name = f"{line} {next_line}"
                if len(combined_name.split()) <= 4 and not re.search(r'\d', combined_name):
                    return combined_name
        
        # This looks like a potential name
        return line
    
    return "Unknown"


def extract_contact_info_improved(lines: List[str]) -> Dict[str, Any]:
    """Extract contact information with improved patterns."""
    text = "\n".join(lines)
    
    # Extract emails
    emails = re.findall(r"\b[\w.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    emails = _dedupe_list(emails)
    
    # Extract phone numbers (less aggressive)
    phone_patterns = [
        r"\+?[\d\s\-/()]{7,}",  # International format
        r"\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b",  # US/Canada format
        r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}\b",  # French format
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean phone number but preserve + and spaces
            cleaned = re.sub(r'[^\d\s\+\(\)\-]', '', match)
            if len(cleaned.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 7:
                phones.append(cleaned.strip())
    
    phones = _dedupe_list(phones)
    
    # Extract LinkedIn
    linkedin = ""
    linkedin_match = re.search(r'linkedin\.com/[^\s]+', text, re.IGNORECASE)
    if linkedin_match:
        linkedin = linkedin_match.group(0)
    
    # Extract address (look for postal code patterns)
    address = ""
    address_match = re.search(r'[A-Za-zÀ-ÿ\s]+\d{4,5}\s*[A-Za-zÀ-ÿ\s]*', text)
    if address_match:
        address = address_match.group(0).strip()
    
    return {
        "emails": emails,
        "phones": phones,
        "linkedin": linkedin,
        "address": address
    }


def extract_summary_improved(lines: List[str]) -> List[str]:
    """Extract professional summary with better content preservation."""
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
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
            summary_lines.append(cleaned)
    
    return _dedupe_list(summary_lines)


def extract_skills_improved(lines: List[str]) -> List[str]:
    """Extract skills with improved bullet point handling."""
    skills = []
    
    for line in lines:
        if not line:
            continue
        
        # Check if this is a bullet line
        if _detect_bullet_line(line):
            content = _extract_bullet_content(line)
            if content:
                # Split by common separators
                parts = re.split(r'[,:/;\|\u2013\u2014\-]', content)
                for part in parts:
                    skill = part.strip()
                    if skill and len(skill) >= 2 and _is_meaningful_text(skill):
                        skills.append(skill)
        else:
            # Handle non-bullet lines that might contain skills
            if ':' in line:
                # Extract content after colon
                content = line.split(':', 1)[1].strip()
                if content:
                    parts = re.split(r'[,:/;\|\u2013\u2014\-]', content)
                    for part in parts:
                        skill = part.strip()
                        if skill and len(skill) >= 2 and _is_meaningful_text(skill):
                            skills.append(skill)
    
    return _dedupe_list(skills)


def extract_languages_improved(lines: List[str]) -> List[Dict[str, str]]:
    """Extract language information with improved pattern matching."""
    languages = []
    
    for line in lines:
        if not line:
            continue
        
        # Check if this is a bullet line
        if _detect_bullet_line(line):
            content = _extract_bullet_content(line)
            if content:
                # Look for language: level pattern
                lang_match = re.match(r'^([A-Za-zÀ-ÿ]+)\s*[:\-–]\s*([A-Za-zÀ-ÿ\s]+)$', content)
                if lang_match:
                    language = lang_match.group(1).title()
                    level = lang_match.group(2).strip().title()
                    if language and level:
                        languages.append({"language": language, "level": level})
    
    return languages


def extract_education_improved(lines: List[str]) -> List[Dict[str, Any]]:
    """Extract education information with improved parsing."""
    education_entries = []
    current_entry = None
    
    for line in lines:
        if not line:
            continue
        
        # Check if this is a bullet line
        if _detect_bullet_line(line):
            content = _extract_bullet_content(line)
            if content:
                # Start new entry
                if current_entry:
                    education_entries.append(current_entry)
                
                current_entry = {"details": []}
                
                # Extract dates
                dates = re.findall(r'\b(?:19|20)\d{2}\b', content)
                if dates:
                    if len(dates) >= 2:
                        current_entry["start_year"] = dates[0]
                        current_entry["end_year"] = dates[1]
                    else:
                        current_entry["start_year"] = dates[0]
                
                # Extract degree and institution
                if re.search(r'\b(?:bachelor|licence|ingénieur|ingenieur|cycle|master|phd|doctorat|diplôme|diploma|degree|diplome|bac|baccalauréat|baccalaureat)\b', content, re.IGNORECASE):
                    current_entry["degree"] = content
                elif re.search(r'\b(?:university|université|faculté|faculte|school|lycée|lycee|ecole|institute|institut|academy|académie|academie)\b', content, re.IGNORECASE):
                    current_entry["institution"] = content
                else:
                    current_entry["degree"] = content
        else:
            # Add details to current entry
            if current_entry and _is_meaningful_text(line):
                current_entry["details"].append(line.strip())
    
    # Add final entry
    if current_entry:
        education_entries.append(current_entry)
    
    return education_entries


def extract_experience_improved(lines: List[str]) -> List[Dict[str, Any]]:
    """Extract experience information with improved parsing."""
    experience_entries = []
    current_entry = None
    current_details = []
    
    for line in lines:
        if not line:
            continue
        
        # Check if this is a bullet line
        if _detect_bullet_line(line):
            content = _extract_bullet_content(line)
            if content:
                # Check if this looks like a new entry (contains dates or company info)
                has_date = re.search(r'\b(?:19|20)\d{2}\b', content)
                has_company = re.search(r'\b(?:inc|corp|company|ltd|llc|sarl|eurl|sa|sas)\b', content, re.IGNORECASE)
                
                if has_date or has_company or len(content.split()) <= 8:
                    # Finalize previous entry
                    if current_entry:
                        if current_details:
                            current_entry["details"] = _dedupe_list(current_details)
                        experience_entries.append(current_entry)
                    
                    # Start new entry
                    current_entry = {"title": content}
                    current_details = []
                    
                    # Extract dates
                    dates = re.findall(r'\b(?:19|20)\d{2}\b', content)
                    if dates:
                        if len(dates) >= 2:
                            current_entry["start_year"] = dates[0]
                            current_entry["end_year"] = dates[1]
                        else:
                            current_entry["start_year"] = dates[0]
                else:
                    # This is a detail line
                    if current_entry and _is_meaningful_text(content):
                        current_details.append(content)
        else:
            # Add non-bullet lines as details
            if current_entry and _is_meaningful_text(line):
                current_details.append(line.strip())
    
    # Add final entry
    if current_entry:
        if current_details:
            current_entry["details"] = _dedupe_list(current_details)
        experience_entries.append(current_entry)
    
    return experience_entries


def extract_projects_improved(lines: List[str]) -> List[Dict[str, Any]]:
    """Extract project information."""
    projects = []
    
    for line in lines:
        if not line:
            continue
        
        # Check if this is a bullet line
        if _detect_bullet_line(line):
            content = _extract_bullet_content(line)
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


# ----------------------- Improved section classification -----------------------

def classify_sections_improved(raw_sections: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Classify sections with improved heuristics."""
    classified = {
        "contact": [],
        "professional_summary": [],
        "skills": [],
        "languages": [],
        "education": [],
        "experience": [],
        "projects": [],
    }
    
    # Process each section
    for header, lines in raw_sections.items():
        if not lines:
            continue
        
        header_lower = header.lower()
        
        # Direct mapping based on header content
        if any(keyword in header_lower for keyword in ["contact", "coordonnées", "contacto"]):
            classified["contact"].extend(lines)
        elif any(keyword in header_lower for keyword in ["summary", "resume", "profile", "about", "overview", "introduction", "présentation", "profil", "aperçu"]):
            classified["professional_summary"].extend(lines)
        elif any(keyword in header_lower for keyword in ["skills", "compétences", "competences", "aptitudes", "capacités", "capabilities", "technical"]):
            classified["skills"].extend(lines)
        elif any(keyword in header_lower for keyword in ["languages", "langues", "idiomas", "sprachen", "lingue"]):
            classified["languages"].extend(lines)
        elif any(keyword in header_lower for keyword in ["education", "formation", "études", "academic", "académique", "diplômes", "diplomas"]):
            classified["education"].extend(lines)
        elif any(keyword in header_lower for keyword in ["experience", "work", "employment", "emploi", "travail", "expérience", "carrière", "career", "professional"]):
            classified["experience"].extend(lines)
        elif any(keyword in header_lower for keyword in ["projects", "projets", "proyectos", "projekte", "progetti"]):
            classified["projects"].extend(lines)
        elif any(keyword in header_lower for keyword in ["certifications", "certificaciones", "zertifikate", "certificazioni"]):
            # Add certifications to experience or create new section
            classified["experience"].extend(lines)
        else:
            # Default classification based on content analysis
            if header == "header":  # Top section
                classified["professional_summary"].extend(lines)
            else:
                # Try to infer from content
                text = "\n".join(lines)
                if re.search(r'\b(?:19|20)\d{2}\b', text):
                    if re.search(r'\b(?:bachelor|master|phd|degree|diploma|licence|ingénieur)\b', text, re.IGNORECASE):
                        classified["education"].extend(lines)
                    else:
                        classified["experience"].extend(lines)
                elif re.search(r'[,:/;\|\u2013\u2014\-]', text) and len(lines) <= 3:
                    classified["skills"].extend(lines)
                else:
                    classified["professional_summary"].extend(lines)
    
    return classified


# ----------------------- Main assembly function -----------------------

def assemble_cv_data_improved(sections: Dict[str, List[str]], text: str) -> Dict[str, Any]:
    """Assemble the final CV data structure."""
    # Extract name
    name = extract_name_improved(text)
    
    # Extract contact info from header section (regardless of classification)
    header_contact = extract_contact_info_improved(sections.get("header", []))
    
    # Build the data structure
    data = {
        "name": name,
        "contact_info": header_contact,  # Always extract from header
        "professional_summary": extract_summary_improved(sections.get("professional_summary", [])),
        "skills": extract_skills_improved(sections.get("skills", [])),
        "languages": extract_languages_improved(sections.get("languages", [])),
        "education": extract_education_improved(sections.get("education", [])),
        "experience": extract_experience_improved(sections.get("experience", [])),
        "projects": extract_projects_improved(sections.get("projects", [])),
    }
    
    # Clean empty fields
    return {k: v for k, v in data.items() if v and (not isinstance(v, list) or len(v) > 0) and (not isinstance(v, dict) or any(v.values()))}


# ----------------------- Main CV Extractor Class -----------------------

class CVExtractor:
    """Improved CV extractor with better section detection and parsing."""
    
    def extract_cv_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured CV data with improved parsing."""
        text = load_text(file_path)
        
        # Debug dump
        with open("debug_extracted_text.txt", "w", encoding="utf-8") as dbg:
            dbg.write(text)
        
        # Improved section detection and classification
        raw_sections = split_sections_improved(text)
        classified_sections = classify_sections_improved(raw_sections)
        
        # Assemble final data
        return assemble_cv_data_improved(classified_sections, text)


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


