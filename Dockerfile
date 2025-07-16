# ------------------ build stage ------------------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ------------------ runtime stage ------------------
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-spa \
        tesseract-ocr-chi-tra \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1 \
        fontconfig && \
    fc-cache -f -v && \
    rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src/ src/
COPY data/ data/
COPY pdfs/ pdfs/
COPY resultado/ resultado/

CMD ["python", "-m", "main"]