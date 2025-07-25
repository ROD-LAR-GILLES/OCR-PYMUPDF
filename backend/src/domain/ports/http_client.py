"""HTTP client port for external services."""
from abc import ABC, abstractmethod
from typing import Dict, Any

class HTTPClientPort(ABC):
    """Abstract interface for HTTP operations."""
    
    @abstractmethod
    def post(self, url: str, headers: Dict[str, str], json: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP POST request.
        
        Args:
            url: The endpoint URL
            headers: HTTP headers
            json: Request body
            
        Returns:
            Dict with response data
            
        Raises:
            HTTPError: If request fails
        """
        pass
