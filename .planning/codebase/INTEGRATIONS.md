# External Integrations

**Analysis Date:** 2026-02-25

## APIs & External Services

**Image Processing:**
- rembg (AI Background Removal)
  - SDK/Client: `rembg` Python package with ONNX Runtime
  - Auth: None (open-source model)
  - Usage: Conditional import in `universal_processor.py` lines 472-496 with graceful fallback
  - Status: Optional - application continues without it if not installed

**Content Delivery:**
- Static file serving (CSS, JS, HTML) via Flask `send_from_directory()`
  - Location: `static/` directory
  - No CDN integration currently

## Data Storage

**Databases:**
- None detected - application is stateless image processor
- No database client dependencies in requirements

**File Storage:**
- Local filesystem only
  - Input directory: `temp_uploads/` (temporary uploads from requests)
  - Output directory: `processed_images/` (specified in config.json)
  - Configurable via `input_dir` and `output_dir` in `config.json`
  - Temporary processing: Python `tempfile.TemporaryDirectory()` for request isolation
  - Files: Automatically cleaned up after request completion

**Configuration Storage:**
- JSON file: `config.json` (local file at project root)
  - Loaded on startup: `api_server.py` line 71
  - Updated via POST `/api/config` endpoint
  - Persisted to disk for runtime configuration

**Caching:**
- None implemented
- Suggested optimization in `DEPLOYMENT.md` line 204: Redis cache for frequently used configurations

## Authentication & Identity

**Auth Provider:**
- None - Application is unauthenticated
- No login/user management
- Public API endpoints with no API key requirement
- CORS enabled for cross-origin access

**Security Considerations:**
- File upload validation: `allowed_file()` function checks extensions (whitelisted: png, jpg, jpeg, bmp, tiff, webp)
- Secure filename handling: `werkzeug.utils.secure_filename()` prevents path traversal
- Temporary storage: Requests use isolated temp directories

## Monitoring & Observability

**Error Tracking:**
- None detected - no external error tracking service integration
- Local error handling with try/except blocks throughout codebase

**Logs:**
- Local file logging: `app.log` (written by logging handlers in `api_server.py`)
- Log retrieval via API: GET `/api/logs` endpoint returns log file contents
- Console logging: Both stdout and file handlers configured in `api_server.py` lines 410-421
- Format: `%(asctime)s - %(levelname)s - %(message)s`
- Log level: DEBUG for application, WARNING for PIL/Pillow

**Debugging:**
- 500 error handler with full traceback response in JSON (lines 45-55 in `api_server.py`)
- Health check endpoint for liveness monitoring: `/api/health`

## CI/CD & Deployment

**Hosting:**
- Primary: Railway.app (documented in `DEPLOYMENT.md` and `railway.json`)
  - Platform: Docker-based (uses Dockerfile)
  - Health check: `/api/health` with 100s timeout
  - Restart policy: ON_FAILURE with 10 max retries
  - URL format: `https://{app-name}.railway.app`

**CI Pipeline:**
- Railway automatic deployment:
  - Trigger: Git push to main branch
  - Detection: Automatic via Dockerfile presence
  - Build: Docker image build (3-5 minutes first time)
  - Deploy: Zero-downtime deployment
  - Logs: Real-time available in Railway dashboard

**Build Configuration:**
- Dockerfile: Standard Python 3.11-slim with pip dependencies
- Alternative build: nixpacks.toml for Nix-based builds
- Fallback: Procfile (web process type)

## Environment Configuration

**Required env vars:**
- `PORT` - HTTP server port (default: 8080)
  - Read at runtime: `os.environ.get('PORT', 8080)`
  - Used in production via Railway

**Optional env vars (suggested in DEPLOYMENT.md):**
- `TARGET_WIDTH` - Output image width
- `TARGET_HEIGHT` - Output image height
- `BACKGROUND_COLOR` - Background color hex code
- `AUTO_UPSCALE` - Enable automatic upscaling
- Note: Not implemented in current code - would need env var parsing in `get_processor_config()`

**Secrets location:**
- No secrets management integrated
- No API keys, credentials, or sensitive data in codebase
- Configuration stored in `config.json` (version-controlled)
- Railway environment variables available in dashboard

**Local development:**
- No `.env` file required
- Direct Python 3.11 with pip
- Virtual environment: `venv/` directory (excluded via .gitignore)

## Webhooks & Callbacks

**Incoming:**
- None - Application is request-response only
- No webhook listeners

**Outgoing:**
- None - No external service calls for notifications
- Application only receives HTTP requests and returns responses

## Request/Response Protocol

**Request Methods:**
- GET - Configuration retrieval, health checks, static files, logs
- POST - Image upload and processing

**Content Types:**
- Accepts: multipart/form-data (file uploads), application/json (base64 images)
- Returns: image/webp (processed images), application/zip (batch results), application/json (API responses)

## External Dependencies Loading

**Import Chain:**
- Core: Flask, Werkzeug for HTTP handling
- Image Processing: Pillow, NumPy, OpenCV
- Optional: rembg with graceful import try/except at lines 472-476 in `universal_processor.py`
- Progress: tqdm for iteration progress
- Utilities: requests library available but not used in main endpoints

---

*Integration audit: 2026-02-25*
