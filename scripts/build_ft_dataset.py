"""
build_ft_dataset.py
Genera un dataset JSONL para fine-tuning de OpenAI a partir de pares
raw-OCR / Markdown limpio.

Estructura esperada
───────────────────
data/ft_pairs/
    0001_raw.txt
    0001_target.md
    0002_raw.txt
    0002_target.md
    …

Uso
───
python scripts/build_ft_dataset.py --out data/ft_training.jsonl
"""
import json, argparse
from pathlib import Path

PAIRS_DIR = Path("data/ft_pairs")
SYSTEM_PROMPT = (
    "You are a Markdown formatter for Spanish legal OCR text. "
    "Convert the user content into well-structured Markdown, preserving "
    "legal headings, numbered lists, and tables. Output **only** Markdown."
)

def build_examples() -> list[dict]:
    examples = []
    for raw in sorted(PAIRS_DIR.glob("*_raw.txt")):
        idx = raw.stem.replace("_raw", "")
        tgt = raw.with_name(f"{idx}_target.md")
        if not tgt.exists():
            print(f"[WARN] Falta {tgt.name} — se omite")
            continue
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",    "content": raw.read_text(encoding="utf-8").strip()},
                {"role": "assistant","content": tgt.read_text(encoding="utf-8").strip()}
            ]
        })
    return examples

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("data/ft_training.jsonl"))
    args = p.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for ex in build_examples():
            fh.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"[OK] Dataset escrito en {args.out}")