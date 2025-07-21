"""LLM configuration state management."""
from typing import Optional, Dict, Any
import json
from pathlib import Path
from infrastructure.logging_setup import logger

CONFIG_FILE = Path("config/llm_config.json")

class LLMConfig:
    """Manages LLM configuration state."""
    
    DEFAULT_CONFIG = {
        "provider": None,  # None means no LLM processing
        "settings": {},
        "providers": {
            "deepseek": {
                "name": "DeepSeek API",
                "api_key": None
            }
        }
    }
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> None:
        """Save LLM configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            CONFIG_FILE.parent.mkdir(exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving LLM config: {e}")

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load LLM configuration from file.
        
        Returns:
            Dictionary with current LLM configuration
        """
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading LLM config: {e}")
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def get_current_provider(cls) -> Optional[str]:
        """Get current LLM provider name or None if disabled.
        
        Returns:
            Provider name or None if LLM processing is disabled
        """
        config = cls.load_config()
        provider = config.get("provider")
        
        # Log provider state change
        if provider:
            logger.info(f"Using LLM provider: {provider}")
        else:
            logger.info("LLM processing is disabled")
            
        return provider
    
    @classmethod
    def set_provider(cls, provider: Optional[str], settings: Dict[str, Any] = None) -> None:
        """Set LLM provider and its settings.
        
        Args:
            provider: Provider name or None to disable LLM processing
            settings: Optional provider-specific settings
        """
        config = cls.load_config()
        config["provider"] = provider
        if settings:
            config["settings"] = settings
        cls.save_config(config)
