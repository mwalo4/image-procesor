# Coding Conventions

**Analysis Date:** 2026-02-25

## Naming Patterns

**Files:**
- PascalCase for main modules: `UniversalProcessor` logic in `universal_processor.py`
- snake_case for utility files: `convert_png_to_jpg_better.py`, `quality_upscale_smart.py`, `dev_server.py`, `api_server.py`
- Python script convention with shebang: `#!/usr/bin/env python3` at the top of executable files

**Functions:**
- snake_case for all function names: `allowed_file()`, `get_processor_config()`, `process_single_image()`, `smart_resize_and_center()`
- Private methods prefixed with underscore: `_hex_to_rgb()`, `_unmatte_rgba()`, `_compute_background_mask_rgb()`, `_compute_product_mask()`
- Nested/local functions also use snake_case: `enqueue_edge_seeds()`, `dilate_mask()`

**Variables:**
- snake_case for all variables and parameters: `target_width`, `background_color`, `white_threshold`, `product_size_ratio`
- Configuration dictionaries in snake_case: `config = { 'target_width': 1000, 'target_height': 1000 }`
- Private/internal variables prefixed with underscore in some contexts: `_hex_to_rgb(hex_color: str)`

**Classes:**
- PascalCase for class names: `UniversalProcessor`, `RestartHandler`, `DevServer`
- Constructor method: `__init__()` following Python conventions

**Constants:**
- UPPER_SNAKE_CASE for constants (when used): `UPLOAD_FOLDER`, `ALLOWED_EXTENSIONS`, `IMAGE_EXTS`, `HAS_CV2`

## Code Style

**Formatting:**
- No explicit code formatter configured (no black config, prettier, or similar found)
- Indentation: 4 spaces (Python standard)
- Line length: observed to be variable, some lines exceed 80 characters
- Spacing: single space after commas, consistent spacing around operators

**Linting:**
- No linting configuration found (.flake8, .pylintrc, pyproject.toml, setup.cfg not present)
- Code appears to follow general PEP 8 conventions without strict enforcement
- Type hints are used in function signatures: `def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:`

## Import Organization

**Order:**
1. Shebang and docstring: `#!/usr/bin/env python3`, `"""Module docstring"""`
2. Standard library imports: `import sys`, `import logging`, `import os`, `import json`
3. Third-party imports: `from flask import Flask`, `from PIL import Image`, `import numpy as np`
4. Local/relative imports: `from universal_processor import UniversalProcessor`, `from pathlib import Path`

**Example from `api_server.py` (lines 7-32):**
```python
import sys
import logging
# ... logging setup ...
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
```

**Example from `universal_processor.py` (lines 7-15):**
```python
import os
from PIL import Image, ImageFilter
from io import BytesIO
from tqdm import tqdm
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
import numpy as np
from collections import deque
```

**Path Aliases:**
- No path aliases configured (no jsconfig.json, tsconfig paths, or PYTHONPATH configuration found)
- Imports are relative to the project root where scripts are located

## Error Handling

**Patterns:**
- Generic `try/except Exception` blocks catching all exceptions broadly
- Print statements used for error logging: `print(f"Chyba při změně velikosti: {e}")`
- Functions return False or None on error: `process_image()` returns `bool`, `find_product_bbox()` returns `Optional[Tuple]`
- Error messages often include Czech language comments and emoji indicators
- Nested try/except blocks for handling optional imports: see `universal_processor.py` lines 471-498 for rembg AI background removal

**Example from `universal_processor.py` (lines 439-443):**
```python
try:
    try:
        relative_path = image_path.relative_to(self.input_dir)
    except Exception:
        relative_path = Path(image_path.name)
    # ... rest of processing ...
except Exception as e:
    print(f"Chyba při zpracování {image_path}: {e}")
    return False
```

**Example from `api_server.py` (lines 471-498):**
```python
try:
    from rembg import remove
    # ... process with rembg ...
except ImportError:
    print(f"  ⚠️ rembg není nainstalované, přeskakuji AI background removal")
except Exception as e:
    print(f"  ⚠️ Chyba při AI background removal: {e}")
```

## Logging

**Framework:** `logging` module (Python standard library)

**Setup Pattern (in `api_server.py` lines 10-18):**
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logging.getLogger('PIL').setLevel(logging.WARNING)
```

**Patterns:**
- Logger created per module using `logger = logging.getLogger(__name__)`
- Log levels: DEBUG, ERROR used
- Format: timestamp, level, message
- Print statements also used for user-facing output and debugging
- Emoji icons used in print statements for visual feedback: `✅`, `❌`, `⚠️`, `🔧`, `📋`

**Example logging calls:**
```python
logger.info("🔧 Starting imports...")
logger.error(f"❌ Import error: {e}", exc_info=True)
print(f"📋 Finální konfigurace: {default_config}")
```

## Comments

**When to Comment:**
- Inline comments explain complex business logic and configuration decisions
- IMPORTANT markers for critical settings that should not be overridden
- Configuration comments explain threshold choices and algorithm rationale
- Czech language used in comments and docstrings (code is in a Czech context)

**Example from `api_server.py` (lines 83-92):**
```python
'white_threshold': 190, # Sníženo na 190 + změna logiky na průměrný jas (catch more shadows)
...
'flatten_png_first': False,  # Vypnuto - nyní používáme nativní alfa kanál pro správnou kompozici
'recolor_background': False # DŮLEŽITÉ: Vypnout, jinak ničí černé/bílé části produktu!
```

**JSDoc/TSDoc:**
- Not used (Python project, not TypeScript)
- Python docstrings used for function documentation

## Docstrings

**Pattern:** Triple-quoted strings for functions and class documentation

**Example from `universal_processor.py`:**
```python
def _unmatte_rgba(self, img: Image.Image) -> Image.Image:
    """Odstraní barevný matte z RGBA pouze na pixelech s bílým fringe.

    Nová verze: aplikuje unmatte POUZE na pixely které:
    1. Jsou na okraji (sousedí s průhledností)
    2. Mají světlou barvu blízkou matte (bílý fringe)

    Tmavé okrajové pixely zůstávají nedotčeny (žádný černý okraj).
    """

def _compute_background_mask_rgb(self, img: Image.Image) -> np.ndarray:
    """Rychlé flood-fill pozadí: vyhodnotí bělavost/černost na downscalované verzi a výsledek upscaluje.
    ...
    """
```

## Function Design

**Size:** Functions range from small utility functions (10-20 lines) to larger processing pipelines (100+ lines)
- Example small: `_hex_to_rgb()` - 3 lines
- Example medium: `change_background()` - ~16 lines
- Example large: `process_image()` - ~120 lines with nested logic

**Parameters:**
- Explicit typed parameters using type hints: `def process_image(self, image_path: Path) -> bool:`
- Configuration often passed as Dict: `def __init__(self, config: Dict):`
- Optional parameters used: `custom_config: Optional[Dict] = None`

**Return Values:**
- Functions return meaningful types: `bool` for success/failure, `Dict` for results
- None used for "not found" cases: `Optional[Tuple[int, int, int, int]]`
- Broad types used: `Dict`, `List[Path]` without specific type parameters in older code

## Module Design

**Exports:**
- Main class exported implicitly through module: `UniversalProcessor` in `universal_processor.py`
- Main entry point via `if __name__ == "__main__":` pattern
- Flask routes defined directly in `api_server.py` with `@app.route()` decorator

**Example from `universal_processor.py` (line 694-695):**
```python
if __name__ == "__main__":
    main()
```

**Barrel Files:** Not used - no `__init__.py` files creating barrel exports (single-file modules approach)

## Class Structure

**Class Design in `UniversalProcessor` (lines 17-62):**
```python
class UniversalProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.target_width = config.get('target_width', 400)
        self.target_height = config.get('target_height', 400)
        # ... multiple instance variables initialized from config
```

- Configuration-driven approach: constructor takes config dict and extracts settings
- Instance variables store configuration as attributes: `self.target_width`, `self.background_color`
- Private methods for internal operations: `_hex_to_rgb()`, `_compute_background_mask_rgb()`
- Public methods for main API: `process_image()`, `process_all_images()`, `get_image_files()`

## Type Hints Usage

**Pattern:** Type hints used in function signatures (targeting Python 3.7+)

**Examples:**
```python
def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
def _unmatte_rgba(self, img: Image.Image) -> Image.Image:
def find_product_bbox(self, img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
def get_image_files(self) -> List[Path]:
def process_all_images(self) -> Dict:
```

---

*Convention analysis: 2026-02-25*
