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