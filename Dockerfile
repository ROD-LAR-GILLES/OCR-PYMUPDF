FROM python:3.11-slim

# Instalar tesseract y utilidades del sistema
RUN apt-get update && \
    apt-get install -y tesseract-ocr libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY pdfs/ ./pdfs/
COPY resultado/ ./resultado/

# Comando por defecto
CMD ["python", "src/main.py"]