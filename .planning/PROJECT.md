# Image Processor - White Product Detection Fix

## What This Is

Existující Python image processor (Flask API + UniversalProcessor engine) pro e-commerce produktové fotky. Zpracovává obrázky: resize, centrování, background removal (AI i flood-fill), export do WEBP. Nasazeno na Railway. Bug fix pro detekci bílých produktů na bílém pozadí.

## Core Value

Produktové fotky musí mít všechny produkty kompletně zachované a čistě zobrazené na cílovém pozadí — žádné oříznuté, duchové, nebo splývající produkty.

## Requirements

### Validated

- ✓ Resize a centrování produktových fotek — existing
- ✓ Background replacement (flood-fill based) — existing
- ✓ AI background removal via rembg — existing
- ✓ WEBP output s adaptivní kompresí — existing
- ✓ Flask API + web frontend — existing
- ✓ Batch processing — existing

### Active

- [ ] AI režim: bílé produkty na bílém pozadí nesmí být "duchové" (rembg dává nízkou alfu → průsvitné produkty)
- [ ] AI režim: všechny produkty v kompozici musí zůstat zachovány (rembg někdy odstraní vedlejší produkty)
- [ ] Non-AI režim: bílé produkty nesmí splývat s #F3F3F3 pozadím (flood-fill vtéká do bílých ploch produktu)
- [ ] Oprava nesmí zhoršit 99% fotek které fungují správně

### Out of Scope

- Změna rembg modelu — nemáme kontrolu nad AI, řešíme post-processing
- Změna cílové barvy pozadí — #F3F3F3 je požadavek
- Nové funkce — jen oprava stávajícího chování

## Context

- Testovací fotka: Natura Siberica zubní pasta (3 produkty: levá krabice, tuba, malá krabice vpravo)
- Origo fotka: `/Users/marek/Downloads/unnamed (1) .webp`
- Problém se projevuje u produktů s velkými bílými plochami které navazují na bílé pozadí
- Klíčový soubor: `universal_processor.py` — metody `_compute_background_mask_rgb`, `find_product_bbox`, `smart_resize_and_center`, `process_image`
- Již existující pokusy o fix: gradient edge barrier (pomáhá částečně), alpha blending (způsobuje artefakty)
- Server běží na Railway (deployment přes git push)

## Constraints

- **Stack**: Python 3.11, Pillow, NumPy, rembg — žádné nové heavy dependencies
- **Kompatibilita**: Nesmí rozbít 99% fotek které fungují správně
- **Performance**: Zpracování jedné fotky musí zůstat pod pár sekund

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| rembg se nedá "opravit" přímo | Je to black-box AI model, musíme řešit post-processing | — Pending |
| Flood-fill bleeding je hlavní příčina non-AI problému | Bílé plochy produktu spojené s bílým pozadím | — Pending |

---
*Last updated: 2026-02-25 after initialization*
