"""
utils/registry.py
Persistencia local de contenido generado (hilos, dosiers, blogs).
"""
import json
import os
from datetime import datetime
from config import CONTENT_REGISTRY_PATH


def _ensure_registry():
    os.makedirs(os.path.dirname(CONTENT_REGISTRY_PATH), exist_ok=True)
    if not os.path.exists(CONTENT_REGISTRY_PATH):
        with open(CONTENT_REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)


def load_registry() -> list:
    _ensure_registry()
    try:
        with open(CONTENT_REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_to_registry(tipo: str, titulo: str, contenido: str):
    registry = load_registry()
    new_entry = {
        "id": len(registry) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "titulo": titulo,
        "contenido": contenido
    }
    registry.insert(0, new_entry)
    with open(CONTENT_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)
