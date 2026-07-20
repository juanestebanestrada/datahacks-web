# -*- coding: utf-8 -*-
"""
demo_api_calls.py — Demostración didáctica del llamado a las APIs externas.
Muestra las URLs de consulta, los parámetros y la estructura de datos que regresa cada API.
"""
import sys
import os
import io
import json

# Forzar codificación UTF-8 en consolas Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Asegurar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import GEMINI_API_KEY

def print_header(title):
    print("\n" + "="*70)
    print(f"📡 API: {title}")
    print("="*70)

def demo_fotmob_api():
    print_header("FOTMOB API (Vía HTTP Request)")
    team_id = 9815 # Colombia
    
    # 1. URL construida por el backend
    url_info = f"https://www.fotmob.com/api/teams?id={team_id}"
    print(f"👉 Método de Consulta: HTTP GET")
    print(f"👉 URL construida: {url_info}")
    
    # 2. Simulación de estructura de respuesta JSON de FotMob
    mock_response = {
        "id": team_id,
        "name": "Colombia",
        "ccode": "COL",
        "fixtures": {
            "allFixtures": {
                "fixtures": [
                    {
                        "id": 4351234,
                        "opponent": {"name": "Portugal", "id": 8206},
                        "status": {"finished": True, "started": True},
                        "home": {"name": "Colombia", "score": 2},
                        "away": {"name": "Portugal", "score": 1}
                    }
                ]
            }
        }
    }
    print("\n📦 Estructura del JSON de respuesta (Equipo & Calendario):")
    print(json.dumps(mock_response, indent=2))
    
    # 3. Detalle del mapa de tiros (Shotmap de un partido)
    match_id = 4351234
    url_shotmap = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
    print(f"\n👉 URL de Consulta para Mapa de Tiros: {url_shotmap}")
    
    mock_shotmap = [
        {
            "id": 10592312,
            "teamId": team_id,
            "playerName": "Luis Díaz",
            "eventType": "Goal",
            "x": 88.5,       # Coordenada en base 105 metros
            "y": 34.2,       # Coordenada en base 68 metros
            "expectedGoals": 0.38,  # xG del disparo
            "shotType": "RightFoot"
        }
    ]
    print("📦 Estructura del JSON del Shotmap:")
    print(json.dumps(mock_shotmap, indent=2))
    print("\n⚙️ Normalización del Backend: Multiplicamos 'x' por 1.2 y 'y' por 0.8 para ajustarlo al estándar de StatsBomb (120x80).")

def demo_sofascore_api():
    print_header("SOFASCORE API (Vía Headers Personalizados)")
    team_id = 4825 # Argentina
    
    # SofaScore requiere headers especiales (User-Agent) para saltarse protecciones Cloudflare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
    }
    url_events = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
    
    print(f"👉 Método de Consulta: HTTP GET")
    print(f"👉 URL construida: {url_events}")
    print(f"👉 Headers necesarios en Python:")
    print(json.dumps(headers, indent=2))
    
    mock_events = {
        "events": [
            {
                "id": 11843219,
                "customId": "abc123xyz",
                "status": {"code": 100, "description": "Ended", "type": "finished"},
                "homeTeam": {"name": "Argentina", "id": 4825},
                "awayTeam": {"name": "Francia", "id": 4481},
                "homeScore": {"current": 3},
                "awayScore": {"current": 3}
            }
        ]
    }
    print("\n📦 Estructura de Respuesta (Últimos Partidos):")
    print(json.dumps(mock_events, indent=2))

def demo_statsbomb_api():
    print_header("STATSBOMB OPEN DATA (Vía SDK Oficial)")
    comp_id = 43  # World Cup
    seas_id = 3   # 2018
    
    print("👉 Inicialización en Python:")
    print("   from statsbombpy import sb")
    print(f"👉 Llamados a la SDK:")
    print(f"   1. sb.matches(competition_id={comp_id}, season_id={seas_id})  -> Trae metadatos de los partidos.")
    print("   2. sb.events(match_id=7580)  -> Trae DataFrame completo con más de 3,000 eventos (Pases, Presiones, Faltas).")
    
    # Columnas típicas que devuelve StatsBomb en Pandas DataFrame
    columnas_sb = ["match_id", "timestamp", "team", "player", "type", "location", "pass_end_location", "shot_statsbomb_xg", "outcome"]
    print("\n📦 Columnas principales que extrae y normaliza el backend:")
    for col in columnas_sb:
        print(f"   - {col}")

def demo_gemini_api():
    print_header("GEMINI AI API (SDK Oficial google-genai)")
    
    print("👉 Librería requerida: google-genai")
    print("👉 Inicialización del cliente en backend:")
    print("   from google import genai")
    print(f"   client = genai.Client(api_key='{GEMINI_API_KEY[:8] + '...' if GEMINI_API_KEY else 'NO_KEY_CONFIGURED'}')")
    
    # 1. Prompt estructurado con datos tácticos
    prompt = """
    [Contexto Táctico]
    Equipo: Colombia
    xG Promedio: 1.85 | Goles Reales: 2 | PPDA: 7.8 (Presión alta)
    
    [Instrucción]
    Escribe un tuit analizando la efectividad de esta presión.
    """
    
    # 2. Llamada a la API
    print("\n👉 Llamado a la API (Endpoint de Chat/Generación):")
    print("   response = client.models.generate_content(")
    print("       model='gemini-2.0-flash',")
    print("       contents=prompt")
    print("   )")
    
    # 3. Respuesta esperada
    mock_gemini_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Con un PPDA de 7.8, la presión alta de Colombia es élite 🇨🇴. Recuperaciones rápidas para alimentar el xG. #TácticaMundial"}
                    ]
                }
            }
        ]
    }
    print("\n📦 Estructura del Payload de Respuesta de Gemini:")
    print(json.dumps(mock_gemini_resp, indent=2))
    print("\n⚙️ Extracción del backend: texto = response.text")
    print("="*70 + "\n")

if __name__ == "__main__":
    demo_fotmob_api()
    demo_sofascore_api()
    demo_statsbomb_api()
    demo_gemini_api()
