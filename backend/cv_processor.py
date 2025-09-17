#!/usr/bin/env python3

import os
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

import sys
import os

# Add ai-service to path for llama_service
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-service'))

from cv_extractor_cli import CVExtractor
from cv_validation import validate_cv_structure, detect_partial_cv, CVValidator
from llama_service import LlamaService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CVProcessingResult:
    """Result of CV processing with metadata."""
    
    def __init__(self, 
                 structured_data: Dict[str, Any],
                 source: str,
                 used_ai: bool,
                 used_fallback: bool,
                 validation_passed: bool,
                 validation_reason: str,
                 processing_logs: List[str],
                 raw_text: str,
                 ai_output: Optional[Dict[str, Any]] = None,
                 fallback_output: Optional[Dict[str, Any]] = None):
        self.structured_data = structured_data
        self.source = source
        self.used_ai = used_ai
        self.used_fallback = used_fallback
        self.validation_passed = validation_passed
        self.validation_reason = validation_reason
        self.processing_logs = processing_logs
        self.raw_text = raw_text
        self.ai_output = ai_output
        self.fallback_output = fallback_output


class CVProcessor:
    """Two-step, fault-tolerant CV processing pipeline."""
    
    def __init__(self):
        self.cv_extractor = CVExtractor()
        self.llama_service = LlamaService()
        self.validator = CVValidator()
    
    def process_cv(self, file_path: str) -> CVProcessingResult:
        """
        Process CV using two-step pipeline:
        1. Extract raw text and save to data.txt
        2. Try AI structuring, validate, fallback to CLI if needed
        3. Merge partial outputs if necessary
        """
        processing_logs = []
        
        try:
            # Step 1: Extract raw text and save to data.txt
            logger.info(f"Step 1: Extracting raw text from {file_path}")
            raw_text = self.cv_extractor.extract_raw_text(file_path)
            processing_logs.append(f"Raw text extracted: {len(raw_text)} characters")
            
            # Step 2: Try AI structuring
            logger.info("Step 2: Attempting AI structuring")
            ai_output = None
            ai_success = False
            validation_passed = False
            validation_reason = ""
            
            try:
                ai_output = self.llama_service.structure_cv_text(raw_text)
                processing_logs.append(f"AI structuring completed: {len(str(ai_output))} characters")
                
                # Validate AI output
                validation_passed, validation_reason, validation_details = validate_cv_structure(ai_output, raw_text)
                processing_logs.append(f"AI validation: {validation_reason}")
                
                if validation_passed:
                    ai_success = True
                    logger.info("AI structuring successful and validated")
                else:
                    logger.warning(f"AI output failed validation: {validation_reason}")
                    
            except Exception as e:
                processing_logs.append(f"AI structuring failed: {str(e)}")
                logger.error(f"AI structuring error: {e}")
            
            # Step 3: Determine final approach
            if ai_success:
                # AI succeeded - use AI output
                final_data = ai_output
                source = "ai"
                used_ai = True
                used_fallback = False
                
                # Check for partial output and merge if needed
                is_partial, missing_sections = detect_partial_cv(ai_output)
                if is_partial:
                    logger.info(f"AI output is partial, missing sections: {missing_sections}")
                    processing_logs.append(f"Partial AI output detected, merging with CLI parser")
                    
                    # Get CLI fallback for missing sections
                    cli_output = self.cv_extractor.extract_cv_data(file_path)
                    final_data = self._merge_partial_outputs(ai_output, cli_output, missing_sections)
                    source = "ai+cli"
                    used_fallback = True
                    processing_logs.append("Merged partial AI output with CLI parser")
                
            else:
                # AI failed - use CLI fallback
                logger.info("Falling back to CLI parser")
                processing_logs.append("AI failed, using CLI parser fallback")
                
                cli_output = self.cv_extractor.extract_cv_data(file_path)
                final_data = cli_output
                source = "fallback-cli"
                used_ai = False
                used_fallback = True
                validation_passed = True  # Assume CLI output is valid
                validation_reason = "CLI parser fallback used"
            
            # Step 4: Preserve all data and create result
            result = CVProcessingResult(
                structured_data=final_data,
                source=source,
                used_ai=used_ai,
                used_fallback=used_fallback,
                validation_passed=validation_passed,
                validation_reason=validation_reason,
                processing_logs=processing_logs,
                raw_text=raw_text,
                ai_output=ai_output,
                fallback_output=cli_output if not ai_success else None
            )
            
            # Log final result
            logger.info(f"CV processing completed - Source: {source}, AI: {used_ai}, Fallback: {used_fallback}")
            processing_logs.append(f"Processing completed - Source: {source}")
            
            return result
            
        except Exception as e:
            logger.error(f"CV processing failed: {e}")
            processing_logs.append(f"Processing failed: {str(e)}")
            
            # Return error result
            return CVProcessingResult(
                structured_data={},
                source="error",
                used_ai=False,
                used_fallback=False,
                validation_passed=False,
                validation_reason=f"Processing error: {str(e)}",
                processing_logs=processing_logs,
                raw_text=""
            )
    
    def _merge_partial_outputs(self, ai_data: Dict[str, Any], cli_data: Dict[str, Any], missing_sections: List[str]) -> Dict[str, Any]:
        """
        Merge partial AI output with CLI parser output.
        Prefer AI fields but fill missing sections from CLI.
        """
        merged_data = ai_data.copy()
        
        for section in missing_sections:
            if section in cli_data and cli_data[section]:
                logger.info(f"Filling missing section '{section}' from CLI parser")
                merged_data[section] = cli_data[section]
        
        # Special handling for contact_info - merge fields
        if "contact_info" in missing_sections and "contact_info" in cli_data:
            ai_contact = ai_data.get("contact_info", {})
            cli_contact = cli_data.get("contact_info", {})
            
            # Merge contact info fields
            merged_contact = ai_contact.copy()
            for field in ["emails", "phones", "linkedin", "address", "name"]:
                if field not in merged_contact or not merged_contact[field]:
                    if field in cli_contact and cli_contact[field]:
                        merged_contact[field] = cli_contact[field]
            
            merged_data["contact_info"] = merged_contact
        
        return merged_data
    
    def save_processing_artifacts(self, result: CVProcessingResult, base_path: str) -> Dict[str, str]:
        """
        Save all processing artifacts (raw text, AI output, fallback output).
        
        Returns:
            Dict with paths to saved files
        """
        artifacts = {}
        
        try:
            # Save raw text (already saved by extract_raw_text)
            data_txt_path = os.path.join(os.path.dirname(base_path), "data.txt")
            if os.path.exists(data_txt_path):
                artifacts["raw_text"] = data_txt_path
            
            # Save AI output if available
            if result.ai_output:
                ai_output_path = base_path.replace(".pdf", "_ai_output.json").replace(".docx", "_ai_output.json").replace(".txt", "_ai_output.json")
                with open(ai_output_path, "w", encoding="utf-8") as f:
                    json.dump(result.ai_output, f, ensure_ascii=False, indent=2)
                artifacts["ai_output"] = ai_output_path
            
            # Save fallback output if available
            if result.fallback_output:
                fallback_output_path = base_path.replace(".pdf", "_fallback_output.json").replace(".docx", "_fallback_output.json").replace(".txt", "_fallback_output.json")
                with open(fallback_output_path, "w", encoding="utf-8") as f:
                    json.dump(result.fallback_output, f, ensure_ascii=False, indent=2)
                artifacts["fallback_output"] = fallback_output_path
            
            # Save processing logs
            logs_path = base_path.replace(".pdf", "_processing_logs.json").replace(".docx", "_processing_logs.json").replace(".txt", "_processing_logs.json")
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "source": result.source,
                "used_ai": result.used_ai,
                "used_fallback": result.used_fallback,
                "validation_passed": result.validation_passed,
                "validation_reason": result.validation_reason,
                "logs": result.processing_logs
            }
            with open(logs_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            artifacts["processing_logs"] = logs_path
            
        except Exception as e:
            logger.error(f"Error saving processing artifacts: {e}")
        
        return artifacts


def process_cv_file(file_path: str) -> CVProcessingResult:
    """
    Convenience function to process a CV file.
    
    Args:
        file_path: Path to the CV file
        
    Returns:
        CVProcessingResult with all processing metadata
    """
    processor = CVProcessor()
    return processor.process_cv(file_path)
