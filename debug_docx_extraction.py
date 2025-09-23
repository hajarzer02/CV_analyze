#!/usr/bin/env python3
"""
Debug script to test DOCX extraction and identify why John Doe is returned.
"""

import os
import sys
from docx import Document

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_docx_extraction():
    """Test DOCX extraction to find the issue."""
    print("🔍 Testing DOCX Extraction")
    print("=" * 50)
    
    # Look for DOCX files in the CV files directory
    cv_files_dir = os.path.join(os.path.dirname(__file__), 'backend', 'cv_files')
    
    if not os.path.exists(cv_files_dir):
        print(f"❌ CV files directory not found: {cv_files_dir}")
        return
    
    docx_files = [f for f in os.listdir(cv_files_dir) if f.lower().endswith('.docx')]
    
    if not docx_files:
        print("❌ No DOCX files found in cv_files directory")
        print("Available files:")
        for f in os.listdir(cv_files_dir):
            print(f"  - {f}")
        return
    
    print(f"Found {len(docx_files)} DOCX files:")
    for f in docx_files:
        print(f"  - {f}")
    
    # Test each DOCX file
    for docx_file in docx_files:
        print(f"\n📄 Testing: {docx_file}")
        print("-" * 30)
        
        file_path = os.path.join(cv_files_dir, docx_file)
        
        try:
            # Test direct DOCX extraction
            print("1. Direct DOCX extraction:")
            doc = Document(file_path)
            lines = []
            for p in doc.paragraphs:
                t = (p.text or "").strip()
                if t:
                    lines.append(t)
            
            raw_text = "\n".join(lines)
            print(f"   Raw text length: {len(raw_text)} characters")
            print(f"   First 200 characters:")
            print(f"   {raw_text[:200]}...")
            
            # Check if "John Doe" appears in the raw text
            if "John Doe" in raw_text:
                print("   ⚠️  'John Doe' found in raw text!")
            else:
                print("   ✅ No 'John Doe' in raw text")
            
            # Test with CV extractor
            print("\n2. CV Extractor test:")
            from cv_extractor_cli import CVExtractor
            extractor = CVExtractor()
            
            extracted_data = extractor.extract_cv_data(file_path)
            print(f"   Contact info: {extracted_data.get('contact_info', {})}")
            
            # Check if John Doe appears in extracted data
            contact_info = extracted_data.get('contact_info', {})
            if 'name' in contact_info and 'John Doe' in str(contact_info['name']):
                print("   ⚠️  'John Doe' found in extracted contact info!")
            else:
                print("   ✅ No 'John Doe' in extracted contact info")
            
            # Test with LLaMA service
            print("\n3. LLaMA Service test:")
            sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-service'))
            from llama_service import LlamaService
            
            llama_service = LlamaService()
            structured_data = llama_service.structure_cv_text(raw_text)
            
            print(f"   Structured contact info: {structured_data.get('contact_info', {})}")
            
            # Check if John Doe appears in structured data
            structured_contact = structured_data.get('contact_info', {})
            if 'name' in structured_contact and 'John Doe' in str(structured_contact['name']):
                print("   ⚠️  'John Doe' found in structured data!")
            else:
                print("   ✅ No 'John Doe' in structured data")
                
        except Exception as e:
            print(f"   ❌ Error processing {docx_file}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_docx_extraction()


