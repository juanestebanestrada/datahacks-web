"""pages/3_📊_Tablas_Posiciones.py"""
import streamlit as st
from LanusStats import FotMob
from utils.style_loader import load_css

st.set_page_config(page_title="Tablas · Mundial 2026", page_icon="📊", layout="wide")
load_css()
st.markdown("""<div class="hero" style="padding:30px;">
    <h1 class="hero-title" style="font-size:2.5rem;">📊 Tablas de Posiciones</h1>
    <p class="hero-sub">Clasificaciones en Vivo · FotMob</p>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    torneo = st.selectbox("Liga:", ["Euros","Europa League","Champions League","Premier League","LaLiga"])
    season = st.selectbox("Temporada:", ["2023/2024","2024/2025"])
    if st.button("Cargar Tabla", use_container_width=True, type="primary"):
        st.session_state['tabla_query'] = (torneo, season)
with col2:
    if 'tabla_query' in st.session_state:
        t, s = st.session_state['tabla_query']
        with st.spinner(f"Descargando {t}..."):
            try:
                fm = FotMob()
                tabla = fm.get_season_tables(t, s, 'all')
                if isinstance(tabla, list):
                    st.success(f"{len(tabla)} grupos encontrados.")
                    for i, df in enumerate(tabla):
                        st.markdown(f"#### Grupo {chr(65+i)}")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.dataframe(tabla, use_container_width=True, hide_index=True)
            except Exception as e:
                if "403" in str(e) or "TURNSTILE" in str(e).upper():
                    st.error("🛡️ FotMob requiere verificación humana. Visita fotmob.com en tu navegador.")
                else:
                    st.error(f"Error: {e}")
