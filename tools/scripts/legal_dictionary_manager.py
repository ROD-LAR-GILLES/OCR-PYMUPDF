#!/usr/bin/env python3
"""
Legal Dictionary Manager
-----------------------
Script para mantener organizado el diccionario de términos legales.

Funcionalidades:
- Elimina duplicados
- Organiza alfabéticamente
- Categoriza términos
- Valida formato
- Añade términos nuevos
"""

import re
from pathlib import Path
from typing import Dict, List, Set

# Categorías de términos legales
CATEGORIES = {
    "DOCUMENTOS": [
        "ACTA", "CONTRATO", "DECRETO", "RESOLUCION", "OFICIO", "CIRCULAR", "DOCUMENTO",
        "EXPEDIENTE", "INFORME", "MEMORIAL", "DICTAMEN", "CEDULA", "CERTIFICADO"
    ],
    "PROCEDIMIENTOS": [
        "LICITACION", "TRAMITACION", "ADJUDICACION", "APELACION", "NOTIFICACION",
        "EJECUCION", "PROCESO", "PROCEDIMIENTO", "AUDIENCIA", "DILIGENCIA"
    ],
    "ENTIDADES": [
        "MINISTERIO", "SECRETARIA", "SUBSECRETARIA", "DIRECCION", "DEPARTAMENTO",
        "TRIBUNAL", "CORTE", "JUZGADO", "FISCALIA", "SUPERINTENDENCIA"
    ],
    "ACCIONES": [
        "ADJUDICAR", "AUTORIZAR", "CERTIFICAR", "DECRETAR", "EJECUTAR", "NOTIFICAR",
        "RESOLVER", "TRAMITAR", "APELAR", "RECURRIR"
    ],
    "ROLES": [
        "ABOGADO", "JUEZ", "FISCAL", "NOTARIO", "SECRETARIO", "MINISTRO", "DIRECTOR",
        "SUBDIRECTOR", "JEFE", "COORDINADOR"
    ],
    "ESTADOS": [
        "VIGENTE", "APROBADO", "RECHAZADO", "PENDIENTE", "FINALIZADO", "SUSPENDIDO",
        "ANULADO", "REVOCADO", "ACTIVO", "CADUCADO"
    ]
}

# Términos adicionales comunes en documentos legales
ADDITIONAL_TERMS = [
    # Términos de validez
    "VALIDO", "INVALIDO", "NULO", "VIGENTE", "VENCIDO",
    
    # Términos de tiempo
    "PLAZO", "TERMINO", "VENCIMIENTO", "PRORROGA", "PRESCRIPCION",
    
    # Términos de obligación
    "DEBER", "OBLIGACION", "DERECHO", "FACULTAD", "POTESTAD",
    
    # Términos de sanción
    "MULTA", "SANCION", "PENALIDAD", "CASTIGO", "INHABILITACION",
    
    # Términos de validación
    "AUTENTICAR", "LEGALIZAR", "VALIDAR", "VERIFICAR", "CERTIFICAR"
]

class LegalDictionaryManager:
    def __init__(self, dictionary_path: Path):
        self.dictionary_path = dictionary_path
        self.terms: Set[str] = set()
        self.categorized_terms: Dict[str, List[str]] = {}
        
    def load_current_dictionary(self) -> None:
        """Carga el diccionario actual."""
        if self.dictionary_path.exists():
            self.terms = set(self.dictionary_path.read_text().splitlines())
    
    def add_category_terms(self) -> None:
        """Añade términos de las categorías definidas."""
        for category, terms in CATEGORIES.items():
            self.terms.update(terms)
            self.categorized_terms[category] = sorted(terms)
    
    def add_additional_terms(self) -> None:
        """Añade términos adicionales comunes."""
        self.terms.update(ADDITIONAL_TERMS)
    
    def clean_and_validate(self) -> None:
        """Limpia y valida los términos."""
        cleaned_terms = set()
        for term in self.terms:
            # Eliminar espacios y convertir a mayúsculas
            term = term.strip().upper()
            
            # Ignorar líneas vacías o comentarios
            if not term or term.startswith("#"):
                continue
                
            # Validar formato (solo letras, números y algunos caracteres especiales)
            if re.match(r'^[A-Z0-9\-_.]+$', term):
                cleaned_terms.add(term)
        
        self.terms = cleaned_terms
    
    def save_dictionary(self) -> None:
        """Guarda el diccionario organizado."""
        # Preparar contenido con categorías
        content = []
        
        # Añadir encabezado
        content.append("# Diccionario de Términos Legales")
        content.append("# ============================")
        content.append("")
        
        # Añadir términos por categoría
        for category, terms in self.categorized_terms.items():
            content.append(f"# {category}")
            content.append("# " + "-" * len(category))
            content.extend(sorted(terms))
            content.append("")
        
        # Añadir términos no categorizados
        uncategorized = self.terms - {term for terms in self.categorized_terms.values() for term in terms}
        if uncategorized:
            content.append("# OTROS TÉRMINOS")
            content.append("# -------------")
            content.extend(sorted(uncategorized))
        
        # Guardar archivo
        self.dictionary_path.write_text("\n".join(content))
        
    def process_dictionary(self) -> None:
        """Procesa el diccionario completo."""
        self.load_current_dictionary()
        self.add_category_terms()
        self.add_additional_terms()
        self.clean_and_validate()
        self.save_dictionary()

def main():
    """Función principal."""
    # Obtener la ruta del directorio raíz del proyecto
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent  # Subir dos niveles desde tools/scripts
    dictionary_path = script_dir / "data" / "dictionaries" / "legal_words.txt"
    
    manager = LegalDictionaryManager(dictionary_path)
    manager.process_dictionary()
    print(f"Diccionario actualizado: {dictionary_path}")

if __name__ == "__main__":
    main()
