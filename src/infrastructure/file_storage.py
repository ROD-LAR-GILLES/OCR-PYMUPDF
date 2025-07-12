"""Infraestructura de almacenamiento de resultados."""
from pathlib import Path
from loguru import logger

OUTPUT_DIR = Path("resultado")


def save_markdown(stem: str, markdown: str) -> Path:
    """Guarda el texto Markdown en `resultado/<stem>.md`.

    Args:
        stem: Nombre base del archivo sin extensión.
        markdown: Contenido Markdown a escribir.

    Returns:
        Ruta completa del archivo generado.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = OUTPUT_DIR / f"{stem}.md"
    md_path.write_text(markdown, encoding="utf-8")
    logger.info(f"Markdown guardado en {md_path}")
    return md_path