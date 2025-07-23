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
- Manejo de errores robusto 
- Logging de operaciones 
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('legal_dictionary.log')
    ]
)
logger = logging.getLogger(__name__)

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
    """Gestor del diccionario de términos legales."""
    
    def __init__(self, dictionary_path: Path):
        self.dictionary_path = dictionary_path
        self.terms: Set[str] = set()
        self.categorized_terms: Dict[str, List[str]] = {}
        logger.info(f"Inicializando gestor de diccionario: {dictionary_path}")
        
    def load_current_dictionary(self) -> None:
        """Carga el diccionario actual."""
        try:
            if self.dictionary_path.exists():
                content = self.dictionary_path.read_text(encoding='utf-8')
                self.terms = set(line.strip() for line in content.splitlines() if line.strip())
                logger.info(f"Diccionario cargado: {len(self.terms)} términos encontrados")
            else:
                logger.info("No se encontró diccionario existente, creando uno nuevo")
                # Crear directorio si no existe
                self.dictionary_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error al cargar diccionario: {e}")
            raise
    
    def add_category_terms(self) -> None:
        """Añade términos de las categorías definidas."""
        try:
            initial_count = len(self.terms)
            for category, terms in CATEGORIES.items():
                self.terms.update(terms)
                self.categorized_terms[category] = sorted(terms)
                logger.debug(f"Categoría {category}: {len(terms)} términos añadidos")
            
            added_count = len(self.terms) - initial_count
            logger.info(f"Términos de categorías añadidos: {added_count}")
        except Exception as e:
            logger.error(f"Error al añadir términos de categorías: {e}")
            raise
    
    def add_additional_terms(self) -> None:
        """Añade términos adicionales comunes."""
        try:
            initial_count = len(self.terms)
            self.terms.update(ADDITIONAL_TERMS)
            added_count = len(self.terms) - initial_count
            logger.info(f"Términos adicionales añadidos: {added_count}")
        except Exception as e:
            logger.error(f"Error al añadir términos adicionales: {e}")
            raise
    
    def clean_and_validate(self) -> None:
        """Limpia y valida los términos."""
        try:
            initial_count = len(self.terms)
            cleaned_terms = set()
            invalid_terms = []
            
            for term in self.terms:
                # Eliminar espacios y convertir a mayúsculas
                term = term.strip().upper()
                
                # Ignorar líneas vacías o comentarios
                if not term or term.startswith("#"):
                    continue
                    
                # Validar formato (solo letras, números y algunos caracteres especiales)
                if re.match(r'^[A-Z0-9\-_.]+$', term):
                    cleaned_terms.add(term)
                else:
                    invalid_terms.append(term)
            
            self.terms = cleaned_terms
            removed_count = initial_count - len(cleaned_terms)
            
            logger.info(f"Términos limpiados: {removed_count} términos removidos")
            if invalid_terms:
                logger.warning(f"Términos inválidos encontrados: {invalid_terms[:10]}...")
                
        except Exception as e:
            logger.error(f"Error al limpiar y validar términos: {e}")
            raise
    
    def save_dictionary(self) -> None:
        """Guarda el diccionario organizado."""
        try:
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
            self.dictionary_path.parent.mkdir(parents=True, exist_ok=True)
            self.dictionary_path.write_text("\n".join(content), encoding='utf-8')
            logger.info(f"Diccionario guardado en: {self.dictionary_path}")
            logger.info(f"Total de términos: {len(self.terms)}")
            logger.info(f"Términos categorizados: {sum(len(terms) for terms in self.categorized_terms.values())}")
            logger.info(f"Términos no categorizados: {len(uncategorized)}")
        except Exception as e:
            logger.error(f"Error al guardar diccionario: {e}")
            raise
        
    def process_dictionary(self) -> None:
        """Procesa el diccionario completo."""
        self.load_current_dictionary()
        self.add_category_terms()
        self.add_additional_terms()
        self.clean_and_validate()
        self.save_dictionary()

def main():
    """Función principal."""
    try:
        # Obtener la ruta del directorio raíz del proyecto
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent  # Subir un nivel desde scripts
        dictionary_path = project_root / "dictionaries" / "legal_words.txt"
        
        logger.info(f"Iniciando procesamiento del diccionario: {dictionary_path}")
        manager = LegalDictionaryManager(dictionary_path)
        manager.process_dictionary()
        logger.info(f"Procesamiento completado exitosamente")
        print(f"Diccionario actualizado: {dictionary_path}")
        return 0
    except Exception as e:
        logger.critical(f"Error fatal durante el procesamiento: {e}")
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    main()
