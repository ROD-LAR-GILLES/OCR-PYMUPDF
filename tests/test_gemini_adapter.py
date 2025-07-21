"""Test suite for Gemini adapter."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.exceptions.llm_exceptions import (
    LLMConfigurationError,
    LLMConnectionError,
    LLMResponseError,
    LLMRateLimitError
)
from src.domain.models.gemini_config import GeminiConfig
from src.adapters.llm.gemini_adapter import GeminiAdapter
from src.domain.ports.http_client import HTTPResponse

@pytest.fixture
def valid_config():
    """Fixture for valid Gemini configuration."""
    return {
        "api_key": "test_key",
        "model_id": "gemini-2.0-flash",
        "max_retries": 3
    }

@pytest.fixture
def mock_http_client():
    """Fixture for mock HTTP client."""
    client = AsyncMock()
    client.post = AsyncMock()
    return client

@pytest.fixture
def gemini_adapter(valid_config, mock_http_client):
    """Fixture for Gemini adapter with mock client."""
    return GeminiAdapter(valid_config, mock_http_client)

class TestGeminiConfig:
    """Test suite for Gemini configuration validation."""
    
    def test_valid_config(self, valid_config):
        """Test valid configuration."""
        config = GeminiConfig(valid_config)
        assert config.api_key == "test_key"
        assert config.model_name == "gemini-2.0-flash"
        assert config.max_retries == 3
        
    def test_missing_api_key(self):
        """Test configuration without API key."""
        with pytest.raises(LLMConfigurationError, match="API key is required"):
            GeminiConfig({})
            
    def test_invalid_api_key_type(self):
        """Test configuration with invalid API key type."""
        with pytest.raises(LLMConfigurationError, match="API key must be a string"):
            GeminiConfig({"api_key": 123})

class TestGeminiAdapter:
    """Test suite for Gemini adapter."""
    
    @pytest.mark.asyncio
    async def test_generate_text_success(self, gemini_adapter, mock_http_client):
        """Test successful text generation."""
        mock_response = HTTPResponse(
            status_code=200,
            body=json.dumps({
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": "Generated text"
                        }]
                    }
                }]
            })
        )
        mock_http_client.post.return_value = mock_response
        
        result = await gemini_adapter.generate_text("Test prompt")
        assert result == "Generated text"
        
        # Verify request
        called_url = mock_http_client.post.call_args[1]["url"]
        assert "gemini-2.0-flash:generateContent" in called_url
        assert "key=test_key" in called_url
        
    @pytest.mark.asyncio
    async def test_generate_text_rate_limit(self, gemini_adapter, mock_http_client):
        """Test rate limit error handling."""
        mock_response = HTTPResponse(
            status_code=429,
            body=json.dumps({"error": {"message": "Rate limit exceeded"}})
        )
        mock_http_client.post.return_value = mock_response
        
        with pytest.raises(LLMRateLimitError):
            await gemini_adapter.generate_text("Test prompt")
            
    @pytest.mark.asyncio
    async def test_generate_text_server_error(self, gemini_adapter, mock_http_client):
        """Test server error handling."""
        mock_response = HTTPResponse(
            status_code=500,
            body=json.dumps({"error": {"message": "Internal error"}})
        )
        mock_http_client.post.return_value = mock_response
        
        with pytest.raises(LLMConnectionError):
            await gemini_adapter.generate_text("Test prompt")
            
    @pytest.mark.asyncio
    async def test_embed_text_success(self, gemini_adapter, mock_http_client):
        """Test successful text embedding."""
        mock_response = HTTPResponse(
            status_code=200,
            body=json.dumps({
                "embedding": {
                    "values": [0.1, 0.2, 0.3]
                }
            })
        )
        mock_http_client.post.return_value = mock_response
        
        result = await gemini_adapter.embed_text("Test text")
        assert result == [0.1, 0.2, 0.3]
        
        # Verify request
        called_url = mock_http_client.post.call_args[1]["url"]
        assert "gemini-2.0-flash:embedContent" in called_url
        assert "key=test_key" in called_url
        
    @pytest.mark.asyncio
    async def test_embed_text_invalid_response(self, gemini_adapter, mock_http_client):
        """Test invalid response format handling."""
        mock_response = HTTPResponse(
            status_code=200,
            body=json.dumps({})  # Invalid response missing embedding
        )
        mock_http_client.post.return_value = mock_response
        
        with pytest.raises(LLMResponseError, match="Invalid response format"):
            await gemini_adapter.embed_text("Test text")
