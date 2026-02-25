# Technology Stack

**Analysis Date:** 2026-02-25

## Languages

**Primary:**
- Python 3.11 - Backend API server and image processing logic
- HTML5 - Frontend interface
- CSS3 - Frontend styling
- JavaScript (ES6) - Frontend interaction and client-side logic

**Secondary:**
- Bash - Deployment and startup scripts

## Runtime

**Environment:**
- Python 3.11 (specified in `runtime.txt` and `.python-version`)
- Docker container: `python:3.11-slim` (from `Dockerfile`)

**Package Manager:**
- pip (Python package manager)
- Lockfile: `requirements.txt` (primary) and `api_requirements.txt` (API-specific)

## Frameworks

**Core:**
- Flask 2.3.0+ - Web framework for REST API server
- Flask-CORS 4.0.0+ - Cross-Origin Resource Sharing support for React/Node.js integration

**Web Server:**
- Werkzeug 2.3.0+ - WSGI utilities for Flask
- Gunicorn 21.0.0+ - Production WSGI HTTP server (used via `start.sh`)

**Image Processing:**
- Pillow 10.0.0+ - Primary image manipulation and format conversion
- NumPy 1.24.0+ - Numerical computing for pixel array manipulation
- OpenCV (opencv-python) 4.8.0+ - Computer vision operations for image analysis
- rembg - AI-based background removal (optional, graceful degradation if not installed)

**Build/Dev:**
- Nix (optional Nix environment via `shell.nix` for reproducible development)

## Key Dependencies

**Critical:**
- Pillow 10.0.0+ - Image loading, manipulation, format conversion (JPEG, PNG, WebP, BMP, TIFF)
- NumPy 1.24.0+ - Array operations for pixel processing, masking, filtering
- Flask 2.3.0+ - API endpoints and request routing
- Flask-CORS 4.0.0+ - CORS headers for cross-origin API access from frontend

**Infrastructure:**
- tqdm 4.66.0+ - Progress bars and iteration utilities
- requests 2.31.0+ - HTTP client library (available, not actively used in main code)
- Werkzeug 2.3.0+ - Secure filename handling, HTTP utilities
- Gunicorn 21.0.0+ - Production server (higher performance than Flask development server)

**Optional/Graceful Degradation:**
- rembg - AI-powered background removal (imported conditionally with try/except fallback)
- onnxruntime - Required by rembg for neural network inference
- scipy - Scientific computing (available in Dockerfile but not in primary requirements)

## Configuration

**Environment:**
- `PORT` - HTTP server port (default: 8080, read from `os.environ.get('PORT', 8080)`)
- Can be extended with custom env variables at deployment time (documented in `DEPLOYMENT.md`)

**Build:**
- `Dockerfile` - Docker image definition with Python 3.11-slim base
- `nixpacks.toml` - Nix-based build configuration (alternative to Dockerfile)
- `railway.json` - Railway.app deployment configuration with health check settings
- `config.json` - Runtime configuration for image processing parameters (loaded at startup in `api_server.py`)

**Processing Config (config.json):**
- `target_width` / `target_height` - Output image dimensions (default: 1000x1000)
- `background_color` - Background color for processed images (default: #F3F3F3)
- `quality` - Output quality (default: 95)
- `output_format` - Output format: 'webp' | 'jpeg' | 'png' (default: webp)
- `target_max_kb` - Maximum output file size in KB (adaptive compression)
- `auto_upscale` - Enable upscaling for small images
- `ai_background_removal` - Enable AI-based background removal via rembg

## Platform Requirements

**Development:**
- Python 3.11+ (with pip)
- Virtual environment: Python venv or Nix shell
- Docker (for containerized testing)

**Production:**
- Deployment target: Railway.app (primary, documented in `DEPLOYMENT.md`)
- Container runtime: Docker (Dockerfile provided)
- Health check: GET `/api/health` (Railway configured with 100s timeout)
- Restart policy: ON_FAILURE with max 10 retries
- Port: 8080 (HTTP server)
- Memory: Minimum 256MB recommended (higher for batch processing)

## Supported Image Formats

**Input:**
- PNG, JPG/JPEG, BMP, TIFF, WebP (extensions checked in `allowed_file()` function)

**Output:**
- WebP (default, 95 quality)
- JPEG (fallback)
- PNG (with alpha channel support for transparency)

## API Endpoints

**Core Endpoints (from `api_server.py`):**
- `GET /` - Frontend HTML interface
- `GET /api/health` - Health status check
- `POST /api/process-single` - Single image processing
- `POST /api/process-batch` - Batch processing (returns ZIP)
- `POST /api/process-base64` - Base64-encoded image processing
- `GET /api/config` - Get current processing configuration
- `POST /api/config` - Update processing configuration
- `GET /api/logs` - Retrieve application logs for debugging

## Frontend Integration

**Frontend Files:**
- `static/index.html` - Web UI (served by Flask)
- `static/script.js` - JavaScript client logic
- `static/style.css` - UI styling

**CORS Configuration:**
- `CORS(app)` enabled in `api_server.py` for cross-origin requests from React/Node.js applications
- Allows frontend on different origin/port to access API endpoints

---

*Stack analysis: 2026-02-25*
