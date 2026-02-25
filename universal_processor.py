#!/usr/bin/env python3
"""
Universal Processor - Funguje s jakýmikoli rozměry obrázků
Univerzální řešení pro všechny typy produktových obrázků
"""

import os
from PIL import Image, ImageFilter
from io import BytesIO
from tqdm import tqdm
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
import numpy as np
from collections import deque

class UniversalProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.target_width = config.get('target_width', 400)
        self.target_height = config.get('target_height', 400)
        self.quality = config.get('quality', 98)
        # Minimální povolená kvalita při adaptivní kompresi
        self.min_quality = config.get('min_quality', 65)
        # Cílová maximální velikost souboru ve kB (pouze pro WEBP, None = vypnuto)
        self.target_max_kb = config.get('target_max_kb', None)
        # Výstupní formát: 'jpeg' | 'webp' | 'png'
        self.output_format = config.get('output_format', 'jpeg').lower()
        self.background_color = config.get('background_color', '#F3F3F3')
        # PNG předzploštění (PNG -> RGB/JPG-like) před zpracováním, aby se odstranily alfa artefakty
        self.flatten_png_first = config.get('flatten_png_first', False)
        self.white_threshold = config.get('white_threshold', 240)
        # Prah pro černou barvu (pro obrázky s černým pozadím)
        self.black_threshold = config.get('black_threshold', 15)
        self.product_size_ratio = config.get('product_size_ratio', 0.75)
        # Přidán práh pro alfa kanál (pro PNG/WebP s průhledností)
        self.alpha_threshold = config.get('alpha_threshold', 5)
        # Přepínač pro recolor (výchozí vypnuto, aby se nebarvily světlé části produktu)
        self.recolor_background = config.get('recolor_background', False)
        # Nové nastavení centrování a okrajů
        self.center_mode = config.get('center_mode', 'bbox')  # 'bbox' | 'centroid'
        self.min_margin_ratio = config.get('min_margin_ratio', 0.05)  # 5% na každé straně
        # Měkké hrany masky proti halo efektu
        self.soft_edges = config.get('soft_edges', True)
        self.soft_edges_radius = config.get('soft_edges_radius', 1.0)
        # PNG unmatte (odstranění bílého lemu z předchozího matte)
        self.png_edge_fix = config.get('png_edge_fix', True)
        self.png_matte = config.get('png_matte', '#FFFFFF')
        # Režim detekce okrajového pozadí: 'auto' | 'white' | 'black'
        self.background_edge_mode = config.get('background_edge_mode', 'auto')
        # AI background removal using rembg
        self.ai_background_removal = config.get('ai_background_removal', False)
        # Gradient edge barrier pro flood fill (zabraňuje vtékání do bílých/černých produktů)
        # Vyšší hodnota = méně bariér (permisivnější fill), nižší = více bariér
        # 0 = vypnuto (legacy chování)
        self.edge_barrier_threshold = config.get('edge_barrier_threshold', 15)
        
        # Vytvoření složek
        self.input_dir = Path(config.get('input_dir', 'input_images'))
        self.output_dir = Path(config.get('output_dir', 'processed_images'))
        self.output_dir.mkdir(exist_ok=True)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        h = hex_color.lstrip('#')
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    
    def _unmatte_rgba(self, img: Image.Image) -> Image.Image:
        """Odstraní barevný matte z RGBA pouze na pixelech s bílým fringe.
        
        Nová verze: aplikuje unmatte POUZE na pixely které:
        1. Jsou na okraji (sousedí s průhledností)
        2. Mají světlou barvu blízkou matte (bílý fringe)
        
        Tmavé okrajové pixely zůstávají nedotčeny (žádný černý okraj).
        """
        if img.mode != 'RGBA':
            return img
        
        arr = np.array(img).astype(np.float32) / 255.0
        rgb = arr[:, :, :3]
        a = arr[:, :, 3]
        
        # Matte barva (typicky bílá)
        matte = np.array(self._hex_to_rgb(self.png_matte), dtype=np.float32) / 255.0
        
        # Práh pro detekci "neprůhledných" a "průhledných" pixelů
        opaque_threshold = 0.95
        transparent_threshold = 0.05
        
        # Vytvoř binární masku neprůhledných a průhledných pixelů
        opaque_mask = a >= opaque_threshold
        transparent_mask = a <= transparent_threshold
        
        # Jednoduchá dilatace pomocí numpy
        def dilate_mask(mask, iterations=1):
            result = mask.copy()
            for _ in range(iterations):
                padded = np.pad(result, 1, mode='constant', constant_values=False)
                dilated = (
                    padded[:-2, :-2] | padded[:-2, 1:-1] | padded[:-2, 2:] |
                    padded[1:-1, :-2] | padded[1:-1, 1:-1] | padded[1:-1, 2:] |
                    padded[2:, :-2] | padded[2:, 1:-1] | padded[2:, 2:]
                )
                result = dilated
            return result
        
        # Dilatuj průhlednou oblast
        dilated_transparent = dilate_mask(transparent_mask, iterations=2)
        
        # Okrajové pixely (sousedí s průhledností, nejsou plně neprůhledné/průhledné)
        edge_mask = dilated_transparent & (~opaque_mask) & (~transparent_mask)
        
        # Anti-aliased hrany s nízkou alfou
        low_alpha_mask = (a < 0.5) & (a > transparent_threshold)
        dilated_opaque = dilate_mask(opaque_mask, iterations=1)
        antialiased_edges = low_alpha_mask & dilated_opaque
        
        # Kombinuj obě masky
        potential_fringe_mask = edge_mask | antialiased_edges
        
        # Pokud nemáme žádné potenciální fringe pixely, vrať originál
        if not np.any(potential_fringe_mask):
            return img
        
        # === KLÍČOVÁ ZMĚNA: Detekce bílého fringe ===
        # Pixel má bílý fringe pokud je jeho barva blízká matte barvě
        # Vypočítej vzdálenost od matte barvy
        rgb_distance = np.sqrt(np.sum((rgb - matte) ** 2, axis=2))
        
        # Práh pro "blízko matte" - pixel musí být docela světlý
        # Nižší hodnota = přísněji (detekuje jen velmi bílé pixely)
        white_fringe_threshold = 0.35  # Max vzdálenost od bílé
        
        # Pixel má bílý fringe jen pokud je světlý (blízko matte)
        has_white_fringe = rgb_distance < white_fringe_threshold
        
        # Finální maska: okrajové pixely které SKUTEČNĚ mají bílý fringe
        final_unmatte_mask = potential_fringe_mask & has_white_fringe
        
        # Pokud žádný pixel nemá bílý fringe, vrať originál
        if not np.any(final_unmatte_mask):
            return img
        
        eps = 1e-6
        a_expanded = a[:, :, np.newaxis]
        
        # Vypočítej unmatted RGB
        rgb_unmatted = (rgb - matte * (1.0 - a_expanded)) / np.clip(a_expanded, eps, 1.0)
        rgb_unmatted = np.clip(rgb_unmatted, 0.0, 1.0)
        
        # Aplikuj unmatte POUZE na pixely s bílým fringe
        final_unmatte_mask_3d = final_unmatte_mask[:, :, np.newaxis]
        rgb_result = np.where(final_unmatte_mask_3d, rgb_unmatted, rgb)
        
        # Sestav výstup
        out = np.concatenate([rgb_result, a[:, :, np.newaxis]], axis=2)
        out = (out * 255.0 + 0.5).astype(np.uint8)
        return Image.fromarray(out, mode='RGBA')
    
    def _compute_background_mask_rgb(self, img: Image.Image) -> np.ndarray:
        """Rychlé flood-fill pozadí: vyhodnotí bělavost/černost na downscalované verzi a výsledek upscaluje.

        - Pokud je `background_edge_mode` 'white', bere se jako pozadí světlá oblast.
        - Pokud je 'black', bere se jako pozadí tmavá oblast.
        - Pokud je 'auto', vybere se varianta s více hraničními seed pixely.
        """
        if img.mode != 'RGB':
            img = img.convert('RGB')
        orig_w, orig_h = img.size
        max_dim = 256
        scale = 1.0
        if max(orig_w, orig_h) > max_dim:
            scale = max_dim / float(max(orig_w, orig_h))
            small_w = max(1, int(round(orig_w * scale)))
            small_h = max(1, int(round(orig_h * scale)))
            work_img = img.resize((small_w, small_h), Image.Resampling.BILINEAR)
        else:
            small_w, small_h = orig_w, orig_h
            work_img = img
        arr = np.array(work_img)
        # Použijeme průměrný jas (luminanci) pro robustnější detekci "špinavé" bílé/černé
        # (řeší barevný nádech stínů, např. do modra/žluta)
        mean_brightness = np.mean(arr[:, :, :3], axis=2)
        
        # Dynamický výpočet prahu podle rohů obrázku (pokud je pozadí tmavší než default threshold)
        # Získáme průměrný jas rohů (předpokládáme že rohy jsou pozadí)
        tl = mean_brightness[0:10, 0:10].mean()
        tr = mean_brightness[0:10, -10:].mean()
        bl = mean_brightness[-10:, 0:10].mean()
        br = mean_brightness[-10:, -10:].mean()
        corners_mean = np.mean([tl, tr, bl, br])
        
        # Pokud je pozadí "bílé" (jas > 100), ale tmavší než default threshold (např. 180),
        # snížíme práh dynamicky, aby zachytil toto pozadí.
        # Nechceme jít příliš nízko (pod 150), abychom neřízli do produktu.
        effective_white_threshold = self.white_threshold
        if corners_mean > 100: # Je to spíše světlé pozadí
             # Nastavíme threshold kousek pod jas pozadí (tolerance 10-15)
             dynamic_threshold = max(150, corners_mean - 15)
             # Použijeme ten nižší (buď default nebo dynamický), ale ne vyšší než default
             # (aby user mohl threshold manuálně snížit, pokud chce)
             # Zde chceme povolit POKLES pod 190, pokud je fotka tmavá.
             # Ale default 190 může být moc vysoko pro tmavou fotku (kde pozadí je 160).
             # Takže effective = min(default, dynamic)
             effective_white_threshold = min(self.white_threshold, dynamic_threshold)
             # Ale zároveň, pokud je fotka PERFEKTNÍ (pozadí 255), dynamic bude 240.
             # Pokud user nastavil 190, tak min(190, 240) = 190. To je OK (190 zachytí 255).
             # Problém je, když pozadí je 180. Dynamic = 165. Min(190, 165) = 165.
             # Tím pádem 165 zachytí 180. Bingo!
        
        white_like = mean_brightness >= effective_white_threshold
        black_like = mean_brightness <= self.black_threshold

        # --- Edge-barrier: gradient jako bariéra pro flood fill ---
        # Zabraňuje vtékání do produktů, které sdílejí barvu s pozadím
        if self.edge_barrier_threshold > 0:
            padded = np.pad(mean_brightness, 1, mode='edge')
            gx = (padded[1:-1, 2:] - padded[1:-1, :-2]) / 2.0
            gy = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / 2.0
            grad_mag = np.sqrt(gx * gx + gy * gy)
            is_edge_barrier = grad_mag >= self.edge_barrier_threshold
            white_like = white_like & ~is_edge_barrier
            black_like = black_like & ~is_edge_barrier

        h, w = white_like.shape
        visited = np.zeros((h, w), dtype=bool)
        q = deque()

        def enqueue_edge_seeds(mask: np.ndarray):
            for x in range(w):
                if mask[0, x] and not visited[0, x]:
                    visited[0, x] = True; q.append((0, x))
                if mask[h-1, x] and not visited[h-1, x]:
                    visited[h-1, x] = True; q.append((h-1, x))
            for y in range(h):
                if mask[y, 0] and not visited[y, 0]:
                    visited[y, 0] = True; q.append((y, 0))
                if mask[y, w-1] and not visited[y, w-1]:
                    visited[y, w-1] = True; q.append((y, w-1))

        # Zvol seed masku podle režimu
        if self.background_edge_mode == 'white':
            seed_mask = white_like
        elif self.background_edge_mode == 'black':
            seed_mask = black_like
        else:  # auto
            # sečti hraniční true pixely pro white a black a vyber větší
            white_count = int(white_like[0, :].sum() + white_like[-1, :].sum() +
                              white_like[:, 0].sum() + white_like[:, -1].sum())
            black_count = int(black_like[0, :].sum() + black_like[-1, :].sum() +
                              black_like[:, 0].sum() + black_like[:, -1].sum())
            seed_mask = white_like if white_count >= black_count else black_like

        enqueue_edge_seeds(seed_mask)
        while q:
            y, x = q.popleft()
            if y+1 < h and not visited[y+1, x] and seed_mask[y+1, x]:
                visited[y+1, x] = True; q.append((y+1, x))
            if y-1 >= 0 and not visited[y-1, x] and seed_mask[y-1, x]:
                visited[y-1, x] = True; q.append((y-1, x))
            if x+1 < w and not visited[y, x+1] and seed_mask[y, x+1]:
                visited[y, x+1] = True; q.append((y, x+1))
            if x-1 >= 0 and not visited[y, x-1] and seed_mask[y, x-1]:
                visited[y, x-1] = True; q.append((y, x-1))
        visited_img = Image.fromarray((visited.astype(np.uint8) * 255))
        up_mask = visited_img.resize((orig_w, orig_h), Image.Resampling.NEAREST)
        return np.array(up_mask) > 0
    
    def _compute_product_mask(self, img: Image.Image) -> np.ndarray:
        """Vrátí boolean masku produktu z RGBA alfy nebo flood-fill z RGB."""
        if 'A' in img.getbands():
            rgba = img.convert('RGBA')
            arr = np.array(rgba)
            alpha = arr[:, :, 3]
            return alpha > self.alpha_threshold
        else:
            background_mask = self._compute_background_mask_rgb(img)
            return ~background_mask
    
    def find_product_bbox(self, img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """Najde bounding box produktu s vylepšenou detekcí (alfa nebo bílá)"""
        try:
            product_mask = self._compute_product_mask(img)
            if not np.any(product_mask):
                return None
            rows = np.any(product_mask, axis=1)
            cols = np.any(product_mask, axis=0)
            y1, y2 = np.where(rows)[0][[0, -1]]
            x1, x2 = np.where(cols)[0][[0, -1]]
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img.size[0], x2 + padding)
            y2 = min(img.size[1], y2 + padding)
            return (x1, y1, x2, y2)
        except Exception as e:
            print(f"Chyba při hledání bounding box: {e}")
            return None
    
    def smart_resize_and_center(self, img: Image.Image) -> Image.Image:
        """Chytře změní velikost a vycentruje produkt (s podporou alfa)"""
        try:
            hex_color = self.background_color.lstrip('#')
            bg_color = (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )
            result = Image.new('RGB', (self.target_width, self.target_height), bg_color)
            
            bbox = self.find_product_bbox(img)
            
            if bbox:
                x1, y1, x2, y2 = bbox
                product_width = x2 - x1
                product_height = y2 - y1
                cropped_product = img.crop(bbox)
                
                # PNG unmatte (pouze RGBA a pokud povoleno)
                if 'A' in cropped_product.getbands() and self.png_edge_fix:
                    cropped_product = self._unmatte_rgba(cropped_product)
                
                # Vypočítej masku produktu v oblasti bboxu
                mask_small = self._compute_product_mask(cropped_product)
                
                # Škálování včetně minimálních okrajů
                margin_x = int(round(self.target_width * self.min_margin_ratio))
                margin_y = int(round(self.target_height * self.min_margin_ratio))
                target_product_width = int(self.target_width * self.product_size_ratio)
                target_product_height = int(self.target_height * self.product_size_ratio)
                scale_x = min(target_product_width, self.target_width - 2 * margin_x) / product_width
                scale_y = min(target_product_height, self.target_height - 2 * margin_y) / product_height
                scale = min(scale_x, scale_y)
                new_width = max(1, int(product_width * scale))
                new_height = max(1, int(product_height * scale))
                resized_product = cropped_product.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Maska pro kompozici
                if 'A' in cropped_product.getbands():
                    # Pro RGBA obrázky použij přímo alfa kanál (zachová anti-aliased hrany)
                    print(f"  🔷 DEBUG: Image has Alpha channel, using native alpha for compositing")
                    rgba_arr = np.array(cropped_product)
                    alpha_channel = rgba_arr[:, :, 3]
                    print(f"  🔷 DEBUG: Alpha channel stats - min: {alpha_channel.min()}, max: {alpha_channel.max()}")
                    mask_img = Image.fromarray(alpha_channel)
                else:
                    # Pro RGB obrázky vypočítej masku z pozadí
                    print(f"  🔶 DEBUG: Image is RGB (no alpha), using computed mask")
                    mask_img = Image.fromarray((mask_small.astype(np.uint8) * 255))
                
                resized_mask = mask_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                if self.soft_edges and self.soft_edges_radius > 0:
                    resized_mask = resized_mask.filter(ImageFilter.GaussianBlur(radius=self.soft_edges_radius))
                
                # Centrovaní
                if self.center_mode == 'centroid':
                    ys, xs = np.where(mask_small)
                    if ys.size > 0:
                        centroid_x_small = xs.mean()
                        centroid_y_small = ys.mean()
                        center_x = centroid_x_small * scale
                        center_y = centroid_y_small * scale
                    else:
                        center_x = new_width / 2
                        center_y = new_height / 2
                else:  # bbox center
                    center_x = new_width / 2
                    center_y = new_height / 2
                canvas_center_x = self.target_width / 2
                canvas_center_y = self.target_height / 2
                paste_x = int(round(canvas_center_x - center_x))
                paste_y = int(round(canvas_center_y - center_y))
                paste_x = max(margin_x, min(paste_x, self.target_width - margin_x - new_width))
                paste_y = max(margin_y, min(paste_y, self.target_height - margin_y - new_height))
                
                # Vložit s maskou - pro RGBA správně blenduj proti pozadí (ne černé!)
                if 'A' in resized_product.getbands():
                    # Vytvoř RGB verzi blendovanou s cílovou barvou pozadí
                    bg_for_blend = Image.new('RGBA', resized_product.size, bg_color + (255,))
                    blended = Image.alpha_composite(bg_for_blend, resized_product)
                    rgb_product = blended.convert('RGB')
                    print(f"  🔷 DEBUG: RGBA->RGB blended against background {bg_color}")
                else:
                    rgb_product = resized_product.convert('RGB')
                
                result.paste(rgb_product, (paste_x, paste_y), resized_mask)
                
                print(f"  Produkt: {product_width}x{product_height}px → {new_width}x{new_height}px")
                print(f"  Pozice: ({paste_x}, {paste_y})")
                
            else:
                print(f"  Produkt nenalezen, používám celý obrázek")
                img_ratio = img.width / img.height
                target_ratio = self.target_width / self.target_height
                if img_ratio > target_ratio:
                    new_width = int(self.target_height * img_ratio)
                    new_height = self.target_height
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    left = (new_width - self.target_width) // 2
                    cropped = resized.crop((left, 0, left + self.target_width, self.target_height))
                else:
                    new_width = self.target_width
                    new_height = int(self.target_width / img_ratio)
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    top = (new_height - self.target_height) // 2
                    cropped = resized.crop((0, top, self.target_width, top + self.target_height))
                paste_x = (self.target_width - cropped.width) // 2
                paste_y = (self.target_height - cropped.height) // 2
                result.paste(cropped, (paste_x, paste_y))
            
            return result
            
        except Exception as e:
            print(f"Chyba při změně velikosti: {e}")
            return img
    
    def change_background(self, img: Image.Image) -> Image.Image:
        """Změní bílé i velmi tmavé (černé) pozadí na cílovou barvu."""
        try:
            hex_color = self.background_color.lstrip('#')
            new_bg_color = (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )
            img_array = np.array(img)
            white_mask = np.all(img_array >= self.white_threshold, axis=2)
            black_mask = np.all(img_array <= self.black_threshold, axis=2)
            bg_mask = white_mask | black_mask
            img_array[bg_mask] = new_bg_color
            result = Image.fromarray(img_array)
            return result
        except Exception as e:
            print(f"Chyba při změně barvy pozadí: {e}")
            return img
    
    def process_image(self, image_path: Path) -> bool:
        """Zpracuje jeden obrázek - univerzální přístup"""
        try:
            try:
                relative_path = image_path.relative_to(self.input_dir)
            except Exception:
                relative_path = Path(image_path.name)
            output_path = self.output_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Nastav příponu podle cílového formátu
            if self.output_format == 'webp':
                output_path = output_path.with_suffix('.webp')
            elif self.output_format == 'png':
                output_path = output_path.with_suffix('.png')
            else:
                output_path = output_path.with_suffix('.jpg')
            with Image.open(image_path) as img:
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                elif img.mode in ('LA',):
                    img = img.convert('RGBA')
                elif img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                # Volitelně: PNG s alfou nejprve zploštit na bílé pozadí (simulace JPG),
                # čímž odstraníme řídké průhledné pixely (fleky) mimo produkt
                if self.flatten_png_first and 'A' in img.getbands():
                    rgba = img.convert('RGBA')
                    white_bg = Image.new('RGBA', rgba.size, (255, 255, 255, 255))
                    img = Image.alpha_composite(white_bg, rgba).convert('RGB')
                
                # AI Background Removal using rembg
                if self.ai_background_removal:
                    print(f"  🤖 AI Background Removal: Odstraňuji pozadí...")
                    try:
                        from rembg import remove
                        original_rgb = img.convert('RGB')
                        rembg_result = remove(img)
                        rembg_rgba = rembg_result.convert('RGBA')
                        print(f"  🤖 AI Background Removal: Hotovo! Mode: {rembg_rgba.mode}")

                        # Strategie: na originální pixely aplikujeme rembg alfu
                        # jako masku pro záměnu pozadí. Žádné blendování dvou obrázků.
                        # Produkt (alfa=1): originální pixel beze změny
                        # Pozadí (alfa=0): cílová barva pozadí
                        # Hrana (částečná alfa): plynulý přechod z produktu do cílové barvy
                        bg_color = self._hex_to_rgb(self.background_color)

                        rembg_alpha = np.array(rembg_rgba)[:, :, 3]
                        alpha_f = rembg_alpha.astype(np.float32) / 255.0
                        alpha_3d = alpha_f[:, :, np.newaxis]

                        orig_arr = np.array(original_rgb).astype(np.float32)
                        bg_arr = np.full_like(orig_arr, bg_color)
                        result = orig_arr * alpha_3d + bg_arr * (1.0 - alpha_3d)

                        img = Image.fromarray(result.astype(np.uint8), 'RGB')
                        print(f"  🤖 AI Background Removal: Pozadí nahrazeno, výstup RGB pro standardní pipeline")
                    except ImportError:
                        print(f"  ⚠️ rembg není nainstalované, přeskakuji AI background removal")
                    except Exception as e:
                        print(f"  ⚠️ Chyba při AI background removal: {e}")
                
                print(f"Zpracovávám {image_path.name}: {img.width}x{img.height}px")
                processed_img = self.smart_resize_and_center(img)
                
                if self.recolor_background:
                    processed_img = self.change_background(processed_img)
                # Ulož podle formátu
                if self.output_format == 'webp':
                    if self.target_max_kb is not None:
                        # Adaptivní komprese na cílovou velikost
                        quality_try = int(self.quality)
                        best_bytes = None
                        best_quality = quality_try
                        # Startovní uložení a kontrola velikosti
                        for _ in range(10):  # max 10 iterací
                            buf = BytesIO()
                            processed_img.save(
                                buf,
                                format='WEBP',
                                quality=max(1, quality_try),
                                method=6
                            )
                            data = buf.getvalue()
                            size_kb = len(data) / 1024.0
                            best_bytes = data
                            best_quality = quality_try
                            if size_kb <= float(self.target_max_kb) or quality_try <= self.min_quality:
                                break
                            # sniž kvalitu a zkus znovu
                            if quality_try > 85:
                                quality_try -= 7
                            elif quality_try > 75:
                                quality_try -= 5
                            else:
                                quality_try -= 3
                        # Zapiš nejlepší výsledek
                        with open(output_path, 'wb') as f:
                            f.write(best_bytes)
                    else:
                        processed_img.save(
                            output_path,
                            format='WEBP',
                            quality=self.quality,
                            method=6
                        )
                elif self.output_format == 'png':
                    processed_img.save(
                        output_path,
                        format='PNG'
                    )
                else:  # jpeg
                    processed_img.save(
                        output_path,
                        format='JPEG',
                        quality=self.quality,
                        optimize=True,
                        subsampling=0
                    )
                return True
        except Exception as e:
            print(f"Chyba při zpracování {image_path}: {e}")
            return False
    
    def get_image_files(self) -> List[Path]:
        """Získá seznam všech obrázků ve vstupní složce"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = []
        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)
        return sorted(image_files)
    
    def process_all_images(self) -> Dict:
        """Zpracuje všechny obrázky"""
        image_files = self.get_image_files()
        if not image_files:
            print(f"Žádné obrázky nenalezeny ve složce: {self.input_dir}")
            return {'total': 0, 'processed': 0, 'errors': []}
        results = {
            'total': len(image_files),
            'processed': 0,
            'errors': []
        }
        print(f"Načteno {len(image_files)} obrázků ze složky: {self.input_dir}")
        print(f"Cílové rozměry: {self.target_width}x{self.target_height}px")
        print(f"Barva pozadí: {self.background_color}")
        print(f"Velikost produktu: {self.product_size_ratio * 100:.0f}% obrázku")
        print(f"Kvalita JPG: {self.quality}%")
        print(f"Výstupní složka: {self.output_dir}")
        print(f"Univerzální zpracování pro všechny rozměry")
        for image_path in tqdm(image_files, desc="Univerzální zpracování"):
            try:
                if self.process_image(image_path):
                    results['processed'] += 1
                else:
                    results['errors'].append(str(image_path))
            except Exception as e:
                results['errors'].append(f"{image_path}: {e}")
        return results

def main():
    parser = argparse.ArgumentParser(description='Universal Processor')
    parser.add_argument('--input', default='input_images', help='Vstupní složka s obrázky')
    parser.add_argument('--file', default=None, help='Zpracovat jediný soubor (přeskočí dávkové skenování)')
    parser.add_argument('--output', default='processed_images', help='Výstupní složka')
    parser.add_argument('--width', type=int, default=400, help='Cílová šířka (výchozí: 400)')
    parser.add_argument('--height', type=int, default=400, help='Cílová výška (výchozí: 400)')
    parser.add_argument('--quality', type=int, default=98, help='Kvalita JPG (1-100, výchozí: 98)')
    parser.add_argument('--min-quality', type=int, default=65, help='Minimální kvalita při adaptivní WEBP kompresi (výchozí: 65)')
    parser.add_argument('--target-max-kb', type=int, default=None, help='Cílová maximální velikost souboru ve kB pro WEBP (např. 120). Výchozí: vypnuto')
    parser.add_argument('--format', choices=['jpeg', 'webp', 'png'], default='jpeg', help='Výstupní formát (jpeg/webp/png)')
    parser.add_argument('--background-color', default='#F3F3F3', help='Barva pozadí (hex, výchozí: #F3F3F3)')
    parser.add_argument('--white-threshold', type=int, default=240, help='Prah pro bílou barvu (0-255, výchozí: 240)')
    parser.add_argument('--black-threshold', type=int, default=15, help='Prah pro černou barvu (0-255, výchozí: 15)')
    parser.add_argument('--product-size', type=float, default=0.75, help='Velikost produktu v % obrázku (0.1-1.0, výchozí: 0.75)')
    parser.add_argument('--recolor-background', action='store_true', help='Přepínač pro změnu barvy pozadí na #F3F3F3')
    parser.add_argument('--center-mode', choices=['bbox', 'centroid'], default='bbox', help='Režim centrování produktu (bbox nebo centroid)')
    parser.add_argument('--background-edge-mode', choices=['auto', 'white', 'black'], default='auto', help='Jak detekovat okrajové pozadí (auto/white/black)')
    parser.add_argument('--min-margin-ratio', type=float, default=0.05, help='Minimální okraj v % obrázku (0-1, výchozí: 0.05)')
    parser.add_argument('--soft-edges', action='store_true', help='Použít měkké hrany masky pro anti-aliasing')
    parser.add_argument('--soft-edges-radius', type=float, default=1.0, help='Poloměr měkkých hran pro anti-aliasing (0-10, výchozí: 1.0)')
    parser.add_argument('--png-edge-fix', action='store_true', help='Použít PNG unmatte pro odstranění bílého lemu z předchozího matte')
    parser.add_argument('--png-matte', default='#FFFFFF', help='Barva matte pro PNG unmatte (hex, výchozí: #FFFFFF)')
    parser.add_argument('--flatten-png-first', action='store_true', help='Nejprve zploštit PNG s alfou na bílé pozadí (simulace JPG)')
    parser.add_argument('--edge-barrier-threshold', type=int, default=15, help='Práh gradientu pro bariéru flood fill (0=vypnuto, výchozí: 15)')
    
    args = parser.parse_args()
    
    # Vytvoření konfigurace
    config = {
        'target_width': args.width,
        'target_height': args.height,
        'quality': args.quality,
        'min_quality': args.min_quality,
        'target_max_kb': args.target_max_kb,
        'output_format': args.format,
        'input_dir': args.input,
        'output_dir': args.output,
        'background_color': args.background_color,
        'white_threshold': args.white_threshold,
        'black_threshold': args.black_threshold,
        'product_size_ratio': args.product_size,
        'recolor_background': args.recolor_background,
        'center_mode': args.center_mode,
        'background_edge_mode': args.background_edge_mode,
        'min_margin_ratio': args.min_margin_ratio,
        'soft_edges': args.soft_edges,
        'soft_edges_radius': args.soft_edges_radius,
        'png_edge_fix': args.png_edge_fix,
        'png_matte': args.png_matte,
        'flatten_png_first': args.flatten_png_first,
        'edge_barrier_threshold': args.edge_barrier_threshold
    }
    
    # Kontrola existence vstupní složky
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Chyba: Vstupní složka '{args.input}' neexistuje!")
        return
    
    # Vytvoření procesoru
    processor = UniversalProcessor(config)
    
    # Spuštění zpracování
    if args.file:
        single_path = Path(args.file)
        if not single_path.exists():
            print(f"Chyba: Soubor '{args.file}' neexistuje!")
            return
        ok = processor.process_image(single_path)
        results = {'total': 1, 'processed': 1 if ok else 0, 'errors': [] if ok else [str(single_path)]}
    else:
        results = processor.process_all_images()
    
    # Výpis výsledků
    print("\n" + "="*50)
    print("VÝSLEDKY UNIVERZÁLNÍHO ZPRACOVÁNÍ")
    print("="*50)
    print(f"Celkem obrázků: {results['total']}")
    print(f"Úspěšně zpracováno: {results['processed']}")
    print(f"Chyby: {len(results['errors'])}")
    
    if results['processed'] > 0:
        success_rate = (results['processed'] / results['total']) * 100
        print(f"Úspěšnost: {success_rate:.1f}%")
    
    if results['errors']:
        print("\nChyby:")
        for error in results['errors'][:10]:
            print(f"  - {error}")
        if len(results['errors']) > 10:
            print(f"  ... a dalších {len(results['errors']) - 10} chyb")
    
    print(f"\nZpracované obrázky najdete ve složce: {args.output}")

if __name__ == "__main__":
    main() 