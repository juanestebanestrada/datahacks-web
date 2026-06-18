# -*- coding: utf-8 -*-
"""
pages/19_📊_Analisis_Postmundial.py
Dashboard de consulta táctica para análisis post-partido y visualización de gráficos.
"""
import streamlit as st
import os
import json
from config import DATA_DIR, BASE_DIR
from utils.style_loader import load_css
from utils.build_match_pages import parse_markdown_file

st.set_page_config(page_title="Análisis Postmundial · Mundial 2026", page_icon="📊", layout="wide")
load_css()

# Directorios de origen
ANALISIS_DATA_DIR = os.path.join(DATA_DIR, 'analisis_partidos')
WEBSITE_ASSETS_DIR = os.path.join(BASE_DIR, 'website', 'assets')

# Cargar banderas desde la definición de grupos
@st.cache_data
def get_team_flags():
    flags = {}
    grupos_json = os.path.join(DATA_DIR, 'grupos.json')
    try:
        if os.path.exists(grupos_json):
            with open(grupos_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for group, teams in data.items():
                    for team, info in teams.items():
                        flags[team.lower()] = info.get('bandera', '')
    except Exception:
        pass
    # Fallbacks de seguridad
    flags.setdefault('usa', '🇺🇸')
    flags.setdefault('paraguay', '🇵🇾')
    return flags

team_flags = get_team_flags()

# Obtener todos los análisis md de la carpeta de datos
def get_all_analyses():
    files = []
    if os.path.exists(ANALISIS_DATA_DIR):
        for f in os.listdir(ANALISIS_DATA_DIR):
            if f.endswith('.md'):
                files.append(f)
    return sorted(files, reverse=True)

existing_files = get_all_analyses()

# Hero Principal
st.markdown("""
<div class="hero" style="padding:30px; background:linear-gradient(135deg,#0d1e35,#15305b); border-left: 5px solid #3b82f6;">
    <div class="hero-tag">📊 SECCIÓN TÁCTICA EXPERTA</div>
    <h1 class="hero-title" style="font-size:2.3rem;">Análisis Postmundial</h1>
    <p class="hero-sub">Estudio táctico profundo y visualización de eventos de la Copa del Mundo 2026</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Buscar índice predeterminado para USA vs Paraguay
default_idx = 0
for idx, f in enumerate(existing_files):
    if "usa_paraguay" in f.lower():
        default_idx = idx
        break

# Selector de Partido
if existing_files:
    selected_file = st.selectbox(
        "🔎 Selecciona el partido que deseas analizar:",
        existing_files,
        index=default_idx,
        format_func=lambda x: x.replace('.md', '').replace('_', ' ').title()
    )
else:
    st.info("No se han encontrado análisis de partidos en `data/analisis_partidos`.")
    selected_file = None

if selected_file:
    # Parsear el archivo markdown
    file_path = os.path.join(ANALISIS_DATA_DIR, selected_file)
    meta, body = parse_markdown_file(file_path)
    
    # Extraer metadatos
    home = meta.get('home_team', 'Local')
    away = meta.get('away_team', 'Visitante')
    goles_h = meta.get('goles_home', '0')
    goles_a = meta.get('goles_away', '0')
    grupo = meta.get('grupo', 'Grupo')
    fecha = meta.get('fecha', '')
    hora = meta.get('hora', '')
    pronostico = meta.get('pronostico', '-')
    titulo = meta.get('titulo', f"{home} vs {away}")
    
    flag_home = team_flags.get(home.lower(), '🏳️')
    flag_away = team_flags.get(away.lower(), '🏳️')
    
    # Cabecera interactiva con marcador real y banderas
    st.markdown(f"""
    <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 16px; padding: 25px; text-align: center; margin-bottom: 25px;">
        <div style="font-size: 0.85rem; color: #888888; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">
            {grupo} · Copa del Mundo 2026
        </div>
        <div style="display: flex; justify-content: center; align-items: center; gap: 30px; margin-bottom: 15px;">
            <div style="text-align: right; min-width: 150px;">
                <span style="font-size: 3rem; display: block;">{flag_home}</span>
                <span style="font-size: 1.4rem; font-weight: 700; color: white;">{home}</span>
            </div>
            <div style="background-color: rgba(255,255,255,0.07); padding: 10px 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 2.2rem; font-weight: 900; color: #FFD700; font-family: monospace;">{goles_h} - {goles_a}</span>
            </div>
            <div style="text-align: left; min-width: 150px;">
                <span style="font-size: 3rem; display: block;">{flag_away}</span>
                <span style="font-size: 1.4rem; font-weight: 700; color: white;">{away}</span>
            </div>
        </div>
        <div style="font-size: 0.9rem; color: #aaaaaa;">
            📅 Fecha: <b>{fecha}</b> a las <b>{hora}</b> | 🔮 Pronóstico previo: <b>{pronostico}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Procesar imágenes asociadas de la crónica
    imagenes_str = meta.get('imagenes', '')
    home_images = []
    away_images = []
    general_images = []
    
    if imagenes_str:
        # Separar por comas
        parts = [p.strip() for p in imagenes_str.split(',') if p.strip()]
        for part in parts:
            if ':' in part:
                img_file, img_title = part.split(':', 1)
            else:
                img_file, img_title = part, part.replace('_', ' ').replace('.png', '')
            
            img_file = img_file.strip()
            img_title = img_title.strip()
            
            # Buscar en website/assets
            full_img_path = os.path.join(WEBSITE_ASSETS_DIR, img_file)
            if os.path.exists(full_img_path):
                img_data = (full_img_path, img_title)
                
                # Clasificar según el nombre del archivo
                # Se compara normalizando a minúsculas
                if home.lower() in img_file.lower():
                    home_images.append(img_data)
                elif away.lower() in img_file.lower():
                    away_images.append(img_data)
                else:
                    general_images.append(img_data)
            else:
                # Probar en la raíz del proyecto por si acaso
                local_path = os.path.join(BASE_DIR, img_file)
                if os.path.exists(local_path):
                    img_data = (local_path, img_title)
                    if home.lower() in img_file.lower():
                        home_images.append(img_data)
                    elif away.lower() in img_file.lower():
                        away_images.append(img_data)
                    else:
                        general_images.append(img_data)
    
    # Pestañas principales
    tab_cronica, tab_home_charts, tab_away_charts, tab_general_charts = st.tabs([
        "📝 Crónica y Análisis",
        f"{flag_home} Táctica {home}",
        f"{flag_away} Táctica {away}",
        "📊 Gráficos Generales"
    ])
    
    with tab_cronica:
        st.subheader("Crónica Táctica del Partido")
        st.markdown(body)
        
    with tab_home_charts:
        st.subheader(f"Visualizaciones Tácticas: {home}")
        if home_images:
            for path, title in home_images:
                st.markdown(f"<div style='margin-top:20px; font-weight:bold; color:#FFD700;'>⚽ {title}</div>", unsafe_allow_html=True)
                st.image(path, use_container_width=True)
        else:
            st.warning(f"No se encontraron gráficos tácticos específicos para {home}.")
            
    with tab_away_charts:
        st.subheader(f"Visualizaciones Tácticas: {away}")
        if away_images:
            for path, title in away_images:
                st.markdown(f"<div style='margin-top:20px; font-weight:bold; color:#FFD700;'>⚽ {title}</div>", unsafe_allow_html=True)
                st.image(path, use_container_width=True)
        else:
            st.warning(f"No se encontraron gráficos tácticos específicos para {away}.")
            
    with tab_general_charts:
        st.subheader("Gráficos Comparativos y Generales")
        if general_images:
            for path, title in general_images:
                st.markdown(f"<div style='margin-top:20px; font-weight:bold; color:#FFD700;'>⚽ {title}</div>", unsafe_allow_html=True)
                st.image(path, use_container_width=True)
        else:
            st.info("No hay gráficos generales adicionales cargados para este partido.")
