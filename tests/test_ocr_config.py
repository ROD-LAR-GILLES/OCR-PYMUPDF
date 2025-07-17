# tests/test_ocr_config.py
from pathlib import Path

def test_tesseract_config_loads():
    from adapters.ocr_adapter import build_tesseract_config
    config = build_tesseract_config(6)
    assert "--user-words data/legal_words.txt" in config
    assert "--user-patterns data/legal_patterns.txt" in config

def test_tesseract_custom_files_exist():
    assert Path("data/legal_words.txt").exists(), "Falta data/legal_words.txt"
    assert Path("data/legal_patterns.txt").exists(), "Falta data/legal_patterns.txt"