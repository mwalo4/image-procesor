# Codebase Structure

**Analysis Date:** 2026-02-25

## Directory Layout

```
image-procesor-repo/
├── api_server.py                     # Flask HTTP API server (423 lines)
├── universal_processor.py            # Core image processing engine (694 lines)
├── dev_server.py                     # Development server with file watching (116 lines)
├── quality_upscale_smart.py          # Utility for smart upscaling (304 lines)
├── convert_png_to_jpg_better.py      # Utility for format conversion (142 lines)
├── universal_processor_original.py   # Legacy version (archived)
│
├── static/                           # Frontend web assets
│   ├── index.html                    # HTML entry point
│   ├── script.js                     # JavaScript event handlers and API calls
│   └── style.css                     # Styling (9677 bytes)
│
├── input_images/                     # Input directory for batch processing
│   └── (user-provided image files)
├── processed_images/                 # Output directory for processed results
│   └── (generated image files)
│
├── config.json                       # Persistent configuration file
├── requirements.txt                  # Production dependencies
├── api_requirements.txt              # API-specific dependencies
│
├── .planning/                        # Planning documentation (auto-generated)
│   └── codebase/                     # Codebase analysis
│       ├── ARCHITECTURE.md
│       ├── STRUCTURE.md
│       └── (other analysis documents)
│
├── Dockerfile                        # Container definition
├── Procfile                          # Process file for deployment
├── railway.json                      # Railway platform config
├── nixpacks.toml                     # Nix package config
├── shell.nix                         # Nix development environment
├── runtime.txt                       # Python runtime version
├── .python-version                   # Local Python version (.7 = 3.7)
│
├── .gitignore                        # Git ignore rules
├── start.sh                          # Deployment startup script
├── README.md                         # Project documentation
├── DEPLOYMENT.md                     # Deployment guide
└── API_INTEGRATION_GUIDE.txt         # API usage documentation
```

## Directory Purposes

**Root Directory:**
- Purpose: Contains core application files, configuration, and entry points
- Contains: Python modules, configuration files, deployment configs
- Key files: `api_server.py` (main API), `universal_processor.py` (core logic), `config.json`

**`static/`:**
- Purpose: Static web assets served directly to browser
- Contains: HTML markup, JavaScript, CSS stylesheets
- Served by: Flask's static file handler (configured on line 40 of `api_server.py`)
- Not committed to git: May include minified or bundled assets

**`input_images/`:**
- Purpose: Staging directory for batch processing via CLI
- Contains: Image files (JPG, PNG, BMP, TIFF, WebP)
- Generated: Manual placement or script-generated
- Committed: No - contains user data
- Usage: `python universal_processor.py --input ./input_images --output ./processed_images`

**`processed_images/`:**
- Purpose: Output directory for batch processing results
- Contains: Processed image files in target format (WebP, JPEG, PNG)
- Generated: By processor, auto-created if missing (line 61)
- Committed: No - contains generated data
- Cleanup: User responsibility (not auto-deleted)

**`.planning/codebase/`:**
- Purpose: Codebase analysis and documentation for development guidance
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md
- Generated: By GSD codebase mapper tool
- Committed: Yes - referenced by other GSD tools

## Key File Locations

**Entry Points:**

| File | Purpose | Trigger |
|------|---------|---------|
| `api_server.py` | Flask HTTP API server | `python api_server.py` or Gunicorn |
| `universal_processor.py:main()` | CLI batch processor | `python universal_processor.py [args]` |
| `dev_server.py` | Development file watcher | `python dev_server.py` |
| `static/index.html` | Web frontend | Browser: `http://localhost:PORT/` |

**Configuration:**

| File | Purpose | Format |
|------|---------|--------|
| `config.json` | Persistent processor settings | JSON object (lines 1-12) |
| `requirements.txt` | Production dependencies | pip requirements format |
| `api_requirements.txt` | API-specific dependencies | pip requirements format |
| `Dockerfile` | Container image definition | Docker syntax |
| `runtime.txt` | Python version for deployment | Plain text (e.g., "3.9.18") |

**Core Logic:**

| File | Purpose | Size |
|------|---------|------|
| `universal_processor.py` | Image processing engine class | 694 lines |
| `api_server.py` | HTTP API routes and handlers | 423 lines |
| `dev_server.py` | File watching and restart logic | 116 lines |

**Documentation:**

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `DEPLOYMENT.md` | Deployment instructions |
| `API_INTEGRATION_GUIDE.txt` | API endpoint documentation |
| `.planning/codebase/ARCHITECTURE.md` | Architecture analysis |
| `.planning/codebase/STRUCTURE.md` | Directory structure guide |

**Utilities (Legacy/Optional):**

| File | Purpose | Used by |
|------|---------|---------|
| `quality_upscale_smart.py` | Standalone upscaling tool | CLI only (not API) |
| `convert_png_to_jpg_better.py` | Format converter | CLI only (not API) |
| `universal_processor_original.py` | Original implementation (archived) | Not used |

## Naming Conventions

**Files:**

| Pattern | Example | Usage |
|---------|---------|-------|
| `api_*.py` | `api_server.py` | HTTP API modules |
| `*_processor.py` | `universal_processor.py` | Image processing classes |
| `dev_*.py` | `dev_server.py` | Development tools |
| `index.html` | (standard) | Web entry point |
| `script.js` | (standard) | Frontend JavaScript |
| `style.css` | (standard) | Frontend styling |
| `requirements*.txt` | `requirements.txt`, `api_requirements.txt` | Dependency manifests |

**Directories:**

| Pattern | Example | Purpose |
|---------|---------|---------|
| `static/` | (standard) | Public web assets |
| `input_images/` | (project-specific) | Batch processing input |
| `processed_images/` | (project-specific) | Batch processing output |
| `.planning/` | (GSD convention) | Analysis documentation |
| `__pycache__/` | (auto-generated) | Python compiled cache |
| `.git/` | (auto-generated) | Git repository metadata |

**Python Naming (in code):**

- **Classes:** PascalCase (`UniversalProcessor`, `RestartHandler`)
- **Functions/Methods:** snake_case (`process_image()`, `smart_resize_and_center()`)
- **Constants:** UPPER_SNAKE_CASE (`ALLOWED_EXTENSIONS`, `UPLOAD_FOLDER`)
- **Private methods:** Leading underscore (`_hex_to_rgb()`, `_compute_product_mask()`)

**JavaScript Naming (in static/script.js):**

- **DOM IDs:** kebab-case (`#dropZone`, `#fileInput`, `#processButton`)
- **Functions:** camelCase (`handleDragOver()`, `getConfig()`, `processImages()`)
- **Variables:** camelCase (`selectedFiles`, `aiBackgroundRemoval`)
- **CSS classes:** kebab-case (`.drop-zone`, `.file-item`, `.glass-card`)

## Where to Add New Code

**New Image Processing Feature:**
- **Primary implementation:** Add method to `UniversalProcessor` class in `universal_processor.py`
- **Configuration parameter:** Add key/value to default_config in `get_processor_config()` (line 78)
- **API exposure:** Add new route in `api_server.py` if HTTP access needed
- **CLI argument:** Add argparse argument in `main()` (around line 600)
- **Example:** To add a new filter, add method to UniversalProcessor and expose via `/api/process-single` config

**New HTTP Endpoint:**
- **Location:** `api_server.py` as decorated route method
- **Pattern:** Follow existing endpoints (lines 109-387)
- **Error handling:** Wrap in try-catch, return JSON with error field
- **File handling:** Use `tempfile.TemporaryDirectory()` for cleanup
- **Validation:** Check request.files/request.json before processing
- **Example:** New endpoint for preview generation would be added after line 387

**New Frontend Feature:**
- **HTML markup:** Add to `static/index.html` in appropriate section
- **Styling:** Add CSS rules to `static/style.css`
- **Logic:** Add JavaScript functions to `static/script.js`
- **API integration:** Call Flask endpoints via `fetch()` API
- **Pattern:** Follow existing drag-drop and file list patterns (script.js lines 22-88)
- **Example:** Adding color picker for background would require HTML input, CSS styling, and JS event handler

**Utility Scripts:**
- **Location:** Root directory as `<name>.py`
- **Purpose:** CLI-only tools that don't integrate with API
- **Entry point:** `if __name__ == "__main__": main()` pattern
- **Dependencies:** Add to `requirements.txt`
- **Example:** Add new script like `analyze_images.py` for batch analysis without modifying core classes

**Configuration-Driven Customization:**
- **Modify config.json:** For persistent settings changes (no code change needed)
- **Environment variables:** Not currently used (could be added for PORT via os.environ.get())
- **Request-time config:** Pass custom config in API request body (line 142-145)
- **No code change required:** Configuration-driven approach allows tuning without deployment

**Development/Testing:**
- **Test scripts:** Create in root as `test_*.py` (follows naming convention)
- **Location:** Not committed to git (add to .gitignore if created)
- **Pattern:** Import UniversalProcessor or use API with requests library
- **Example:** `test_processor.py` for unit testing image operations

## Special Directories

**`__pycache__/`:**
- Purpose: Python compiled bytecode cache
- Generated: Yes (auto-created by Python interpreter)
- Committed: No (in .gitignore)
- When to clean: Rarely needed, but `find . -type d -name __pycache__ -exec rm -rf {} +` removes all

**`.git/`:**
- Purpose: Git repository metadata
- Generated: Yes (by `git init`)
- Committed: No (is itself the commit history)
- Ignore: Never modify directly

**`input_images/` and `processed_images/`:**
- Purpose: Runtime data directories
- Generated: Yes (auto-created if missing, line 61)
- Committed: No (.gitignore entries)
- Workflow: Users place images in input_images, processor writes to processed_images
- Cleanup: Manual (not auto-deleted) - user responsibility

**`.planning/codebase/`:**
- Purpose: GSD analysis documentation (auto-generated)
- Generated: Yes (by GSD codebase mapper)
- Committed: Yes (version control for documentation)
- Content: Markdown files for architecture, structure, conventions, testing, concerns
- Update frequency: As needed when major refactoring occurs

## Key File Dependencies

**api_server.py imports:**
- `universal_processor.UniversalProcessor` - Core processing logic
- `flask` - HTTP server
- `flask_cors.CORS` - Cross-origin request handling
- `werkzeug.utils.secure_filename` - File name sanitization
- `tempfile` - Temporary directory management
- `json`, `base64`, `io` - Data encoding/serialization

**universal_processor.py imports:**
- `PIL.Image` - Image manipulation
- `numpy` - Array operations
- `tqdm` - Progress bars
- `pathlib.Path` - File path handling
- `argparse` - CLI argument parsing

**static/script.js uses:**
- Fetch API - HTTP requests to `/api/*` endpoints
- DOM manipulation - Standard JavaScript APIs
- FormData - Multipart file upload encoding

---

*Structure analysis: 2026-02-25*
