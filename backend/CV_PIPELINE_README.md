# Two-Step CV Processing Pipeline

This document describes the implementation of a fault-tolerant, two-step CV processing pipeline that combines AI-powered structuring with traditional parsing as a fallback.

## Overview

The pipeline implements the following workflow:

1. **Raw Text Extraction**: Extract raw text from uploaded CVs and save to `data.txt`
2. **AI Structuring**: Attempt to structure the CV using LLaMA models
3. **Validation**: Validate AI output against strict heuristics
4. **Fallback**: If AI fails or validation fails, use CLI parser as fallback
5. **Merging**: If AI output is partial, merge with CLI parser for missing sections
6. **Storage**: Preserve all artifacts and metadata

## Architecture

### Core Components

- **`cv_validation.py`**: Validation heuristics for AI output
- **`cv_processor.py`**: Main processing pipeline orchestrator
- **`cv_extractor_cli.py`**: Traditional CLI parser (existing)
- **`llama_service.py`**: AI service for structuring (existing)

### Database Schema Updates

New fields added to `Candidate` table:
- `used_ai`: Whether AI was used for structuring
- `used_fallback`: Whether CLI fallback was used
- `processing_source`: Source of final data ("ai", "fallback-cli", "ai+cli", "error")
- `validation_passed`: Whether AI output passed validation
- `validation_reason`: Reason for validation failure/success
- `processing_logs`: JSON array of processing logs
- `raw_text_path`: Path to saved raw text
- `ai_output_path`: Path to AI output JSON
- `fallback_output_path`: Path to CLI fallback JSON

## Validation Heuristics

The validation system checks:

1. **Name Presence**: Name must be present in contact_info or professional_summary
2. **Content Length**: Structured content must be > 200 characters
3. **Meaningful Content**: Must contain substantial, non-empty data
4. **Required Sections**: At least one of skills, experience, or education must have content
5. **No Dummy Content**: Must not contain placeholder/dummy text

### Dummy Content Detection

Detects common placeholder patterns:
- "N/A", "No information", "Sample data"
- "John Doe", "Jane Doe" (common placeholder names)
- Very short responses (< 5 characters)
- Repetitive patterns
- Empty JSON structures ("{}", "[]", "null")

## Processing Flow

### Step 1: Raw Text Extraction
```python
raw_text = cv_extractor.extract_raw_text(file_path)
# Saves to data.txt in same directory as CV
```

### Step 2: AI Structuring
```python
ai_output = llama_service.structure_cv_text(raw_text)
is_valid, reason, details = validate_cv_structure(ai_output, raw_text)
```

### Step 3: Fallback Decision
- If AI succeeds and validation passes → Use AI output
- If AI fails or validation fails → Use CLI parser
- If AI output is partial → Merge with CLI parser

### Step 4: Partial Output Merging
```python
is_partial, missing_sections = detect_partial_cv(ai_output)
if is_partial:
    final_data = merge_partial_outputs(ai_output, cli_output, missing_sections)
```

## API Response Changes

### Upload Response
```json
{
  "candidate_id": 123,
  "extracted_data": {...},
  "message": "CV uploaded and processed successfully",
  "source": "ai",  // "ai", "fallback-cli", "ai+cli", "error"
  "used_ai": true,
  "used_fallback": false,
  "validation_passed": true,
  "validation_reason": "AI output passed validation"
}
```

### Candidate Response
```json
{
  "id": 123,
  "name": "John Doe",
  "extracted_data": {...},
  "used_ai": true,
  "used_fallback": false,
  "processing_source": "ai",
  "validation_passed": true,
  "validation_reason": "AI output passed validation",
  "processing_logs": ["Raw text extracted: 1500 characters", ...],
  "raw_text_path": "/path/to/data.txt",
  "ai_output_path": "/path/to/ai_output.json",
  "fallback_output_path": null
}
```

## Testing

### Test Scenarios

1. **Well-structured CV with AI success** (Test A)
   - AI produces valid, complete output
   - Validation passes
   - Source: "ai"

2. **Messy CV where AI fails** (Test B)
   - AI produces dummy/placeholder output
   - Validation fails
   - Fallback to CLI parser
   - Source: "fallback-cli"

3. **Partial AI output requiring merge** (Test C)
   - AI produces valid but incomplete output
   - Missing sections detected
   - Merge with CLI parser
   - Source: "ai+cli"

### Running Tests

```bash
cd backend
python run_tests.py
```

## Usage Examples

### Basic Processing
```python
from cv_processor import process_cv_file

# Process a CV file
result = process_cv_file("path/to/cv.pdf")

print(f"Source: {result.source}")
print(f"Used AI: {result.used_ai}")
print(f"Used Fallback: {result.used_fallback}")
print(f"Validation Passed: {result.validation_passed}")
```

### Validation Only
```python
from cv_validation import validate_cv_structure

is_valid, reason, details = validate_cv_structure(ai_data, raw_text)
if not is_valid:
    print(f"Validation failed: {reason}")
    print(f"Score: {details['overall_score']:.2f}")
```

### Partial Detection
```python
from cv_validation import detect_partial_cv

is_partial, missing = detect_partial_cv(ai_data)
if is_partial:
    print(f"Missing sections: {missing}")
```

## Error Handling

The pipeline is designed to be fault-tolerant:

1. **AI Service Unavailable**: Falls back to CLI parser
2. **Invalid AI Output**: Falls back to CLI parser
3. **Partial AI Output**: Merges with CLI parser
4. **File Processing Errors**: Returns error result with details
5. **Database Errors**: Preserves processing logs for debugging

## Logging

All processing steps are logged:
- Raw text extraction
- AI structuring attempts
- Validation results
- Fallback decisions
- Merge operations
- Error conditions

Logs are stored in the database and returned in API responses for debugging.

## Performance Considerations

- AI processing is attempted first (faster for good CVs)
- CLI parser is only used when necessary
- Partial merging minimizes redundant processing
- All artifacts are preserved for analysis
- Database queries include new fields for filtering

## Future Enhancements

1. **Confidence Scoring**: Add confidence scores to AI outputs
2. **Adaptive Validation**: Adjust validation thresholds based on CV quality
3. **Hybrid Processing**: Use both AI and CLI, then choose best result
4. **Caching**: Cache AI outputs for similar CVs
5. **Metrics**: Track success rates and performance metrics



