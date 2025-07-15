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

def revisar_palabras(palabras: list[tuple[str, int, str]]):
    """
    CLI de revisión.

    Parameters
    ----------
    palabras : list[tuple[str, int, str]]
        Lista de tuplas (token, page_num, doc_name).
    """
    conocidas = cargar_diccionario()
    vistos: set[str] = set()

    for token, page, doc in palabras:
        token_norm = unidecode(token.lower())
        # -- ya aceptada o en diccionario
        if token_norm in conocidas or token_norm in vistos:
            continue
        vistos.add(token_norm)

        print(f"\n Documento: {doc} · Página: {page}")
        print(f"» Token OCR: '{token}'")
        resp = input("[Enter]=Aceptar / (c)=Corregir / (s)=Saltar : ").strip().lower()
        if resp == "c":
            nueva = input("Corrección: ").strip()
            guardar_correccion(token, nueva)
        elif resp == "":
            guardar_correccion(token, token)
        else:
            print("· Saltado.")