#!/usr/bin/env python3
"""
Better PNG to JPG conversion that preserves original background
"""

import os
import sys
from PIL import Image
from pathlib import Path
from tqdm import tqdm

def convert_png_to_jpg_better(input_dir, output_dir, quality=95):
    """Convert PNG files to JPG preserving original background"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PNG files
    png_files = list(input_path.rglob("*.png"))
    print(f"🔍 Found {len(png_files)} PNG files to convert")
    
    if not png_files:
        print("✅ No PNG files found!")
        return
    
    converted_count = 0
    error_count = 0
    
    for png_file in tqdm(png_files, desc="Converting PNG to JPG"):
        try:
            # Open PNG image
            with Image.open(png_file) as img:
                # Get original mode
                original_mode = img.mode
                
                if original_mode in ('RGBA', 'LA'):
                    # For RGBA/LA, we need to handle transparency properly
                    if original_mode == 'RGBA':
                        # Create a new image with the same size
                        # Use the alpha channel to blend with a white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:  # LA mode
                        # Convert LA to RGB
                        img = img.convert('RGB')
                elif original_mode == 'P':
                    # Palette mode with transparency
                    if 'transparency' in img.info:
                        img = img.convert('RGBA')
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif original_mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create output filename
                jpg_file = output_path / (png_file.stem + '.jpg')
                
                # Save as JPG
                img.save(jpg_file, 'JPEG', quality=quality, optimize=True)
                
                converted_count += 1
                
        except Exception as e:
            print(f"❌ Error converting {png_file}: {e}")
            error_count += 1
    
    print(f"\n✅ Conversion complete!")
    print(f"📊 Converted: {converted_count}")
    print(f"❌ Errors: {error_count}")

if __name__ == "__main__":
    # Convert the 20 selected files
    selected_files = [
        "processed_grizly/Full_prevest_png/Cptml100.png",
        "processed_grizly/Full_prevest_png/fbsmrp300_1.png", 
        "processed_grizly/Full_prevest_png/TCDrhc30.png",
        "processed_grizly/Full_prevest_png/miwg-cok_1.png",
        "processed_grizly/Full_prevest_png/Lpo20.png",
        "processed_grizly/Full_prevest_png/kbpsk120_1.png",
        "processed_grizly/Full_prevest_png/Efdko50.png",
        "processed_grizly/Full_prevest_png/gbpjw2000-sc_1.png",
        "processed_grizly/Full_prevest_png/LLmkč300.png",
        "processed_grizly/Full_prevest_png/kmkj480.png",
        "processed_grizly/Full_prevest_png/bpmb120_1.png",
        "processed_grizly/Full_prevest_png/NSpszps100.png",
        "processed_grizly/Full_prevest_png/ffppam66_2.png",
        "processed_grizly/Full_prevest_png/gpbko70_1.png",
        "processed_grizly/Full_prevest_png/bpbgspch60_1.png",
        "processed_grizly/Full_prevest_png/gbppmv500_1.png",
        "processed_grizly/Full_prevest_png/tchvelmix12_1.png",
        "processed_grizly/Full_prevest_png/Ym550.png",
        "processed_grizly/Full_prevest_png/fbkjmrs100_1.png",
        "processed_grizly/Full_prevest_png/CCHvvč120.png"
    ]
    
    print("🔄 Better PNG to JPG Converter")
    print("=" * 40)
    print(f"📁 Converting 20 selected PNG files")
    print(f"📁 Output directory: processed_grizly/test_conversion")
    
    # Convert selected files
    for png_file in tqdm(selected_files, desc="Converting selected files"):
        try:
            png_path = Path(png_file)
            if not png_path.exists():
                print(f"❌ File not found: {png_file}")
                continue
                
            with Image.open(png_path) as img:
                original_mode = img.mode
                
                if original_mode in ('RGBA', 'LA'):
                    if original_mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif original_mode == 'P':
                    if 'transparency' in img.info:
                        img = img.convert('RGBA')
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif original_mode != 'RGB':
                    img = img.convert('RGB')
                
                jpg_file = Path("processed_grizly/test_conversion") / (png_path.stem + '.jpg')
                img.save(jpg_file, 'JPEG', quality=95, optimize=True)
                
        except Exception as e:
            print(f"❌ Error converting {png_file}: {e}")
    
    print(f"\n✅ Conversion complete!")
    print(f"📁 Check results in: processed_grizly/test_conversion")
