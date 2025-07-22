# OCR-PYMUPDF Documentation

## Overview

OCR-PYMUPDF is a powerful document processing system that combines OCR capabilities with advanced PDF handling. Built with a hexagonal architecture, it provides a robust and maintainable solution for extracting and processing text from both digital and scanned PDF documents.

## Key Features

### PDF Processing
- Digital PDF text extraction
- OCR for scanned documents
- Table detection and extraction
- Parallel processing capabilities

### Advanced Processing
- Multi-language support
- LLM-based text refinement
- Intelligent error correction
- Cache system for improved performance

### Architecture
- Hexagonal (Ports & Adapters) architecture
- Clean separation of concerns
- Extensible adapter system
- Robust error handling

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ROD-LAR-GILLES/OCR-PYMUPDF.git
cd OCR-PYMUPDF

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

```python
from src.domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from src.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.adapters.ocr_adapter import OCRAdapter

# Initialize adapters
pdf_adapter = PyMuPDFAdapter()
ocr_adapter = OCRAdapter()

# Create use case
use_case = PDFToMarkdownUseCase(pdf_adapter, ocr_adapter)

# Process document
result = use_case.execute("document.pdf")
```

## Project Structure

```
OCR-PYMUPDF/
├── src/
│   ├── domain/        # Business logic and entities
│   ├── adapters/      # External service implementations
│   ├── infrastructure/# Technical services
│   └── interfaces/    # User interfaces
├── tests/             # Test suite
└── docs/              # Documentation
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [License](about/license.md) file for details.