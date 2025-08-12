FROM python:3.11-slim

WORKDIR /app

# Kopírování requirements
COPY requirements.txt .

# Instalace závislostí
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování aplikace
COPY . .

# Expose port
EXPOSE 8080

# Spuštění Flask serveru (bez warningů)
CMD ["python", "api_server.py"] 