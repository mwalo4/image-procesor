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

# Spuštění aplikace s Gunicorn (produkční WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "api_server:app"] 