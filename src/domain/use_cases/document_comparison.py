"""Caso de uso para comparar diferentes versiones de documentos PDF.

Permite identificar diferencias entre dos versiones de un mismo documento,
mostrando cambios en texto, estructura y contenido.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import difflib
import re

from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.dtos.document_dtos import DocumentComparisonDTO, DocumentDiffDTO

class DocumentComparisonUseCase:
    """Caso de uso para comparar diferentes versiones de documentos."""
    
    def __init__(
        self,
        document_port: DocumentPort,
        storage_port: StoragePort
    ) -> None:
        """Inicializa el caso de uso.

        Args:
            document_port: Puerto para operaciones con documentos
            storage_port: Puerto para almacenamiento de resultados
        """
        self.document_port = document_port
        self.storage_port = storage_port
    
    def execute(
        self,
        original_pdf_path: Path,
        new_pdf_path: Path,
        output_path: Optional[Path] = None
    ) -> DocumentComparisonDTO:
        """Compara dos versiones de un documento PDF.

        Args:
            original_pdf_path: Ruta al PDF original
            new_pdf_path: Ruta al PDF nuevo
            output_path: Ruta opcional para guardar el informe de diferencias

        Returns:
            DTO con resultados de la comparación
        """
        # Extraer contenido de ambos documentos
        original_pages = self.document_port.extract_pages(original_pdf_path)
        new_pages = self.document_port.extract_pages(new_pdf_path)

        # Extraer metadatos
        original_metadata = self.document_port.extract_metadata(original_pdf_path)
        new_metadata = self.document_port.extract_metadata(new_pdf_path)

        # Comparar contenido página por página
        page_diffs = self._compare_pages(original_pages, new_pages)

        # Generar informe de diferencias
        comparison_result = DocumentComparisonDTO(
            original_path=str(original_pdf_path),
            new_path=str(new_pdf_path),
            original_pages=len(original_pages),
            new_pages=len(new_pages),
            page_differences=page_diffs,
            metadata_changes=self._compare_metadata(original_metadata, new_metadata)
        )

        # Guardar informe si se especificó una ruta
        if output_path:
            markdown_report = self._generate_markdown_report(comparison_result)
            self.storage_port.save_markdown(markdown_report, output_path)
            comparison_result.report_path = str(output_path)

        return comparison_result

    def _compare_pages(
        self,
        original_pages: List[str],
        new_pages: List[str]
    ) -> List[DocumentDiffDTO]:
        """Compara el contenido de las páginas entre dos versiones.

        Args:
            original_pages: Lista de contenido de páginas originales
            new_pages: Lista de contenido de páginas nuevas

        Returns:
            Lista de diferencias por página
        """
        result = []

        # Determinar el número de páginas a comparar
        max_pages = max(len(original_pages), len(new_pages))

        for i in range(max_pages):
            # Manejar caso donde una versión tiene más páginas que la otra
            original_content = original_pages[i] if i < len(original_pages) else ""
            new_content = new_pages[i] if i < len(new_pages) else ""

            # Si ambos contenidos son idénticos, no hay diferencias
            if original_content == new_content:
                continue

            # Calcular diferencias usando difflib
            diff = list(difflib.ndiff(
                self._normalize_text(original_content).splitlines(),
                self._normalize_text(new_content).splitlines()
            ))

            # Contar cambios
            additions = len([line for line in diff if line.startswith('+ ')])
            deletions = len([line for line in diff if line.startswith('- ')])
            changes = len([line for line in diff if line.startswith('? ')])

            # Crear DTO de diferencias para esta página
            page_diff = DocumentDiffDTO(
                page_number=i + 1,  # 1-indexed para usuarios
                additions=additions,
                deletions=deletions,
                changes=changes,
                diff_text="\n".join(diff) if (additions + deletions + changes) > 0 else ""
            )

            result.append(page_diff)

        return result

    def _compare_metadata(
        self,
        original_metadata,
        new_metadata
    ) -> Dict[str, Tuple[str, str]]:
        """Compara los metadatos entre dos versiones.

        Args:
            original_metadata: Metadatos del documento original
            new_metadata: Metadatos del documento nuevo

        Returns:
            Diccionario con cambios en metadatos
        """
        changes = {}

        # Comparar atributos comunes
        for attr in ['title', 'author', 'producer']:
            original_value = getattr(original_metadata, attr, None)
            new_value = getattr(new_metadata, attr, None)

            if original_value != new_value:
                changes[attr] = (str(original_value), str(new_value))

        # Comparar fechas
        for attr in ['creation_date', 'modification_date']:
            original_date = getattr(original_metadata, attr, None)
            new_date = getattr(new_metadata, attr, None)

            if original_date != new_date:
                original_str = original_date.isoformat() if original_date else "None"
                new_str = new_date.isoformat() if new_date else "None"
                changes[attr] = (original_str, new_str)

        return changes

    def _normalize_text(self, text: str) -> str:
        """Normaliza el texto para comparación más precisa.

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado
        """
        # Eliminar espacios en blanco múltiples
        text = re.sub(r'\s+', ' ', text)

        # Eliminar espacios al inicio y final de líneas
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)

        return text.strip()

    def _generate_markdown_report(self, comparison: DocumentComparisonDTO) -> str:
        """Genera un informe en formato Markdown con los resultados de la comparación.

        Args:
            comparison: Resultados de la comparación

        Returns:
            Informe en formato Markdown
        """
        lines = []

        # Encabezado
        lines.append("# Informe de Comparación de Documentos\n")
        lines.append("## Resumen\n")
        lines.append(f"- **Documento Original**: {comparison.original_path}")
        lines.append(f"- **Documento Nuevo**: {comparison.new_path}")
        lines.append(f"- **Páginas Original**: {comparison.original_pages}")
        lines.append(f"- **Páginas Nuevo**: {comparison.new_pages}")
        lines.append(f"- **Páginas con Diferencias**: {len(comparison.page_differences)}\n")

        # Cambios en metadatos
        if comparison.metadata_changes:
            lines.append("## Cambios en Metadatos\n")
            lines.append("| Campo | Valor Original | Valor Nuevo |")
            lines.append("| ----- | -------------- | ----------- |")

            for field, (original, new) in comparison.metadata_changes.items():
                lines.append(f"| {field} | {original} | {new} |")

            lines.append("\n")

        # Diferencias por página
        if comparison.page_differences:
            lines.append("## Diferencias por Página\n")

            for diff in comparison.page_differences:
                lines.append(f"### Página {diff.page_number}\n")
                lines.append(f"- **Adiciones**: {diff.additions}")
                lines.append(f"- **Eliminaciones**: {diff.deletions}")
                lines.append(f"- **Cambios**: {diff.changes}\n")

                if diff.diff_text:
                    lines.append("```diff")
                    lines.append(diff.diff_text)
                    lines.append("```\n")

        return "\n".join(lines)