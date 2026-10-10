import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
CERTIFICATES_DIR = STORAGE_DIR / "certificates"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure required directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/certificates.db")
APP_TITLE = "Bulk Certificate Generator API"
APP_VERSION = "1.0.0"
