"""OCR-PYMUPDF System CLI.

Features:
1. List PDFs
2. Convert to Markdown
3. Compare Documents
4. Configuration
5. Exit
"""

import sys
import os
import signal
from pathlib import Path
from time import sleep
from loguru import logger
from application.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from application.use_cases.document_comparison import DocumentComparisonUseCase
from adapters.inbound.cli.config_menu import ConfigMenu
from config.llm_config import LLMConfig
from adapters.out.ocr.pymupdf_adapter import PyMuPDFAdapter
from adapters.out.llm.llm_refiner import LLMRefiner
from adapters.out.storage.file_storage import FileStorage

PDF_DIR = Path("pdfs")

def _show_llm_status() -> None:
    """Display current LLM configuration status."""
    provider = LLMConfig.get_current_provider()
    status = "Disabled" if provider is None else f"Enabled ({provider})"
    print(f"\nLLM Processing: {status}")

def _convert_pdf(pdf_path: Path) -> None:
    """Convert PDF to Markdown using current configuration."""
    logger.info(f"Converting to Markdown: {pdf_path}")
    try:
        # Initialize basic ports
        document_port = PyMuPDFAdapter()
        storage_port = FileStorage()
        llm_port = None
        
        # Configurar LLM solo si está activado
        provider_name = LLMConfig.get_current_provider()
        if provider_name:
            # Importar el proveedor específico
            if provider_name == "openai":
                from adapters.providers.openai_provider import OpenAIProvider
                provider = OpenAIProvider()
            elif provider_name == "gemini":
                from adapters.providers.gemini_provider import GeminiProvider
                provider = GeminiProvider()
            elif provider_name == "deepseek":
                from adapters.providers.deepseek_provider import DeepSeekProvider
                provider = DeepSeekProvider()
            
            # Intentar inicializar el proveedor LLM
            try:
                # Obtener la configuración del proveedor
                from config.api_settings import load_api_settings
                api_config = load_api_settings()
                
                if provider_name not in api_config:
                    raise ValueError(f"No configuration found for {provider_name}")
                    
                provider.initialize(api_config[provider_name])
                llm_port = LLMRefiner(provider)
                logger.info(f"Using LLM refinement with {provider_name}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM provider: {e}")
                logger.info("Falling back to traditional processing")
                llm_port = None
        else:
            logger.info("Using traditional processing without LLM refinement")
        
        # Create and execute use case with required ports
        use_case = PDFToMarkdownUseCase(
            document_port=document_port,
            storage_port=storage_port,
            llm_port=llm_port
        )
        md_path = use_case.execute(pdf_path)
        print(f"[OK] Markdown generated: {md_path}")
    except Exception as e:
        print(f"[Error] Failed to convert PDF: {e}")

def list_pdfs() -> list[str]:
    """List available PDFs in the pdfs directory."""
    return [p.name for p in sorted(PDF_DIR.glob("*.pdf"))]

def select_pdf(prompt: str = "\nSelect number: ") -> str | None:
    """Show PDF selection menu."""
    files = list_pdfs()
    if not files:
        print("[INFO] No PDFs found in ./pdfs directory")
        return None
        
    print("\nAvailable PDFs:")
    for i, pdf in enumerate(files, 1):
        print(f"{i}. {pdf}")
    
    try:
        sel = input(prompt).strip()
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            return files[int(sel) - 1]
        print("[ERROR] Invalid selection")
        return None
    except (ValueError, IndexError):
        print("[ERROR] Invalid selection")
        return None

def select_processing_mode() -> None:
    """Select between traditional or LLM-enhanced processing."""
    while True:
        print("\nProcessing Mode Selection")
        print("1. Traditional (PyMuPDF + OCR when needed)")
        print("2. LLM-Enhanced (Traditional + LLM refinement)")
        print("3. Back")
        
        choice = input("\nSelect mode (1-3): ").strip()
        
        match choice:
            case "1":
                LLMConfig.set_provider(None)  # Desactivar LLM
                print("\n[OK] Traditional mode activated - No LLM refinement will be used")
                return
            case "2":
                if select_llm_provider():
                    return
            case "3":
                return
            case _:
                print("\n[ERROR] Invalid option. Please select 1, 2 or 3")
        
def select_llm_provider() -> bool:
    """Select and validate LLM provider.
    
    Returns:
        bool: True if a provider was successfully selected, False otherwise
    """
    from adapters.providers.openai_provider import OpenAIProvider
    from adapters.providers.gemini_provider import GeminiProvider
    from adapters.providers.deepseek_provider import DeepSeekProvider
    
    providers = {
        "1": ("OpenAI GPT", OpenAIProvider),
        "2": ("Google Gemini", GeminiProvider),
        "3": ("DeepSeek", DeepSeekProvider)
    }
    
    while True:
        print("\nAvailable LLM Providers:")
        for key, (name, _) in providers.items():
            print(f"{key}. {name}")
        print("4. Back")
        
        choice = input("\nSelect provider (1-4): ").strip()
        
        if choice == "4":
            return False
            
        if choice not in providers:
            print("\n[ERROR] Invalid option. Please select 1-4")
            continue
            
        name, provider_class = providers[choice]
        
        try:
            # Cargar la configuración del proveedor
            from config.api_settings import load_api_settings
            api_config = load_api_settings()
            
            # Crear instancia del proveedor
            provider = provider_class()
            provider_key = provider.get_config_key()
            
            # Verificar que tenemos configuración para este proveedor
            if provider_key not in api_config:
                logger.error(f"No configuration found for {name}")
                raise ValueError(f"No configuration found for {name}")
            
            config = api_config[provider_key]
            if not config.get("api_key"):
                logger.error(f"No API key found for {name}")
                raise ValueError(f"No API key found for {name}")
            
            # Intentar inicializar el proveedor
            logger.debug(f"Initializing {name} with config (API Key: {config['api_key'][:10]}...)")
            provider.initialize(config)
            
            # Si la inicialización es exitosa, activar el proveedor
            print(f"\nActivating {name}...")
            LLMConfig.set_provider(provider_key)
            logger.debug(f"Successfully initialized {name}")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Failed to initialize {name}.")
            print("Please check your configuration and API keys.")
            logger.error(f"Provider initialization error: {e}")
            # Asegurarse de que permanecemos en modo clásico
            LLMConfig.set_provider(None)
            print("\n[INFO] Falling back to Traditional mode")
            return False
    
def _get_mode_display() -> str:
    """Get the current processing mode display text."""
    provider = LLMConfig.get_current_provider()
    return f"[{provider.upper() if provider else 'Modo Clásico'}]"

def _compare_pdfs() -> None:
    """Compare two PDF documents and generate a report."""
    logger.info("Iniciando comparación de documentos")
    try:
        print("\nSeleccione el documento PDF original:")
        original_pdf = select_pdf("\nSeleccione documento original: ")
        if not original_pdf:
            return
            
        print("\nSeleccione el documento PDF nuevo:")
        new_pdf = select_pdf("\nSeleccione documento nuevo: ")
        if not new_pdf:
            return
            
        # Inicializar puertos necesarios
        document_port = PyMuPDFAdapter()
        storage_port = FileStorage()
        
        # Crear y ejecutar caso de uso
        use_case = DocumentComparisonUseCase(
            document_port=document_port,
            storage_port=storage_port
        )
        
        # Generar nombre para el informe
        original_name = Path(original_pdf).stem
        new_name = Path(new_pdf).stem
        output_path = Path(f"output/{original_name}_vs_{new_name}_comparison.md")
        
        # Ejecutar comparación
        print("\nComparando documentos...")
        result = use_case.execute(
            original_pdf_path=PDF_DIR / original_pdf,
            new_pdf_path=PDF_DIR / new_pdf,
            output_path=output_path
        )
        
        # Mostrar resultados
        print(f"\n[OK] Informe de comparación generado: {output_path}")
        print(f"Páginas con diferencias: {len(result.page_differences)}")
        if result.metadata_changes:
            print(f"Cambios en metadatos: {len(result.metadata_changes)}")
            
    except Exception as e:
        print(f"[Error] Error al comparar documentos: {e}")
        logger.exception("Error en la comparación de documentos")

def mostrar_menu() -> None:
    """Display and handle the main menu."""
    while True:
        try:
            _show_llm_status()
            print("\nOCR-PYMUPDF System")
            print(f"1. Select Processing Mode {_get_mode_display()}")
            print("2. Convert PDF to Markdown")
            print("3. Compare Documents")
            print("4. Exit")
            choice = input("\nSelect option (1-4): ").strip()

            match choice:
                case "1":
                    select_processing_mode()
                case "2":
                    if pdf := select_pdf():
                        _convert_pdf(PDF_DIR / pdf)
                case "3":
                    _compare_pdfs()
                case "4":
                    print("\nGoodbye!")
                    sys.exit(0)
                case _:
                    print("[ERROR] Invalid option")
        except Exception as e:
            logger.exception("Error in menu")
            print(f"[ERROR] {e}")