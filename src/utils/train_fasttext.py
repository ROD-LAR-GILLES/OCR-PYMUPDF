"""
Entrena (o re-entrena) un clasificador fastText que distingue palabras OCR correctas
de errores. Usa:

* data/legal_words.txt      → palabras válidas   (__label__OK)
* data/corrections.csv      → columnas: ocr,correct
                              - columna 'ocr'      => ejemplos __label__ERR
                              - columna 'correct'  => ejemplos __label__OK

Genera/actualiza:  models/ocr_correction_model.ftz
"""

from pathlib import Path
import fasttext                     # pip install fasttext-wheel
import pandas as pd

DATA_DIR   = Path("data")
MODEL_DIR  = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

LEGAL_WORDS = DATA_DIR / "legal_words.txt"
CORRECTIONS = DATA_DIR / "corrections.csv"
TRAIN_TXT   = MODEL_DIR / "train_fasttext.txt"
MODEL_PATH  = MODEL_DIR / "ocr_correction_model.ftz"


def build_training_file() -> None:
    lines: list[str] = []

    # 1) Palabras legales → etiqueta OK
    if LEGAL_WORDS.exists():
        with LEGAL_WORDS.open(encoding="utf-8") as f:
            for word in f:
                w = word.strip()
                if w:
                    lines.append(f"__label__OK {w}")

    # 2) Correcciones → OCR (ERR) y correctas (OK)
    if CORRECTIONS.exists():
        df = pd.read_csv(CORRECTIONS)
        for _, row in df.iterrows():
            ocr   = str(row["ocr"]).strip()
            corr  = str(row["correct"]).strip()
            if ocr:
                lines.append(f"__label__ERR {ocr}")
            if corr:
                lines.append(f"__label__OK {corr}")

    # 3) Guardar archivo temporal para fastText
    TRAIN_TXT.write_text("\n".join(lines), encoding="utf-8")
    print(f" Dataset generado: {TRAIN_TXT}  ({len(lines)} ejemplos)")


def train():
    build_training_file()

    print(" Entrenando modelo fastText…")
    model = fasttext.train_supervised(
        input=str(TRAIN_TXT),
        epoch=30,
        lr=0.5,
        wordNgrams=2,
        dim=50,
        loss="ova"     # one-vs-all, estable para datasets desbalanceados
    )

    model.save_model(str(MODEL_PATH))
    print(f"Modelo guardado en {MODEL_PATH}")


if __name__ == "__main__":
    train()