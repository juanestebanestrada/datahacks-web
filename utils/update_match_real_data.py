# -*- coding: utf-8 -*-
"""
utils/update_match_real_data.py
Actualiza las crónicas y gráficos de tiros (Shot Maps) con datos reales del Mundial 2026
obtenidos directamente de la API de FotMob.
"""
import os
import sys
import io
import re
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Forzar codificación UTF-8 en consolas Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar directorio raíz para importaciones de utils
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.visualization import generar_mapa

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Configuración de partidos y sus IDs reales en FotMob
MATCHES_CONFIG = [
    {
        "match_id": 4667751,
        "slug": "mexico_sudafrica",
        "md_filename": "20260611_mexico_sudafrica.md",
        "home_name": "México",
        "away_name": "Sudáfrica",
        "home_flag": "🇲🇽",
        "away_flag": "🇿🇦",
        "home_img": "ShotMapMéxico.png",
        "away_img": "ShotMapSudáfrica.png"
    },
    {
        "match_id": 4667752,
        "slug": "repcheca_coreasur",
        "md_filename": "20260611_repcheca_coreasur.md",
        "home_name": "Rep. Checa",
        "away_name": "Corea del Sur",
        "home_flag": "🇨🇿",
        "away_flag": "🇰🇷",
        "home_img": "ShotMapRep.Checa.png",
        "away_img": "ShotMapCoreaDelSur.png"
    },
    {
        "match_id": 4667758,
        "slug": "qatar_suiza",
        "md_filename": "20260613_qatar_suiza.md",
        "home_name": "Qatar",
        "away_name": "Suiza",
        "home_flag": "🇶🇦",
        "away_flag": "🇨🇭",
        "home_img": "ShotMap_Qatar_horizontal_20260613.png",
        "away_img": "ShotMap_Suiza_horizontal_20260613.png"
    },
    {
        "match_id": 4667764,
        "slug": "brasil_marruecos",
        "md_filename": "20260613_brasil_marruecos.md",
        "home_name": "Brasil",
        "away_name": "Marruecos",
        "home_flag": "🇧🇷",
        "away_flag": "🇲🇦",
        "home_img": "ShotMap_Brasil_horizontal_20260613.png",
        "away_img": "ShotMap_Marruecos_horizontal_20260613.png"
    },
    {
        "match_id": 4667765,
        "slug": "haiti_escocia",
        "md_filename": "20260613_haiti_escocia.md",
        "home_name": "Haití",
        "away_name": "Escocia",
        "home_flag": "🇭🇹",
        "away_flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "home_img": "ShotMap_Haití_horizontal_20260613.png",
        "away_img": "ShotMap_Escocia_horizontal_20260613.png"
    },
    {
        "match_id": 4667772,
        "slug": "australia_turquia",
        "md_filename": "20260613_australia_turquia.md",
        "home_name": "Australia",
        "away_name": "Turquía",
        "home_flag": "🇦🇺",
        "away_flag": "🇹🇷",
        "home_img": "ShotMap_Australia_horizontal_20260613.png",
        "away_img": "ShotMap_Turquía_horizontal_20260613.png"
    }
]

def fetch_match_details(match_id):
    url = f"https://www.fotmob.com/api/data/matchDetails?matchId={match_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def run_update():
    print("Iniciando actualización de datos reales del Mundial 2026...")
    
    for match in MATCHES_CONFIG:
        match_id = match["match_id"]
        slug = match["slug"]
        print(f"\n⚽ Procesando partido: {match['home_name']} vs {match['away_name']} (ID: {match_id})...")
        
        try:
            # 1. Obtener detalles del partido
            data = fetch_match_details(match_id)
            
            general = data.get("general", {})
            header = data.get("header", {})
            
            home_id = general.get("homeTeam", {}).get("id")
            away_id = general.get("awayTeam", {}).get("id")
            
            home_score = None
            away_score = None
            for t in header.get("teams", []):
                t_id = t.get("id")
                if t_id == home_id:
                    home_score = t.get("score")
                elif t_id == away_id:
                    away_score = t.get("score")
                    
            if home_score is None or away_score is None:
                print(f"⚠️ No se pudieron determinar los goles para {slug}. Saltando.")
                continue
                
            # 2. Obtener goles reales y estado
            finished = header.get("status", {}).get("finished", False)
            if home_score is not None and away_score is not None:
                finished = True
            finished_str = "true" if finished else "false"
            
            print(f"   Resultado Real: {home_score} - {away_score} | Finalizado: {finished}")
            
            # 3. Procesar y generar Shot Maps
            content = data.get("content", {})
            shotmap_data = content.get("shotmap", {})
            shots = shotmap_data.get("shots", [])
            
            print(f"   Se encontraron {len(shots)} disparos en el shotmap.")
            
            # Dividir tiros
            home_shots = [s for s in shots if s.get("teamId") == home_id]
            away_shots = [s for s in shots if s.get("teamId") == away_id]
            
            # Generar mapa local
            if home_shots:
                df_home = pd.DataFrame(home_shots)
                df_home['shot_outcome'] = df_home['eventType'].apply(lambda x: 'Goal' if 'Goal' in str(x) else x)
                df_home['x'] = df_home['x'] * 1.2
                df_home['y'] = df_home['y'] * 0.8
                df_home['shot_statsbomb_xg'] = pd.to_numeric(df_home['expectedGoals'], errors='coerce').fillna(0.05)
                
                fig = generar_mapa(df_home, match["home_name"], "Mundial 2026", match["home_flag"], "horizontal")
                out_path = os.path.join(BASE_DIR, "website", "assets", match["home_img"])
                fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
                plt.close(fig)
                print(f"   ✅ Guardado Shot Map local en: website/assets/{match['home_img']}")
            else:
                print("   ⚠️ No hay disparos registrados para el equipo local.")
                
            # Generar mapa visitante
            if away_shots:
                df_away = pd.DataFrame(away_shots)
                df_away['shot_outcome'] = df_away['eventType'].apply(lambda x: 'Goal' if 'Goal' in str(x) else x)
                df_away['x'] = df_away['x'] * 1.2
                df_away['y'] = df_away['y'] * 0.8
                df_away['shot_statsbomb_xg'] = pd.to_numeric(df_away['expectedGoals'], errors='coerce').fillna(0.05)
                
                fig = generar_mapa(df_away, match["away_name"], "Mundial 2026", match["away_flag"], "horizontal")
                out_path = os.path.join(BASE_DIR, "website", "assets", match["away_img"])
                fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
                plt.close(fig)
                print(f"   ✅ Guardado Shot Map visitante en: website/assets/{match['away_img']}")
            else:
                print("   ⚠️ No hay disparos registrados para el equipo visitante.")
                
            # 4. Actualizar archivo markdown
            md_path = os.path.join(BASE_DIR, "data", "analisis_partidos", match["md_filename"])
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    content_md = f.read()
                    
                content_md = re.sub(r'goles_home:\s*\d+', f'goles_home: {home_score}', content_md)
                content_md = re.sub(r'goles_away:\s*\d+', f'goles_away: {away_score}', content_md)
                content_md = re.sub(r'finalizado:\s*"\w+"', f'finalizado: "{finished_str}"', content_md)
                
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content_md)
                print(f"   ✅ Actualizado archivo Markdown: data/analisis_partidos/{match['md_filename']}")
            else:
                print(f"   ❌ No se encontró el archivo Markdown en {md_path}")
                
        except Exception as e:
            print(f"   ❌ Error al procesar {slug}: {e}")
            
    # 5. Compilar páginas web
    print("\n🔨 Iniciando compilación de crónicas y páginas estáticas...")
    try:
        import subprocess
        build_script = os.path.join(BASE_DIR, 'utils', 'build_match_pages.py')
        subprocess.run([sys.executable, build_script], check=True)
        print("🎉 Proceso finalizado exitosamente!")
    except Exception as e:
        print(f"❌ Error al ejecutar el compilador: {e}")

if __name__ == "__main__":
    run_update()
