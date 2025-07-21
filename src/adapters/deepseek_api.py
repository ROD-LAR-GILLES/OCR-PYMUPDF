"""DeepSeek API adapter for LLM refinement."""
import os
from typing import Optional
import requests
from loguru import logger

class DeepSeekAPI:
    """Client for DeepSeek API."""
    
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize DeepSeek API client.
        
        Args:
            api_key: DeepSeek API key. If not provided, will look for DEEPSEEK_API_KEY env var
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not found")
            
    def refine_text(self, text: str) -> str:
        """Refine extracted text using DeepSeek API.
        
        Args:
            text: Raw text to refine
            
        Returns:
            Refined text with improved formatting and corrections
        """
        try:
            response = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that improves text formatting and readability while preserving the original meaning."
                        },
                        {
                            "role": "user", 
                            "content": f"Please improve the formatting and readability of this text while preserving its meaning:\n\n{text}"
                        }
                    ],
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {e}")
            return text  # Return original text on error
            
    def check_api_key(self) -> bool:
        """Validate API key by making a test request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            response = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": "test"}
                    ]
                }
            )
            return response.status_code == 200
        except:
            return False
