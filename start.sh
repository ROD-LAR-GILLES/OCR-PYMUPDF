#!/bin/bash

# Print banner
echo "=== OCR-PYMUPDF Container Setup ==="
echo "This script will set up and run all services in containers"
echo "No local installation required"
echo "----------------------------------------"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start services with Docker Compose
echo "
[1/4] Building container images..."
docker-compose build

echo "
[2/4] Starting containers..."
docker-compose up -d

# Wait for DeepSeek service to be ready
echo "
[3/4] Waiting for DeepSeek service to initialize..."
echo "This may take a few minutes on first run while downloading the model..."
until curl -s http://localhost:8000/docs &> /dev/null; do
    echo "Waiting for DeepSeek API..."
    sleep 5
done

echo "
[4/4] Setup complete!"
echo "
System Information:
- All services are running in containers
- No local installation needed
- Model and dependencies are contained within Docker
- Your files in ./pdfs will be accessible to the system

Usage:
1. Place PDF files in the './pdfs' directory
2. Access the application through: docker-compose exec ocr-pymupdf python -m src.main
3. To stop all services run: docker-compose down

Containers running:
"
docker-compose ps
