"""
Módulo de infraestructura encargado del almacenamiento de resultados del procesamiento OCR de archivos PDF.

Este módulo define funciones para guardar el contenido extraído en formato Markdown. Los archivos generados
se escriben en el directorio `resultado/`, utilizando como nombre base el del archivo PDF procesado.

Pertenece a la capa de infraestructura en la arquitectura limpia, y se comunica con la capa de dominio a través
de interfaces definidas. No contiene lógica de negocio, solo responsabilidades técnicas relacionadas al sistema
de archivos.
"""
from pathlib import Path
from loguru import logger

OUTPUT_DIR = Path("resultado")


def save_markdown(stem: str, markdown: str) -> Path:
    """
    Guarda el contenido Markdown como archivo `.md` en el directorio de salida.

    Args:
        stem (str): Nombre base del archivo sin extensión.
        markdown (str): Contenido en formato Markdown a escribir.

    Returns:
        Path: Ruta absoluta del archivo `.md` generado.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = OUTPUT_DIR / f"{stem}.md"
    md_path.write_text(markdown, encoding="utf-8")
    logger.info(f"Markdown guardado en {md_path}")
    return md_path