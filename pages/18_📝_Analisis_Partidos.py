"""
pages/18_📝_Analisis_Partidos.py
Dashboard interactivo para crear, editar, visualizar y compilar las crónicas tácticas de los partidos.
"""

import streamlit as st
import os
import json
from datetime import datetime
from utils.style_loader import load_css
from utils.build_match_pages import build_all_pages, parse_markdown_file
from config import GRUPOS_JSON_PATH, DATA_DIR

st.set_page_config(page_title="Editor de Crónicas · Mundial 2026", page_icon="📝", layout="wide")
load_css()

# Asegurar directorios
ANALISIS_DATA_DIR = os.path.join(DATA_DIR, 'analisis_partidos')
os.makedirs(ANALISIS_DATA_DIR, exist_ok=True)

# Cargar grupos y selecciones para autocompletar dinámicamente
@st.cache_data
def load_tournament_structure():
    try:
        with open(GRUPOS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

tournament_data = load_tournament_structure()

# Hero Principal
st.markdown("""<div class="hero" style="padding:30px; background:linear-gradient(135deg,#1f1f1e,#112233);">
    <h1 class="hero-title" style="font-size:2.3rem;">📝 Panel de Crónicas y Análisis</h1>
    <p class="hero-sub">Escribe y gestiona los análisis tácticos de cada partido del Mundial 2026</p>
</div>""", unsafe_allow_html=True)

col_list, col_editor = st.columns([1, 2])

# Obtener archivos existentes
def get_existing_analyses():
    files = []
    if os.path.exists(ANALISIS_DATA_DIR):
        for f in os.listdir(ANALISIS_DATA_DIR):
            if f.endswith('.md'):
                files.append(f)
    return sorted(files, reverse=True)

with col_list:
    st.subheader("📁 Análisis Guardados")
    existing_files = get_existing_analyses()
    
    selected_file = None
    if existing_files:
        selected_file = st.selectbox("Selecciona un partido para editar o leer:", ["-- Crear Nuevo --"] + existing_files)
    else:
        st.info("No hay análisis creados aún. Comienza creando uno nuevo.")
        selected_file = "-- Crear Nuevo --"

    # Cargar datos si se selecciona un archivo existente
    init_data = {
        "slug": "",
        "titulo": "",
        "grupo": "Grupo A",
        "fecha": datetime.today(),
        "hora": "14:00",
        "home_team": "",
        "away_team": "",
        "goles_home": 0,
        "goles_away": 0,
        "pronostico": "0 - 0",
        "finalizado": False,
        "imagenes": "",
        "body": ""
    }
    
    is_edit_mode = selected_file != "-- Crear Nuevo --"
    
    if is_edit_mode:
        meta, body = parse_markdown_file(os.path.join(ANALISIS_DATA_DIR, selected_file))
        init_data["slug"] = meta.get('slug', selected_file.replace('.md', ''))
        init_data["titulo"] = meta.get('titulo', '')
        init_data["grupo"] = meta.get('grupo', 'Grupo A')
        try:
            init_data["fecha"] = datetime.strptime(meta.get('fecha', ''), '%Y-%m-%d')
        except ValueError:
            init_data["fecha"] = datetime.today()
        init_data["hora"] = meta.get('hora', '14:00')
        init_data["home_team"] = meta.get('home_team', '')
        init_data["away_team"] = meta.get('away_team', '')
        init_data["goles_home"] = int(meta.get('goles_home', 0))
        init_data["goles_away"] = int(meta.get('goles_away', 0))
        init_data["pronostico"] = meta.get('pronostico', '0 - 0')
        init_data["finalizado"] = meta.get('finalizado', 'false').lower() == 'true'
        init_data["imagenes"] = meta.get('imagenes', '')
        init_data["body"] = body

    # Sección de acciones rápidas
    st.markdown("---")
    st.subheader("⚙️ Compilador Web")
    st.write("Genera las páginas HTML individuales y actualiza el match center dinámico en la web pública.")
    if st.button("⚡ Compilar Sitio Web", type="primary", use_container_width=True):
        with st.spinner("Compilando sitio web..."):
            success = build_all_pages()
            if success:
                st.success("🎉 ¡Sitio compilado y actualizado exitosamente!")
                st.balloons()
            else:
                st.error("Ocurrió un error en la compilación.")

with col_editor:
    st.subheader("✍️ Editor de Análisis" if not is_edit_mode else f"✏️ Editando: {init_data['titulo']}")
    
    with st.form("editor_form"):
        # Fila 1: Metadatos del archivo
        col_f1_1, col_f1_2 = st.columns(2)
        with col_f1_1:
            slug = st.text_input("Identificador Único (Slug / Nombre Archivo):", 
                                  value=init_data["slug"], 
                                  placeholder="ej: 20260611_mexico_sudafrica",
                                  disabled=is_edit_mode)
        with col_f1_2:
            titulo = st.text_input("Título del Análisis:", value=init_data["titulo"], placeholder="ej: México vs Sudáfrica: Pulso Táctico")
            
        # Fila 2: Grupo y Fecha
        col_f2_1, col_f2_2, col_f2_3 = st.columns(3)
        with col_f2_1:
            grupo_opciones = list(tournament_data.keys()) if tournament_data else ["Grupo A"]
            default_g_idx = grupo_opciones.index(init_data["grupo"]) if init_data["grupo"] in grupo_opciones else 0
            grupo = st.selectbox("Grupo del Torneo:", grupo_opciones, index=default_g_idx)
        with col_f2_2:
            fecha = st.date_input("Fecha del Partido:", value=init_data["fecha"])
        with col_f2_3:
            hora = st.text_input("Hora del Partido (HH:MM Local):", value=init_data["hora"])
            
        # Fila 3: Equipos dinámicos basados en el grupo seleccionado
        col_f3_1, col_f3_2 = st.columns(2)
        
        # Obtener equipos del grupo seleccionado
        teams_in_group = []
        if tournament_data and grupo in tournament_data:
            teams_in_group = list(tournament_data[grupo].keys())
        else:
            teams_in_group = ["México", "Sudáfrica", "Corea del Sur", "Rep. Checa"]
            
        with col_f3_1:
            default_h_idx = teams_in_group.index(init_data["home_team"]) if init_data["home_team"] in teams_in_group else 0
            home_team = st.selectbox("Equipo Local (Home):", teams_in_group, index=default_h_idx)
        with col_f3_2:
            default_a_idx = teams_in_group.index(init_data["away_team"]) if init_data["away_team"] in teams_in_group else min(1, len(teams_in_group)-1)
            away_team = st.selectbox("Equipo Visitante (Away):", teams_in_group, index=default_a_idx)
            
        # Fila 4: Marcador Real del Partido
        col_f4_1, col_f4_2, col_f4_3 = st.columns(3)
        with col_f4_1:
            goles_home = st.number_input(f"Marcador Real {home_team}:", min_value=0, max_value=20, value=init_data["goles_home"])
        with col_f4_2:
            goles_away = st.number_input(f"Marcador Real {away_team}:", min_value=0, max_value=20, value=init_data["goles_away"])
        with col_f4_3:
            st.write("")
            st.write("")
            finalizado = st.checkbox("¿Partido Finalizado?", value=init_data["finalizado"])

        # Fila 5: Pronóstico e Imágenes Asociadas
        col_f5_1, col_f5_2 = st.columns(2)
        with col_f5_1:
            pronostico = st.text_input("Marcador Proyectado / Pronóstico (ej: 1 - 0):", value=init_data["pronostico"])
        with col_f5_2:
            imagenes = st.text_input("Gráficos Tácticos (ej: archivo1.png:Título 1, archivo2.png:Título 2):", value=init_data["imagenes"])

        # Fila 6: Cuerpo del Análisis (Markdown)
        body = st.text_area("Análisis Táctico (Formato Markdown):", value=init_data["body"], height=350, placeholder="Escribe aquí los apuntes tácticos, alineaciones y proyecciones...")
        
        submit_btn = st.form_submit_button("💾 Guardar Análisis", use_container_width=True)
        
        if submit_btn:
            if not slug or not titulo:
                st.error("El Identificador Único y el Título son obligatorios.")
            else:
                clean_slug = "".join([c if c.isalnum() or c in ['_', '-'] else '' for c in slug]).lower()
                file_name = f"{clean_slug}.md"
                file_path = os.path.join(ANALISIS_DATA_DIR, file_name)
                
                file_content = f"""---
id: {clean_slug}
titulo: "{titulo}"
grupo: "{grupo}"
fecha: "{fecha.strftime('%Y-%m-%d')}"
hora: "{hora}"
home_team: "{home_team}"
away_team: "{away_team}"
goles_home: {goles_home}
goles_away: {goles_away}
pronostico: "{pronostico}"
finalizado: "{'true' if finalizado else 'false'}"
imagenes: "{imagenes}"
slug: "{clean_slug}"
---
{body}"""
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    st.success(f"✅ Análisis guardado correctamente en: `data/analisis_partidos/{file_name}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al escribir archivo: {e}")
                    
    # Vista previa del renderizado
    if body:
        with st.expander("👁️ Vista Previa del Análisis Renderizado"):
            st.markdown(f"# {titulo}")
            st.markdown(f"**Grupo:** {grupo} | **Fecha:** {fecha.strftime('%d/%m/%Y')} a las {hora}")
            st.markdown(f"**Resultado Real:** {home_team} **{goles_home} - {goles_away}** {away_team} | **Pronóstico:** {pronostico} | **Finalizado:** {'Sí' if finalizado else 'No'}")
            st.markdown("---")
            st.markdown(body)
