"""Adapter for Google's Gemini LLM service."""
import json
from typing import Dict, Any, Optional
from domain.models.gemini_config import GeminiConfig
from domain.exceptions.llm_exceptions import (
    LLMConnectionError, 
    LLMResponseError,
    LLMRateLimitError
)
from domain.ports.http_client import HTTPClient
from domain.ports.llm_provider import LLMProvider

class GeminiAdapter(LLMProvider):
    """Adapter implementation for Google's Gemini LLM service."""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def __init__(self, config: Dict[str, Any], http_client: HTTPClient):
        """Initialize the Gemini adapter.
        
        Args:
            config: Configuration dictionary
            http_client: HTTP client implementation
        """
        self.config = GeminiConfig(config)
        self.http_client = http_client
        
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for API endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Complete URL with API key
        """
        return f"{self.BASE_URL}/{endpoint}?key={self.config.api_key}"
        
    def _handle_error(self, status_code: int, response_body: Dict[str, Any]) -> None:
        """Handle error responses from the API.
        
        Args:
            status_code: HTTP status code
            response_body: Response body dictionary
            
        Raises:
            LLMConnectionError: For connection issues
            LLMRateLimitError: When rate limit is exceeded
            LLMResponseError: For other API errors
        """
        if status_code == 429:
            raise LLMRateLimitError("Gemini API rate limit exceeded")
        elif status_code >= 500:
            raise LLMConnectionError(f"Gemini API server error: {status_code}")
        else:
            error_msg = response_body.get("error", {}).get("message", "Unknown error")
            raise LLMResponseError(f"Gemini API error: {error_msg}")
            
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini.
        
        Args:
            prompt: Input prompt for generation
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
            
        Raises:
            LLMConnectionError: For connection issues
            LLMRateLimitError: When rate limit is exceeded
            LLMResponseError: For other API errors
        """
        url = self._build_url(f"{self.config.model_name}:generateContent")
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "topK": kwargs.get("top_k", 40),
                "topP": kwargs.get("top_p", 0.95),
                "maxOutputTokens": kwargs.get("max_tokens", 1024),
            }
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        response = await self.http_client.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code != 200:
            self._handle_error(response.status_code, response.json())
            
        try:
            response_data = response.json()
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise LLMResponseError(f"Invalid response format: {str(e)}")
            
    async def embed_text(self, text: str) -> list[float]:
        """Get text embeddings from Gemini.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
            
        Raises:
            LLMConnectionError: For connection issues
            LLMRateLimitError: When rate limit is exceeded
            LLMResponseError: For other API errors
        """
        url = self._build_url(f"{self.config.model_name}:embedContent")
        
        data = {
            "content": {
                "parts": [{
                    "text": text
                }]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        response = await self.http_client.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code != 200:
            self._handle_error(response.status_code, response.json())
            
        try:
            response_data = response.json()
            return response_data["embedding"]["values"]
        except (KeyError, IndexError) as e:
            raise LLMResponseError(f"Invalid response format: {str(e)}")
