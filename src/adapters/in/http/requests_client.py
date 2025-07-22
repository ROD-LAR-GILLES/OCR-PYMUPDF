"""Requests implementation of HTTP client."""
import requests
from typing import Dict, Any
from domain.ports.http_client import HTTPClientPort
from domain.exceptions.llm_exceptions import LLMConnectionError

class RequestsClient(HTTPClientPort):
    """Implementation of HTTP client using requests library."""
    
    def post(self, url: str, headers: Dict[str, str], json: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP POST request using requests library.
        
        Args:
            url: The endpoint URL
            headers: HTTP headers
            json: Request body
            
        Returns:
            Dict with response data
            
        Raises:
            LLMConnectionError: If request fails
        """
        try:
            response = requests.post(url, headers=headers, json=json)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LLMConnectionError(f"HTTP request failed: {str(e)}")
