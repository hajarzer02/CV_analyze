import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class LlamaService:
    def __init__(self):
        self.api_key = os.getenv("LLAMA3_API_KEY", "")
        self.api_url = os.getenv("LLAMA3_API_URL", "https://api.example.com/llama3")
    
    def generate_recommendations(self, candidate_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate job recommendations using LLaMA 3 API or return dummy data if API key is not available.
        """
        if not self.api_key:
            return self._get_dummy_recommendations()
        
        try:
            # Prepare the prompt for LLaMA 3
            prompt = self._create_prompt(candidate_data)
            
            # Call LLaMA 3 API
            response = self._call_llama_api(prompt)
            
            # Parse the response
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Error calling LLaMA 3 API: {e}")
            return self._get_dummy_recommendations()
    
    def _create_prompt(self, candidate_data: Dict[str, Any]) -> str:
        """Create a prompt for LLaMA 3 based on candidate data."""
        prompt = f"""You are an assistant that recommends job roles based on CV data.
Here is the candidate profile (JSON):
{json.dumps(candidate_data, indent=2)}

Return 3-5 job titles suitable for this candidate with a one-sentence explanation each in JSON format.
The response should be a JSON array of objects with "title" and "reason" fields.

Example format:
[
  {{"title": "Software Engineer", "reason": "Strong programming skills in Python and experience with web development."}},
  {{"title": "Data Analyst", "reason": "Experience with data analysis and statistical tools."}}
]"""
        return prompt
    
    def _call_llama_api(self, prompt: str) -> str:
        """Call the LLaMA 3 API with the given prompt."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("text", "")
    
    def _parse_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the LLaMA 3 response into structured recommendations."""
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
