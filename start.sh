#!/bin/bash

echo "🚀 Spouštím Universal Image Processor API..."
echo "📡 API bude dostupné na portu: 8080"
echo "🔗 Endpointy:"
echo "  - GET /api/health - Health check"
echo "  - POST /api/process-single - Zpracování jednoho obrázku"
echo "  - POST /api/process-batch - Zpracování více obrázků"
echo "  - POST /api/process-base64 - Zpracování base64 obrázku"
echo "  - GET /api/config - Získání konfigurace"
echo "  - POST /api/config - Aktualizace konfigurace"
echo "🏭 Produkční prostředí - Spouštím Gunicorn"
echo "🌐 Port: 8080"

# Spuštění Gunicorn
exec gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 --access-logfile - --error-logfile - api_server:app 