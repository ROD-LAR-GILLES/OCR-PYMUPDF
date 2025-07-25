"""Domain exceptions for LLM operations."""

class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass

class LLMConfigurationError(LLMProviderError):
    """Exception raised when configuration is invalid."""
    pass

class LLMConnectionError(LLMProviderError):
    """Exception raised when connection to LLM service fails."""
    pass

class LLMResponseError(LLMProviderError):
    """Exception raised when LLM response is invalid."""
    pass
