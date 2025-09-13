#!/usr/bin/env python3
"""
Dynamic address extraction for English and French CVs.
Uses pattern recognition and contextual clues to identify addresses without hardcoded dictionaries.
"""

import re
from typing import List

def extract_address_dynamic(text: str) -> str:
    """
    Dynamic address extraction for English and French CVs.
    Uses pattern recognition and contextual clues to identify addresses without hardcoded dictionaries.
    """
    
    def clean_and_normalize(text: str) -> str:
        """Clean text while preserving structure."""
        # Remove excessive whitespace but keep line breaks
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def has_address_indicators(line: str) -> bool:
        """Check if line contains address-related keywords in English/French."""
        address_keywords = [
            # English
            r'\baddress\b', r'\bhome\b', r'\blocation\b', r'\bresidence\b', r'\bresidential\b',
            r'\blives?\s+(?:at|in)\b', r'\bresiding\s+(?:at|in)\b', r'\bdomiciled\s+(?:at|in)\b',
            # French
            r'\badresse\b', r'\bdomicile\b', r'\brésidence\b', r'\blieu\s+de\s+résidence\b',
            r'\bdemeurant\s+(?:à|au|aux)\b', r'\bhabite\s+(?:à|au|aux)\b',
        ]
        
        line_lower = line.lower()
        return any(re.search(keyword, line_lower) for keyword in address_keywords)
    
    def has_postal_code(text: str) -> bool:
        """Check if text contains postal code patterns (various countries)."""
        postal_patterns = [
            r'\b\d{5}(?:-\d{4})?\b',      # US: 12345 or 12345-6789
            r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b',  # Canada: K1A 0A6
            r'\b\d{5}\b',                  # France/Morocco: 75001
            r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b',  # UK: SW1A 1AA
            r'\b\d{4}\s?[A-Z]{2}\b',       # Netherlands: 1012 AB
            r'\b\d{5}\s+\w+\b',            # Germany: 10115 Berlin
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in postal_patterns)
    
    def has_address_structure_words(text: str) -> bool:
        """Check for words that commonly appear in addresses (English/French)."""
        structure_patterns = [
            # Numbers + street indicators
            r'\b\d+\s*[,.]?\s*\w+',  # Street numbers
            # English street types
            r'\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|boulevard|blvd\.?|lane|ln\.?|drive|dr\.?|court|ct\.?|place|pl\.?|way|circle|square|park|plaza)\b',
            # French street types
            r'\b(?:rue|avenue|boulevard|place|impasse|allée|chemin|route|quai|cours|passage|villa|square|esplanade|promenade)\b',
            # Building/housing types
            r'\b(?:apartment|apt\.?|suite|unit|floor|building|house|residence|complex)\b',
            r'\b(?:appartement|appt\.?|étage|bâtiment|maison|résidence|immeuble|villa)\b',
            # Area/district indicators
            r'\b(?:district|neighborhood|area|zone|sector|quarter|region)\b',
            r'\b(?:quartier|secteur|zone|région|arrondissement)\b',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in structure_patterns)
    
    def has_geographic_indicators(text: str) -> bool:
        """Check for geographic/location indicators."""
        geo_patterns = [
            r'\b\w+\s*,\s*\w+',  # City, State/Country pattern
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,',  # Proper noun followed by comma
            r'\b\w+\s+\d{4,5}\b',   # Location + postal code
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\d{4,5}\b',  # Capitalized location + postal
            # Country indicators (common ones)
            r'\b(?:france|canada|usa|united\s+states|uk|united\s+kingdom|germany|spain|italy|morocco|maroc)\b',
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in geo_patterns)
    
    def has_state_province_pattern(text: str) -> bool:
        """Check for state/province abbreviations or full names."""
        # Common patterns for states/provinces
        state_patterns = [
            r'\b[A-Z]{2}\s+\d{5}\b',  # US state abbreviation + ZIP
            r'\b(?:ON|BC|AB|QC|NS|NB|MB|SK|PE|NL|NT|YT|NU)\s+[A-Z]\d[A-Z]\s?\d[A-Z]\d\b',  # Canadian provinces
            r'\b\d{5}\s+[A-Z][a-z]+\b',  # Postal code + city/state
        ]
        
        return any(re.search(pattern, text) for pattern in state_patterns)
    
    def score_address_candidate(candidate: str) -> int:
        """Score a potential address based on various criteria."""
        score = 0
        candidate_lower = candidate.lower()
        candidate_clean = candidate.strip()
        
        # Length scoring (prefer moderate length)
        length = len(candidate_clean)
        if 20 <= length <= 200:
            score += 3
        elif 10 <= length <= 300:
            score += 1
        elif length > 300:
            score -= 2  # Too long, probably not just an address
        
        # Has postal code (strong indicator)
        if has_postal_code(candidate):
            score += 5
        
        # Has address structure words
        if has_address_structure_words(candidate):
            score += 4
        
        # Has geographic indicators
        if has_geographic_indicators(candidate):
            score += 3
        
        # Has state/province pattern
        if has_state_province_pattern(candidate):
            score += 2
        
        # Contains numbers (street numbers, postal codes)
        number_count = len(re.findall(r'\d+', candidate))
        if number_count >= 1:
            score += min(number_count, 3)  # Cap at 3 points
        
        # Contains comma (often separates address components)
        comma_count = candidate.count(',')
        if 1 <= comma_count <= 3:
            score += comma_count
        elif comma_count > 3:
            score -= 1  # Too many commas might be a list
        
        # Proper capitalization (addresses often have proper nouns)
        capital_words = len(re.findall(r'\b[A-Z][a-z]+', candidate))
        if capital_words >= 2:
            score += min(capital_words // 2, 3)
        
        # Avoid obviously non-address content
        non_address_indicators = [
            r'\b(?:email|telephone|phone|mobile|cell|fax|tel|gsm|contact)\b',
            r'\b(?:experience|education|formation|compétences|skills|work|employment|job)\b',
            r'\b(?:born|né|date|age|single|married|célibataire|marié|divorced)\b',
            r'\b(?:objective|summary|profile|profil|résumé|curriculum)\b',
            r'@',  # Email addresses
            r'(?:\+|00)\d{10,}',  # Long phone numbers
            r'\b(?:https?://|www\.)',  # URLs
            r'\b(?:mr\.?|mrs\.?|ms\.?|dr\.?|prof\.?|m\.?|mme\.?|mlle\.?)\s+\w+',  # Titles + names
        ]
        
        penalty_count = 0
        for pattern in non_address_indicators:
            if re.search(pattern, candidate_lower):
                penalty_count += 1
        
        score -= penalty_count * 3  # Heavy penalty for non-address indicators
        
        # Bonus for complete-looking addresses
        if (has_postal_code(candidate) and 
            has_address_structure_words(candidate) and 
            has_geographic_indicators(candidate)):
            score += 3
        
        return max(0, score)  # Don't go below 0
    
    def extract_candidates_from_lines(text: str) -> List[str]:
        """Extract address candidates from text lines."""
        candidates = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Method 1: Lines with address indicators
            if has_address_indicators(line):
                # Extract everything after the indicator
                patterns = [
                    r'(?:address|adresse|location|domicile|résidence)\s*:?\s*(.+)',
                    r'(?:lieu\s+de\s+résidence|home\s+address|residential\s+address)\s*:?\s*(.+)',
                    r'(?:lives?\s+(?:at|in)|residing\s+(?:at|in)|domiciled\s+(?:at|in))\s*(.+)',
                    r'(?:demeurant\s+(?:à|au|aux)|habite\s+(?:à|au|aux))\s*(.+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        extracted = match.group(1).strip()
                        if extracted:
                            candidates.append(extracted)
                        break
                else:
                    # If no specific pattern matches, consider the whole line
                    candidates.append(line)
            
            # Method 2: Lines that structurally look like addresses
            elif (has_address_structure_words(line) or 
                  has_postal_code(line) or 
                  has_geographic_indicators(line) or
                  has_state_province_pattern(line)):
                candidates.append(line)
            
            # Method 3: Multi-line addresses (combine with next line if it looks related)
            if (i < len(lines) - 1 and 
                (has_address_structure_words(line) or re.search(r'\b\d+\b', line)) and
                not has_postal_code(line)):
                next_line = lines[i + 1].strip()
                if (next_line and 
                    (has_postal_code(next_line) or 
                     has_geographic_indicators(next_line) or
                     has_state_province_pattern(next_line))):
                    combined = f"{line}, {next_line}".strip()
                    candidates.append(combined)
        
        return candidates
    
    def extract_candidates_from_patterns(text: str) -> List[str]:
        """Extract candidates using regex patterns."""
        candidates = []
        
        # Pattern 1: Text with postal codes and surrounding context
        postal_patterns = [
            r'([^\n\r]{15,}?\b\d{5}(?:-\d{4})?\b[^\n\r]{0,50})',  # US ZIP
            r'([^\n\r]{15,}?\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b[^\n\r]{0,30})',  # Canadian postal
            r'([^\n\r]{15,}?\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b[^\n\r]{0,30})',  # UK postal
            r'([^\n\r]{15,}?\b\d{5}\b[^\n\r]{0,50})',  # General 5-digit postal
        ]
        
        for pattern in postal_patterns:
            matches = re.findall(pattern, text)
            candidates.extend(matches)
        
        # Pattern 2: Structured address patterns
        structure_patterns = [
            r'([^\n\r]*(?:street|st\.?|road|rd\.?|avenue|ave\.?|boulevard|blvd\.?|rue|avenue|boulevard)[^\n\r]{5,})',
            r'([^\n\r]*\b\d+[^\n\r]*(?:street|st\.?|road|rd\.?|avenue|ave\.?|rue|avenue)[^\n\r]{5,})',
            r'(\b\d+[^\n\r,]*,[^\n\r]*\b[A-Z][a-z]+[^\n\r]{5,})',  # Number, comma, capitalized location
        ]
        
        for pattern in structure_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            candidates.extend(matches)
        
        # Pattern 3: Geographic patterns with proper capitalization
        geo_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*[^\n\r]*\b\d{4,5}[^\n\r]*)',  # City + postal
            r'([^\n\r]*[A-Z][a-z]+\s*,\s*[A-Z][a-z]+[^\n\r]*\b\d{4,5}[^\n\r]*)',  # City, State/Country + postal
            r'(\b\d+[^\n\r]*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*[^\n\r]*)',  # Street number + capitalized words
        ]
        
        for pattern in geo_patterns:
            matches = re.findall(pattern, text)
            candidates.extend(matches)
        
        return candidates
    
    # Main extraction logic
    text = clean_and_normalize(text)
    all_candidates = []
    
    # Collect candidates from different methods
    all_candidates.extend(extract_candidates_from_lines(text))
    all_candidates.extend(extract_candidates_from_patterns(text))
    
    if not all_candidates:
        return ""
    
    # Remove duplicates and very similar candidates
    unique_candidates = []
    for candidate in all_candidates:
        candidate = candidate.strip()
        if not candidate or len(candidate) < 10:
            continue
            
        # Check if this candidate is too similar to existing ones
        is_duplicate = False
        candidate_words = set(candidate.lower().split())
        
        for existing in unique_candidates:
            existing_words = set(existing.lower().split())
            # Calculate word overlap
            overlap = len(candidate_words & existing_words)
            similarity = overlap / max(len(candidate_words), len(existing_words))
            
            if similarity > 0.7:  # 70% similarity threshold
                is_duplicate = True
                # Keep the longer/more complete version
                if len(candidate) > len(existing):
                    unique_candidates.remove(existing)
                    unique_candidates.append(candidate)
                break
        
        if not is_duplicate:
            unique_candidates.append(candidate)
    
    # Score and select the best candidate
    scored_candidates = [(candidate, score_address_candidate(candidate)) 
                        for candidate in unique_candidates]
    
    # Filter out candidates with very low scores
    good_candidates = [c for c in scored_candidates if c[1] > 2]
    
    if not good_candidates:
        # If no good candidates, try with lower threshold
        good_candidates = [c for c in scored_candidates if c[1] > 0]
    
    if not good_candidates:
        return ""
    
    # Return the highest-scoring candidate
    best_candidate = max(good_candidates, key=lambda x: x[1])
    return best_candidate[0].strip()

# Simplified wrapper for easy integration
def extract_contact_address(text: str) -> str:
    """Extract address from CV text - simplified interface."""
    return extract_address_dynamic(text)

# Test function
def test_address_extraction():
    """Test the address extraction with sample CV text."""
    
    test_cases = [
        # English CVs
        """
        John Smith
        Email: john.smith@email.com
        Address: 123 Main Street, Apt 4B, New York, NY 10001
        Phone: (555) 123-4567
        """,
        
        """
        Contact Information:
        Phone: +1-555-0123
        Home: 456 Oak Avenue, Springfield, IL 62701
        Email: contact@example.com
        """,
        
        """
        Personal Details
        Name: Sarah Johnson
        Location: 789 Elm Street, Unit 12, Toronto, ON M5V 3A1
        Mobile: 416-555-0198
        """,
        
        # French CVs
        """
        Marie Dupont
        Adresse: 25 Rue de la République, 75011 Paris, France
        Téléphone: 01 42 34 56 78
        Email: marie.dupont@email.fr
        """,
        
        """
        Informations personnelles:
        Domicile: 42 Boulevard Saint-Michel, Appartement 5, Lyon 69002
        Mobile: 06 12 34 56 78
        """,
        
        """
        CV - Pierre Martin
        Lieu de résidence: 18 Avenue des Champs-Élysées, Paris 75008, France
        Contact: pierre.martin@gmail.com
        """,
        
        # Mixed/Complex cases
        """
        Experience: Software Developer at Tech Corp (2020-Present)
        Education: Bachelor of Computer Science
        Address: 321 Tech Drive, Suite 100, San Francisco, CA 94105, USA
        Skills: Python, JavaScript, React
        """,
    ]
    
    print("🏠 Testing Dynamic Address Extraction (English & French)")
    print("=" * 60)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 20)
        print(f"Input text sample: {test_text.strip()[:100]}...")
        
        extracted_address = extract_contact_address(test_text)
        print(f"Extracted Address: '{extracted_address}'")
        
        if extracted_address:
            print("✓ Address found")
        else:
            print("✗ No address found")

if __name__ == "__main__":
    test_address_extraction()
