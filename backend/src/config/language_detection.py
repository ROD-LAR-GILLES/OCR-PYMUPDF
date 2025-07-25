"""
Detector de idiomas híbrido que combina FastText y langdetect.
"""
import os
from pathlib import Path
from loguru import logger
import fasttext
import langdetect

class LanguageDetector:
    def __init__(self):
        self.fasttext_model = None
        self.model_path = Path("/app/data/models/fasttext/lid.176.ftz")
        try:
            # Solo intentar cargar el modelo si existe
            if self.model_path.exists():
                self.fasttext_model = fasttext.load_model(str(self.model_path))
            else:
                logger.warning("Modelo FastText no encontrado, usando langdetect como respaldo")
        except Exception as e:
            logger.warning(f"No se pudo cargar FastText, usando langdetect como respaldo: {e}")
    
    def detect(self, text: str) -> str:
        """
        Detecta el idioma del texto usando FastText o langdetect como respaldo.
        
        Args:
            text: Texto a analizar
            
        Returns:
            str: Código ISO del idioma (ej: 'es', 'en')
        """
        if not text.strip():
            return "es"
            
        try:
            # Intentar primero con FastText si está disponible
            if self.fasttext_model:
                predictions = self.fasttext_model.predict(text, k=1)
                lang_code = predictions[0][0].replace("__label__", "")
                # Convertir códigos de 3 letras a 2 letras si es necesario
                if lang_code == "spa":
                    return "es"
                return lang_code
                
            # Fallback a langdetect
            return langdetect.detect(text)
        except Exception as e:
            logger.error(f"Error en detección de idioma: {e}")
            return "es"  # Valor por defecto

# Instancia global
detector = LanguageDetector()
