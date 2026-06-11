"""pages/11_🧪_Lab_Pro.py — Async Consolidation + Pizza + KDE"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.style_loader import load_css
from core.scouting_engine import ScoutingEngine
from utils.visualization import fig_to_png_bytes

st.set_page_config(page_title="Lab Pro · Mundial 2026", page_icon="🧪", layout="wide")
load_css()

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#00c6ff,#0072ff);margin-bottom:20px;border-radius:12px;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">🧪 Laboratorio Pro</h1>
    <p style="margin:0;color:#fff;opacity:0.85;">High-Performance Analytics · Pizza Plots · KDE Heatmaps</p>
</div>""", unsafe_allow_html=True)

engine = ScoutingEngine()
tab1, tab2, tab3 = st.tabs(["🚀 Consolidación Async", "🍕 Radar de Élite", "🔥 KDE Heatmap Pro"])

with tab1:
    st.subheader("Consolidación Multimétrica (FotMob)")
    st.write("Extrae y une múltiples rankings en segundos.")
    col1, col2 = st.columns([2, 1])
    with col1:
        stats_to_fetch = st.multiselect("Métricas:", [
            "expected_goals_team","expected_goals_conceded_team","possession_percentage_team",
            "big_chance_team","touches_in_opp_box_team","accurate_pass_team"
        ], default=["expected_goals_team","possession_percentage_team"])
    with col2:
        st.write("")
        if st.button("🚀 Master Merge", use_container_width=True, type="primary"):
            with st.spinner("Sincronizando endpoints FotMob..."):
                df_master = engine.get_all_team_season_stats(47, "2023/2024", stats_to_fetch)
                st.session_state['master_df_lab'] = df_master

    if st.session_state.get('master_df_lab') is not None:
        df = st.session_state['master_df_lab']
        if df is not None and not df.empty:
            st.success("¡Master Table generada!")
            st.dataframe(df.style.background_gradient(cmap='Blues'), use_container_width=True)
        else:
            st.warning("No se pudo generar la tabla. Verifica conexión o IDs de liga.")
    with st.expander("⚠️ Nomenclatura FotMob"):
        st.info("Usar sufijo `_team` en las métricas. Ej: `expected_goals_team`, `possession_percentage_team`.")

with tab2:
    st.subheader("Radar de Percentiles (Pizza Plot)")
    player_name = st.text_input("Nombre del Jugador:", value="Luis Díaz")
    params = ["Goles","Asistencias","xG","xA","Regates","Pases Clave","Tackles","Intercepciones"]
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("**Configura los percentiles (0-100):**")
        values = [st.slider(f"{p}:", 0, 100, 50 + i*5, key=f"slider_{p}") for i, p in enumerate(params)]
    with col_p2:
        try:
            fig = engine.plot_advanced_radar(player_name, params, values)
            st.pyplot(fig, use_container_width=True)
            st.download_button("📥 Descargar Pizza Chart", data=fig_to_png_bytes(fig),
                               file_name=f"Pizza_{player_name}.png", mime="image/png")
            plt.close(fig)
        except Exception as e:
            st.error(f"Error al generar radar: {e}")

with tab3:
    st.subheader("KDE Heatmap · Densidad Ofensiva (FotMob → StatsBomb)")
    st.write("Coordenadas FotMob (0-100) normalizadas automáticamente a espacio StatsBomb (120x80).")
    col_h1, col_h2 = st.columns([1, 2])
    with col_h1:
        n_points = st.slider("Puntos simulados:", 20, 200, 50)
        zone = st.selectbox("Zona de ataque:", ["Área rival (70-100)", "Media punta (50-70)", "Campo completo"])
        if zone == "Área rival (70-100)":
            x_range = (70, 100)
        elif zone == "Media punta (50-70)":
            x_range = (50, 70)
        else:
            x_range = (20, 100)
        mock_shots = pd.DataFrame({
            'x': np.random.uniform(*x_range, n_points),
            'y': np.random.uniform(20, 80, n_points)
        })
    with col_h2:
        try:
            fig_kde = engine.plot_kde_heatmap(mock_shots, title=f"Densidad Ofensiva — {player_name}")
            st.pyplot(fig_kde, use_container_width=True)
            st.download_button("📥 Descargar KDE", data=fig_to_png_bytes(fig_kde),
                               file_name=f"KDE_{player_name}.png", mime="image/png")
            plt.close(fig_kde)
        except Exception as e:
            st.error(f"Error KDE: {e}")
