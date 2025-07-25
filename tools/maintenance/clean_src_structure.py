#!/usr/bin/env python3
"""
Script para limpiar y reorganizar la estructura src/ siguiendo Clean Architecture.
"""
import os
import shutil
import subprocess
from pathlib import Path

class SrcCleaner:
    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.duplicates_removed = []
        self.empty_dirs_removed = []
        
    def clean_empty_files(self):
        """Elimina archivos Python vacíos."""
        print(" Eliminando archivos vacíos...")
        empty_files = []
        
        for py_file in self.src_path.rglob("*.py"):
            if py_file.stat().st_size == 0:
                empty_files.append(py_file)
                py_file.unlink()
                
        print(f"    {len(empty_files)} archivos vacíos eliminados")
        return empty_files
    
    def remove_duplicates(self):
        """Elimina archivos duplicados manteniendo la versión en la ubicación correcta."""
        print(" Identificando y eliminando duplicados...")
        
        # Reglas de duplicados: mantener la versión en la ubicación más apropiada para Clean Architecture
        duplicate_rules = {
            # LLM adapters - mantener en adapters/out/llm/
            "llm_refiner.py": ["adapters/out/llm/llm_refiner.py"],
            "deepseek_api.py": ["adapters/out/llm/deepseek_api.py"],
            "deepseek_provider.py": ["adapters/out/llm/deepseek_provider.py"],
            "openai_provider.py": ["adapters/out/llm/openai_provider.py"],
            "gemini_provider.py": ["adapters/out/llm/gemini_provider.py"],
            "gemini_adapter.py": ["adapters/out/llm/gemini_adapter.py"],
            
            # OCR adapters - mantener en adapters/out/ocr/
            "ocr_adapter.py": ["adapters/out/ocr/ocr_adapter.py"],
            "pymupdf_adapter.py": ["adapters/out/ocr/pymupdf_adapter.py"],
            "parallel_ocr.py": ["adapters/out/ocr/parallel_ocr.py"],
            
            # Storage - mantener en adapters/out/storage/
            "file_storage.py": ["adapters/out/storage/file_storage.py"],
            
            # Infrastructure HTTP
            "aiohttp_client.py": ["infrastructure/http/aiohttp_client.py"],
            "requests_client.py": ["infrastructure/http/requests_client.py"],
            
            # Use cases - mantener en application/use_cases/
            "use_cases.py": ["application/use_cases/use_cases.py"],
            
            # Interfaces - mantener en adapters/inbound/
            "cli_menu.py": ["adapters/inbound/cli/cli_menu.py"],
            "config_menu.py": ["adapters/inbound/cli/config_menu.py"],
            "api_server.py": ["adapters/inbound/http/api/api_server.py"],
            
            # Config
            "llm_keys_check.py": ["config/llm_keys_check.py"],
        }
        
        for filename, keep_paths in duplicate_rules.items():
            # Buscar todas las instancias del archivo
            all_instances = list(self.src_path.rglob(filename))
            
            if len(all_instances) <= 1:
                continue
                
            # Determinar cuál mantener
            keep_file = None
            for instance in all_instances:
                relative_path = str(instance.relative_to(self.src_path))
                if relative_path in keep_paths:
                    keep_file = instance
                    break
            
            # Si no encontramos la ubicación preferida, mantener la primera con contenido
            if not keep_file:
                for instance in all_instances:
                    if instance.stat().st_size > 0:
                        keep_file = instance
                        break
            
            # Eliminar duplicados
            for instance in all_instances:
                if instance != keep_file and instance.exists():
                    print(f"     Eliminando duplicado: {instance.relative_to(self.src_path)}")
                    instance.unlink()
                    self.duplicates_removed.append(str(instance.relative_to(self.src_path)))
        
        print(f"    {len(self.duplicates_removed)} duplicados eliminados")
    
    def clean_empty_directories(self):
        """Elimina directorios vacíos."""
        print(" Eliminando directorios vacíos...")
        
        def remove_empty_dirs(path):
            if not path.is_dir():
                return False
            
            # Primero limpiar subdirectorios
            for subdir in path.iterdir():
                if subdir.is_dir():
                    remove_empty_dirs(subdir)
            
            # Luego verificar si este directorio está vacío
            try:
                if not any(path.iterdir()):  # Si está vacío
                    print(f"     Eliminando directorio vacío: {path.relative_to(self.src_path)}")
                    path.rmdir()
                    self.empty_dirs_removed.append(str(path.relative_to(self.src_path)))
                    return True
            except OSError:
                pass
            return False
        
        # Hacer múltiples pasadas para limpiar directorios anidados vacíos
        for _ in range(5):
            for subdir in self.src_path.rglob("*"):
                if subdir.is_dir() and subdir != self.src_path:
                    remove_empty_dirs(subdir)
        
        print(f"    {len(self.empty_dirs_removed)} directorios vacíos eliminados")
    
    def create_proper_init_files(self):
        """Crea archivos __init__.py apropiados donde sean necesarios."""
        print(" Creando archivos __init__.py necesarios...")
        
        # Directorios que necesitan __init__.py
        required_dirs = [
            "src",
            "src/domain",
            "src/domain/entities",
            "src/domain/value_objects", 
            "src/domain/ports",
            "src/domain/exceptions",
            "src/application",
            "src/application/use_cases",
            "src/adapters",
            "src/adapters/inbound",
            "src/adapters/inbound/cli",
            "src/adapters/inbound/http",
            "src/adapters/inbound/http/api",
            "src/adapters/out",
            "src/adapters/out/llm",
            "src/adapters/out/ocr",
            "src/adapters/out/storage",
            "src/infrastructure",
            "src/infrastructure/http",
            "src/config"
        ]
        
        created = 0
        for dir_path in required_dirs:
            full_path = Path(dir_path)
            if full_path.exists() and full_path.is_dir():
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""Package initialization."""\n')
                    created += 1
                    print(f"    Creado: {init_file}")
        
        print(f"    {created} archivos __init__.py creados")
    
    def organize_by_clean_architecture(self):
        """Reorganiza archivos siguiendo Clean Architecture."""
        print("  Organizando según Clean Architecture...")
        
        # Verificar que los directorios principales existan
        main_dirs = [
            "domain/entities",
            "domain/value_objects",
            "domain/ports", 
            "domain/exceptions",
            "application/use_cases",
            "adapters/inbound/cli",
            "adapters/inbound/http/api",
            "adapters/out/llm",
            "adapters/out/ocr", 
            "adapters/out/storage",
            "infrastructure/http",
            "config"
        ]
        
        for dir_path in main_dirs:
            full_path = self.src_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        print("    Estructura de directorios verificada")
    
    def run_cleanup(self):
        """Ejecuta todo el proceso de limpieza."""
        print(" Iniciando limpieza de estructura src/")
        print("=" * 50)
        
        # 1. Eliminar archivos vacíos
        self.clean_empty_files()
        
        # 2. Organizar estructura
        self.organize_by_clean_architecture()
        
        # 3. Eliminar duplicados
        self.remove_duplicates()
        
        # 4. Limpiar directorios vacíos
        self.clean_empty_directories()
        
        # 5. Crear __init__.py necesarios
        self.create_proper_init_files()
        
        print("=" * 50)
        print("✨ Limpieza completada!")
        print(f"  Resumen:")
        print(f"   • {len(self.duplicates_removed)} duplicados eliminados")
        print(f"   • {len(self.empty_dirs_removed)} directorios vacíos eliminados")
        
        return {
            "duplicates_removed": self.duplicates_removed,
            "empty_dirs_removed": self.empty_dirs_removed
        }

if __name__ == "__main__":
    cleaner = SrcCleaner()
    result = cleaner.run_cleanup()
