# src/utils/detect_errores.py
from pathlib import Path
import fasttext
from utils.ocr_lexicon import revisar_palabras

MODEL_PATH = Path("models/ocr_correction_model.ftz")

def revisar_documento(palabras: list[str]) -> None:
    """Filtra con fastText (si existe) y lanza CLI de revisión."""
    if MODEL_PATH.exists():
        model = fasttext.load_model(str(MODEL_PATH))
        sospechosas = [
            w for w in palabras
            if model.predict(w)[0][0] == "__label__ERR"
        ]
    else:
        sospechosas = palabras
    revisar_palabras(sospechosas)
