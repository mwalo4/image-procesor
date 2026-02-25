# Architecture

**Analysis Date:** 2026-02-25

## Pattern Overview

**Overall:** Monolithic Client-Server Pattern with Single-Responsibility Image Processing Pipeline

**Key Characteristics:**
- Stateless REST API serving image processing operations
- Decoupled processor engine that handles complex image transformations
- Lightweight web frontend for user interaction
- Configuration-driven processing (flexible settings per request)
- Batch and single-image processing support
- Temporary file-based workflow with cleanup via context managers

## Layers

**Presentation Layer (Frontend):**
- Purpose: User interface for image selection, upload, and result preview
- Location: `static/` directory (`index.html`, `script.js`, `style.css`)
- Contains: HTML markup, vanilla JavaScript event handlers, CSS styling
- Depends on: `/api/*` REST endpoints
- Used by: Web browsers accessing the application

**API Gateway Layer:**
- Purpose: HTTP request routing, file validation, response formatting, CORS handling
- Location: `api_server.py` (lines 39-340)
- Contains: Flask application, route handlers, file upload validation, error handling
- Depends on: UniversalProcessor, OS file operations, JSON serialization
- Used by: Frontend JavaScript, external API clients
- Key Routes:
  - `GET /` - Serve frontend
  - `POST /api/process-single` - Single image processing
  - `POST /api/process-batch` - Batch processing with ZIP download
  - `POST /api/process-base64` - Base64 image processing
  - `GET /api/health` - Health check
  - `GET|POST /api/config` - Configuration management

**Image Processing Engine:**
- Purpose: Core image manipulation, optimization, and quality management
- Location: `universal_processor.py` (entire file)
- Contains: UniversalProcessor class with specialized methods for each processing step
- Depends on: PIL/Pillow, NumPy, file system operations
- Used by: API layer for all image transformations
- Key Methods:
  - `process_image()` - Primary entry point for single image
  - `process_all_images()` - Batch processing coordinator
  - `smart_resize_and_center()` - Intelligent scaling and positioning
  - `_compute_product_mask()` - Object detection from alpha or background
  - `_compute_background_mask_rgb()` - Flood-fill based background detection
  - `_unmatte_rgba()` - Alpha channel correction

**Configuration Layer:**
- Purpose: Load, merge, and validate processing parameters
- Location: `api_server.py` (lines 67-107, method `get_processor_config()`)
- Contains: Default configuration, file-based overrides, request-time customization
- Sources: `config.json` file, HTTP request parameters, hardcoded defaults
- Behavior: Three-level cascade with request config > file config > defaults

## Data Flow

**Single Image Processing:**

1. Browser uploads image via drag-drop or file picker → `POST /api/process-single`
2. API validates file extension against `ALLOWED_EXTENSIONS` (PNG, JPG, JPEG, BMP, TIFF, WebP)
3. Creates temporary directory with `tempfile.TemporaryDirectory()`
4. Saves uploaded file with `secure_filename()` to temp location
5. Loads configuration cascade via `get_processor_config()`
6. Instantiates `UniversalProcessor` with merged config
7. Calls `processor.process_image(Path)`
8. Processor opens image with `PIL.Image.open()`
9. Converts image mode if needed (P→RGBA, LA→RGBA, others→RGB/RGBA)
10. Optional AI background removal if enabled (rembg library)
11. Crops product from background using product mask
12. Resizes and centers product with margins using `smart_resize_and_center()`
13. Saves output in target format (WebP with adaptive quality, JPEG, or PNG)
14. Returns processed image via `send_file()` with cleanup on context exit

**Batch Processing:**

1. Browser uploads multiple images via file input
2. API receives via `POST /api/process-batch`
3. Creates temp directory with `input/` and `output/` subdirectories
4. Saves all files to `temp/input/`
5. Instantiates UniversalProcessor with temp paths
6. Calls `processor.process_all_images()` which:
   - Recursively discovers all image files in input directory
   - Iterates with progress bar (tqdm) over files
   - Calls `process_image()` for each, collecting results
   - Returns summary dict with total/processed/errors
7. Creates ZIP archive of all output files
8. Returns ZIP via `send_file()` with automatic cleanup

**Configuration State Management:**

- **Runtime Default:** Hardcoded in `get_processor_config()` (lines 78-93)
- **Persistent Override:** Loaded from `config.json` at request time
- **Request Override:** Custom config in form data/JSON body
- **Forced Settings:** `flatten_png_first=False` always forced (line 104) to prevent data loss

**Image Transformation Pipeline:**

1. **Mode Conversion:** Standardize to RGB or RGBA based on input
2. **PNG Flattening (Optional):** Composite RGBA onto white background (disabled by default)
3. **AI Background Removal (Optional):** Use rembg if enabled, produces RGBA result
4. **Product Mask Computation:** From alpha channel or RGB flood-fill
5. **Bounding Box Detection:** Find tightest product bounds with 10px padding
6. **PNG Unmatte Fix:** Remove white fringe artifacts from edge pixels (RGBA only)
7. **Cropping:** Extract product region from full image
8. **Resizing:** Scale product to target size with aspect ratio preservation
9. **Centering:** Position within canvas with minimum margin constraints
10. **Background Recoloring (Optional):** Replace white/black backgrounds with target color
11. **Compression:** Adaptive quality adjustment for WebP to meet size targets

## Key Abstractions

**UniversalProcessor Class:**
- Purpose: Encapsulates all image processing logic with configurable parameters
- Location: `universal_processor.py` (lines 17-597)
- Pattern: Stateful processor with configuration in `__init__`, public methods for processing
- Methods exposed: `process_image()`, `process_all_images()`, `find_product_bbox()`, `smart_resize_and_center()`, `change_background()`
- Private methods: `_hex_to_rgb()`, `_unmatte_rgba()`, `_compute_background_mask_rgb()`, `_compute_product_mask()`

**Flask Application (app):**
- Purpose: HTTP server and route handler orchestration
- Location: `api_server.py` (lines 39-42)
- Pattern: Singleton Flask instance with decorator-based routes
- Configuration: CORS enabled, static folder set to `static/`
- Error handling: Global 500 error handler (lines 45-55)

**Configuration Object (Dict):**
- Purpose: Centralized settings container
- Structure: Dictionary with ~20 keys controlling all processing behavior
- Validation: Minimal (some values have implicit ranges like 0-255)
- Merging: Three-level cascade with update() calls

## Entry Points

**HTTP API Server:**
- Location: `api_server.py`
- Triggers: `python api_server.py` or via Gunicorn in production
- Port: Environment variable `PORT` (default 8080)
- Responsibilities: Request routing, validation, response formatting, file handling
- Key initialization (lines 389-424):
  - Sets logging configuration
  - Configures Flask app
  - Starts Werkzeug server on configured port

**CLI Image Processor:**
- Location: `universal_processor.py` (lines 599-693, `main()` function)
- Triggers: `python universal_processor.py [arguments]`
- Responsibilities: Standalone batch processing without HTTP layer
- Argparse configuration: ~20 command-line arguments for full configuration
- Workflow: Parse args → build config dict → instantiate processor → process_all_images()

**Development Server:**
- Location: `dev_server.py`
- Triggers: `python dev_server.py`
- Responsibilities: File watching and automatic restart for development
- Uses watchdog library to monitor `.py` file changes
- Launches `api_server.py` as subprocess (debounced with 2-second minimum)

## Error Handling

**Strategy:** Try-catch with detailed error logging and user-friendly JSON responses

**API Layer (api_server.py):**
- Global 500 handler returns JSON with error message, traceback, and error type
- Per-route try-catch blocks return 400 for validation errors, 500 for server errors
- All errors logged to stdout and optionally to `app.log` file
- File operations wrapped in checks (file exists, readable, writable)

**Processor Layer (universal_processor.py):**
- `process_image()` catches exceptions and prints error, returns boolean
- `process_all_images()` collects errors in results dict without halting batch
- Exception messages include context (image path, operation being performed)
- Silent fallback for missing features (e.g., rembg not installed, falls back to standard processing)

**Validation:**
- File extension validation against `ALLOWED_EXTENSIONS` before processing
- Mode conversion with fallback conversions (P→RGBA, LA→RGBA, default→RGB)
- Image existence checks before operations (lines 165-167)
- Configuration value validation through implicit type coercion

## Cross-Cutting Concerns

**Logging:**
- Python logging module configured in `api_server.py` (lines 11-18)
- Level: DEBUG in development, ERROR for werkzeug suppression
- Output: Stdout with format `%(asctime)s - %(levelname)s - %(message)s`
- File logging: Optional to `app.log` (lines 313-317)
- Print statements throughout for visibility (debug comments like `🔍 DEBUG:`, `✅`, `❌`)

**Validation:**
- File extension whitelist: `ALLOWED_EXTENSIONS` = {png, jpg, jpeg, bmp, tiff, webp}
- Filename sanitization: `werkzeug.utils.secure_filename()` before save
- Image mode validation: Convert unsupported modes to RGB/RGBA
- Configuration bounds: Implicit constraints (e.g., quality 1-100, thresholds 0-255)

**Authentication:**
- Not implemented - API is publicly accessible
- CORS enabled with `Flask-CORS` for cross-origin requests
- No token/credential validation

**Concurrency:**
- Gunicorn handles multiple worker processes in production
- Each request isolated in temporary directory (no shared state)
- No database locks or transaction handling needed
- File-based processing (read input, write output) naturally concurrent

**Resource Management:**
- Temporary files: Context manager `with tempfile.TemporaryDirectory()` auto-cleanup
- Memory: PIL images loaded entirely into memory (potential concern for huge images)
- Storage: Processed images deleted immediately after download (temp files)
- CPU: Blocking I/O during image processing (no async operations)

---

*Architecture analysis: 2026-02-25*
