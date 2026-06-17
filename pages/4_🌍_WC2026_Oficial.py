"""pages/4_🌍_WC2026_Oficial.py"""
import streamlit as st
import requests
import pandas as pd
import os
import json
from config import API_FOOTBALL_DATA_TOKEN, COMMON_HEADERS, GRUPOS_JSON_PATH, DATA_DIR, BASE_DIR
from utils.style_loader import load_css

st.set_page_config(page_title="WC 2026 Oficial · Mundial 2026", page_icon="🌍", layout="wide")
load_css()

st.markdown("""<div class="hero" style="padding:30px;background:linear-gradient(135deg,#1b0033,#3d0075);">
    <h1 class="hero-title" style="font-size:2.5rem;">🌍 Mundial 2026 Oficial</h1>
    <p class="hero-sub">Clasificaciones del Torneo y Resultados del Match Center</p>
</div>""", unsafe_allow_html=True)

# Selector de origen de datos
source_type = st.radio(
    "Selecciona el origen de los datos de clasificación:",
    ["Simulación Local (Resultados del Match Center)", "Datos Oficiales (Football-Data.org API)"],
    horizontal=True
)

if source_type == "Datos Oficiales (Football-Data.org API)":
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_wc_standings():
        url = "http://api.football-data.org/v4/competitions/2000/standings"
        headers = {**COMMON_HEADERS, "X-Auth-Token": API_FOOTBALL_DATA_TOKEN}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json(), None
            return None, f"Error HTTP {res.status_code}"
        except Exception as e:
            return None, str(e)

    with st.spinner("Conectando con Football-Data.org..."):
        data, err = get_wc_standings()

    if err:
        st.error(f"⚠️ {err}")
    elif data and 'standings' in data:
        st.success("✅ Conectado a Football-Data.org")
        for group_data in data['standings']:
            if group_data.get('type') == 'TOTAL':
                g = group_data.get('group', '').replace('_', ' ')
                st.markdown(f"#### 🏆 {g}")
                filas = []
                for row in group_data.get('table', []):
                    t = row['team']
                    filas.append({"Pos":row['position'],"Equipo":t['name'],"PJ":row['playedGames'],
                                  "G":row['won'],"E":row['draw'],"P":row['lost'],
                                  "GF":row['goalsFor'],"GC":row['goalsAgainst'],
                                  "DG":row['goalDifference'],"Pts":row['points']})
                if filas:
                    st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)

else:
    # Simulación Local (Resultados del Match Center)
    st.info("📊 Calculando posiciones basadas en las crónicas y resultados de partidos guardados en el Match Center local.")
    
    # 1. Cargar la definición de grupos
    try:
        with open(GRUPOS_JSON_PATH, "r", encoding="utf-8") as f:
            grupos_dict = json.load(f)
    except Exception as e:
        st.error(f"Error al cargar grupos.json: {e}")
        grupos_dict = {}

    if grupos_dict:
        # 2. Inicializar standings para cada equipo en cada grupo
        standings = {}
        for grupo, teams in grupos_dict.items():
            standings[grupo] = {}
            for team_name, team_info in teams.items():
                bandera = team_info.get("bandera", "")
                standings[grupo][team_name] = {
                    "Equipo": f"{bandera} {team_name}",
                    "PJ": 0,
                    "G": 0,
                    "E": 0,
                    "P": 0,
                    "GF": 0,
                    "GC": 0,
                    "DG": 0,
                    "Pts": 0
                }

        # 3. Leer y procesar partidos
        analisis_partidos_dir = os.path.join(DATA_DIR, "analisis_partidos")
        if os.path.exists(analisis_partidos_dir):
            for filename in os.listdir(analisis_partidos_dir):
                if filename.endswith(".md"):
                    file_path = os.path.join(analisis_partidos_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Parse simple frontmatter
                        metadata = {}
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                for line in frontmatter.strip().split('\n'):
                                    if ':' in line:
                                        k, v = line.split(':', 1)
                                        metadata[k.strip()] = v.strip().strip('"').strip("'")
                        
                        # Si está finalizado, acumular estadísticas
                        finalizado = metadata.get("finalizado", "false").lower() == "true"
                        if finalizado:
                            g = metadata.get("grupo")
                            home = metadata.get("home_team")
                            away = metadata.get("away_team")
                            
                            # Buscar en standings
                            if g in standings and home in standings[g] and away in standings[g]:
                                gh = int(metadata.get("goles_home", 0))
                                ga = int(metadata.get("goles_away", 0))
                                
                                h_stats = standings[g][home]
                                a_stats = standings[g][away]
                                
                                h_stats["PJ"] += 1
                                a_stats["PJ"] += 1
                                h_stats["GF"] += gh
                                h_stats["GC"] += ga
                                a_stats["GF"] += ga
                                a_stats["GC"] += gh
                                h_stats["DG"] = h_stats["GF"] - h_stats["GC"]
                                a_stats["DG"] = a_stats["GF"] - a_stats["GC"]
                                
                                if gh > ga:
                                    h_stats["G"] += 1
                                    h_stats["Pts"] += 3
                                    a_stats["P"] += 1
                                elif ga > gh:
                                    a_stats["G"] += 1
                                    a_stats["Pts"] += 3
                                    h_stats["P"] += 1
                                else:
                                    h_stats["E"] += 1
                                    h_stats["Pts"] += 1
                                    a_stats["E"] += 1
                                    a_stats["Pts"] += 1
                    except Exception as e:
                        pass

        # 4. Renderizar las tablas ordenadas para cada grupo
        for grupo, table_data in standings.items():
            st.markdown(f"#### 🏆 {grupo}")
            
            # Convertir a DataFrame y ordenar
            df_group = pd.DataFrame(list(table_data.values()))
            # Criterios de desempate de la FIFA: Puntos -> Diferencia Goles -> Goles a Favor
            df_group = df_group.sort_values(by=["Pts", "DG", "GF", "Equipo"], ascending=[False, False, False, True]).reset_index(drop=True)
            df_group.index += 1
            df_group.insert(0, "Pos", df_group.index)
            
            st.dataframe(df_group, hide_index=True, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # --- Sección de Crónicas y Análisis Táctico ---
        st.markdown("---")
        st.subheader("📝 Crónicas de Partidos y Análisis Post-Partido (Match Center)")
        
        cronicas_list = []
        if os.path.exists(analisis_partidos_dir):
            for filename in os.listdir(analisis_partidos_dir):
                if filename.endswith(".md"):
                    file_path = os.path.join(analisis_partidos_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        metadata = {}
                        body = content
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                body = parts[2]
                                for line in frontmatter.strip().split('\n'):
                                    if ':' in line:
                                        k, v = line.split(':', 1)
                                        metadata[k.strip()] = v.strip().strip('"').strip("'")
                        
                        finalizado = metadata.get("finalizado", "false").lower() == "true"
                        home = metadata.get("home_team", "Local")
                        away = metadata.get("away_team", "Visitante")
                        fecha_str = metadata.get("fecha", "")
                        goles_h = metadata.get("goles_home", "0")
                        goles_a = metadata.get("goles_away", "0")
                        pronostico_val = metadata.get("pronostico", "0 - 0")
                        
                        if finalizado:
                            desc = f"⚽ {home} {goles_h} - {goles_a} {away} ({fecha_str}) — FINALIZADO"
                        else:
                            desc = f"🔮 {home} vs {away} (Predicción: {pronostico_val}) ({fecha_str}) — PREVIO"
                        
                        cronicas_list.append({
                            "desc": desc,
                            "filename": filename,
                            "metadata": metadata,
                            "body": body,
                            "fecha": fecha_str,
                            "hora": metadata.get("hora", "")
                        })
                    except Exception as e:
                        pass
        
        if cronicas_list:
            # Ordenar por fecha y hora descendente
            cronicas_list = sorted(cronicas_list, key=lambda x: (x["fecha"], x["hora"]), reverse=True)
            
            opciones_desc = [c["desc"] for c in cronicas_list]
            selected_desc = st.selectbox("Selecciona un análisis de partido para visualizar en la app:", opciones_desc)
            
            # Obtener el partido seleccionado
            selected_match = next(c for c in cronicas_list if c["desc"] == selected_desc)
            meta = selected_match["metadata"]
            body_text = selected_match["body"]
            
            # Renderizado estético
            st.markdown(f"### {meta.get('titulo')}")
            
            # Fila de métricas del partido
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Grupo", meta.get("grupo", "N/A"))
            col_m2.metric("Fecha / Hora", f"{meta.get('fecha')} a las {meta.get('hora')}")
            if meta.get("finalizado", "false").lower() == "true":
                col_m3.metric("Resultado Real", f"{meta.get('home_team')} {meta.get('goles_home')} - {meta.get('goles_away')} {meta.get('away_team')}")
                col_m4.metric("Pronóstico Inicial", meta.get("pronostico"))
            else:
                col_m3.metric("Pronóstico IA", meta.get("pronostico"))
                col_m4.metric("Estado", "Por Jugar / Pre-Partido")
            
            # Cuerpo del análisis
            st.markdown("#### 📖 Crónica Táctica")
            st.markdown(body_text)
            
            # Pizarras y Gráficos Tácticos
            imagenes_raw = meta.get("imagenes", "")
            if imagenes_raw:
                st.markdown("#### 📊 Pizarras y Gráficos Tácticos")
                images_list = []
                img_items = imagenes_raw.split(',')
                for item in img_items:
                    if ':' in item:
                        filename, caption = item.split(':', 1)
                        images_list.append((filename.strip(), caption.strip()))
                    else:
                        images_list.append((item.strip(), ""))
                
                # Agrupar imágenes por tipo (similar a build_match_pages.py)
                def get_clean_key(fname):
                    name = fname.lower()
                    if 'defensivo' in name: return 'mapadefensivo'
                    if 'expectedthreatxt' in name or 'xt' in name: return 'xt'
                    if 'calor' in name: return 'calor'
                    if 'shotmap' in name or 'tiro' in name: return 'shotmap'
                    if 'reddepases' in name or 'pases' in name: return 'pases'
                    if 'conducciones' in name: return 'conducciones'
                    if 'asistencias' in name: return 'asistencias'
                    return name.strip()
                
                grouped_visuals = []
                used_indices = set()
                for i in range(len(images_list)):
                    if i in used_indices:
                        continue
                    filename_i, caption_i = images_list[i]
                    key_i = get_clean_key(filename_i)
                    
                    paired = False
                    for j in range(i + 1, len(images_list)):
                        if j in used_indices:
                            continue
                        filename_j, caption_j = images_list[j]
                        key_j = get_clean_key(filename_j)
                        
                        if key_i == key_j:
                            grouped_visuals.append(('pair', (filename_i, caption_i), (filename_j, caption_j)))
                            used_indices.add(i)
                            used_indices.add(j)
                            paired = True
                            break
                    
                    if not paired:
                        grouped_visuals.append(('single', (filename_i, caption_i)))
                        used_indices.add(i)
                
                assets_path = os.path.join(BASE_DIR, "website", "assets")
                
                for item in grouped_visuals:
                    if item[0] == 'pair':
                        img1, cap1 = item[1]
                        img2, cap2 = item[2]
                        img1_path = os.path.join(assets_path, img1.replace('.jpg', '.png'))
                        img2_path = os.path.join(assets_path, img2.replace('.jpg', '.png'))
                        
                        col_img1, col_img2 = st.columns(2)
                        with col_img1:
                            if os.path.exists(img1_path):
                                st.image(img1_path, caption=cap1, use_container_width=True)
                            else:
                                st.warning(f"No se encontró la imagen: {img1}")
                        with col_img2:
                            if os.path.exists(img2_path):
                                st.image(img2_path, caption=cap2, use_container_width=True)
                            else:
                                st.warning(f"No se encontró la imagen: {img2}")
                    else:
                        img, cap = item[1]
                        img_path = os.path.join(assets_path, img.replace('.jpg', '.png'))
                        if os.path.exists(img_path):
                            st.image(img_path, caption=cap, use_container_width=True)
                        else:
                            st.warning(f"No se encontró la imagen: {img}")
        else:
            st.info("No se encontraron crónicas de partidos guardadas.")
