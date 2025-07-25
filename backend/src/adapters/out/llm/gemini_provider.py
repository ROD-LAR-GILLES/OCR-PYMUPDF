"""Google Gemini implementation for LLM provider."""
import requests
from typing import Dict, Any
from domain.ports.llm_provider import LLMProvider
from infrastructure.logging_setup import logger

class GeminiProvider(LLMProvider):
    """Google's Gemini implementation of LLM provider."""

    def get_config_key(self) -> str:
        """Get the configuration key for Gemini settings."""
        return "gemini"

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Gemini client with configuration.
        
        Args:
            config: Dictionary with Gemini-specific settings
            
        Raises:
            ValueError: If required settings are missing
        """
        if "api_key" not in config or not config["api_key"]:
            raise ValueError("Gemini API key not found in configuration")
            
        try:
            
            self.api_key = config["api_key"]
            self.model_name = config.get("model_id", "gemini-2.0-flash")
            self.max_retries = config.get("max_retries", 5)
            
            logger.debug(f"Configuring Gemini with API key: {self.api_key[:10]}...")
            logger.debug(f"Using model: {self.model_name}")
            
            # Test connection
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            data = {
                "contents": [{
                    "parts": [{
                        "text": "Test connection"
                    }]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                raise ValueError(f"Failed to connect to Gemini API: {response.text}")
                
            logger.debug("Gemini model test successful")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise ValueError(f"Gemini initialization failed: {str(e)}")
        
    def generate_completion(self, 
                          prompt: str,
                          system_prompt: str = None,
                          temperature: float = 0.1) -> str:
        """Generate completion using Gemini's chat model.
        
        Args:
            prompt: The text to process
            system_prompt: Optional system context
            temperature: Controls response creativity
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If API call fails after max retries
        """
        # No necesitamos la estructura de mensajes ya que usamos la API REST directamente
        
        for attempt in range(self.max_retries):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
                
                # Construir el mensaje
                content = prompt
                if system_prompt:
                    content = f"{system_prompt}\n\n{prompt}"
                
                data = {
                    "contents": [{
                        "parts": [{
                            "text": content
                        }]
                    }]
                }
                
                response = requests.post(url, headers=headers, json=data)
                if response.status_code != 200:
                    raise ValueError(f"Failed to generate completion: {response.text}")
                
                response_json = response.json()
                return response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Gemini API failed after {self.max_retries} attempts: {e}")
                    
        raise Exception("Unexpected error in Gemini completion generation")
