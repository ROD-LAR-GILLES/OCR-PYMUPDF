"""OCR-PYMUPDF System CLI.

Features:
1. List PDFs
2. Convert to Markdown
3. Configuration
4. Exit
"""

import sys
import os
import signal
from pathlib import Path
from time import sleep
from loguru import logger
from domain.use_cases import PDFToMarkdownUseCase
from interfaces.config_menu import ConfigMenu
from config.llm_config import LLMConfig
from adapters.pymupdf_adapter import PyMuPDFAdapter
from adapters.llm_refiner import LLMRefiner
from infrastructure.file_storage import FileStorage

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
        # Initialize adapters and ports
        document_port = PyMuPDFAdapter()
        storage_port = FileStorage()
        llm_port = LLMRefiner()
        
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

def select_pdf() -> str | None:
    """Show PDF selection menu."""
    files = list_pdfs()
    if not files:
        print("[INFO] No PDFs found in ./pdfs directory")
        return None
        
    print("\nAvailable PDFs:")
    for i, pdf in enumerate(files, 1):
        print(f"{i}. {pdf}")
    
    try:
        sel = input("\nSelect number: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            return files[int(sel) - 1]
        print("[ERROR] Invalid selection")
        return None
    except (ValueError, IndexError):
        print("[ERROR] Invalid selection")
        return None

def select_processing_mode() -> None:
    """Select between traditional or LLM-enhanced processing."""
    print("\nProcessing Mode Selection")
    print("1. Traditional (No LLM)")
    print("2. LLM-Enhanced")
    print("3. Back")
    
    choice = input("\nSelect mode (1-3): ").strip()
    if choice == "2":
        select_llm_provider()
    elif choice != "1":
        return
        
def select_llm_provider() -> None:
    """Select and validate LLM provider."""
    config = LLMConfig.load_config()
    providers = {
        "1": ("OpenAI GPT", "openai", "OPENAI_API_KEY"),
        "2": ("Google Gemini", "gemini", "GEMINI_API_KEY"),
        "3": ("DeepSeek", "deepseek", "DEEPSEEK_API_KEY")
    }
    
    print("\nAvailable LLM Providers:")
    for key, (name, _, _) in providers.items():
        print(f"{key}. {name}")
    print("4. Back")
    
    choice = input("\nSelect provider (1-4): ").strip()
    if choice in providers and choice != "4":
        name, provider, key_env = providers[choice]
        if os.getenv(key_env):
            print(f"\nActivating {name}...")
            LLMConfig.set_provider(provider)
        else:
            print(f"\n[ERROR] {name} API key not found. Please check your configuration.")
    
def mostrar_menu() -> None:
    """Display and handle the main menu."""
    while True:
        try:
            _show_llm_status()
            print("\nOCR-PYMUPDF System")
            print("1. Select Processing Mode")
            print("2. List PDFs")
            print("3. Convert PDF to Markdown")
            print("4. Exit")
            choice = input("\nSelect option (1-4): ").strip()

            match choice:
                case "1":
                    select_processing_mode()
                case "2":
                    files = list_pdfs()
                    if files:
                        print("\nFound PDFs:")
                        for pdf in files:
                            print(f" - {pdf}")
                    else:
                        print("[INFO] No PDFs found in ./pdfs directory")
                case "3":
                    if pdf := select_pdf():
                        _convert_pdf(PDF_DIR / pdf)
                case "4":
                    print("\nGoodbye!")
                    sys.exit(0)
                case _:
                    print("[ERROR] Invalid option")
        except Exception as e:
            logger.exception("Error in menu")
            print(f"[ERROR] {e}")