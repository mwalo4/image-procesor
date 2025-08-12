# 🖼️ Universal Image Processor - Integrace s Node.js/React

Tento projekt poskytuje univerzální zpracování obrázků s možností integrace do Node.js/React aplikací.

## 🚀 Rychlé spuštění

### 1. Spuštění Python API serveru

```bash
# Aktivace virtuálního prostředí
source venv/bin/activate

# Instalace závislostí pro API
pip install -r api_requirements.txt

# Spuštění API serveru
python3 api_server.py
```

API bude dostupné na: `http://localhost:5000`

### 2. Integrace do React aplikace

#### Instalace komponenty

```bash
# Zkopírujte soubory do vaší React aplikace
cp ImageProcessor.jsx src/components/
cp ImageProcessor.css src/components/
```

#### Použití v React aplikaci

```jsx
import React from 'react';
import ImageProcessor from './components/ImageProcessor';

function App() {
  return (
    <div className="App">
      <ImageProcessor />
    </div>
  );
}

export default App;
```

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

### Konfigurace
```http
GET /api/config
POST /api/config
Content-Type: application/json
```

## ⚙️ Konfigurace

```json
{
  "target_width": 1000,
  "target_height": 1000,
  "quality": 95,
  "background_color": "#F3F3F3",
  "white_threshold": 240,
  "product_size_ratio": 0.75,
  "auto_upscale": false,
  "upscale_threshold": 800,
  "upscale_method": "multi-scale"
}
```

## 🎯 Funkce

### ✅ Automatické zpracování
- **Smart resize** s LANCZOS algoritmem
- **Automatická detekce produktů** pomocí analýzy pixelů
- **Centrování produktů** v obrázku
- **Změna barvy pozadí** z bílé na šedou

### ✅ Pokročilé funkce
- **Multi-scale upscaling** pro malé obrázky
- **Post-processing** (ostření, kontrast, sytost)
- **Batch processing** více obrázků najednou
- **Drag & drop** upload

### ✅ Formáty
- **Vstupní**: JPG, PNG, BMP, TIFF, WebP
- **Výstupní**: JPG s vysokou kvalitou

## 🔧 Deployment

### Lokální vývoj
```bash
# Python API server
python3 api_server.py

# React aplikace (v jiném terminálu)
npm start
```

### Produkční nasazení

#### Railway (Doporučeno)
```bash
# Vytvoření Procfile pro Python API
echo "web: python api_server.py" > Procfile

# Railway CLI
railway login
railway init
railway up
```

#### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "api_server.py"]
```

## 📱 React Komponenta

### Vlastnosti
- **Moderní UI** s gradient designem
- **Real-time API status** kontrola
- **Drag & drop** upload
- **Konfigurace v reálném čase**
- **Progress tracking**
- **Responsive design**

### Props
```jsx
<ImageProcessor 
  apiUrl="http://localhost:5000/api"  // volitelné
  onProcessed={(results) => console.log(results)}  // callback
/>
```

## 🛠️ Vývoj

### Struktura projektu
```
imagecrop/
├── universal_processor.py    # Hlavní zpracování obrázků
├── api_server.py            # Flask API server
├── ImageProcessor.jsx       # React komponenta
├── ImageProcessor.css       # Styly
├── config.json             # Konfigurace
├── api_requirements.txt    # Python závislosti
└── README_INTEGRATION.md   # Tento soubor
```

### Přidání nových funkcí

1. **Python API**: Upravte `api_server.py`
2. **React UI**: Upravte `ImageProcessor.jsx`
3. **Styly**: Upravte `ImageProcessor.css`

## 🐛 Řešení problémů

### API server neběží
```bash
# Kontrola portu
lsof -i :5000

# Restart serveru
pkill -f api_server.py
python3 api_server.py
```

### CORS chyby
```python
# V api_server.py
CORS(app, origins=['http://localhost:3000'])
```

### Velké soubory
```python
# V api_server.py
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

## 📞 Podpora

- **GitHub Issues**: Pro bug reports
- **Discord**: Pro rychlé dotazy
- **Email**: Pro enterprise podporu

---

**Vytvořeno s ❤️ pro snadné zpracování obrázků** 