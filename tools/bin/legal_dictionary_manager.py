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

Uso:
  python tools/bin/legal_dictionary_manager.py [opciones]

Opciones:
  --add TERM     Añadir un nuevo término al diccionario
  --category CAT Especificar categoría al añadir un término
  --list         Listar todos los términos
  --update       Actualizar y reorganizar el diccionario
  --help         Mostrar esta ayuda
"""

import argparse
import re
import sys
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
    
    def add_term(self, term: str, category: str = None) -> bool:
        """Añade un nuevo término al diccionario."""
        term = term.strip().upper()
        
        # Validar formato
        if not re.match(r'^[A-Z0-9\-_.]+$', term):
            print(f"Error: El término '{term}' contiene caracteres no válidos.")
            return False
            
        # Verificar si ya existe
        if term in self.terms:
            print(f"El término '{term}' ya existe en el diccionario.")
            return False
            
        # Añadir a la categoría si se especificó
        if category:
            category = category.upper()
            if category not in CATEGORIES:
                print(f"Error: La categoría '{category}' no existe.")
                print(f"Categorías disponibles: {', '.join(CATEGORIES.keys())}")
                return False
                
            self.categorized_terms.setdefault(category, []).append(term)
            
        # Añadir al conjunto general
        self.terms.add(term)
        print(f"Término '{term}' añadido correctamente.")
        return True
    
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
    
    def list_terms(self) -> None:
        """Lista todos los términos del diccionario."""
        self.load_current_dictionary()
        
        if not self.terms:
            print("El diccionario está vacío.")
            return
            
        print("\nDiccionario de Términos Legales:")
        print("============================\n")
        
        # Organizar por categorías
        self.add_category_terms()
        
        for category, terms in self.categorized_terms.items():
            print(f"\n{category}:")
            print("-" * len(category))
            for term in sorted(terms):
                print(f"  {term}")
        
        # Mostrar términos no categorizados
        uncategorized = self.terms - {term for terms in self.categorized_terms.values() for term in terms}
        if uncategorized:
            print("\nOTROS TÉRMINOS:")
            print("-------------")
            for term in sorted(uncategorized):
                print(f"  {term}")
    
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
        
        # Asegurar que el directorio existe
        self.dictionary_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        self.dictionary_path.write_text("\n".join(content))
        print(f"Diccionario actualizado: {self.dictionary_path}")
        
    def process_dictionary(self) -> None:
        """Procesa el diccionario completo."""
        self.load_current_dictionary()
        self.add_category_terms()
        self.add_additional_terms()
        self.clean_and_validate()
        self.save_dictionary()

def parse_arguments():
    """Analiza los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Gestor de Diccionario Legal")
    parser.add_argument("--add", help="Añadir un nuevo término al diccionario")
    parser.add_argument("--category", help="Especificar categoría al añadir un término")
    parser.add_argument("--list", action="store_true", help="Listar todos los términos")
    parser.add_argument("--update", action="store_true", help="Actualizar y reorganizar el diccionario")
    parser.add_argument("--path", default="data/legal_words.txt", help="Ruta al archivo del diccionario")
    
    return parser.parse_args()

def main():
    """Función principal."""
    args = parse_arguments()
    
    # Obtener la ruta del proyecto
    project_root = Path(__file__).parent.parent.parent
    dictionary_path = project_root / args.path
    
    manager = LegalDictionaryManager(dictionary_path)
    
    if args.list:
        manager.list_terms()
    elif args.add:
        manager.load_current_dictionary()
        if manager.add_term(args.add, args.category):
            manager.save_dictionary()
    elif args.update or len(sys.argv) == 1:
        manager.process_dictionary()
    else:
        print("Uso: python legal_dictionary_manager.py [opciones]")
        print("Ejecute con --help para ver las opciones disponibles.")

if __name__ == "__main__":
    main()