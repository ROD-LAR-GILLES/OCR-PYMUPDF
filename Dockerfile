# ------------------ build stage ------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias de sistema necesarias para la compilación
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements
COPY requirements/ requirements/

# Instalar dependencias de Python en el build stage
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements/requirements.txt && \
    pip install --prefix=/install -r requirements/requirements-dev.txt

# ------------------ runtime stage ------------------
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-spa \
        tesseract-ocr-eng \
        tesseract-ocr-chi-tra \
        build-essential \
        python3-dev \
        git \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1 \
        fontconfig && \
    fc-cache -f -v && \
    rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PYTHONPATH=/app/src

WORKDIR /app

# Crear estructura de directorios necesaria
RUN mkdir -p /app/data/models/fasttext \
            /app/data/corrections \
            /app/pdfs \
            /app/resultado \
            /app/docs

COPY --from=builder /install /usr/local

# Copiar archivos de configuración y código
COPY . .

# Configurar pre-commit hooks
RUN git init && \
    pre-commit install

# Asegurar permisos de escritura y ownership
RUN chown -R 1000:1000 /app && \
    chmod -R 777 /app

# Configurar volúmenes persistentes
VOLUME ["/app/data/models/fasttext", "/app/pdfs", "/app/resultado", "/app/docs"]

# Exponer puerto para documentación
EXPOSE 8000

# Comando por defecto para desarrollo
CMD ["tail", "-f", "/dev/null"]