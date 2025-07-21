"""HTTP client implementation using aiohttp."""
import aiohttp
from typing import Dict, Optional
from domain.ports.http_client import HTTPClient, HTTPResponse

class AiohttpClient(HTTPClient):
    """aiohttp-based HTTP client implementation."""
    
    def __init__(self):
        """Initialize client."""
        self._session = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            
    async def _close(self):
        """Close aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
            
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """Make GET request.
        
        Args:
            url: Request URL
            headers: Optional request headers
            params: Optional query parameters
            
        Returns:
            Response object
        """
        await self._ensure_session()
        async with self._session.get(url, headers=headers, params=params) as response:
            return HTTPResponse(
                status_code=response.status,
                body=await response.text(),
                headers=dict(response.headers)
            )
            
    async def post(
        self,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """Make POST request.
        
        Args:
            url: Request URL
            data: Request body
            headers: Optional request headers
            
        Returns:
            Response object
        """
        await self._ensure_session()
        async with self._session.post(url, data=data, headers=headers) as response:
            return HTTPResponse(
                status_code=response.status,
                body=await response.text(),
                headers=dict(response.headers)
            )
            
    def __del__(self):
        """Cleanup when object is destroyed."""
        import asyncio
        if self._session:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._close())
            else:
                loop.run_until_complete(self._close())
