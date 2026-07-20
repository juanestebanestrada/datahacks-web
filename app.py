"""
app.py — Página de Inicio (Home/Tutorial) · Mundial 2026 Tactical Dashboard
Este archivo ahora tiene ~80 líneas. El resto de páginas está en pages/.
"""
import streamlit as st
from config import PAGE_CONFIG
from utils.style_loader import load_css

# ── Configuración de la Página ──
st.set_page_config(**PAGE_CONFIG)
load_css()

# ── Hero Principal ──
st.markdown("""
<div class="hero">
    <div class="hero-tag">⚽ ANÁLISIS TÁCTICO DE ÉLITE</div>
    <h1 class="hero-title">Mundial 2026</h1>
    <p class="hero-sub">Plataforma de Inteligencia Táctica · Powered by Gemini AI × NotebookLM</p>
</div>
""", unsafe_allow_html=True)

# ── Stats de la App ──
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌍 Selecciones", "48", help="Equipos del Mundial 2026 con datos disponibles.")
c2.metric("📊 Fuentes de Datos", "6", help="StatsBomb, FotMob, SofaScore, 365Scores, ESPN, Football-Data.org")
c3.metric("🧠 Modelos IA", "3", help="Poisson Bivariada, K-Means, Similitud Coseno + Gemini 2.0 Flash")
c4.metric("📡 APIs Integradas", "6", help="6 proveedores de datos futbolísticos integrados.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Módulos del Sistema ──
st.subheader("🚀 Módulos de la Plataforma")
cols = st.columns(3)
modules = [
    ("🎯", "Mapas de Tiros", "Shot Maps xG · Mapas de Calor KDE · Redes de Pases · K-Means ADN Táctico", "StatsBomb / FotMob / SofaScore"),
    ("📈", "Match Momentum", "Intensidad del partido minuto a minuto. Análisis de ritmo ofensivo/defensivo.", "FotMob / SofaScore"),
    ("📊", "Tablas de Posiciones", "Clasificaciones actualizadas de las principales ligas europeas y torneos FIFA.", "FotMob API"),
    ("🌍", "WC2026 Oficial", "Datos oficiales del torneo. Fixtures, resultados y grupos verificados.", "Football-Data.org"),
    ("📡", "ESPN Live", "Scoreboard en vivo con probabilidades algorítmicas de resultado.", "ESPN Hidden API"),
    ("🧠", "Inteligencia IA", "Podcast táctico, trivia y dosieres de scouting generados con Gemini 2.0 Flash.", "Gemini + NotebookLM"),
    ("📱", "Content Factory", "Hilos virales de X, artículos SEO y guiones TikTok generados por IA.", "Gemini 2.0 Flash"),
    ("🧪", "Laboratorio Deep", "Simulación Poisson Bivariada · Tabla de Justicia Matemática · Gemelos Tácticos.", "StatsBomb + scipy"),
    ("🔍", "Explorador de Datos", "Búsqueda profunda de jugadores y equipos en el universo FBref.", "soccerdata + FBref"),
    ("🌍", "Spotlight Selecciones", "Análisis de las 48 selecciones del Mundial 2026 con Pizza Charts.", "48 Naciones Integradas"),
    ("📰", "Panel Informativo", "Resultados, fixtures, tabla y goleadores de cualquier liga o torneo.", "Football-Data.org"),
    ("🧪", "Laboratorio Pro", "Consolidación asíncrona multi-métrica · Pizza de Percentiles · KDE Heatmaps.", "FotMob + soccerdata"),
    ("🧠", "Simulador What-If", "Inyecta variables externas (lesiones, crisis, clima) y analiza el impacto táctico.", "Híbrido Gemini/Grok"),
    ("🏆", "Simulador de Pronósticos", "Configura tu llave del Mundial 2026 y pronostica al próximo Campeón del Mundo.", "Manual / Histórico"),
    ("🎨", "Bracket Interactivo", "Visualiza el bracket gráfico oficial y haz clic sobre los equipos para avanzar de ronda en tiempo real.", "Gráfico / Interactivo"),
]
for i, (icon, name, desc, source) in enumerate(modules):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="team-card" style="text-align:left; padding:16px 18px; margin-bottom:12px;">
            <div style="font-size:1.8rem; margin-bottom:8px;">{icon}</div>
            <div class="team-name" style="font-size:1rem; margin-bottom:6px;">{name}</div>
            <div style="font-size:0.8rem; color:rgba(255,255,255,0.45); line-height:1.4; margin-bottom:10px;">{desc}</div>
            <span class="team-label label-available">{source}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 ScoutingMundial · Powered by Gemini AI × NotebookLM × StatsBomb | Datos con fines analíticos y educativos.")
