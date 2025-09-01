import os
import fitz
from docx import Document
import re

class CVExtractor:
    
    def extract_text(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        elif file_ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            full_text = []
            
            for page in doc:
                # Get text blocks with their coordinates
                blocks = page.get_text("blocks")
                
                # Sort blocks by vertical position (top to bottom)
                blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by y, then x
                
                for block in blocks:
                    text = block[4].strip()
                    if text:
                        # Clean up any weird spacing or formatting
                        text = re.sub(r'\s+', ' ', text)
                        # Don't add if it's just a single character or number
                        if len(text) > 1 or text.isalpha():
                            full_text.append(text)
            
            doc.close()
            
            # Join with newlines for better section separation
            return '\n'.join(full_text)
            
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            paragraphs = []
            
            for p in doc.paragraphs:
                text = p.text.strip()
                if text:
                    # Clean up any weird spacing or formatting
                    text = re.sub(r'\s+', ' ', text)
                    paragraphs.append(text)
            
            return '\n'.join(paragraphs)
            
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                for line in f:
                    text = line.strip()
                    if text:
                        # Clean up any weird spacing or formatting
                        text = re.sub(r'\s+', ' ', text)
                        lines.append(text)
                return '\n'.join(lines)
        except Exception as e:
            raise Exception(f"Error extracting TXT: {str(e)}")