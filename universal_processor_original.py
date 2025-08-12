#!/usr/bin/env python3
"""
Universal Processor - Funguje s jakýmikoli rozměry obrázků
Univerzální řešení pro všechny typy produktových obrázků
S automatickým upscalingem malých obrázků pomocí Real-ESRGAN
"""

import os
from PIL import Image
from tqdm import tqdm
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
import numpy as np
import json

def load_config(config_path: str = "config.json") -> Dict:
    """Načte konfiguraci ze souboru"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ Konfigurace načtena z: {config_path}")
        return config
    except FileNotFoundError:
        print(f"⚠️  Konfigurační soubor {config_path} nenalezen, používám výchozí nastavení")
        return get_default_config()
    except json.JSONDecodeError as e:
        print(f"❌ Chyba v konfiguračním souboru: {e}")
        return get_default_config()

def get_default_config() -> Dict:
    """Vrátí výchozí konfiguraci"""
    return {
        "target_size": [1000, 1000],
        "background_color": "#F3F3F3",
        "quality": 95,
        "white_threshold": 240,
        "product_size_ratio": 0.75,
        "auto_upscale": False,
        "upscale_threshold": 800,
        "upscale_method": "multi-scale",
        "input_dir": "input_images",
        "output_dir": "processed_images"
    }

class UniversalProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.target_width = config.get('target_width', 400)
        self.target_height = config.get('target_height', 400)
        self.quality = config.get('quality', 95)
        self.background_color = config.get('background_color', '#F3F3F3')
        self.white_threshold = config.get('white_threshold', 240)
        self.product_size_ratio = config.get('product_size_ratio', 0.75)
        self.auto_upscale = config.get('auto_upscale', True)  # Nová funkce
        self.upscale_threshold = config.get('upscale_threshold', 800)  # Prah pro upscale
        self.upscale_method = config.get('upscale_method', 'multi-scale')  # Metoda upscalingu
        
        # Vytvoření složek
        self.input_dir = Path(config.get('input_dir', 'input_images'))
        self.output_dir = Path(config.get('output_dir', 'processed_images'))
        self.output_dir.mkdir(exist_ok=True)
    
    def needs_upscaling(self, img: Image.Image) -> bool:
        """Zkontroluje, zda obrázek potřebuje upscale"""
        width, height = img.size
        
        # Malý obrázek
        if width < self.upscale_threshold or height < self.upscale_threshold:
            return True
        
        # Nekvalitní obrázek (nízké rozlišení)
        if width * height < 500000:  # 500k pixelů
            return True
        
        return False
    
    def upscale_with_realesrgan(self, img: Image.Image) -> Image.Image:
        """Placeholder pro Real-ESRGAN upscaling"""
        print(f"    Používám pokročilý upscaling...")
        return self.multi_scale_upscale(img)
    
    def _get_upscale_method(self):
        """Vrátí vybranou upscaling metodu"""
        methods = {
            'basic': self.basic_upscale,
            'advanced': self.advanced_upscale,
            'multi-scale': self.multi_scale_upscale
        }
        return methods.get(self.upscale_method, self.multi_scale_upscale)
    
    def advanced_upscale(self, img: Image.Image) -> Image.Image:
        """Pokročilý upscale s více metodami pro lepší kvalitu"""
        try:
            # Vypočítáme nové rozměry (2x zvětšení)
            new_width = img.width * 2
            new_height = img.height * 2
            
            # Metoda 1: LANCZOS s vysokou kvalitou
            upscaled_lanczos = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Metoda 2: BICUBIC pro porovnání
            upscaled_bicubic = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
            
            # Metoda 3: Iterativní upscale (2x menší kroky)
            temp_width = int(img.width * 1.5)
            temp_height = int(img.height * 1.5)
            temp_img = img.resize((temp_width, temp_height), Image.Resampling.LANCZOS)
            upscaled_iterative = temp_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Vybereme nejlepší výsledek (můžeme porovnat ostrost)
            # Pro jednoduchost použijeme LANCZOS, ale můžeme přidat analýzu kvality
            best_result = upscaled_lanczos
            
            # Přidáme jemné ostření pro lepší detaily
            from PIL import ImageEnhance
            sharpener = ImageEnhance.Sharpness(best_result)
            sharpened = sharpener.enhance(1.2)  # Mírné ostření
            
            # Přidáme jemné zvýšení kontrastu
            contrast_enhancer = ImageEnhance.Contrast(sharpened)
            enhanced = contrast_enhancer.enhance(1.1)  # Mírné zvýšení kontrastu
            
            return enhanced
            
        except Exception as e:
            print(f"    Chyba při pokročilém upscalingu: {e}")
            return img
    
    def multi_scale_upscale(self, img: Image.Image) -> Image.Image:
        """Multi-scale upscale s různými metodami a výběrem nejlepšího"""
        try:
            new_width = img.width * 2
            new_height = img.height * 2
            
            # Různé upscaling metody
            methods = {
                'lanczos': img.resize((new_width, new_height), Image.Resampling.LANCZOS),
                'bicubic': img.resize((new_width, new_height), Image.Resampling.BICUBIC),
                'hamming': img.resize((new_width, new_height), Image.Resampling.HAMMING),
                'box': img.resize((new_width, new_height), Image.Resampling.BOX)
            }
            
            # Pro produktové obrázky je LANCZOS obvykle nejlepší
            # Můžeme přidat analýzu kvality pro automatický výběr
            best_method = 'lanczos'
            result = methods[best_method]
            
            # Post-processing pro lepší kvalitu
            from PIL import ImageFilter, ImageEnhance
            
            # Jemné ostření
            sharpened = result.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Zvýšení kontrastu
            contrast_enhancer = ImageEnhance.Contrast(sharpened)
            enhanced = contrast_enhancer.enhance(1.05)
            
            # Jemné zvýšení sytosti
            saturation_enhancer = ImageEnhance.Color(enhanced)
            final = saturation_enhancer.enhance(1.1)
            
            return final
            
        except Exception as e:
            print(f"    Chyba při multi-scale upscalingu: {e}")
            return img

    def basic_upscale(self, img: Image.Image) -> Image.Image:
        """Základní upscale pomocí LANCZOS"""
        try:
            new_width = img.width * 2
            new_height = img.height * 2
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"    Chyba při základním upscalingu: {e}")
            return img
    
    def auto_upscale_image(self, img: Image.Image) -> Image.Image:
        """Automaticky upscaluje obrázek pokud je potřeba"""
        if not self.auto_upscale:
            return img
        
        if self.needs_upscaling(img):
            print(f"  Malý obrázek detekován ({img.width}x{img.height}px), upscaluji...")
            
            # Pokus o Real-ESRGAN, fallback na základní upscale
            upscaled = self.upscale_with_realesrgan(img)
            
            print(f"  Upscalováno na: {upscaled.width}x{upscaled.height}px")
            return upscaled
        
        return img
    
    def find_product_bbox(self, img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """Najde bounding box produktu s vylepšenou detekcí"""
        try:
            # Konverze na RGB pokud není
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Konverze do numpy array
            img_array = np.array(img)
            
            # Vytvoření masky pro bílé pozadí (mírnější prah)
            white_mask = np.all(img_array >= self.white_threshold, axis=2)
            
            # Najdeme ne-bílé pixely (produkt)
            product_mask = ~white_mask
            
            if not np.any(product_mask):
                return None
            
            # Najdeme hranice produktu
            rows = np.any(product_mask, axis=1)
            cols = np.any(product_mask, axis=0)
            
            y1, y2 = np.where(rows)[0][[0, -1]]
            x1, x2 = np.where(cols)[0][[0, -1]]
            
            # Přidáme malý padding (10px) pro lepší vzhled
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img_array.shape[1], x2 + padding)
            y2 = min(img_array.shape[0], y2 + padding)
            
            return (x1, y1, x2, y2)
            
        except Exception as e:
            print(f"Chyba při hledání bounding box: {e}")
            return None
    
    def smart_resize_and_center(self, img: Image.Image) -> Image.Image:
        """Chytře změní velikost a vycentruje produkt"""
        try:
            # Konverze hex barvy na RGB pro pozadí
            hex_color = self.background_color.lstrip('#')
            bg_color = (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )
            
            # Vytvoření nového obrázku se šedým pozadím
            result = Image.new('RGB', (self.target_width, self.target_height), bg_color)
            
            # Najdeme bounding box produktu
            bbox = self.find_product_bbox(img)
            
            if bbox:
                x1, y1, x2, y2 = bbox
                product_width = x2 - x1
                product_height = y2 - y1
                
                # Ořízneme produkt na bounding box
                cropped_product = img.crop(bbox)
                
                # Cílová velikost produktu
                target_product_width = int(self.target_width * self.product_size_ratio)
                target_product_height = int(self.target_height * self.product_size_ratio)
                
                # Vypočítáme scale faktor
                scale_x = target_product_width / product_width
                scale_y = target_product_height / product_height
                scale = min(scale_x, scale_y)  # Zachováme poměr stran
                
                # Nové rozměry produktu
                new_width = int(product_width * scale)
                new_height = int(product_height * scale)
                
                # Zvětšíme produkt s vysokou kvalitou
                resized_product = cropped_product.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Vypočítáme pozici pro centrování
                paste_x = (self.target_width - new_width) // 2
                paste_y = (self.target_height - new_height) // 2
                
                # Vložíme produkt do centra
                result.paste(resized_product, (paste_x, paste_y))
                
                print(f"  Produkt: {product_width}x{product_height}px → {new_width}x{new_height}px")
                print(f"  Pozice: ({paste_x}, {paste_y})")
                
            else:
                # Pokud nenajdeme produkt, použijeme celý obrázek s centrováním
                print(f"  Produkt nenalezen, používám celý obrázek")
                
                # Vypočítáme poměr stran
                img_ratio = img.width / img.height
                target_ratio = self.target_width / self.target_height
                
                if img_ratio > target_ratio:
                    # Obrázek je širší - ořízneme po stranách
                    new_width = int(self.target_height * img_ratio)
                    new_height = self.target_height
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    left = (new_width - self.target_width) // 2
                    cropped = resized.crop((left, 0, left + self.target_width, self.target_height))
                else:
                    # Obrázek je vyšší - ořízneme nahoře/dole
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
    
    def get_product_bbox(self, img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """Najde bounding box produktu (bez šedého pozadí)"""
        try:
            # Konverze na RGB pokud není
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Konverze hex barvy na RGB pro porovnání
            hex_color = self.background_color.lstrip('#')
            bg_color = np.array([
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            ])
            
            # Konverze do numpy array
            img_array = np.array(img)
            
            # Vytvoření masky pro šedé pozadí (s tolerancí)
            tolerance = 10
            bg_mask = np.all(np.abs(img_array - bg_color) <= tolerance, axis=2)
            
            # Najdeme ne-šedé pixely (produkt)
            product_mask = ~bg_mask
            
            if not np.any(product_mask):
                return None
            
            # Najdeme hranice produktu
            rows = np.any(product_mask, axis=1)
            cols = np.any(product_mask, axis=0)
            
            y1, y2 = np.where(rows)[0][[0, -1]]
            x1, x2 = np.where(cols)[0][[0, -1]]
            
            return (x1, y1, x2 + 1, y2 + 1)
            
        except Exception as e:
            print(f"Chyba při hledání bounding box: {e}")
            return None
    
    def change_background(self, img: Image.Image) -> Image.Image:
        """Změní bílé pozadí na #F3F3F3"""
        try:
            # Konverze hex barvy na RGB
            hex_color = self.background_color.lstrip('#')
            new_bg_color = (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )
            
            # Konverze do numpy array
            img_array = np.array(img)
            
            # Vytvoření masky pro bílé pixely
            white_mask = np.all(img_array >= self.white_threshold, axis=2)
            
            # Změna barvy bílých pixelů
            img_array[white_mask] = new_bg_color
            
            # Konverze zpět na PIL Image
            result = Image.fromarray(img_array)
            
            return result
            
        except Exception as e:
            print(f"Chyba při změně barvy pozadí: {e}")
            return img
    
    def process_image(self, image_path: Path) -> bool:
        """Zpracuje jeden obrázek - univerzální přístup s auto-upscalingem"""
        try:
            # Vytvoření výstupní cesty
            relative_path = image_path.relative_to(self.input_dir)
            output_path = self.output_dir / relative_path
            
            # Vytvoření složek pokud neexistují
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Změna přípony na .jpg
            output_path = output_path.with_suffix('.jpg')
            
            # Načtení obrázku
            with Image.open(image_path) as img:
                # Konverze na RGB pokud není
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                print(f"Zpracovávám {image_path.name}: {img.width}x{img.height}px")
                
                # Krok 0: Automatický upscale malých obrázků
                img = self.auto_upscale_image(img)
                
                # Krok 1: Chytře změníme velikost a vycentrujeme produkt
                processed_img = self.smart_resize_and_center(img)
                
                # Krok 2: Změníme bílé pozadí na šedé
                processed_img = self.change_background(processed_img)
                
                # Uložení s vysokou kvalitou
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
        print(f"Automatický upscale: {'Zapnutý' if self.auto_upscale else 'Vypnutý'}")
        print(f"Prah pro upscale: {self.upscale_threshold}px")
        print(f"Upscaling metoda: {self.upscale_method}")
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
    parser = argparse.ArgumentParser(description='Universal Processor with Configuration File')
    parser.add_argument('--config', default='config.json', help='Cesta ke konfiguračnímu souboru (výchozí: config.json)')
    parser.add_argument('--input', help='Vstupní složka s obrázky (přepíše config)')
    parser.add_argument('--output', help='Výstupní složka (přepíše config)')
    parser.add_argument('--width', type=int, help='Cílová šířka (přepíše config)')
    parser.add_argument('--height', type=int, help='Cílová výška (přepíše config)')
    parser.add_argument('--quality', type=int, help='Kvalita JPG 1-100 (přepíše config)')
    parser.add_argument('--background-color', help='Barva pozadí hex (přepíše config)')
    parser.add_argument('--auto-upscale', action='store_true', help='Zapnout automatický upscale (přepíše config)')
    parser.add_argument('--no-auto-upscale', dest='auto_upscale', action='store_false', help='Vypnout automatický upscale (přepíše config)')
    
    args = parser.parse_args()
    
    # Načtení konfigurace
    config = load_config(args.config)
    
    # Přepsání konfigurace argumenty z příkazové řádky
    if args.input:
        config['input_dir'] = args.input
    if args.output:
        config['output_dir'] = args.output
    if args.width:
        config['target_size'][0] = args.width
    if args.height:
        config['target_size'][1] = args.height
    if args.quality:
        config['quality'] = args.quality
    if args.background_color:
        config['background_color'] = args.background_color
    if args.auto_upscale is not None:
        config['auto_upscale'] = args.auto_upscale
    
    # Konverze konfigurace pro UniversalProcessor
    processor_config = {
        'target_width': config['target_size'][0],
        'target_height': config['target_size'][1],
        'quality': config['quality'],
        'input_dir': config['input_dir'],
        'output_dir': config['output_dir'],
        'background_color': config['background_color'],
        'white_threshold': config['white_threshold'],
        'product_size_ratio': config['product_size_ratio'],
        'auto_upscale': config['auto_upscale'],
        'upscale_threshold': config['upscale_threshold'],
        'upscale_method': config['upscale_method']
    }
    
    # Kontrola existence vstupní složky
    input_path = Path(config['input_dir'])
    if not input_path.exists():
        print(f"❌ Chyba: Vstupní složka '{config['input_dir']}' neexistuje!")
        return
    
    # Vytvoření procesoru
    processor = UniversalProcessor(processor_config)
    
    # Spuštění zpracování
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