# 🚀 Railway Deployment - Universal Image Processor API

## 📋 Předpoklady

1. **Railway účet** - [railway.app](https://railway.app)
2. **Git repository** s kódem
3. **Railway CLI** (volitelné)

## 🚀 Rychlé nasazení

### Metoda 1: Railway Dashboard (Nejjednodušší)

1. **Přihlaste se na Railway**
   - Jděte na [railway.app](https://railway.app)
   - Přihlaste se s GitHub/GitLab účtem

2. **Vytvořte nový projekt**
   - Klikněte na "New Project"
   - Vyberte "Deploy from GitHub repo"
   - Vyberte váš repository

3. **Konfigurace**
   - Railway automaticky detekuje Python projekt
   - Použije `Procfile` a `requirements.txt`
   - Spustí `python api_server.py`

4. **Deployment**
   - Railway automaticky nasadí aplikaci
   - Získáte URL ve formátu: `https://your-app-name.railway.app`

### Metoda 2: Railway CLI

```bash
# Instalace Railway CLI
npm install -g @railway/cli

# Přihlášení
railway login

# Inicializace projektu
railway init

# Deploy
railway up
```

## ⚙️ Konfigurace

### Environment Variables (volitelné)

V Railway dashboard můžete nastavit:

```bash
# Port (automaticky nastaven Railway)
PORT=5000

# Debug mode (produkce = false)
FLASK_ENV=production

# CORS origins (pro vaši React aplikaci)
CORS_ORIGINS=https://your-react-app.railway.app
```

### Automatické nasazení

Railway automaticky:
- ✅ Detekuje změny v Git repository
- ✅ Spustí nový build při push
- ✅ Nasadí novou verzi
- ✅ Poskytne HTTPS URL

## 🔗 Použití v React aplikaci

Po nasazení na Railway upravte React komponentu:

```jsx
// ImageProcessor.jsx
const API_BASE_URL = 'https://your-app-name.railway.app/api';
```

Nebo použijte environment proměnnou:

```jsx
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
```

## 📊 Monitoring

Railway poskytuje:
- **Logs** - real-time logy aplikace
- **Metrics** - CPU, RAM, disk usage
- **Deployments** - historie nasazení
- **Custom domains** - vlastní domény

## 🔧 Troubleshooting

### Build chyby
```bash
# Zkontrolujte requirements.txt
pip install -r api_requirements.txt

# Zkontrolujte Python verzi
python --version
```

### Runtime chyby
```bash
# Zkontrolujte logy v Railway dashboard
# Nejčastější problémy:
# - Chybějící závislosti
# - Špatný port
# - CORS chyby
```

### CORS chyby
```python
# V api_server.py upravte CORS
CORS(app, origins=['https://your-react-app.railway.app'])
```

## 💰 Ceny

Railway nabízí:
- **Free tier**: $5 kredit měsíčně
- **Pro plan**: $20 měsíčně
- **Enterprise**: Custom pricing

## 🚀 Výhody Railway

- ✅ **Automatické HTTPS**
- ✅ **Global CDN**
- ✅ **Auto-scaling**
- ✅ **Git integration**
- ✅ **Custom domains**
- ✅ **Environment variables**
- ✅ **Database hosting**

## 📞 Podpora

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Discord**: Railway Discord server
- **GitHub Issues**: Pro bug reports

---

**🎉 Váš API server bude dostupný na: `https://your-app-name.railway.app`** 