import os
import json
import torch
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

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
        
        # Fallback to dummy recommendations
        print("⚠️  Using dummy recommendations (no API key or GPU available)")
        return "dummy"
    
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

    def generate_recommendations(self, candidate_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate job recommendations using the best available LLaMA provider or return dummy data.
        """
        if self.provider == "dummy":
            return self._get_dummy_recommendations()
        
        try:
            # Prepare the prompt for LLaMA
            prompt = self._create_prompt(candidate_data)
            
            # Call the appropriate LLaMA provider
            response = self.generate_llama_content(prompt)
            
            # Parse the response
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Error calling LLaMA provider ({self.provider}): {e}")
            return self._get_dummy_recommendations()
    
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
        """Parse the LLaMA response into structured recommendations."""
        try:
            # Try to extract JSON from the response
            # Look for JSON array in the response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                recommendations = json.loads(json_str)
                
                # Validate the structure
                if isinstance(recommendations, list):
                    return [
                        {
                            "title": rec.get("title", "Unknown Position"),
                            "reason": rec.get("reason", "No reason provided")
                        }
                        for rec in recommendations
                        if isinstance(rec, dict)
                    ]
        except Exception as e:
            print(f"Error parsing LLaMA response: {e}")
        
        # Fallback to dummy data if parsing fails
        return self._get_dummy_recommendations()
    
    def _get_dummy_recommendations(self) -> List[Dict[str, str]]:
        """Return dummy recommendations for testing when API key is not available."""
        return [
            {
                "title": "Software Engineer",
                "reason": "Strong programming skills and technical background make this candidate suitable for software development roles."
            },
            {
                "title": "Data Analyst",
                "reason": "Analytical skills and experience with data processing tools indicate potential for data analysis positions."
            },
            {
                "title": "Project Manager",
                "reason": "Leadership experience and organizational skills suggest potential for project management roles."
            },
            {
                "title": "Technical Consultant",
                "reason": "Diverse technical skills and problem-solving abilities make this candidate suitable for consulting roles."
            },
            {
                "title": "Product Manager",
                "reason": "Technical background combined with communication skills indicates potential for product management positions."
            }
        ]
    
    def extract_skills_from_job_description(self, job_description: str) -> List[str]:
        """
        Extract required skills from a job description using LLaMA.
        """
        if self.provider == "dummy":
            return self._get_dummy_skills()
        
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
            return self._get_dummy_skills()
    
    def _parse_skills_response(self, response: str) -> List[str]:
        """Parse the LLaMA response to extract skills."""
        try:
            # Try to extract JSON array from the response
            import re
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                skills = json.loads(json_str)
                
                # Validate the structure
                if isinstance(skills, list):
                    return [skill.strip() for skill in skills if isinstance(skill, str)]
        except Exception as e:
            print(f"Error parsing skills response: {e}")
        
        # Fallback to dummy data if parsing fails
        return self._get_dummy_skills()
    
    def _get_dummy_skills(self) -> List[str]:
        """Return dummy skills for testing when API key is not available."""
        return ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker", "AWS"]
    
    def structure_cv_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Structure raw CV text into JSON format using LLaMA.
        This replaces the old section parsing logic with AI-powered structuring.
        """
        if self.provider == "dummy":
            return self._get_dummy_cv_structure()
        
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
            return self._get_dummy_cv_structure()
    
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
        """Parse the LLaMA response into structured CV data."""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                structured_data = json.loads(json_str)
                
                # Validate and clean the structure
                return self._validate_cv_structure(structured_data)
        except Exception as e:
            print(f"Error parsing CV structure response: {e}")
        
        # Fallback to dummy data if parsing fails
        return self._get_dummy_cv_structure()
    
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
        
        # Ensure lists are actually lists
        for key in ["professional_summary", "skills", "languages", "education", "experience", "projects", "additional_info"]:
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
                # Ensure all fields are strings if they exist
                for field in ["date_range", "degree", "institution", "location"]:
                    if field in edu and not isinstance(edu[field], str):
                        edu[field] = str(edu[field]) if edu[field] else ""
        
        # Validate experience entries to ensure details are preserved
        for exp in validated_data["experience"]:
            if isinstance(exp, dict):
                if "details" not in exp or not isinstance(exp["details"], list):
                    exp["details"] = []
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
    
    def _get_dummy_cv_structure(self) -> Dict[str, Any]:
        """Return dummy CV structure for testing when API key is not available."""
        return {
            "contact_info": {
                "emails": ["example@email.com"],
                "phones": ["+1234567890"],
                "linkedin": "",
                "address": "Sample Address",
                "name": "John Doe"
            },
            "professional_summary": [
                "Experienced software developer with strong technical skills",
                "Passionate about creating innovative solutions"
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL"],
            "languages": [
                {"language": "English", "level": "Fluent"},
                {"language": "French", "level": "Intermediate"}
            ],
            "education": [
                {
                    "date_range": "2020-2024",
                    "degree": "Bachelor of Computer Science",
                    "institution": "University Name",
                    "location": "City, Country",
                    "details": ["Relevant coursework and achievements", "Additional details"]
                }
            ],
            "experience": [
                {
                    "date_range": "2022-2024",
                    "company": "Tech Company",
                    "role": "Software Developer",
                    "location": "City, Country",
                    "details": ["Developed web applications", "Collaborated with team members", "Additional responsibilities"]
                }
            ],
            "projects": [
                {
                    "title": "Sample Project",
                    "description": "A detailed sample project description with all relevant information"
                }
            ],
            "additional_info": [
                "Any additional information that doesn't fit other categories"
            ]
        }