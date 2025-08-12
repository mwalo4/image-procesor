# 📚 **Universal Image Processor - Kompletní Dokumentace**

## 🏗️ **Architektura**

**Universal Image Processor** je webová aplikace pro automatické zpracování produktových obrázků s moderním frontendem a robustním backendem.

### **Technologie:**
- **Backend:** Python Flask API
- **Frontend:** HTML/CSS/JavaScript (vanilla)
- **Image Processing:** Pillow (PIL), NumPy
- **Deployment:** Railway (Docker)
- **Version Control:** Git/GitHub

---

## 📁 **Struktura Projektu**

```
imagecrop/
├── api_server.py              # Flask API server
├── universal_processor.py     # Core image processing logic
├── config.json               # Default configuration
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── railway.json             # Railway deployment config
├── static/
│   ├── index.html           # Frontend interface
│   ├── style.css            # Modern CSS styling
│   └── script.js            # Frontend JavaScript
├── input_images/            # Sample input images
├── processed_images/        # Output directory
└── venv/                   # Python virtual environment
```

---

## 🔧 **Backend (Python Flask)**

### **1. `api_server.py` - Hlavní API Server**

**Funkce:**
- Flask web server s REST API
- File upload handling
- Image processing orchestration
- Error handling a logging

**Klíčové endpointy:**
```python
GET  /                    # Frontend interface
GET  /api/health         # Health check
POST /api/process-single # Zpracování jednoho obrázku
POST /api/process-batch  # Zpracování více obrázků
POST /api/process-base64 # Base64 image processing
GET  /api/config         # Získání konfigurace
POST /api/config         # Aktualizace konfigurace
GET  /api/logs           # Debugging logs
```

**Workflow pro single image processing:**
1. **File validation** - kontrola typu souboru
2. **Configuration parsing** - načtení parametrů
3. **Temporary directory creation** - vytvoření dočasné složky
4. **File saving** - uložení uploadovaného souboru
5. **Image processing** - volání UniversalProcessor
6. **File delivery** - odeslání zpracovaného obrázku

### **2. `universal_processor.py` - Core Processing Logic**

**Hlavní třída:** `UniversalProcessor`

**Klíčové metody:**
```python
def process_image(self, image_path: Path) -> bool:
    # Hlavní metoda pro zpracování jednoho obrázku
    
def auto_upscale_image(self, img: Image.Image) -> Image.Image:
    # Automatický upscale malých obrázků
    
def smart_resize_and_center(self, img: Image.Image) -> Image.Image:
    # Chytré změna velikosti a centrování produktu
    
def change_background(self, img: Image.Image) -> Image.Image:
    # Změna barvy pozadí
    
def find_product_bbox(self, img: Image.Image) -> Optional[Tuple]:
    # Detekce hranic produktu
```

**Processing pipeline:**
1. **Auto upscale** - zvětšení malých obrázků
2. **Product detection** - nalezení hranic produktu
3. **Smart resize** - změna velikosti s zachováním poměru
4. **Background change** - změna barvy pozadí
5. **Quality optimization** - optimalizace kvality

---

## 🎨 **Frontend (HTML/CSS/JavaScript)**

### **1. `static/index.html` - Hlavní Interface**

**Struktura:**
- **Header** - název aplikace a API status
- **Configuration section** - nastavení parametrů
- **File upload area** - drag & drop zone
- **File list** - seznam vybraných souborů
- **Processing button** - spuštění zpracování
- **Results section** - zobrazení výsledků
- **API info** - informace o endpointech

### **2. `static/style.css` - Modern Design**

**Klíčové vlastnosti:**
- **Gradient backgrounds** - moderní vzhled
- **Glass morphism** - průhledné karty
- **Responsive design** - adaptivní layout
- **Smooth animations** - plynulé přechody
- **Dark/light theme** - flexibilní barevné schéma

### **3. `static/script.js` - Frontend Logic**

**Hlavní funkce:**
```javascript
async function processImages() {
    // Hlavní funkce pro zpracování obrázků
    
async function processSingleImage(file, config) {
    // Zpracování jednoho obrázku
    
function updateUI() {
    // Aktualizace uživatelského rozhraní
    
function handleFileUpload() {
    // Zpracování nahrávání souborů
```

---

## ⚙️ **Konfigurace**

### **`config.json` - Default Settings**
```json
{
  "target_size": [1000, 1000],
  "background_color": "#F3F3F3",
  "quality": 95,
  "white_threshold": 240,
  "product_size_ratio": 0.75,
  "auto_upscale": false,
  "upscale_threshold": 800,
  "upscale_method": "multi-scale"
}
```

**Parametry:**
- **target_size** - cílové rozměry [šířka, výška]
- **background_color** - barva pozadí (hex)
- **quality** - kvalita JPG (1-100)
- **product_size_ratio** - velikost produktu v % obrázku
- **auto_upscale** - automatický upscale malých obrázků
- **upscale_method** - metoda upscalingu

---

## 🚀 **Deployment**

### **Railway Deployment**

**1. Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "api_server.py"]
```

**2. Railway Configuration:**
```json
{
  "build": {
    "builder": "DOCKERFILE"
  }
}
```

**3. Dependencies:**
```
Flask>=2.3.0
Flask-CORS>=4.0.0
Pillow>=10.0.0
tqdm>=4.66.0
numpy>=1.24.0
werkzeug>=2.3.0
gunicorn>=21.0.0
```

---

## 🔄 **Workflow**

### **Kompletní proces zpracování:**

1. **User upload** - uživatel nahraje obrázek přes frontend
2. **File validation** - API zkontroluje typ souboru
3. **Configuration** - načte se konfigurace z frontendu
4. **Temporary storage** - vytvoří se dočasná složka
5. **Image processing** - UniversalProcessor zpracuje obrázek:
   - Auto upscale (pokud je potřeba)
   - Product detection (bounding box)
   - Smart resize (zachování poměru)
   - Background change
   - Quality optimization
6. **File delivery** - zpracovaný obrázek se odešle uživateli

### **Error Handling:**
- **File validation errors** - neplatný typ souboru
- **Processing errors** - chyby při zpracování
- **Storage errors** - problémy s ukládáním
- **Network errors** - problémy s přenosem

---

## 🎯 **Klíčové Funkce**

### **1. Smart Product Detection**
- Automatické nalezení hranic produktu
- Odstranění bílého pozadí
- Precizní crop produktu

### **2. Auto Upscaling**
- Detekce malých obrázků
- Pokročilé upscaling metody
- Zachování kvality

### **3. Background Customization**
- Změna barvy pozadí
- Zachování průhlednosti
- Optimalizace pro e-commerce

### **4. Quality Optimization**
- Vysoká kvalita JPG
- Optimalizace velikosti
- Zachování detailů

---

## 🔧 **Debugging & Logging**

### **Logging System:**
```python
print(f"🔍 DEBUG: {message}")  # Informační logy
print(f"❌ CHYBA: {error}")     # Error logy
print(f"📋 TRACEBACK: {trace}") # Stack trace
```

### **Debug Endpoints:**
- `/api/logs` - zobrazení logů
- `/api/health` - health check
- `/api/config` - konfigurace

---

## 🎉 **Výsledek**

**Universal Image Processor** je kompletní řešení pro:
- ✅ **Automatické zpracování produktových obrázků**
- ✅ **Moderní webové rozhraní**
- ✅ **Robustní API**
- ✅ **Cloud deployment**
- ✅ **Scalable architecture**

**Aplikace je připravena pro produkční nasazení a další rozvoj!** 🚀

---

## 📊 **Příklad Logů**

```
🔍 DEBUG: Začínám process_single_image
🔍 DEBUG: Kontroluji soubor v requestu
🔍 DEBUG: Soubor: example.jpg
🔍 DEBUG: Získávám konfiguraci
🔍 DEBUG: Vytvářím dočasnou složku
🔍 DEBUG: Dočasná složka vytvořena: /tmp/xyz123
🔍 DEBUG: Ukládám soubor do: /tmp/xyz123/example.jpg
🔍 DEBUG: Soubor úspěšně uložen
🔍 DEBUG: Očekávám výstupní soubor: /tmp/xyz123/processed_example.jpg
🔍 DEBUG: Začínám zpracování
🔍 DEBUG: Otevírám obrázek
🔍 DEBUG: Obrázek načten: 1600x1600px, mode: RGB
🔍 DEBUG: Krok 0 - Auto upscale
🔍 DEBUG: Krok 1 - Smart resize
  Produkt: 425x520px → 612x750px
  Pozice: (194, 125)
🔍 DEBUG: Krok 2 - Background change
🔍 DEBUG: Ukládám obrázek do /tmp/xyz123/processed_example.jpg
🔍 DEBUG: Zpracování úspěšné!
Processing result: True
```

---

## 🚀 **Live Demo**

**Aplikace je dostupná na:** https://web-production-dcb78.up.railway.app

**GitHub Repository:** https://github.com/mwalo4/image-procesor.git 