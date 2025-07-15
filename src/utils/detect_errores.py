"""Filtra tokens con fastText y lanza revisión con contexto (doc + página)."""
from pathlib import Path
import fasttext
from utils.ocr_lexicon import revisar_palabras

MODEL_PATH = Path("models/ocr_correction_model.ftz")

def revisar_documento(tokens_meta: list[tuple[str, int, str]]) -> None:
    """
    tokens_meta : list[(token, page_num, doc_name)]
    """
    if MODEL_PATH.exists():
        model = fasttext.load_model(str(MODEL_PATH))
        sospechosas = [
            meta for meta in tokens_meta
            if model.predict(meta[0])[0][0] == "__label__ERR"
        ]
    else:
        sospechosas = tokens_meta

    revisar_palabras(sospechosas)
