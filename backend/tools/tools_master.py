#!/usr/bin/env python3
"""
Herramienta Maestra de Testing y Mantenimiento - OCR-PYMUPDF

Esta herramienta unifica todas las funciones de testing, calidad,
mantenimiento y diagnóstico del proyecto.
"""

import sys
import argparse
from pathlib import Path
import subprocess
import os

# Configuración de rutas
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
TOOLS_DIR = SCRIPT_DIR

# Agregar directorio del proyecto al path
sys.path.insert(0, str(PROJECT_ROOT))


class ToolsMaster:
    """Controlador maestro de herramientas."""
    
    def __init__(self):
        """Inicializar el controlador maestro."""
        self.tools_dir = TOOLS_DIR
        self.project_root = PROJECT_ROOT
        
    def run_maintenance_tool(self, tool, *args):
        """Ejecutar herramienta de mantenimiento."""
        tool_path = self.tools_dir / "maintenance" / tool
        return self._run_tool(tool_path, *args)
        
    def run_quality_tool(self, tool, *args):
        """Ejecutar herramienta de calidad."""
        tool_path = self.tools_dir / "quality" / tool
        return self._run_tool(tool_path, *args)
        
    def run_diagnostic_tool(self, tool, *args):
        """Ejecutar herramienta de diagnóstico."""
        tool_path = self.tools_dir / "diagnostics" / tool
        return self._run_tool(tool_path, *args)
        
    def run_security_tool(self, tool, *args):
        """Ejecutar herramienta de seguridad."""
        tool_path = self.tools_dir / "security" / tool
        return self._run_tool(tool_path, *args)
        
    def run_performance_tool(self, tool, *args):
        """Ejecutar herramienta de rendimiento."""
        tool_path = self.tools_dir / "performance" / tool
        return self._run_tool(tool_path, *args)
        
    def run_unit_test_tool(self, tool, *args):
        """Ejecutar herramienta de tests."""
        tool_path = self.tools_dir / "tests" / tool
        return self._run_tool(tool_path, *args)
        
    def run_integration_test_tool(self, tool, *args):
        """Ejecutar herramienta de tests de integración."""
        tool_path = self.tools_dir / "tests" / tool
        return self._run_tool(tool_path, *args)
        
    def _run_tool(self, tool_path, *args):
        """Ejecutar una herramienta específica."""
        if not tool_path.exists():
            print(f"  Error: Herramienta no encontrada: {tool_path}")
            return 1
            
        # Cambiar al directorio del proyecto para ejecutar
        old_cwd = os.getcwd()
        try:
            os.chdir(self.project_root)
            
            if tool_path.suffix == '.py':
                cmd = [sys.executable, str(tool_path)] + list(args)
            else:
                cmd = [str(tool_path)] + list(args)
                
            print(f"  Ejecutando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=False)
            return result.returncode
            
        finally:
            os.chdir(old_cwd)
            
    def list_tools(self):
        """Listar todas las herramientas disponibles."""
        categories = {
            "maintenance": "Mantenimiento de Código",
            "quality": "Análisis de Calidad", 
            "diagnostics": "Diagnóstico",
            "security": "Seguridad",
            "performance": "Rendimiento",
            "tests": "Tests (Unitarios e Integración)"
        }
        
        print(" ️  Herramientas Disponibles")
        print("=" * 50)
        
        for category, description in categories.items():
            category_path = self.tools_dir / category
            if category_path.exists():
                tools = list(category_path.glob("*"))
                tools = [t for t in tools if t.is_file() and not t.name.startswith('.')]
                
                if tools:
                    print(f"\n  {description}:")
                    for tool in sorted(tools):
                        print(f"   • {tool.name}")
                        
    def run_maintenance_suite(self):
        """Ejecutar suite completa de mantenimiento."""
        print("  Ejecutando Suite de Mantenimiento")
        print("=" * 40)
        
        steps = [
            ("clean_emojis.py", "--dry-run"),
            ("code_maintenance.sh", "--check-emojis"),
            ("format_code.sh", "--dry-run"),
        ]
        
        for tool, *args in steps:
            print(f"\n▶️  {tool}")
            result = self.run_maintenance_tool(tool, *args)
            if result != 0:
                print(f"  Error en {tool}")
                return result
                
        return 0
        
    def run_quality_suite(self):
        """Ejecutar suite completa de calidad."""
        print("  Ejecutando Suite de Calidad")
        print("=" * 40)
        
        steps = [
            ("lint_code.sh", "--quick"),
            ("quality_report.sh",),
        ]
        
        for tool, *args in steps:
            print(f"\n▶️  {tool}")
            result = self.run_quality_tool(tool, *args)
            if result != 0:
                print(f" ️  Advertencia en {tool}")
                
        return 0


def main():
    """Función principal CLI."""
    parser = argparse.ArgumentParser(
        description="Herramienta Maestra de Testing y Mantenimiento",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s --list                           # Listar herramientas
  %(prog)s --maintenance-suite              # Suite de mantenimiento
  %(prog)s --quality-suite                  # Suite de calidad
  %(prog)s --run maintenance clean_emojis.py --dry-run
  %(prog)s --run quality lint_code.sh --quick
        """
    )
    
    parser.add_argument('--list', action='store_true', 
                       help='Listar todas las herramientas disponibles')
    parser.add_argument('--maintenance-suite', action='store_true',
                       help='Ejecutar suite completa de mantenimiento')
    parser.add_argument('--quality-suite', action='store_true',
                       help='Ejecutar suite completa de calidad')
    parser.add_argument('--run', nargs='+', metavar=('CATEGORY', 'TOOL'),
                       help='Ejecutar herramienta específica: CATEGORY TOOL [ARGS...]')
    parser.add_argument('remaining_args', nargs='*', 
                       help='Argumentos adicionales para la herramienta')
    
    args, unknown_args = parser.parse_known_args()
    
    master = ToolsMaster()
    
    if args.list:
        master.list_tools()
        return 0
        
    if args.maintenance_suite:
        return master.run_maintenance_suite()
        
    if args.quality_suite:
        return master.run_quality_suite()
        
    if args.run:
        if len(args.run) < 2:
            print("  Error: --run requiere al menos CATEGORY y TOOL")
            return 1
            
        category = args.run[0]
        tool = args.run[1]
        tool_args = args.run[2:] + unknown_args if len(args.run) > 2 else unknown_args
        
        method_map = {
            'maintenance': master.run_maintenance_tool,
            'quality': master.run_quality_tool,
            'diagnostics': master.run_diagnostic_tool,
            'security': master.run_security_tool,
            'performance': master.run_performance_tool,
            'tests': master.run_unit_test_tool,
        }
        
        if category not in method_map:
            print(f"  Error: Categoría desconocida: {category}")
            print(f"Categorías disponibles: {', '.join(method_map.keys())}")
            return 1
            
        return method_map[category](tool, *tool_args)
        
    # Si no se especifica nada, mostrar ayuda
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
