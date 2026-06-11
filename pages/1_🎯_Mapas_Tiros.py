# -*- coding: utf-8 -*-
"""
pages/1_🎯_Mapas_Tiros.py — Módulo de Visualizaciones Tácticas
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json, os
from datetime import datetime

from utils.style_loader import load_css
from utils.data_loaders import (
    cargar_tiros, cargar_tiros_fotmob, cargar_tiros_sofascore,
    cargar_tiros_365scores, cargar_eventos, calcular_ppda,
    calcular_progressive_passes, calcular_estadisticas_generales,
    cargar_tiros_unified, cargar_eventos_unified, STATSBOMB_FALLBACK_CFG
)
from utils.visualization import (
    generar_mapa, generar_mapa_calor, generar_mapa_pases,
    generar_mapa_clusters, fig_to_png_bytes,
    generar_mapa_xt, generar_mapa_sonar, generar_mapa_defensivo,
    generar_mapa_carries, generar_mapa_asistencias
)

st.set_page_config(page_title="Mapas de Tiros · Mundial 2026", page_icon="🎯", layout="wide")
load_css()

# ── Cargar datos ──
_GRUPOS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'grupos.json')
with open(_GRUPOS_PATH, 'r', encoding='utf-8') as f:
    GRUPOS = json.load(f)

if 'grupo_seleccionado' not in st.session_state or st.session_state['grupo_seleccionado'] not in GRUPOS:
    st.session_state['grupo_seleccionado'] = 'Grupo K'

EQUIPOS = GRUPOS[st.session_state['grupo_seleccionado']]

# ── Selector de Grupos ──
with st.expander("🏆 SELECCIONAR GRUPO DEL MUNDIAL", expanded=st.session_state.get('expander_grupos', True)):
    cols_g = st.columns(4)
    for i, (nombre_g, teams_g) in enumerate(GRUPOS.items()):
        with cols_g[i % 4]:
            is_selected = (st.session_state['grupo_seleccionado'] == nombre_g)
            bg_color = "#3b82f6" if is_selected else "rgba(255,255,255,0.05)"
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 10px; border-radius: 12px;
                        border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <div style="font-size: 0.75rem; color: #fff;">{nombre_g}</div>
                <div style="font-size: 1.1rem; margin: 3px 0;">{"".join([v['bandera'] for v in teams_g.values()])}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Analizar", key=f"sel_{nombre_g}", use_container_width=True):
                st.session_state['grupo_seleccionado'] = nombre_g
                st.session_state['expander_grupos'] = False
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
    <div class="hero-tag">FIFA World Cup 2026</div>
    <h1 class="hero-title">{st.session_state['grupo_seleccionado']}</h1>
    <p class="hero-sub">Análisis Avanzado · Mapa de Tiros · ADN Táctico</p>
</div>
""", unsafe_allow_html=True)

tabs_nombres = [f"{v['bandera']} {k}" for k, v in EQUIPOS.items()]
tabs = st.tabs(tabs_nombres)

for tab, (pais, cfg) in zip(tabs, EQUIPOS.items()):
    with tab:
        col_info, col_stats = st.columns([1.3, 2.7], gap="large")

        with col_info:
            fuente_label = {
                'fotmob': 'FotMob API', 'sofascore': 'SofaScore API',
                '365scores': '365Scores API', 'statsbomb': 'StatsBomb Open Data'
            }.get(cfg.get('fuente', ''), 'API Desconocida')

            st.markdown(f"""
            <div style="background: linear-gradient(160deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02));
                        border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:30px 20px; text-align:center;">
                <span style="font-size:4.5rem; display:block; margin-bottom:12px;">{cfg['bandera']}</span>
                <div style="font-size:1.6rem; font-weight:900; color:#fff; margin-bottom:6px;">{pais}</div>
                <div style="font-size:0.85rem; color:rgba(255,255,255,0.45); margin-bottom:14px;">
                    {st.session_state['grupo_seleccionado']} · Mundial 2026</div>
                <div style="background:rgba(46,213,115,0.12); color:#2ed573; border:1px solid rgba(46,213,115,0.3);
                            display:inline-block; padding:5px 16px; border-radius:20px; font-size:0.75rem; font-weight:700;">
                    ● Datos disponibles</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
                        border-radius:14px; padding:16px 18px; margin-top:12px;">
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.35); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px;">Fuente de Datos</div>
                <div style="font-size:0.95rem; color:rgba(255,255,255,0.75); font-weight:600;">{cfg.get('torneo', 'Mundial 2026')}</div>
                <div style="font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:4px;">{fuente_label}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_stats:
            tipo_grafico = st.selectbox(
                "Tipo de Visualización:",
                [
                    "🎯 Mapa de Tiros",
                    "🔥 Mapa de Calor",
                    "🕸️ Red de Pases",
                    "🧬 ADN Pases (K-Means)",
                    "⚡ Expected Threat (xT)",
                    "🧭 Sonar de Pases",
                    "🛡️ Mapa Defensivo",
                    "🏃‍♂️ Conducciones Progresivas",
                    "🎁 Mapa de Asistencias"
                ],
                key=f"sel_grafico_{pais}"
            )
            
            # Selector de formato para exportación en redes sociales
            col_sel_fmt, col_spacer = st.columns([2.2, 1.8])
            with col_sel_fmt:
                formato_sel = st.selectbox(
                    "Formato de Exportación (Social Media):",
                    ["Horizontal (Estándar Web)", "Vertical (9:16 TikTok/Reels)", "Cuadrado (1:1 X/Instagram)"],
                    index=0,
                    key=f"fmt_{pais}_{tipo_grafico}",
                    help="Ajusta el canvas del gráfico para ser descargado con las dimensiones ideales para la red social elegida."
                )
            formato_map = {
                "Horizontal (Estándar Web)": "horizontal",
                "Vertical (9:16 TikTok/Reels)": "vertical",
                "Cuadrado (1:1 X/Instagram)": "cuadrado"
            }
            formato_str = formato_map[formato_sel]
            
            st.markdown("<br>", unsafe_allow_html=True)

            fuente = cfg.get('fuente')

            # Visualizaciones que requieren eventos completos
            if tipo_grafico != "🎯 Mapa de Tiros":
                has_statsbomb = (fuente == 'statsbomb') or (pais in STATSBOMB_FALLBACK_CFG)
                if not has_statsbomb:
                    st.markdown(f"""
                    <div class="no-data" style="padding:40px 20px;">
                        <span class="no-data-icon" style="font-size:2.5rem;">🚨</span>
                        <div class="no-data-title">Visualización no disponible</div>
                        <div class="no-data-sub">La fuente {fuente_label} sólo provee coordenadas de disparos aislados.<br>
                        Se requiere StatsBomb Open Data para mapas de movimiento completos.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    real_cfg = cfg if fuente == 'statsbomb' else STATSBOMB_FALLBACK_CFG[pais]
                    sb_name = real_cfg['statsbomb_name']
                    comp_id = real_cfg['comp_id']
                    seas_id = real_cfg['seas_id']
                    torneo_nombre = real_cfg.get('torneo', 'StatsBomb Fallback')
                    
                    if fuente != 'statsbomb':
                        st.info(f"ℹ️ Usando datos históricos de **{torneo_nombre}** (StatsBomb) como respaldo para habilitar esta visualización.")
                        
                    cache_key_ev = f"eventos_{sb_name}_{comp_id}_{seas_id}"

                    if cache_key_ev not in st.session_state:
                        with st.spinner(f"Extrayendo eventos de {pais} ({torneo_nombre})..."):
                            ev_df, error = cargar_eventos_unified(pais, cfg)
                        if error:
                            st.error(error)
                            ev_df = None
                        else:
                            if ev_df is not None and not ev_df.empty:
                                ev_df['team'] = pais  # Normalizar columna team para filtros en visualizaciones
                            st.session_state[cache_key_ev] = ev_df
                    else:
                        ev_df = st.session_state[cache_key_ev]
                        if ev_df is not None and not ev_df.empty:
                            ev_df['team'] = pais  # Normalizar columna team para filtros en visualizaciones
                        error = None

                    if ev_df is not None and not ev_df.empty:
                        clean_tg = "".join([c for c in tipo_grafico if c.isalnum() or c == "_"])
                        cache_key_fig = f"fig_{clean_tg}_{pais}_{formato_str}"

                        if tipo_grafico == "🔥 Mapa de Calor":
                            if cache_key_fig not in st.session_state:
                                fig = generar_mapa_calor(ev_df, pais, torneo_nombre, cfg['bandera'], formato=formato_str)
                                st.session_state[cache_key_fig] = fig
                            fig = st.session_state[cache_key_fig]
                            st.caption(f"Se procesaron {len(ev_df):,} eventos para calcular la densidad.")

                            # Métricas avanzadas
                            ppda = calcular_ppda(ev_df, pais)
                            prog_passes = calcular_progressive_passes(ev_df, pais)
                            m1, m2 = st.columns(2)
                            m1.metric("PPDA (Presión)", f"{ppda:.2f}" if ppda else "N/A",
                                      help="Pases del rival por acción defensiva. <8 = presión élite. Menor = más agresivo.")
                            m2.metric("Pases Progresivos", f"{prog_passes:,}",
                                      help="Pases que avanzan ≥10m hacia la portería rival. Estándar FBref.")

                        elif tipo_grafico == "🕸️ Red de Pases":
                            if cache_key_fig not in st.session_state:
                                fig = generar_mapa_pases(ev_df, pais, torneo_nombre, cfg['bandera'], formato=formato_str)
                                st.session_state[cache_key_fig] = fig
                            fig = st.session_state[cache_key_fig]
                            st.caption("Visualización del último partido. Líneas gruesas = +3 pases entre esa dupla.")

                        elif tipo_grafico == "🧬 ADN Pases (K-Means)":
                            jugadores = sorted(ev_df[ev_df['type'] == 'Pass']['player'].dropna().unique().tolist())
                            default_idx = 0
                            for preferred in ["James David Rodríguez Rubio", "Luis Fernando Díaz Marulanda"]:
                                if preferred in jugadores:
                                    default_idx = jugadores.index(preferred)
                                    break
                            player_selected = st.selectbox("Selecciona un Jugador:", jugadores, index=default_idx, key=f"sel_{pais}")
                            st.markdown(f"""
                            <div style="background:rgba(255,215,0,0.05); border-left:4px solid #FFD700;
                                        padding:15px; border-radius:8px; margin-bottom:20px;">
                                <p style="margin:0; font-size:0.9rem; color:#ccc; line-height:1.5;">
                                    <b>¿Qué es el ADN Táctico?</b><br>
                                    El algoritmo <b>K-Means</b> agrupa los pases de <b>{player_selected}</b>
                                    en patrones maestros. El grosor de cada flecha indica el volumen de pases
                                    en esa dirección. Identifica la firma táctica real del jugador.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            cache_key_fig_km = f"kmeans_{pais}_{player_selected}_{formato_str}"
                            if cache_key_fig_km not in st.session_state:
                                fig = generar_mapa_clusters(ev_df, pais, torneo_nombre, cfg['bandera'], player_name=player_selected, formato=formato_str)
                                st.session_state[cache_key_fig_km] = fig
                            fig = st.session_state[cache_key_fig_km]
                            st.caption(f"Análisis K-Means para {player_selected}.")

                        elif tipo_grafico == "⚡ Expected Threat (xT)":
                            if cache_key_fig not in st.session_state:
                                fig = generar_mapa_xt(ev_df, pais, torneo_nombre, cfg['bandera'], formato=formato_str)
                                st.session_state[cache_key_fig] = fig
                            fig = st.session_state[cache_key_fig]
                            st.caption("Mapa de Amenaza Esperada (xT): Áreas del campo donde pases y conducciones exitosas incrementan la probabilidad de gol.")

                        elif tipo_grafico == "🧭 Sonar de Pases":
                            jugadores = sorted(ev_df[ev_df['type'] == 'Pass']['player'].dropna().unique().tolist())
                            default_idx = 0
                            for preferred in ["James David Rodríguez Rubio", "Luis Fernando Díaz Marulanda"]:
                                if preferred in jugadores:
                                    default_idx = jugadores.index(preferred)
                                    break
                            player_selected = st.selectbox("Selecciona un Jugador para el Sonar:", jugadores, index=default_idx, key=f"sonar_sel_{pais}")
                            
                            cache_key_fig_sonar = f"sonar_{pais}_{player_selected}_{formato_str}"
                            if cache_key_fig_sonar not in st.session_state:
                                fig = generar_mapa_sonar(ev_df, pais, torneo_nombre, cfg['bandera'], player_name=player_selected, formato=formato_str)
                                st.session_state[cache_key_fig_sonar] = fig
                            fig = st.session_state[cache_key_fig_sonar]
                            st.caption(f"Sonar de Pases para {player_selected}. Longitud de flechas = volumen; Color = precisión.")

                        elif tipo_grafico == "🛡️ Mapa Defensivo":
                            if cache_key_fig not in st.session_state:
                                fig = generar_mapa_defensivo(ev_df, pais, torneo_nombre, cfg['bandera'], formato=formato_str)
                                st.session_state[cache_key_fig] = fig
                            fig = st.session_state[cache_key_fig]
                            st.caption("Distribución espacial de intercepciones, entradas, bloqueos, presiones, recuperaciones y faltas.")

                        elif tipo_grafico == "🏃‍♂️ Conducciones Progresivas":
                            if cache_key_fig not in st.session_state:
                                fig = generar_mapa_carries(ev_df, pais, torneo_nombre, cfg['bandera'], formato=formato_str)
                                st.session_state[cache_key_fig] = fig
                            fig = st.session_state[cache_key_fig]
                            st.caption("Progresiones con balón dominado que avanzan al menos 10 metros en campo rival.")

                        elif tipo_grafico == "🎁 Mapa de Asistencias":
                            if cache_key_fig not in st.session_state:
                                fig = generar_mapa_asistencias(ev_df, pais, torneo_nombre, cfg['bandera'], formato=formato_str)
                                st.session_state[cache_key_fig] = fig
                            fig = st.session_state[cache_key_fig]
                            st.caption("Pases clave que finalizaron directamente en un disparo (asistencias de tiro).")

                        try:
                            st.pyplot(fig, use_container_width=True)
                            png_bytes = fig_to_png_bytes(fig)
                            dl_filename = f"Analisis_{pais}_{clean_tg}_{formato_str}_{datetime.now().strftime('%Y%m%d')}.png"
                            st.download_button(
                                label="📥 Descargar PNG (Alta Resolución)",
                                data=png_bytes,
                                file_name=dl_filename,
                                mime="image/png",
                                key=f"dl_{pais}_{clean_tg}_{formato_str}"
                            )
                        finally:
                            pass

            else:
                # Mapa de Tiros
                cache_key_tiros = f"tiros_{pais}"
                if cache_key_tiros not in st.session_state:
                    with st.spinner(f"Cargando disparos de {pais}..."):
                        tiros, error, fuente_usada = cargar_tiros_unified(pais, cfg)
                    if error:
                        st.error(f"⚠️ {error}")
                        tiros = None
                    elif tiros is not None:
                        st.session_state[cache_key_tiros] = tiros
                        st.session_state[f"fuente_usada_{pais}"] = fuente_usada
                else:
                    tiros = st.session_state[cache_key_tiros]
                    fuente_usada = st.session_state.get(f"fuente_usada_{pais}", fuente)
                    error = None

                if tiros is not None and not tiros.empty:
                    if fuente_usada != fuente:
                        fuente_label_usada = {
                            'fotmob': 'FotMob API', 'sofascore': 'SofaScore API',
                            '365scores': '365Scores API', 'statsbomb': 'StatsBomb Open Data'
                        }.get(fuente_usada, 'API Desconocida')
                        st.warning(f"⚠️ La fuente principal ({fuente_label}) no devolvió datos. Se cargaron tiros desde **{fuente_label_usada}** como respaldo.")
                    
                    stats = calcular_estadisticas_generales(tiros)
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Disparos", stats['n_tiros'], help="Total de disparos registrados en el torneo analizado.")
                    m2.metric("Goles", stats['n_goles'], help="Goles marcados en los partidos analizados.")
                    m3.metric("xG Total", f"{stats['xg_total']:.1f}", help="Expected Goals acumulados. >2.0/partido = ataque élite.")
                    m4.metric("Conversión", f"{stats['conv_rate']:.0f}%", help="% de disparos convertidos en gol.")
                    st.markdown("<br>", unsafe_allow_html=True)

                    cache_key_mapa = f"mapa_{pais}_{formato_str}"
                    if cache_key_mapa not in st.session_state:
                        fig = generar_mapa(tiros, pais, cfg.get('torneo', ''), cfg['bandera'], formato=formato_str)
                        st.session_state[cache_key_mapa] = fig
                    fig = st.session_state[cache_key_mapa]

                    try:
                        st.pyplot(fig, use_container_width=True)
                        png_bytes = fig_to_png_bytes(fig)
                        st.download_button(
                            label="📥 Descargar Mapa PNG",
                            data=png_bytes,
                            file_name=f"ShotMap_{pais}_{formato_str}_{datetime.now().strftime('%Y%m%d')}.png",
                            mime="image/png",
                            key=f"dl_shotmap_{pais}_{formato_str}"
                        )
                    finally:
                        pass
                elif tiros is not None and tiros.empty:
                    st.markdown(f"""
                    <div class="no-data" style="padding:40px 20px;">
                        <span class="no-data-icon" style="font-size:2.5rem;">⏱️</span>
                        <div class="no-data-title">Sin coordenadas de tiros</div>
                        <div class="no-data-sub">La fuente no registró coordenadas<br>para los últimos partidos de {pais}.</div>
                    </div>
                    """, unsafe_allow_html=True)
