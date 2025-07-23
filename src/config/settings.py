"""
Configuración con validación de tipos usando Pydantic.
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: Optional[str] = None
    OPENAI_PROMPT_MODEL: str = "gpt-4"
    OPENAI_FT_MODEL: str = "gpt-3.5-turbo"
    
    # OCR
    OCR_DPI: int = 300
    OCR_LANG: str = "spa"
    OCR_LOG_LEVEL: str = "INFO"
    
    # Rutas
    DATA_DIR: Path = Path("tools/data")
    CORRECTIONS_PATH: Path = DATA_DIR / "corrections.csv"
    WORDS_PATH: Path = DATA_DIR / "dictionaries/legal_words.txt"
    PATTERNS_PATH: Path = DATA_DIR / "dictionaries/legal_patterns.txt"
    
    # Procesamiento de imagen
    CLAHE_CLIP_LIMIT: float = 3.0
    CLAHE_GRID_SIZE: tuple = (8, 8)
    ADAPTIVE_THRESH_BLOCK_SIZE: int = 31
    ADAPTIVE_THRESH_C: int = 15
    
    # Detección de tablas
    MIN_TABLE_WIDTH: int = 50
    MIN_TABLE_HEIGHT: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia global de configuración
settings = Settings()
