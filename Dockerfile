FROM python:3.11-slim

WORKDIR /app

# Kopírování requirements
COPY requirements.txt .

# Instalace závislostí
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování aplikace
COPY . .

# Udělat start script spustitelný
RUN chmod +x start.sh

# Expose port
EXPOSE 8080

# Spuštění aplikace pomocí start scriptu
CMD ["./start.sh"] 