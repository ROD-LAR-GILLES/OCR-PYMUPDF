"""DeepSeek local provider implementation."""
from typing import Dict, Any
import requests
from domain.ports.llm_provider import LLMProvider
from infrastructure.logging_setup import logger

class DeepSeekProvider(LLMProvider):
    """Local DeepSeek implementation of LLM provider."""
    
    def get_config_key(self) -> str:
        """Get the configuration key for DeepSeek settings."""
        return "deepseek"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize DeepSeek client with configuration.
        
        Args:
            config: Dictionary with DeepSeek-specific settings
        """
        self.api_url = config.get("api_url", "http://localhost:8000/v1/chat/completions")
        self.model = config.get("model_id", "deepseek-coder-33b")
        self.max_retries = config.get("max_retries", 3)
        
    def generate_completion(self, 
                          prompt: str,
                          system_prompt: str = None,
                          temperature: float = 0.1) -> str:
        """Generate completion using local DeepSeek instance.
        
        Args:
            prompt: The text to process
            system_prompt: Optional system instructions
            temperature: Controls response randomness
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If API call fails after max retries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, json=payload)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"DeepSeek API error: {e}")
                    raise
                logger.warning(f"Retrying DeepSeek request ({attempt + 1}/{self.max_retries})")
        
        raise Exception("Failed to get response from DeepSeek API")
