# 🖼️ Universal Image Processor API

Univerzální API pro zpracování produktových obrázků s automatickou detekcí produktů a změnou pozadí.

## 🚀 Railway Deployment

Tento repository je připraven pro nasazení na Railway.

### Automatické nasazení:
1. Fork nebo clone tohoto repository
2. Na [railway.app](https://railway.app) vytvoř nový projekt
3. Vyber "Deploy from GitHub repo"
4. Railway automaticky nasadí API server

## 📡 API Endpointy

### Health Check
```http
GET /api/health
```

### Zpracování jednoho obrázku
```http
POST /api/process-single
Content-Type: multipart/form-data

Form data:
- image: soubor
- config: JSON string (volitelné)
```

### Zpracování více obrázků
```http
POST /api/process-batch
Content-Type: multipart/form-data

Form data:
- images: soubory[]
- config: JSON string (volitelné)
```

### Zpracování base64 obrázku
```http
POST /api/process-base64
Content-Type: application/json

{
  "image": "base64_string",
  "config": {} // volitelné
}
```

## ⚙️ Konfigurace

```json
{
  "target_width": 1000,
  "target_height": 1000,
  "quality": 95,
  "background_color": "#F3F3F3",
  "product_size_ratio": 0.75,
  "auto_upscale": false
}
```

## 🎯 Funkce

- ✅ **Smart resize** s LANCZOS algoritmem
- ✅ **Automatická detekce produktů**
- ✅ **Centrování produktů**
- ✅ **Změna barvy pozadí**
- ✅ **Multi-scale upscaling**
- ✅ **Post-processing** (ostření, kontrast)
- ✅ **Batch processing**

## 📦 Soubory

- `api_server.py` - Flask API server
- `universal_processor.py` - Zpracování obrázků
- `api_requirements.txt` - Python závislosti
- `config.json` - Výchozí konfigurace
- `Procfile` - Railway deployment
- `runtime.txt` - Python verze

---

**Deployováno na Railway** 🚀 