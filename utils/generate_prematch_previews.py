# -*- coding: utf-8 -*-
"""
utils/generate_prematch_previews.py
Genera automáticamente archivos Markdown con las previas tácticas de los partidos de una fecha.
Usa la API de Football-Data.org para listar los partidos y Gemini para la generación táctica.
"""
import os
import sys
import re
import json
import requests
from datetime import datetime, timedelta

# Agregar directorio raíz al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import API_FOOTBALL_DATA_TOKEN, COMMON_HEADERS
from core.ai_generator import _generate

DATA_DIR = os.path.join(BASE_DIR, 'data', 'analisis_partidos')
os.makedirs(DATA_DIR, exist_ok=True)

TEAM_NAME_MAP = {
    "Czechia": "Rep. Checa",
    "Czech Republic": "Rep. Checa",
    "Korea Republic": "Corea del Sur",
    "South Korea": "Corea del Sur",
    "Bosnia-Herzegovina": "Bosnia",
    "Bosnia": "Bosnia",
    "United States": "USA",
    "USA": "USA",
    "Switzerland": "Suiza",
    "Morocco": "Marruecos",
    "Scotland": "Escocia",
    "Turkey": "Turquía",
    "Turkiye": "Turquía",
    "Germany": "Alemania",
    "Curaçao": "Curazao",
    "Curacao": "Curazao",
    "Netherlands": "Países Bajos",
    "Japan": "Japón",
    "Sweden": "Suecia",
    "Tunisia": "Túnez",
    "Belgium": "Bélgica",
    "Egypt": "Egipto",
    "Iran": "Irán",
    "New Zealand": "Nueva Zelanda",
    "Spain": "España",
    "Cape Verde": "Cabo Verde",
    "Saudi Arabia": "Arabia Saudí",
    "Arabia Saudí": "Arabia Saudí",
    "Uruguay": "Uruguay",
    "Iraq": "Irak",
    "France": "Francia",
    "Senegal": "Senegal",
    "Norway": "Noruega",
    "Argentina": "Argentina",
    "Algeria": "Argelia",
    "Austria": "Austria",
    "Jordan": "Jordania",
    "Congo DR": "RD Congo",
    "DR Congo": "RD Congo",
    "Portugal": "Portugal",
    "Uzbekistan": "Uzbekistán",
    "Colombia": "Colombia",
    "England": "Inglaterra",
    "Croatia": "Croacia",
    "Ghana": "Ghana",
    "Panama": "Panamá",
    "Ivory Coast": "Costa de Marfil",
    "South Africa": "Sudáfrica",
    "Haiti": "Haití",
    "Qatar": "Qatar",
    "Canada": "Canadá",
    "Brazil": "Brasil",
    "Ecuador": "Ecuador",
    "Paraguay": "Paraguay",
    "Australia": "Australia",
    "Mexico": "México"
}

FLAGS_MAP = {
    "Rep. Checa": "🇨🇿", "México": "🇲🇽", "Sudáfrica": "🇿🇦", "Corea del Sur": "🇰🇷",
    "Bosnia": "🇧🇦", "Canadá": "🇨🇦", "Qatar": "🇶🇦", "Suiza": "🇨🇭",
    "Brasil": "🇧🇷", "Marruecos": "🇲🇦", "Haití": "🇭🇹", "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Turquía": "🇹🇷", "USA": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺",
    "Alemania": "🇩🇪", "Curazao": "🇨🇼", "Costa de Marfil": "🇨🇮", "Ecuador": "🇪🇨",
    "Suecia": "🇸🇪", "Países Bajos": "🇳🇱", "Japón": "🇯🇵", "Túnez": "🇹🇳",
    "Bélgica": "🇧🇪", "Egipto": "🇪🇬", "Irán": "🇮🇷", "Nueva Zelanda": "🇳🇿",
    "España": "🇪🇸", "Cabo Verde": "🇨🇻", "Arabia Saudí": "🇸🇦", "Uruguay": "🇺🇾",
    "Irak": "🇮🇶", "Francia": "🇫🇷", "Senegal": "🇸🇳", "Noruega": "🇳🇴",
    "Argentina": "🇦🇷", "Argelia": "🇩🇿", "Austria": "🇦🇹", "Jordania": "🇯🇴",
    "RD Congo": "🇨🇩", "Portugal": "🇵🇹", "Uzbekistán": "🇺🇿", "Colombia": "🇨🇴",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croacia": "🇭🇷", "Ghana": "🇬🇭", "Panamá": "🇵🇦"
}

def get_matches_for_date(date_str):
    """Obtiene los partidos de la API, con fallback a archivo local."""
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {**COMMON_HEADERS, "X-Auth-Token": API_FOOTBALL_DATA_TOKEN}
    
    matches = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            matches = res.json().get("matches", [])
        else:
            print(f"⚠️ Error API Football-Data ({res.status_code}). Intentando cargar desde fallback local...")
            raise Exception()
    except Exception:
        fallback_path = os.path.join(BASE_DIR, "scratch", "wc_matches.json")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                matches = json.load(f)
        else:
            print("❌ No se encontró el archivo de fallback wc_matches.json.")
            return []
            
    # Filtrar por fecha
    filtered = [m for m in matches if m.get("utcDate", "").startswith(date_str)]
    return filtered

def generate_tactical_previews(date_str):
    print(f"🔍 Buscando partidos programados para la fecha: {date_str}...")
    matches = get_matches_for_date(date_str)
    
    if not matches:
        print(f"ℹ️ No se encontraron partidos programados para el {date_str}.")
        return
        
    print(f"✨ Se encontraron {len(matches)} partidos. Iniciando generación táctica con IA...")
    
    for m in matches:
        home_en = m.get("homeTeam", {}).get("name")
        away_en = m.get("awayTeam", {}).get("name")
        
        home_es = TEAM_NAME_MAP.get(home_en, home_en)
        away_es = TEAM_NAME_MAP.get(away_en, away_en)
        
        home_flag = FLAGS_MAP.get(home_es, "🏳️")
        away_flag = FLAGS_MAP.get(away_es, "🏳️")
        
        group_raw = m.get("group", "GROUP_A")
        group_es = group_raw.replace("GROUP_", "Grupo ")
        
        utc_date_str = m.get("utcDate", "")
        match_time = "14:00"
        if "T" in utc_date_str:
            match_time = utc_date_str.split("T")[1][:5]
            
        slug = f"{home_es.lower().replace(' ', '_').replace('.', '')}_{away_es.lower().replace(' ', '_').replace('.', '')}"
        slug = slug.replace('í', 'i').replace('á', 'a').replace('é', 'e').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        
        date_clean = date_str.replace("-", "")
        filename = f"{date_clean}_{slug}.md"
        filepath = os.path.join(DATA_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"⏭️ El archivo {filename} ya existe. Saltando.")
            continue
            
        print(f"🧠 Generando previa táctica para: {home_es} vs {away_es} ({group_es})...")
        
        prompt = f"""Eres un analista táctico de fútbol de élite mundial para el FIFA Mundial 2026.
Genera un análisis previo al partido (Pre-Partido) sumamente detallado e inteligente para el partido: {home_es} vs {away_es} del {group_es}.

El análisis debe estar en español y redactado en formato Markdown, enfocado en ventajas y desventajas tácticas con base en estadísticas avanzadas (como volumen de juego, presión, mapa de calor, xT, redes de pases, etc.).

Estructura obligatoria del cuerpo:

## {home_flag} {home_es}: Análisis Táctico

### Ventajas
* **[Detalle 1]:** [Explicación detallada de 2-3 líneas sobre cómo y por qué es una ventaja, usando datos tácticos].
* **[Detalle 2]:** [Explicación detallada de 2-3 líneas].

### Desventajas
* **[Detalle 1]:** [Explicación detallada de 2-3 líneas].
* **[Detalle 2]:** [Explicación detallada de 2-3 líneas].

---

## {away_flag} {away_es}: Análisis Táctico

### Ventajas
* **[Detalle 1]:** [Explicación detallada de 2-3 líneas].
* **[Detalle 2]:** [Explicación detallada de 2-3 líneas].

### Desventajas
* **[Detalle 1]:** [Explicación detallada de 2-3 líneas].
* **[Detalle 2]:** [Explicación detallada de 2-3 líneas].

---

## ⚖️ Comparativa y Veredicto (Pre-Partido)
[Redactar 2 párrafos analíticos comparando ambos estilos de juego y cómo se neutralizarán o impondrán en el mediocampo y las áreas].

**El pronóstico inicial apunta a [detallar el marcador exacto proyectado, ej: una victoria de X por 2 - 0 o un empate 1 - 1]**, materializando la superioridad técnica o el equilibrio de ambos planteles.
"""

        body_text, err = _generate(prompt)
        
        if err or not body_text:
            print(f"❌ Error al generar previa para {home_es} vs {away_es}: {err}")
            continue
            
        # Parsear goles del pronóstico generado en el veredicto
        pronostico_val = "0 - 0"
        score_match = re.search(r'(\d+)\s*-\s*(\d+)', body_text)
        if score_match:
            pronostico_val = f"{score_match.group(1)} - {score_match.group(2)}"
            
        poisson_val = "34-33-33"
        if "victoria de " + home_es in body_text.lower():
            poisson_val = "50-30-20"
        elif "victoria de " + away_es in body_text.lower():
            poisson_val = "20-30-50"
            
        markdown_content = f"""---
id: {date_clean}_{slug}
titulo: "{home_es} vs {away_es}: Previa Táctica del {group_es}"
grupo: "{group_es}"
fecha: "{date_str}"
hora: "{match_time}"
home_team: "{home_es}"
away_team: "{away_es}"
goles_home: 0
goles_away: 0
pronostico: "{pronostico_val}"
finalizado: "false"
imagenes: ""
slug: "{slug}"
poisson: "{poisson_val}"
---

{body_text.strip()}
"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"✅ Previa guardada en: data/analisis_partidos/{filename}")

if __name__ == "__main__":
    target_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        
    generate_tactical_previews(target_date)
