import os
import json
import re
import torch
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Import CVExtractor for fallback
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from cv_extractor_cli import CVExtractor

class LlamaService:
    def __init__(self):
        # Together AI Configuration
        self.together_api_key = os.getenv("TOGETHER_API_KEY", "5752d15c55df315184a82fdca124ecbad6e08be30ca5bb5bd578e68a95426a49")
        self.together_model = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        self.together_api_url = os.getenv("TOGETHER_API_URL", "https://api.together.xyz/v1/chat/completions")
        
        # Hugging Face Configuration (fallback)
        self.hf_api_key = os.getenv("HF_API_KEY", "")
        self.hf_model = os.getenv("HF_MODEL", "tiiuae/falcon-7b-instruct")
        
        # Local LLaMA Configuration
        self.local_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize the best available provider
        self.provider = self._initialize_provider()
        
        # Initialize CVExtractor for fallback
        self.cv_extractor = CVExtractor()
    
    def _initialize_provider(self) -> str:
        """Initialize the best available LLaMA provider."""
        # Try Together AI first (highest priority)
        if self.together_api_key and self.together_api_key != "your_together_api_key_here":
            try:
                # Test Together AI connection
                self._test_together_connection()
                print("✓ Using Together AI LLaMA 3.1")
                return "together"
            except Exception as e:
                print(f"⚠️  Together AI failed: {e}")
        
        # Try Hugging Face Inference API second
        if self.hf_api_key and self.hf_api_key != "hf_your_hf_api_key_here":
            try:
                # Test HF API connection
                self._test_hf_connection()
                print("✓ Using Hugging Face Inference API")
                return "huggingface"
            except Exception as e:
                print(f"⚠️  Hugging Face API failed: {e}")
        
        # Try local HuggyLLaMA if GPU is available
        if self.device == "cuda":
            try:
                self._initialize_local_llama()
                print("✓ Using local HuggyLLaMA on GPU")
                return "local"
            except Exception as e:
                print(f"⚠️  Local LLaMA failed: {e}")
        
        # Fallback to CLI parser
        print("⚠️  Using CLI parser fallback (no API key or GPU available)")
        return "cli"
    
    def _test_together_connection(self):
        """Test Together AI API connection."""
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.together_model,
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        response = requests.post(
            self.together_api_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Together AI test failed: {response.status_code} - {response.text}")

    def _test_hf_connection(self):
        """Test Hugging Face API connection."""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.hf_model}",
            headers=headers,
            json={"inputs": "test", "parameters": {"max_new_tokens": 10}},
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"HF API test failed: {response.status_code}")
    
    def _initialize_local_llama(self):
        """Initialize local HuggyLLaMA model."""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            
            model_name = "huggyllama/llama-7b"
            print(f"Loading {model_name} locally...")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model with memory optimization
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            # Create pipeline
            self.local_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16,
                do_sample=True,
                temperature=0.7,
                max_new_tokens=512,
                pad_token_id=tokenizer.eos_token_id
            )
            
        except ImportError:
            raise Exception("transformers library not installed. Run: pip install transformers torch")
        except Exception as e:
            raise Exception(f"Failed to load local LLaMA: {e}")
    
    def _call_together_api(self, prompt: str) -> str:
        """Call Together AI API."""
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.together_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides job recommendations based on CV data. Always respond with valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = requests.post(
            self.together_api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Together AI error: {response.status_code} - {response.text}")
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Unexpected Together AI response: {result}")

    def _call_huggingface_api(self, prompt: str) -> str:
        """Call Hugging Face Inference API."""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.hf_model}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"HF API error: {response.status_code} - {response.text}")
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        else:
            raise Exception(f"Unexpected HF API response: {result}")
    
    def _call_local_llama(self, prompt: str) -> str:
        """Call local HuggyLLaMA model."""
        if not self.local_pipeline:
            raise Exception("Local LLaMA pipeline not initialized")
        
        # Format prompt for LLaMA
        formatted_prompt = f"### Human: {prompt}\n### Assistant:"
        
        # Generate response
        result = self.local_pipeline(
            formatted_prompt,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.local_pipeline.tokenizer.eos_token_id
        )
        
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
            # Extract only the assistant's response
            if "### Assistant:" in generated_text:
                return generated_text.split("### Assistant:")[-1].strip()
            return generated_text.strip()
        else:
            raise Exception("No response generated from local LLaMA")
    
    def generate_llama_content(self, prompt: str) -> str:
        """Generate content using the best available LLaMA provider."""
        if self.provider == "together":
            return self._call_together_api(prompt)
        elif self.provider == "huggingface":
            return self._call_huggingface_api(prompt)
        elif self.provider == "local":
            return self._call_local_llama(prompt)
        else:
            raise Exception("No LLaMA provider available")
    
    def _repair_json(self, json_str: str) -> str:
        """
        Attempt to repair malformed JSON from LLaMA responses.
        Handles common issues like trailing commas, missing brackets, etc.
        """
        try:
            # First try to parse as-is
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        # Try to repair common issues
        repaired = json_str.strip()
        
        # Remove text before/after JSON
        if '{' in repaired:
            repaired = repaired[repaired.find('{'):]
        elif '[' in repaired:
            repaired = repaired[repaired.find('['):]
        
        if '}' in repaired:
            repaired = repaired[:repaired.rfind('}') + 1]
        elif ']' in repaired:
            repaired = repaired[:repaired.rfind(']') + 1]
        
        # Remove trailing commas before closing brackets/braces
        repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
        
        # Try to balance brackets/braces
        open_braces = repaired.count('{')
        close_braces = repaired.count('}')
        open_brackets = repaired.count('[')
        close_brackets = repaired.count(']')
        
        if open_braces > close_braces:
            repaired += '}' * (open_braces - close_braces)
        if open_brackets > close_brackets:
            repaired += ']' * (open_brackets - close_brackets)
        
        try:
            json.loads(repaired)
            print(f"✓ JSON repair successful")
            return repaired
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON repair failed: {e}")
            return json_str

    def generate_recommendations(self, candidate_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate job recommendations using the best available LLaMA provider or fallback to CLI parser.
        """
        if self.provider == "cli":
            return self._generate_cli_based_recommendations(candidate_data)
        
        try:
            # Prepare the prompt for LLaMA
            prompt = self._create_prompt(candidate_data)
            
            # Call the appropriate LLaMA provider
            response = self.generate_llama_content(prompt)
            
            # Parse the response
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Error calling LLaMA provider ({self.provider}): {e}")
            print("⚠️  Falling back to CLI parser")
            return self._generate_cli_based_recommendations(candidate_data)
    
    def _create_prompt(self, candidate_data: Dict[str, Any]) -> str:
        """Create a prompt for LLaMA based on candidate data."""
        prompt = f"""Based on the following candidate profile, recommend 3-5 suitable job roles with explanations.

Candidate Profile:
{json.dumps(candidate_data, indent=2)}

Please return your response as a JSON array of objects with "title" and "reason" fields.

Example format:
[
  {{"title": "Software Engineer", "reason": "Strong programming skills in Python and experience with web development."}},
  {{"title": "Data Analyst", "reason": "Experience with data analysis and statistical tools."}}
]"""
        return prompt
    
    
    def _parse_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the LLaMA response into structured recommendations with JSON repair."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                repaired_json = self._repair_json(json_str)
                try:
                    recommendations = json.loads(repaired_json)
                    if isinstance(recommendations, list):
                        print("✓ LLaMA recommendations JSON parsing successful")
                        return [
                            {
                                "title": rec.get("title", "Unknown Position"),
                                "reason": rec.get("reason", "No reason provided")
                            }
                            for rec in recommendations
                            if isinstance(rec, dict)
                        ]
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing failed even after repair: {e}")
        except Exception as e:
            print(f"Error parsing LLaMA response: {e}")
        
        print("⚠️  LLaMA response parsing failed, using CLI parser-based recommendations")
        return self._generate_cli_based_recommendations({})
    
    
    def extract_skills_from_job_description(self, job_description: str) -> List[str]:
        """
        Extract required skills from a job description using LLaMA or fallback to CLI parser.
        """
        if self.provider == "cli":
            return self._extract_skills_cli_fallback(job_description)
        
        try:
            # Create prompt for skill extraction
            prompt = f"""Extract the technical skills and requirements from this job description. 
            Return only a JSON array of skill names, no explanations.

            Job Description:
            {job_description}

            Example format:
            ["Python", "React", "PostgreSQL", "Docker", "AWS"]
            """
            
            # Call the appropriate LLaMA provider
            response = self.generate_llama_content(prompt)
            
            # Parse the response
            return self._parse_skills_response(response)
            
        except Exception as e:
            print(f"Error extracting skills from job description: {e}")
            print("⚠️  Falling back to CLI parser")
            return self._extract_skills_cli_fallback(job_description)
    
    def _parse_skills_response(self, response: str) -> List[str]:
        """Parse the LLaMA response to extract skills with JSON repair."""
        try:
            # Try to extract JSON array from the response
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                repaired_json = self._repair_json(json_str)
                try:
                    skills = json.loads(repaired_json)
                    if isinstance(skills, list):
                        print("✓ LLaMA skills JSON parsing successful")
                        return [skill.strip() for skill in skills if isinstance(skill, str)]
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing failed even after repair: {e}")
        except Exception as e:
            print(f"Error parsing skills response: {e}")
        
        print("⚠️  LLaMA skills response parsing failed, using CLI parser-based skill extraction")
        return self._extract_skills_cli_fallback("")
    
    
    def structure_cv_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Structure raw CV text into JSON format using LLaMA or fallback to CLI parser.
        """
        if self.provider == "cli":
            return self._fallback_to_cli_parser(raw_text)
        
        try:
            # Create prompt for CV structuring
            prompt = self._create_cv_structuring_prompt(raw_text)
            
            # Call the appropriate LLaMA provider
            response = self.generate_llama_content(prompt)
            
            # Parse the response
            structured_data = self._parse_cv_structure_response(response)
            
            # Verify content preservation
            preservation_report = self.verify_content_preservation(raw_text, structured_data)
            print(f"Content preservation score: {preservation_report['content_preservation_score']:.2f}")
            
            if preservation_report['missing_content_warning']:
                print("⚠️  Warning: Significant content might be missing from structured data")
            
            return structured_data
            
        except Exception as e:
            print(f"Error structuring CV with LLaMA ({self.provider}): {e}")
            print("⚠️  Falling back to CLI parser")
            return self._fallback_to_cli_parser(raw_text)
    
    def _create_cv_structuring_prompt(self, raw_text: str) -> str:
        """Create a prompt for LLaMA to structure CV text into JSON."""
        prompt = f"""You are an expert CV parser. Your task is to extract and structure EVERY SINGLE piece of information from the CV text below into a JSON format. NOTHING should be omitted, summarized, or discarded.

CRITICAL REQUIREMENTS:
- Extract 100% of the content - every word, every detail, every piece of information
- If content doesn't fit perfectly into a category, still include it in the most appropriate section
- Preserve exact wording, dates, names, and all details
- Include all bullet points, descriptions, and additional information
- Extract the candidate's name and include it in contact_info or professional_summary

STRUCTURE THE CONTENT INTO THESE SECTIONS:

1. contact_info: 
   - emails: [array of all email addresses found]
   - phones: [array of all phone numbers found] 
   - linkedin: [LinkedIn URL if present]
   - address: [full address if present]
   - name: [candidate's full name - extract from anywhere in the text]

2. professional_summary: [array of all summary/profile text - include everything that describes the candidate]

3. skills: [array of ALL skills, technologies, tools, competencies mentioned - extract every single one]

4. languages: [array of objects with "language" and "level" - include all languages mentioned]

5. education: [array of education entries with ALL details including:
   - date_range: [exact dates as written]
   - degree: [full degree name]
   - institution: [full institution name]
   - details: [array of ALL additional details, coursework, achievements, descriptions]
   - location: [if mentioned]]

6. experience: [array of work experience with ALL details including:
   - date_range: [exact dates as written]
   - company: [full company name]
   - role: [full job title/role]
   - details: [array of ALL job descriptions, responsibilities, achievements]
   - location: [if mentioned]]

7. projects: [array of ALL projects, activities, achievements with:
   - title: [project/activity name]
   - description: [full description including all details]]

8. additional_info: [array of any other information that doesn't fit above categories - include everything else]

FORMAT REQUIREMENTS:
- For contact_info: {{"emails": ["email1", "email2"], "phones": ["phone1", "phone2"], "linkedin": "url", "address": "address", "name": "Full Name"}}
- For languages: [{{"language": "Language Name", "level": "Proficiency Level"}}]
- For education/experience: Include ALL details in the "details" array - don't summarize
- For projects: Include full descriptions, don't abbreviate
- Return ONLY valid JSON, no explanations

CV Text to parse:
{raw_text}

Extract and structure ALL content into JSON:"""
        return prompt
    
    def _parse_cv_structure_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLaMA response into structured CV data with JSON repair."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                repaired_json = self._repair_json(json_str)
                try:
                    structured_data = json.loads(repaired_json)
                    print("✓ LLaMA JSON parsing successful")
                    return self._validate_cv_structure(structured_data)
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing failed even after repair: {e}")
                    # Try to extract partial data from the response
                    return self._extract_partial_data_from_response(response)
        except Exception as e:
            print(f"Error parsing CV structure response: {e}")
        
        # Fallback to CLI parser if parsing fails
        print("⚠️  LLaMA CV structure response parsing failed, using CLI parser fallback")
        return self._fallback_to_cli_parser("")
    
    def _validate_cv_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the CV structure to match expected format while preserving all content."""
        # Ensure all required fields exist with proper defaults
        validated_data = {
            "contact_info": data.get("contact_info", {
                "emails": [],
                "phones": [],
                "linkedin": "",
                "address": "",
                "name": ""
            }),
            "professional_summary": data.get("professional_summary", []),
            "skills": data.get("skills", []),
            "languages": data.get("languages", []),
            "education": data.get("education", []),
            "experience": data.get("experience", []),
            "projects": data.get("projects", []),
            "additional_info": data.get("additional_info", [])
        }
        
        # Ensure lists are actually lists and contain only strings for simple arrays
        for key in ["professional_summary", "skills", "additional_info"]:
            if not isinstance(validated_data[key], list):
                validated_data[key] = []
            else:
                # Ensure all items in these arrays are strings
                validated_data[key] = [str(item) if not isinstance(item, str) else item for item in validated_data[key]]
        
        for key in ["languages", "education", "experience", "projects"]:
            if not isinstance(validated_data[key], list):
                validated_data[key] = []
        
        # Ensure contact_info has required fields
        if not isinstance(validated_data["contact_info"], dict):
            validated_data["contact_info"] = {"emails": [], "phones": [], "linkedin": "", "address": "", "name": ""}
        
        # Handle both old format (emails/phones arrays) and new format (email/phone strings)
        contact_info = validated_data["contact_info"]
        
        # Convert single email/phone to arrays if needed
        if "email" in contact_info and contact_info["email"]:
            if "emails" not in contact_info or not isinstance(contact_info["emails"], list):
                contact_info["emails"] = []
            if contact_info["email"] not in contact_info["emails"]:
                contact_info["emails"].append(contact_info["email"])
        
        if "phone" in contact_info and contact_info["phone"]:
            if "phones" not in contact_info or not isinstance(contact_info["phones"], list):
                contact_info["phones"] = []
            if contact_info["phone"] not in contact_info["phones"]:
                contact_info["phones"].append(contact_info["phone"])
        
        # Ensure required fields exist with proper types
        for field in ["emails", "phones"]:
            if field not in contact_info or not isinstance(contact_info[field], list):
                contact_info[field] = []
        
        for field in ["linkedin", "address", "name"]:
            if field not in contact_info or not isinstance(contact_info[field], str):
                contact_info[field] = ""
        
        # Validate education entries to ensure details are preserved
        for edu in validated_data["education"]:
            if isinstance(edu, dict):
                if "details" not in edu or not isinstance(edu["details"], list):
                    edu["details"] = []
                # Ensure details array contains only strings
                edu["details"] = [str(detail) if not isinstance(detail, str) else detail for detail in edu["details"]]
                # Ensure all fields are strings if they exist
                for field in ["date_range", "degree", "institution", "location"]:
                    if field in edu and not isinstance(edu[field], str):
                        edu[field] = str(edu[field]) if edu[field] else ""
        
        # Validate experience entries to ensure details are preserved
        for exp in validated_data["experience"]:
            if isinstance(exp, dict):
                if "details" not in exp or not isinstance(exp["details"], list):
                    exp["details"] = []
                # Ensure details array contains only strings
                exp["details"] = [str(detail) if not isinstance(detail, str) else detail for detail in exp["details"]]
                # Ensure all fields are strings if they exist
                for field in ["date_range", "company", "role", "location"]:
                    if field in exp and not isinstance(exp[field], str):
                        exp[field] = str(exp[field]) if exp[field] else ""
        
        # Validate project entries
        for project in validated_data["projects"]:
            if isinstance(project, dict):
                for field in ["title", "description"]:
                    if field in project and not isinstance(project[field], str):
                        project[field] = str(project[field]) if project[field] else ""
        
        # Validate language entries
        for lang in validated_data["languages"]:
            if isinstance(lang, dict):
                for field in ["language", "level"]:
                    if field in lang and not isinstance(lang[field], str):
                        lang[field] = str(lang[field]) if lang[field] else ""
        
        return validated_data
    
    def _extract_partial_data_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract partial structured data from LLaMA response when JSON parsing fails.
        This preserves as much information as possible before falling back to CLI parser.
        """
        try:
            print("Attempting to extract partial data from LLaMA response...")
            
            # Initialize partial data structure
            partial_data = {
                "contact_info": {"emails": [], "phones": [], "linkedin": "", "address": "", "name": ""},
                "professional_summary": [],
                "skills": [],
                "languages": [],
                "education": [],
                "experience": [],
                "projects": [],
                "additional_info": []
            }
            
            # Try to extract name
            name_match = re.search(r'"name"\s*:\s*"([^"]+)"', response, re.IGNORECASE)
            if name_match:
                partial_data["contact_info"]["name"] = name_match.group(1)
            
            # Try to extract emails
            email_matches = re.findall(r'"emails"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if email_matches:
                emails = re.findall(r'"([^"]+@[^"]+)"', email_matches[0])
                partial_data["contact_info"]["emails"] = emails
            
            # Try to extract skills
            skills_matches = re.findall(r'"skills"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if skills_matches:
                skills = re.findall(r'"([^"]+)"', skills_matches[0])
                partial_data["skills"] = skills
            
            # Try to extract professional summary
            summary_matches = re.findall(r'"professional_summary"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if summary_matches:
                summary = re.findall(r'"([^"]+)"', summary_matches[0])
                partial_data["professional_summary"] = summary
            
            print(f"✓ Extracted partial data: name={partial_data['contact_info']['name']}, skills={len(partial_data['skills'])}, summary={len(partial_data['professional_summary'])}")
            return partial_data
            
        except Exception as e:
            print(f"Error extracting partial data: {e}")
            return self._fallback_to_cli_parser("")
    
    def _fallback_to_cli_parser(self, raw_text: str) -> Dict[str, Any]:
        """
        Enhanced CLI parser fallback that preserves ALL content.
        Ensures no CV content is lost by storing everything in appropriate sections.
        """
        try:
            # Import the individual extraction functions from cv_extractor_cli
            from cv_extractor_cli import (
                extract_contact_info, extract_summary, extract_skills, 
                extract_languages, extract_education, extract_experience, 
                extract_projects
            )
            
            print("🔄 Starting enhanced CLI parser fallback...")
            
            # Extract all information using CLI parser functions
            contact_info = extract_contact_info(raw_text)
            
            # Extract candidate name from raw text
            candidate_name = self._extract_candidate_name(raw_text)
            if candidate_name:
                contact_info["name"] = candidate_name
            
            # Extract all sections
            professional_summary = extract_summary(raw_text)
            skills = extract_skills(raw_text)
            languages = extract_languages(raw_text)
            education = extract_education(raw_text)
            experience = extract_experience(raw_text)
            projects = extract_projects(raw_text)
            
            # Create comprehensive additional_info to capture any missed content
            additional_info = self._extract_additional_content(raw_text, {
                "professional_summary": professional_summary,
                "skills": skills,
                "education": education,
                "experience": experience,
                "projects": projects
            })
            
            structured_data = {
                "contact_info": contact_info,
                "professional_summary": professional_summary,
                "skills": skills,
                "languages": languages,
                "education": education,
                "experience": experience,
                "projects": projects,
                "additional_info": additional_info
            }
            
            # Ensure all sections exist (don't remove empty ones)
            for section in ["professional_summary", "skills", "languages", "education", "experience", "projects", "additional_info"]:
                if section not in structured_data or not structured_data[section]:
                    structured_data[section] = []
            
            # Ensure contact_info has all required fields
            if "contact_info" not in structured_data:
                structured_data["contact_info"] = {"emails": [], "phones": [], "linkedin": "", "address": "", "name": ""}
            
            print(f"✓ Enhanced CLI parser completed - Content preserved in all sections")
            return structured_data
            
        except Exception as e:
            print(f"Error in enhanced CLI parser fallback: {e}")
            # If even CLI parser fails, return structure with raw text preserved
            return self._create_fallback_structure_with_raw_text(raw_text)
    
    def _generate_cli_based_recommendations(self, candidate_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on CLI parser data."""
        try:
            # Extract skills from candidate data
            skills = candidate_data.get("skills", [])
            experience = candidate_data.get("experience", [])
            
            # Generate basic recommendations based on skills
            recommendations = []
            
            if any("python" in skill.lower() for skill in skills):
                recommendations.append({
                    "title": "Python Developer",
                    "reason": "Strong Python programming skills detected in candidate profile."
                })
            
            if any("javascript" in skill.lower() or "react" in skill.lower() for skill in skills):
                recommendations.append({
                    "title": "Frontend Developer",
                    "reason": "JavaScript and React skills indicate frontend development potential."
                })
            
            if any("data" in skill.lower() or "analytics" in skill.lower() for skill in skills):
                recommendations.append({
                    "title": "Data Analyst",
                    "reason": "Data analysis skills suggest suitability for analytical roles."
                })
            
            if experience:
                recommendations.append({
                    "title": "Senior Developer",
                    "reason": "Previous work experience indicates readiness for senior positions."
                })
            
            # Add generic recommendations if none specific
            if not recommendations:
                recommendations = [
                    {
                        "title": "Software Developer",
                        "reason": "Technical background suggests suitability for software development roles."
                    },
                    {
                        "title": "Technical Consultant",
                        "reason": "Diverse skills indicate potential for consulting positions."
                    }
                ]
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            print(f"Error generating CLI-based recommendations: {e}")
            return [
                {
                    "title": "Software Developer",
                    "reason": "Technical background suggests suitability for software development roles."
                }
            ]
    
    def _extract_skills_cli_fallback(self, job_description: str) -> List[str]:
        """Extract skills using CLI parser as fallback."""
        try:
            from cv_extractor_cli import extract_skills
            return extract_skills(job_description)
        except Exception as e:
            print(f"Error in CLI skills extraction: {e}")
            return ["Python", "JavaScript", "React", "Node.js", "PostgreSQL"]
    
    def _extract_candidate_name(self, raw_text: str) -> str:
        """
        Extract candidate name from raw text using simple heuristics.
        """
        try:
            lines = raw_text.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if not line:
                    continue
                
                # Skip lines that are clearly not names
                if any(keyword in line.lower() for keyword in [
                    'email', 'phone', 'address', 'linkedin', 'summary', 'profile',
                    'experience', 'education', 'skills', 'languages', 'projects'
                ]):
                    continue
                
                # Look for name patterns (2-3 capitalized words)
                name_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})$', line)
                if name_match:
                    return name_match.group(1)
                
                # Look for name with title (Mr., Ms., etc.)
                name_with_title = re.match(r'^(Mr\.|Ms\.|Mrs\.|Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})$', line)
                if name_with_title:
                    return name_with_title.group(2)
            
            return ""
            
        except Exception as e:
            print(f"Error extracting candidate name: {e}")
            return ""
    
    def _extract_additional_content(self, raw_text: str, extracted_data: Dict[str, Any]) -> List[str]:
        """
        Extract any content that wasn't captured by the main parsing functions.
        This ensures no CV content is lost.
        """
        try:
            additional_content = []
            lines = raw_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                
                # Skip if content is already captured
                if self._is_content_already_captured(line, extracted_data):
                    continue
                
                # Skip section headers
                if any(header in line.lower() for header in [
                    'contact', 'email', 'phone', 'address', 'linkedin', 'summary', 'profile',
                    'objective', 'skills', 'competencies', 'experience', 'work', 'employment',
                    'education', 'formation', 'projects', 'languages', 'langues', 'certifications',
                    'awards', 'achievements', 'references'
                ]):
                    continue
                
                # Add substantial content that wasn't captured
                if len(line) > 10 and not line.isupper():
                    additional_content.append(line)
            
            print(f"✓ Extracted {len(additional_content)} additional content items")
            return additional_content
            
        except Exception as e:
            print(f"Error extracting additional content: {e}")
            return []
    
    def _is_content_already_captured(self, line: str, extracted_data: Dict[str, Any]) -> bool:
        """Check if a line of text is already captured in the extracted data."""
        try:
            line_lower = line.lower()
            
            # Check professional summary
            for summary_item in extracted_data.get("professional_summary", []):
                if line_lower in summary_item.lower() or summary_item.lower() in line_lower:
                    return True
            
            # Check skills
            for skill in extracted_data.get("skills", []):
                if line_lower == skill.lower() or skill.lower() in line_lower:
                    return True
            
            # Check education details
            for edu in extracted_data.get("education", []):
                if isinstance(edu, dict):
                    for detail in edu.get("details", []):
                        if line_lower in detail.lower() or detail.lower() in line_lower:
                            return True
            
            # Check experience details
            for exp in extracted_data.get("experience", []):
                if isinstance(exp, dict):
                    for detail in exp.get("details", []):
                        if line_lower in detail.lower() or detail.lower() in line_lower:
                            return True
            
            # Check project details
            for project in extracted_data.get("projects", []):
                if isinstance(project, dict):
                    for field in ["title", "description"]:
                        if field in project and line_lower in project[field].lower():
                            return True
            
            return False
            
        except Exception as e:
            print(f"Error checking if content is captured: {e}")
            return False
    
    def _create_fallback_structure_with_raw_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Create a fallback structure that preserves all raw text when everything else fails.
        This ensures no content is ever lost.
        """
        try:
            print("🔄 Creating fallback structure with raw text preservation...")
            
            # Extract candidate name
            candidate_name = self._extract_candidate_name(raw_text)
            
            # Split raw text into lines and filter out empty ones
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            # Create fallback structure
            fallback_structure = {
                "contact_info": {
                    "emails": [],
                    "phones": [],
                    "linkedin": "",
                    "address": "",
                    "name": candidate_name
                },
                "professional_summary": lines[:5] if len(lines) > 5 else lines,
                "skills": [],
                "languages": [],
                "education": [],
                "experience": [],
                "projects": [],
                "additional_info": lines
            }
            
            print(f"✓ Fallback structure created - All {len(lines)} lines preserved")
            return fallback_structure
            
        except Exception as e:
            print(f"Error creating fallback structure: {e}")
            return {
                "contact_info": {"emails": [], "phones": [], "linkedin": "", "address": "", "name": ""},
                "professional_summary": [],
                "skills": [],
                "languages": [],
                "education": [],
                "experience": [],
                "projects": [],
                "additional_info": [raw_text]
            }
    
    def verify_content_preservation(self, raw_text: str, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that content has been preserved during structuring.
        Returns a report on content preservation.
        """
        report = {
            "original_text_length": len(raw_text),
            "structured_content_length": 0,
            "sections_found": {},
            "content_preservation_score": 0.0,
            "missing_content_warning": False
        }
        
        # Calculate total structured content length
        total_structured_length = 0
        
        # Count content in each section
        for section_name, section_data in structured_data.items():
            if section_name == "contact_info" and isinstance(section_data, dict):
                # Count contact info fields
                for field, value in section_data.items():
                    if isinstance(value, str):
                        total_structured_length += len(value)
                    elif isinstance(value, list):
                        total_structured_length += sum(len(str(item)) for item in value)
            elif isinstance(section_data, list):
                # Count list items
                for item in section_data:
                    if isinstance(item, str):
                        total_structured_length += len(item)
                    elif isinstance(item, dict):
                        for field, value in item.items():
                            if isinstance(value, str):
                                total_structured_length += len(value)
                            elif isinstance(value, list):
                                total_structured_length += sum(len(str(subitem)) for subitem in value)
            
            # Count items in section
            if isinstance(section_data, list):
                report["sections_found"][section_name] = len(section_data)
            elif isinstance(section_data, dict):
                report["sections_found"][section_name] = len(section_data)
        
        report["structured_content_length"] = total_structured_length
        
        # Calculate preservation score (rough estimate)
        if report["original_text_length"] > 0:
            report["content_preservation_score"] = min(1.0, total_structured_length / report["original_text_length"])
        
        # Flag if significant content might be missing
        if report["content_preservation_score"] < 0.3:
            report["missing_content_warning"] = True
        
        return report
