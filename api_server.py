#!/usr/bin/env python3
"""
Flask API Server pro Universal Image Processor
Integrace s Node.js/React aplikací
"""

import sys
import logging

# Setup logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
# Silence PIL debug logs
logging.getLogger('PIL').setLevel(logging.WARNING)

logger.info("🔧 Starting imports...")

try:
    from flask import Flask, request, jsonify, send_file, send_from_directory
    from flask_cors import CORS
    from werkzeug.utils import secure_filename
    import os
    import tempfile
    import json
    from pathlib import Path
    from universal_processor import UniversalProcessor
    import base64
    from io import BytesIO
    logger.info("✅ All imports successful")
except Exception as e:
    logger.error(f"❌ Import error: {e}", exc_info=True)
    raise


app = Flask(__name__)
app.static_folder = 'static'
app.static_url_path = ''
CORS(app)  # Povolí CORS pro React aplikaci

# Přidáme error handler pro 500 chyby
@app.errorhandler(500)
def internal_error(error):
    import traceback
    error_details = traceback.format_exc()
    print(f"❌ 500 ERROR: {error}")
    print(f"📋 TRACEBACK: {error_details}")
    return jsonify({
        'error': str(error),
        'details': error_details,
        'type': 'Internal Server Error'
    }), 500

# Konfigurace
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

# Vytvoření složky pro uploady
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_processor_config(custom_config=None):
    """Vrátí konfiguraci pro procesor"""
    # Načteme konfiguraci z config.json
    try:
        with open('config.json', 'r') as f:
            file_config = json.load(f)
            print(f"📋 Načtena konfigurace z config.json: {file_config}")
    except Exception as e:
        print(f"⚠️ Chyba při načítání config.json: {e}")
        file_config = {}
    
    default_config = {
        'target_width': 1000,
        'target_height': 1000,
        'quality': 95,
        'background_color': '#F3F3F3',
        'white_threshold': 220,
        'product_size_ratio': 0.75,
        'auto_upscale': False,
        'upscale_threshold': 800,
        'upscale_method': 'multi-scale',
        'output_format': 'webp',
        'target_max_kb': 100,
        'min_quality': 60
    }
    
    # Aktualizujeme s konfigurací z souboru
    default_config.update(file_config)
    
    # Aktualizujeme s custom konfigurací z requestu
    if custom_config:
        default_config.update(custom_config)
    
    print(f"🎯 Finální konfigurace: {default_config}")
    return default_config

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Universal Image Processor API is running',
        'version': '1.0.0'
    })

@app.route('/api/process-single', methods=['POST'])
def process_single_image():
    """Zpracuje jeden obrázek"""
    logger.info("🔍 DEBUG: Začínám process_single_image")
    print("🔍 DEBUG: Začínám process_single_image")
    try:
        print("🔍 DEBUG: Kontroluji soubor v requestu")
        # Kontrola, zda je soubor v requestu
        if 'image' not in request.files:
            print("❌ CHYBA: No image file provided")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        print(f"🔍 DEBUG: Soubor: {file.filename}")
        if file.filename == '':
            print("❌ CHYBA: No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"❌ CHYBA: Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
        
        print("🔍 DEBUG: Získávám konfiguraci")
        # Získání konfigurace z requestu
        config_data = request.form.get('config', '{}')
        print(f"🔍 DEBUG: Config data: {config_data}")
        custom_config = json.loads(config_data) if config_data else {}
        print(f"🔍 DEBUG: Custom config: {custom_config}")
        
        print("🔍 DEBUG: Vytvářím dočasnou složku")
        # Vytvoření dočasné složky
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"🔍 DEBUG: Dočasná složka vytvořena: {temp_dir}")
            
            # Uložení uploadovaného souboru
            filename = secure_filename(file.filename)
            input_path = os.path.join(temp_dir, filename)
            print(f"🔍 DEBUG: Ukládám soubor do: {input_path}")
            
            try:
                file.save(input_path)
                print(f"🔍 DEBUG: Soubor úspěšně uložen: {input_path}")
            except Exception as save_error:
                print(f"❌ CHYBA při ukládání souboru: {save_error}")
                return jsonify({'error': f'Failed to save file: {save_error}'}), 500
            
            # Kontrola, jestli soubor existuje
            if not os.path.exists(input_path):
                print(f"❌ CHYBA: Soubor neexistuje: {input_path}")
                return jsonify({'error': 'File was not saved properly'}), 500
            
            print(f"🔍 DEBUG: Soubor existuje, velikost: {os.path.getsize(input_path)} bytes")
            
            # Vytvoření výstupní cesty
            output_filename = f"processed_{filename.rsplit('.', 1)[0]}.webp"
            output_path = os.path.join(temp_dir, output_filename)
            
            print(f"🔍 DEBUG: Očekávám výstupní soubor: {output_path}")
            
            # Zpracování obrázku
            processor_config = get_processor_config(custom_config)
            processor_config['input_dir'] = temp_dir
            processor_config['output_dir'] = temp_dir
            
            print(f"Processor config: {processor_config}")
            print(f"Input path: {input_path}")
            print(f"Output path: {output_path}")
            
            processor = UniversalProcessor(processor_config)
            
            # Zpracování
            success = processor.process_image(Path(input_path))
            
            # Kontrola, jestli výstupní soubor existuje
            if not os.path.exists(output_path):
                print(f"❌ CHYBA: Výstupní soubor neexistuje: {output_path}")
                # Zkusíme najít jiné soubory ve složce
                files_in_dir = os.listdir(temp_dir)
                print(f"🔍 DEBUG: Soubory ve složce: {files_in_dir}")
                return jsonify({'error': 'Output file not found'}), 500
            
            print(f"Processing result: {success}")
            
            if not success:
                return jsonify({'error': 'Failed to process image'}), 500
            
            # Odeslání zpracovaného obrázku
            return send_file(
                output_path,
                mimetype='image/webp',
                as_attachment=True,
                download_name=output_filename
            )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR in process_single_image: {e}")
        print(f"📋 TRACEBACK: {error_details}")
        print(f"🔍 ERROR TYPE: {type(e).__name__}")
        return jsonify({
            'error': str(e),
            'details': error_details,
            'type': type(e).__name__
        }), 500

@app.route('/api/process-batch', methods=['POST'])
def process_batch_images():
    """Zpracuje více obrázků najednou"""
    try:
        # Kontrola souborů
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Získání konfigurace
        config_data = request.form.get('config', '{}')
        custom_config = json.loads(config_data) if config_data else {}
        
        # Vytvoření dočasné složky
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, 'input')
            output_dir = os.path.join(temp_dir, 'output')
            os.makedirs(input_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)
            
            # Uložení všech souborů
            uploaded_files = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(input_dir, filename)
                    file.save(file_path)
                    uploaded_files.append(filename)
            
            if not uploaded_files:
                return jsonify({'error': 'No valid files uploaded'}), 400
            
            # Zpracování
            processor_config = get_processor_config(custom_config)
            processor_config['input_dir'] = input_dir
            processor_config['output_dir'] = output_dir
            
            processor = UniversalProcessor(processor_config)
            results = processor.process_all_images()
            
            # Vytvoření ZIP souboru s výsledky
            import zipfile
            zip_path = os.path.join(temp_dir, 'processed_images.zip')
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)
            
            return send_file(
                zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name='processed_images.zip'
            )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Hlavní stránka s frontendem"""
    return send_from_directory('static', 'index.html')

@app.route('/style.css')
def style_css():
    """CSS soubor"""
    return send_from_directory('static', 'style.css')

@app.route('/script.js')
def script_js():
    """JavaScript soubor"""
    return send_from_directory('static', 'script.js')



@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Vrátí poslední logy pro debugging"""
    try:
        with open('app.log', 'r') as f:
            logs = f.read()
        return jsonify({'logs': logs})
    except FileNotFoundError:
        return jsonify({'logs': 'No log file found'})

@app.route('/api/config', methods=['GET'])
def get_default_config():
    """Vrátí výchozí konfiguraci"""
    return jsonify(get_processor_config())

@app.route('/api/config', methods=['POST'])
def update_config():
    """Aktualizuje konfiguraci"""
    try:
        config_data = request.json
        if not config_data:
            return jsonify({'error': 'No configuration provided'}), 400
        
        # Uložení do config.json
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'message': 'Configuration updated successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-base64', methods=['POST'])
def process_base64_image():
    """Zpracuje obrázek v base64 formátu"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No base64 image provided'}), 400
        
        # Dekódování base64
        image_data = base64.b64decode(data['image'])
        
        # Získání konfigurace
        custom_config = data.get('config', {})
        
        # Vytvoření dočasné složky
        with tempfile.TemporaryDirectory() as temp_dir:
            # Uložení obrázku
            input_path = os.path.join(temp_dir, 'input.jpg')
            with open(input_path, 'wb') as f:
                f.write(image_data)
            
            # Vytvoření výstupní cesty
            output_path = os.path.join(temp_dir, 'output.jpg')
            
            # Zpracování
            processor_config = get_processor_config(custom_config)
            processor = UniversalProcessor(processor_config)
            
            success = processor.process_image(Path(input_path))
            
            if not success:
                return jsonify({'error': 'Failed to process image'}), 500
            
            # Přečtení výsledku a konverze na base64
            with open(output_path, 'rb') as f:
                processed_data = f.read()
            
            processed_base64 = base64.b64encode(processed_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'processed_image': processed_base64,
                'format': 'image/jpeg'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    
    # Railway používá PORT environment proměnnou
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 Spouštím Universal Image Processor API...")
    print(f"📡 API bude dostupné na portu: {port}")
    print("🔗 Endpointy:")
    print("  - GET  / - Frontend interface")
    print("  - GET  /api/health - Health check")
    print("  - POST /api/process-single - Zpracování jednoho obrázku")
    print("  - POST /api/process-batch - Zpracování více obrázků")
    print("  - POST /api/process-base64 - Zpracování base64 obrázku")
    print("  - GET  /api/config - Získání konfigurace")
    print("  - POST /api/config - Aktualizace konfigurace")
    
    # Spustíme Flask server vždy, ale v produkci režimu
    print("🏭 Spouštím Flask server v produkci režimu...")
    print(f"🌐 Port: {port}")
    
    # Nastavíme logging pro debugging
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Spustíme Flask server bez warningů
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False) 