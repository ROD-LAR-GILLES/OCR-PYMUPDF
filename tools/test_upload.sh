#!/bin/bash
# Script simple para probar la carga de documentos

echo "Probando carga de documento PDF..."

# Verificar si existe un PDF de prueba
if [ -f "pdfs/pdf_scan.pdf" ]; then
    TEST_PDF="pdfs/pdf_scan.pdf"
elif [ -f "test.pdf" ]; then
    TEST_PDF="test.pdf"
else
    echo "No se encontró un PDF para probar. Creando uno simple..."
    echo -e "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj\n4 0 obj<</Length 44>>stream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello, World!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n300\n%%EOF" > test.pdf
    TEST_PDF="test.pdf"
fi

echo "Usando archivo: $TEST_PDF"

# Probar la carga de documento
echo "Enviando solicitud POST a /api/documents..."
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$TEST_PDF" \
  -F "use_llm=false" \
  -w "HTTPSTATUS:%{http_code}" \
  "http://localhost:8000/api/documents")

# Extraer código de estado HTTP
HTTP_STATUS=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
BODY=$(echo $RESPONSE | sed -e 's/HTTPSTATUS.*//g')

echo "Código de estado HTTP: $HTTP_STATUS"
echo "Respuesta del servidor:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"

# Verificar resultado
if [ "$HTTP_STATUS" -eq "201" ]; then
    echo " ¡Éxito! El documento se cargó correctamente."
    
    # Extraer el ID del documento para verificar su estado
    DOC_ID=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)
    
    if [ ! -z "$DOC_ID" ]; then
        echo "ID del documento: $DOC_ID"
        echo "Verificando estado del documento..."
        
        sleep 2  # Esperar un poco para que se procese
        
        STATUS_RESPONSE=$(curl -s "http://localhost:8000/api/documents/$DOC_ID/status")
        echo "Estado del documento:"
        echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
    fi
else
    echo " Error al cargar el documento (código $HTTP_STATUS)"
fi

# Limpiar archivo temporal si se creó
if [ "$TEST_PDF" = "test.pdf" ]; then
    rm -f test.pdf
fi
