# 🚀 Railway Deployment Guide - Image Processor

Kompletní návod pro nasazení Universal Image Processor API na Railway.app.

## Přehled

Tento projekt poskytuje Flask API server pro zpracování produktových obrázků s pokročilými funkcemi:
- ✅ Automatická konverze PNG → JPG
- ✅ Smart product detection a centrování
- ✅ Změna pozadí (bílá/černá → custom barva)
- ✅ Automatický upscaling malých obrázků
- ✅ Batch processing
- ✅ Web interface + REST API

## 📋 Prerequisites

- GitHub účet s push přístupem k `mwalo4/image-procesor`
- Railway.app účet (zdarma tier stačí)
- Git nainstalovaný lokálně

## 🛠️ Lokální Setup

### 1. Clone Repository

```bash
git clone https://github.com/mwalo4/image-procesor.git
cd image-procesor
```

### 2. Vytvoření Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate
```

### 3. Instalace Dependencies

```bash
pip install -r requirements.txt
```

### 4. Lokální Testování

```bash
# Spustit API server
python api_server.py

# V novém terminálu - test health check
curl http://localhost:8080/api/health

# Otevřít v browseru
open http://localhost:8080
```

## 🚂 Railway Deployment

### Krok 1: Připravit GitHub Repository

```bash
# Zkontrolovat status
git status

# Přidat všechny změny (kromě .gitignore souborů)
git add .

# Commit s popisem
git commit -m "Update: Latest image processor with PNG→JPG conversion, web processing, and Railway deployment config"

# Push na GitHub
git push origin main
```

### Krok 2: Vytvořit Projekt na Railway

1. **Přihlásit se na Railway:**
   - Otevřít https://railway.app
   - Přihlásit se přes GitHub účet

2. **Vytvořit nový projekt:**
   - Kliknout na "New Project"
   - Vybrat "Deploy from GitHub repo"
   - Najít a vybrat `mwalo4/image-procesor`
   - Railway automaticky detekuje `Dockerfile`

3. **Počkat na první deploy:**
   - Railway automaticky začne buildovat Docker image
   - Sledovat logy v real-time
   - První build může trvat 3-5 minut

### Krok 3: Konfigurace (Optional)

**Environment Variables:**

Railway automaticky nastaví `PORT`, ale můžeš přidat vlastní config:

```bash
# V Railway dashboard → Variables
TARGET_WIDTH=1000
TARGET_HEIGHT=1000
BACKGROUND_COLOR=#F3F3F3
AUTO_UPSCALE=true
```

**Custom Domain (Optional):**
- V Railway dashboard → Settings → Domains
- Přidat vlastní doménu nebo použít Railway subdomain

### Krok 4: Ověření Deploymentu

Po úspěšném deployi:

1. **Najít Public URL:**
   - V Railway dashboard → Settings → Domains
   - Zkopírovat URL (např. `https://your-app.railway.app`)

2. **Test API Endpointů:**

```bash
# Health check
curl https://your-app.railway.app/api/health

# Config
curl https://your-app.railway.app/api/config
```

3. **Test Web Interface:**
   - Otevřít `https://your-app.railway.app` v browseru
   - Nahrát testovací obrázek
   - Zkontrolovat zpracování

## 📁 Deployment Files

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "api_server.py"]
```

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile (fallback)
```
web: python api_server.py
```

## 🔧 Troubleshooting

### Build Failed

**Problém:** Docker build selhal na dependencies

**Řešení:**
```bash
# Lokálně otestovat Dockerfile
docker build -t image-processor .
docker run -p 8080:8080 image-processor
```

### Health Check Failed

**Problém:** Railway nemůže dosáhnout `/api/health`

**Řešení:**
- Zkontrolovat, že `api_server.py` správně naslouchá na `PORT` env variable
- Zkontrolovat logy v Railway dashboard
- Ověřit, že Flask app běží: `app.run(host='0.0.0.0', port=port)`

### Out of Memory

**Problém:** Aplikace crashuje kvůli nedostatku paměti

**Řešení:**
- V Railway: Upgrade na vyšší tier s více RAM
- Optimalizovat image processing (snížit max upload size)
- Přidat memory limit v `universal_processor.py`

### Slow Response

**Problém:** API je pomalé

**Řešení:**
- Zvětšit Railway instance (více CPU/RAM)
- Optimalizovat processing pipeline
- Zvážit Redis cache pro často používané konfigurace

## 🔄 Continuous Deployment

Railway automaticky deployuje při každém push na main branch:

```bash
# Udělat změny
git add .
git commit -m "Update: feature X"
git push origin main

# Railway automaticky:
# 1. Detekuje změnu
# 2. Spustí nový build
# 3. Deployuje novou verzi
# 4. Zero-downtime deployment
```

## 📊 Monitoring

### Railway Dashboard
- **Deployments:** Historie všech deployů
- **Logs:** Real-time application logs
- **Metrics:** CPU, Memory, Network usage
- **Analytics:** Request counts, response times

### API Logs Endpoint
```bash
# Získat logy z aplikace
curl https://your-app.railway.app/api/logs
```

## 🎯 Best Practices

1. **Testování před push:**
   ```bash
   python api_server.py  # Lokální test
   ```

2. **Sledovat logy:**
   - Railway Dashboard → Deployments → View Logs

3. **Pravidelně aktualizovat dependencies:**
   ```bash
   pip list --outdated
   pip install -U package-name
   pip freeze > requirements.txt
   ```

4. **Backup konfigurace:**
   - Exportovat env variables z Railway
   - Commitnout `config.json` (pokud není citlivý)

## 🌐 API Endpoints

Po nasazení jsou dostupné tyto endpointy:

| Method | Endpoint | Popis |
|--------|----------|-------|
| GET | `/` | Web UI interface |
| GET | `/api/health` | Health check |
| POST | `/api/process-single` | Zpracování jednoho obrázku |
| POST | `/api/process-batch` | Batch zpracování |
| POST | `/api/process-base64` | Base64 image processing |
| GET | `/api/config` | Získat konfiguraci |
| POST | `/api/config` | Aktualizovat konfiguraci |
| GET | `/api/logs` | Application logs |

## 💡 Tips

- Railway free tier má limit 500 hodin/měsíc
- Pro production zvažte upgrade na Pro plan
- Použijte CDN pro static assets (CSS, JS)
- Zvažte Redis pro session management při vysokém trafficu

## 🆘 Support

- Railway Docs: https://docs.railway.app
- GitHub Issues: https://github.com/mwalo4/image-procesor/issues
- Railway Community: https://discord.gg/railway
