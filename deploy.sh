#!/bin/bash

echo "🚀 Railway Deployment Script"
echo "=============================="

# Kontrola, zda je Railway CLI nainstalováno
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI není nainstalováno"
    echo "📦 Instalujte ho pomocí: npm install -g @railway/cli"
    exit 1
fi

# Kontrola, zda je uživatel přihlášen
if ! railway whoami &> /dev/null; then
    echo "🔐 Přihlaste se do Railway..."
    railway login
fi

echo "✅ Railway CLI je připraveno"

# Git commit změn
echo "📝 Commituji změny..."
git add .
git commit -m "🚀 Deploy to Railway - Universal Image Processor API"

# Push na GitHub (pokud existuje remote)
if git remote get-url origin &> /dev/null; then
    echo "📤 Pushuji na GitHub..."
    git push origin main
fi

# Deploy na Railway
echo "🚀 Nasazuji na Railway..."
railway up

echo "✅ Deployment dokončen!"
echo "🌐 Váš API bude dostupný na URL z Railway dashboardu"
echo "📊 Sledujte logy: railway logs" 