import csv
from pathlib import Path
from unidecode import unidecode

CORRECTIONS_PATH = Path("data/corrections.csv")
LEGAL_WORDS_PATH = Path("data/legal_words.txt")

def cargar_diccionario() -> set[str]:
    if not LEGAL_WORDS_PATH.exists():
        return set()
    with open(LEGAL_WORDS_PATH, encoding="utf-8") as f:
        return set(line.strip().lower() for line in f)

def guardar_correccion(original: str, corregido: str):
    with open(CORRECTIONS_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([original.strip(), corregido.strip()])

def revisar_palabras(palabras: list[str]):
    conocidas = cargar_diccionario()
    for palabra in sorted(set(palabras)):
        palabra_limpia = unidecode(palabra.lower())
        if palabra_limpia not in conocidas:
            print(f"\n¿Es correcta la palabra OCR: '{palabra}'?")
            resp = input("[Enter] para confirmar, (c) para corregir, (s) para saltar: ").strip().lower()
            if resp == "c":
                nueva = input("Ingrese corrección: ").strip()
                guardar_correccion(palabra, nueva)
            elif resp == "":
                guardar_correccion(palabra, palabra)
            else:
                print("Saltado.")