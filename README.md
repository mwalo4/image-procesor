# 🖼️ Universal Image Processor

Pokročilý API server pro zpracování produktových obrázků s automatickými optimalizacemi, změnou pozadí a smart detection.

[![Railway Deploy](https://railway.app/button.svg)](https://railway.app)

## ✨ Features

- **🔄 Automatická konverze formátů** - PNG → JPG s optimalizací
- **🎯 Smart Product Detection** - Automatické rozpoznání a centrování produktu
- **🎨 Změna pozadí** - Odstranění bílého/černého pozadí → custom barva
- **📏 Intelligent Resizing** - Zachování poměru stran s optimálním centrováním
- **⬆️ Auto Upscaling** - Automatické zvětšení malých obrázků (multi-scale method)
- **📦 Batch Processing** - Zpracování více obrázků najednou
- **🌐 Web Interface** - Jednoduchý drag & drop UI
- **🔌 REST API** - Snadná integrace do existujících systémů
- **🚀 Production Ready** - Railway deployment s Docker

## 🚀 Quick Start

### Lokální Development

```bash
# Clone repository
git clone https://github.com/mwalo4/image-procesor.git
cd image-procesor

# Vytvoř virtual environment
python3 -m venv venv
source venv/bin/activate

# Nainstaluj dependencies
pip install -r requirements.txt

# Spusť server
python api_server.py
```

Otevři http://localhost:8080 v browseru.

### Railway Deployment

Kompletní návod viz [DEPLOYMENT.md](DEPLOYMENT.md)

**Rychlý deploy:**
1. Fork tento repository
2. Připoj se na [Railway.app](https://railway.app)
3. Vytvoř nový projekt z GitHub repo
4. Railway automaticky deployuje! 🎉

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Popis |
|----------|--------|-------|
| `/` | GET | Web UI interface |
| `/api/health` | GET | Health check |
| `/api/process-single` | POST | Zpracování jednoho obrázku |
| `/api/process-batch` | POST | Batch zpracování (vrací ZIP) |
| `/api/process-base64` | POST | Base64 image processing |
| `/api/config` | GET/POST | Konfigurace procesoru |
| `/api/logs` | GET | Application logs |

### Příklad použití

**Single Image Processing:**

```bash
curl -X POST http://localhost:8080/api/process-single \
  -F "image=@product.png" \
  -F 'config={"target_width":1000,"target_height":1000,"background_color":"#F3F3F3"}' \
  --output processed.jpg
```

**JavaScript/Fetch:**

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('config', JSON.stringify({
  target_width: 1000,
  target_height: 1000,
  background_color: '#F3F3F3',
  auto_upscale: true
}));

const response = await fetch('/api/process-single', {
  method: 'POST',
  body: formData
});

const blob = await response.blob();
```

## ⚙️ Configuration

Default konfigurace v `config.json`:

```json
{
  "target_width": 1000,
  "target_height": 1000,
  "quality": 95,
  "background_color": "#F3F3F3",
  "white_threshold": 220,
  "product_size_ratio": 0.75,
  "auto_upscale": false,
  "upscale_threshold": 800,
  "upscale_method": "multi-scale"
}
```

### Parametry

- **target_width/height** - Cílové rozměry výstupu (px)
- **quality** - JPEG kvalita (1-100)
- **background_color** - Barva pozadí (hex format)
- **white_threshold** - Threshold pro detekci bílého pozadí (0-255)
- **product_size_ratio** - Poměr velikosti produktu k canvasu (0.0-1.0)
- **auto_upscale** - Automatický upscale malých obrázků
- **upscale_threshold** - Min. rozměr pro upscaling (px)
- **upscale_method** - Metoda upscalingu (`lanczos`, `multi-scale`)

## 🛠️ Tech Stack

- **Backend:** Python 3.11+ / Flask
- **Image Processing:** Pillow (PIL), OpenCV, NumPy
- **Deployment:** Docker, Railway
- **Frontend:** Vanilla HTML/CSS/JavaScript

## 📁 Project Structure

```
image-procesor/
│
├── api_server.py              # Flask API server
├── universal_processor.py     # Core image processing logic
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── railway.json              # Railway deployment config
├── DEPLOYMENT.md             # Deployment guide
│
├── static/                   # Web UI assets
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── temp_uploads/             # Temporary upload directory
```

## 🔍 How It Works

1. **Upload** - Obrázek se nahraje přes Web UI nebo API
2. **Detection** - Smart algoritmus detekuje hranice produktu
3. **Processing:**
   - Auto-upscale (pokud je zapnutý)
   - Odstranění/změna pozadí
   - Resize s zachováním poměru stran
   - Centrování produktu
4. **Optimization** - JPEG optimalizace pro web
5. **Output** - Zpracovaný obrázek ready pro e-shop

## 🧪 Advanced Features

### Background Detection Modes

- **Auto** - Automatická detekce bílého/černého pozadí
- **White** - Force white background detection
- **Black** - Force black background detection

### Multi-Scale Upscaling

Pro malé obrázky používá multi-pass upscaling:
1. Lanczos resize na 2x
2. Unsharp mask pro ostrost
3. Final resize na target size
4. Quality optimization

### RGBA Support

Plná podpora průhlednosti:
- Unmatte alpha channel
- Composite na nové pozadí
- Edge refinement

## 📊 Performance

- Single image: ~1-3s (podle velikosti)
- Batch processing: Paralelní zpracování
- Memory efficient: Streaming pro velké soubory
- Production tested: Zpracováno 10,000+ obrázků

## 🤝 Contributing

1. Fork repository
2. Vytvoř feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Otevři Pull Request

## 📝 License

MIT License - volně použitelné pro komerční i nekomerční projekty.

## 🆘 Support

- **Issues:** Nahlaš bug na [GitHub Issues](https://github.com/mwalo4/image-procesor/issues)
- **Deployment Help:** Viz [DEPLOYMENT.md](DEPLOYMENT.md)
- **Questions:** Otevři Discussion na GitHub

## 🎯 Use Cases

- **E-commerce:** Jednotný vzhled produktových fotek
- **Print on Demand:** Příprava designů pro tisk
- **Social Media:** Optimalizace obrázků pro různé platformy
- **Batch Processing:** Hromadné zpracování katalogů
- **API Integration:** Automatizace v existujících workflows

## ⚡ Performance Tips

- Pro batch processing použijte `/api/process-batch`
- Nastavte `auto_upscale: false` pokud už máte high-res obrázky
- Použijte CDN pro škálování při vysokém trafficu
- Railway Pro tier doporučen pro production (více RAM)

---

Made with ❤️ for produktové fotky
