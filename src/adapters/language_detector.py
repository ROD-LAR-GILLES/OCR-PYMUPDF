"""
Detector de idiomas mejorado usando FastText para mayor precisión.
"""
import fasttext
from pathlib import Path
from loguru import logger

class LanguageDetector:
    def __init__(self):
        try:
            # Cargar modelo preentrenado de FastText
            model_path = Path(__file__).parent / "lid.176.ftz"
            if not model_path.exists():
                logger.info("Descargando modelo de FastText...")
                import urllib.request
                urllib.request.urlretrieve(
                    "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz",
                    model_path
                )
            self.model = fasttext.load_model(str(model_path))
        except Exception as e:
            logger.error(f"Error al cargar modelo FastText: {e}")
            self.model = None
            
    def detect_language(self, text: str) -> str:
        """Detecta el idioma del texto usando FastText."""
        if not self.model or not text.strip():
            return "es"  # Valor por defecto
        
        try:
            predictions = self.model.predict(text, k=1)
            lang_code = predictions[0][0].replace("__label__", "")
            return lang_code
        except Exception as e:
            logger.error(f"Error en detección de idioma: {e}")
            return "es"  # Valor por defecto
