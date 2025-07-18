"""
Caso de uso para convertir archivos PDF a formato Markdown utilizando PyMuPDF4LLM y OCR si es necesario.

Este módulo forma parte de la capa de dominio y contiene lógica de negocio independiente de infraestructura.
Se encarga de coordinar la extracción de contenido (a través del adaptador) y el guardado (a través de la infraestructura).
"""
from pathlib import Path
from adapters.pymupdf_adapter import extract_markdown
from infrastructure.file_storage import save_markdown
import markdown2
from jinja2 import Template

def convert_pdf_to_md(pdf_path: Path) -> Path:
    """
    Convierte un archivo PDF en un archivo Markdown, utilizando extracción inteligente (digital u OCR)
    y guarda el resultado en el sistema de archivos.

    Args:
        pdf_path (Path): Ruta al archivo PDF de entrada.

    Returns:
        Path: Ruta al archivo Markdown generado y almacenado.
    """
    markdown = extract_markdown(pdf_path)
    md_path = save_markdown(pdf_path.stem, markdown)
    return md_path

def convert_pdf_to_html(pdf_path: Path) -> Path:
    """
    Convierte un PDF a HTML con formato estructurado (basado en plantilla).
    """
    markdown = extract_markdown(pdf_path)
    body_html = markdown2.markdown(markdown)

    # Plantilla HTML base
    html_template = Template("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 2em;
                line-height: 1.6;
            }
            h1, h2, h3 {
                color: #003366;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
            }
            th, td {
                border: 1px solid #999;
                padding: 0.5em;
                text-align: left;
            }
            hr {
                margin: 2em 0;
                border: none;
                border-top: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        {{ content }}
    </body>
    </html>
    """)

    html = html_template.render(
        title=pdf_path.stem,
        content=body_html
    )

    html_path = Path("resultado") / f"{pdf_path.stem}.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path


# ──────────────────────────────────────────────────────────────
# Nueva función: OCR directo a HTML desde PDF escaneado
def convert_pdf_scanned_direct_to_html(pdf_path: Path) -> Path:
    """
    Realiza OCR directamente desde las páginas escaneadas del PDF y convierte el texto a HTML.
    Se salta la conversión intermedia a Markdown.

    Args:
        pdf_path (Path): Ruta al archivo PDF.

    Returns:
        Path: Ruta al archivo HTML generado.
    """
    import fitz
    from adapters.ocr_adapter import perform_ocr_on_page
    from jinja2 import Template

    body_parts = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = perform_ocr_on_page(page)
            text_html = text.strip().replace("\n", "<br>")
            body_parts.append(f"<h2>Página {i}</h2>\n<p>{text_html}</p>")

    html_template = Template("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 2em;
                line-height: 1.6;
            }
            h1, h2 {
                color: #003366;
            }
            p {
                margin-bottom: 1em;
            }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        {{ content | safe }}
    </body>
    </html>
    """)

    html = html_template.render(
        title=pdf_path.stem,
        content="\n".join(body_parts)
    )

    html_path = Path("resultado") / f"{pdf_path.stem}_ocr.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path