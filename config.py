"""
config.py — Configuración Global de la App Mundial 2026
Carga API keys desde: variables de entorno > secrets_local.json
NUNCA hardcodear tokens en el código fuente.
"""
import os
import json

# ──────────────────────────────────────────────
# CARGA DE SECRETOS LOCALES
# ──────────────────────────────────────────────
_SECRETS_FILE = os.path.join(os.path.dirname(__file__), 'secrets_local.json')

def _load_secrets() -> dict:
    try:
        if os.path.exists(_SECRETS_FILE):
            with open(_SECRETS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

_s = _load_secrets()

# ──────────────────────────────────────────────
# API KEYS (orden de prioridad: env > secrets_local.json)
# ──────────────────────────────────────────────
API_FOOTBALL_DATA_TOKEN: str = (
    os.environ.get('FD_TOKEN', '')
    or _s.get('FD_TOKEN', '')
    or _s.get('API_FOOTBALL_DATA_TOKEN', '5acb2fefb13049828c5d34d10fb49850')  # fallback temporal
)

RAPIDAPI_KEY: str = (
    os.environ.get('RAPIDAPI_KEY', '')
    or _s.get('RAPIDAPI_KEY', '')
)

GEMINI_API_KEY: str = (
    os.environ.get('GEMINI_API_KEY', '')
    or _s.get('GEMINI_API_KEY', '')
)

GROK_API_KEY: str = (
    os.environ.get('GROK_API_KEY', '')
    or _s.get('GROK_API_KEY', '')
)

# ──────────────────────────────────────────────
# NOTEBOOK LM
# ──────────────────────────────────────────────
NOTEBOOK_ID = "a68a9047-1447-4685-befa-a4f1c928da8f"

# ──────────────────────────────────────────────
# CABECERAS ANTI-BLOQUEO COMUNES
# ──────────────────────────────────────────────
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# ──────────────────────────────────────────────
# FOOTBALL98 (RapidAPI) - 100 req/día en plan gratuito
# ──────────────────────────────────────────────
FOOTBALL98_HOST = "football98.p.rapidapi.com"
FOOTBALL98_BASE_URL = f"https://{FOOTBALL98_HOST}"

# ──────────────────────────────────────────────
# STREAMLIT PAGE CONFIG
# ──────────────────────────────────────────────
PAGE_CONFIG = {
    "page_title": "Mundial 2026 · Tactical Dashboard",
    "page_icon": "🌍",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ──────────────────────────────────────────────
# RUTAS DE ARCHIVOS
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')
STYLE_CSS_PATH = os.path.join(ASSETS_DIR, 'style.css')
GRUPOS_JSON_PATH = os.path.join(DATA_DIR, 'grupos.json')
NATIONS_DB_PATH = os.path.join(DATA_DIR, 'nations_db.json')
CONTENT_REGISTRY_PATH = os.path.join(ASSETS_DIR, 'content_registry.json')
