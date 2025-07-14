FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-spa \
        tesseract-ocr-chi-tra \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        build-essential \
        python3-dev \
        ghostscript \
    && echo "Installed chi_tra traineddata" \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip

# Eliminar [cv] de camelot-py para evitar errores con pdftopng
RUN sed -i 's/camelot-py\[cv\]/camelot-py/g' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY pdfs/ pdfs/
COPY resultado/ resultado/

CMD ["python", "-m", "main"]