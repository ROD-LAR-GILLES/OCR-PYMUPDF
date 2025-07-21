#!/bin/bash

# Check for NVIDIA Container Toolkit
if ! command -v nvidia-smi &> /dev/null; then
    echo "[WARNING] NVIDIA Container Toolkit not found. GPU acceleration will not be available."
fi

# Start services with Docker Compose
echo "Starting OCR-PYMUPDF services..."
docker-compose up --build -d

# Wait for DeepSeek service to be ready
echo "Waiting for DeepSeek service to initialize..."
until curl -s http://localhost:8000/docs &> /dev/null; do
    echo "Waiting for DeepSeek API..."
    sleep 5
done

echo "All services are ready!"
echo "Access the application through the OCR-PYMUPDF container"
echo "To stop all services, run: docker-compose down"
