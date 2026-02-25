# Testing Patterns

**Analysis Date:** 2026-02-25

## Test Framework

**Status:** No automated testing framework detected

**Current State:**
- No pytest, unittest, or other test runner configuration found
- No test files present (no `*_test.py` or `test_*.py` files)
- No testing configuration files: pytest.ini, setup.cfg, tox.ini not present
- Codebase is image processing application in production use without automated tests

**Testing Approach:** Manual testing and integration testing through:
- Direct Python script execution: `python universal_processor.py --input input_images --output processed_images`
- Flask API endpoints manually tested via HTTP requests
- Development server with auto-restart for manual iteration: `python dev_server.py`

## Test Organization

**Location:** Not applicable - no test files present

**Naming:** Not applicable - no test files present

**Structure:** Not applicable - no test files present

## Manual Testing Approach

**Command-line Testing:**

The main script `universal_processor.py` can be tested directly with command-line arguments:

```bash
# Single image processing
python universal_processor.py --input input_images --output processed_images --file path/to/image.png

# Batch processing with custom configuration
python universal_processor.py \
  --input input_images \
  --output processed_images \
  --width 1000 \
  --height 1000 \
  --quality 95 \
  --format webp \
  --background-color '#F3F3F3' \
  --white-threshold 190
```

**API Testing:**

Flask API endpoints in `api_server.py` expose these testing points:

- `GET /api/health` - Health check endpoint (line 109-116)
- `POST /api/process-single` - Single image processing (line 118-226)
- `POST /api/process-batch` - Batch image processing (line 228-290)
- `POST /api/process-base64` - Base64 image processing (line 341-387)
- `GET /api/config` - Get current configuration (line 319-322)
- `POST /api/config` - Update configuration (line 324-339)
- `GET /api/logs` - Retrieve debug logs (line 309-317)

**Development Server:**

Auto-restart development server watches for file changes:

```bash
python dev_server.py
# Watches all Python files and restarts Flask server on modifications
```

## Error Handling Testing

**Current Pattern:** Error cases print to console and log files

**Print-based Error Reporting:**

Functions use print statements to report errors rather than raising exceptions:

```python
# From universal_processor.py (line 296-298)
except Exception as e:
    print(f"Chyba při hledání bounding box: {e}")
    return None
```

```python
# From universal_processor.py (line 558-560)
except Exception as e:
    print(f"Chyba při zpracování {image_path}: {e}")
    return False
```

**API Error Responses:**

Flask routes return JSON error responses with HTTP status codes:

```python
# From api_server.py (line 126-128)
if 'image' not in request.files:
    print("❌ CHYBA: No image file provided")
    return jsonify({'error': 'No image file provided'}), 400
```

```python
# From api_server.py (line 45-55)
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
```

## Return Value Pattern

**Success/Failure Indication:**

Methods signal success or failure through return values rather than exceptions:

```python
# From universal_processor.py (line 437-560)
def process_image(self, image_path: Path) -> bool:
    """Zpracuje jeden obrázek - univerzální přístup"""
    try:
        # ... processing logic ...
        return True
    except Exception as e:
        print(f"Chyba při zpracování {image_path}: {e}")
        return False
```

**Result Dictionaries:**

Batch operations return structured result dictionaries:

```python
# From universal_processor.py (line 571-597)
def process_all_images(self) -> Dict:
    """Zpracuje všechny obrázky"""
    # ...
    results = {
        'total': len(image_files),
        'processed': 0,
        'errors': []
    }
    # ... populate results ...
    return results
```

## Integration Testing Points

**File System Integration:**

- Input directory scanning: `get_image_files()` lists all images recursively
- Output directory creation: `mkdir(exist_ok=True)` handles directory creation
- Temporary directory usage: `tempfile.TemporaryDirectory()` for safe intermediate storage

**Image Format Testing:**

Supports multiple input formats:
- PNG (with alpha channel handling)
- JPG/JPEG
- BMP
- TIFF
- WebP
- Palette mode with transparency

Supports multiple output formats:
- WebP (with adaptive quality compression)
- PNG
- JPEG (with quality and optimization settings)

**Configuration Testing:**

- Load from `config.json`: `api_server.py` line 71-76
- Override with request parameters: `api_server.py` line 99-100
- Force critical settings: `api_server.py` line 102-104

## Performance/Quality Verification

**Print-based Progress:**

TQDM progress bars used for visual feedback:

```python
# From universal_processor.py (line 589)
for image_path in tqdm(image_files, desc="Univerzální zpracování"):
```

**Result Statistics:**

Verbose output shows processing results:

```python
# From universal_processor.py (line 674-690)
print("\n" + "="*50)
print("VÝSLEDKY UNIVERZÁLNÍHO ZPRACOVÁNÍ")
print("="*50)
print(f"Celkem obrázků: {results['total']}")
print(f"Úspěšně zpracováno: {results['processed']}")
print(f"Chyby: {len(results['errors'])}")
```

**Debug Logging:**

Flask server logs requests and processing steps:

```python
# From api_server.py (line 121-122)
logger.info("🔍 DEBUG: Začínám process_single_image")
print("🔍 DEBUG: Začínám process_single_image")
```

Logs written to:
- `app.log` file (retrievable via `/api/logs` endpoint)
- stdout for interactive monitoring
- stderr if configured

## Coverage

**Requirements:** None enforced

**No Coverage Tool:** Project lacks coverage measurement (no coverage.py, pytest-cov, or similar)

**Manual Coverage Approach:** Testing done by:
1. Running main script with various image types and configurations
2. Testing Flask API endpoints with curl/Postman
3. Monitoring console output and app.log for errors
4. Manual verification of output image quality and correctness

## Test Types

**Unit Testing:** Not implemented

**Integration Testing:** Manual API testing

**E2E Testing:** Manual end-to-end via Flask API with file uploads

**Performance Testing:** Manual by processing different image sizes and monitoring:
- Processing time output by print statements
- File size of output (especially for WEBP with target_max_kb)
- Memory usage through system monitoring

## Code Path Testing Areas

**Critical Paths Requiring Manual Verification:**

1. **Image Format Conversion** (`universal_processor.py` lines 453-467):
   - PNG with alpha channel handling
   - Palette mode detection and conversion
   - Color space conversions (LA, RGBA, RGB)

2. **Background Detection** (`universal_processor.py` lines 160-267):
   - White background detection with dynamic thresholds
   - Black background detection
   - Auto-detection choosing between white/black
   - Edge barrier gradient calculation

3. **Product Centering** (`universal_processor.py` lines 280-415):
   - Bounding box detection with padding
   - Aspect ratio calculation
   - Canvas padding and centering logic

4. **Quality Compression** (`universal_processor.py` lines 506-543):
   - Adaptive WEBP quality based on target file size
   - Quality degradation loop (max 10 iterations)
   - PNG and JPEG output options

5. **AI Background Removal** (`universal_processor.py` lines 469-498):
   - rembg library import handling (optional dependency)
   - Alpha blending with background color
   - Fallback on import failure

## Suggested Testing Additions

**High Priority:**

1. **Unit Tests for Image Processing:**
   - `_hex_to_rgb()` color conversion
   - `_compute_background_mask_rgb()` background detection accuracy
   - `find_product_bbox()` bounding box edge cases

2. **Integration Tests for API:**
   - POST `/api/process-single` with various image formats
   - POST `/api/process-batch` with multiple files
   - POST `/api/config` configuration persistence

3. **Configuration Tests:**
   - Default config loading from `config.json`
   - Override precedence (file config → custom config → forced settings)
   - Invalid configuration handling

**Medium Priority:**

4. **Output Quality Tests:**
   - WEBP file size vs target_max_kb compliance
   - JPEG quality settings produce expected output
   - PNG transparency preservation

5. **Error Recovery Tests:**
   - Invalid image file handling
   - Missing image files
   - File permission errors
   - Out of disk space handling

---

*Testing analysis: 2026-02-25*
