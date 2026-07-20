"""pages/5_🌍_Spotlight_Selecciones.py — Con datos reales y 48 naciones"""
import streamlit as st
import matplotlib.pyplot as plt
from utils.style_loader import load_css
from core.international_spotlight import InternationalSpotlight
from utils.visualization import fig_to_png_bytes

st.set_page_config(page_title="Spotlight · Mundial 2026", page_icon="🌍", layout="wide")
load_css()

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#1e1e1e,#333);margin-bottom:20px;
border-radius:12px;border-left:5px solid #FFD700;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">🌍 Buscador Universal de Selecciones</h1>
    <p style="margin:0;color:#ccc;">Inteligencia Táctica Mundialista — Camino 2026</p>
</div>""", unsafe_allow_html=True)

spotlight = InternationalSpotlight()
all_nations = spotlight.get_all_nations()
team = st.selectbox("Busca una Selección Nacional:", all_nations,
                    index=all_nations.index("Argentina") if "Argentina" in all_nations else 0)

meta = spotlight.get_team_metadata(team)
conf_data = spotlight.confederations.get(meta['conf'], {"color": "#6971ff", "icon": "🏳️"})

col1, col2 = st.columns([1, 2])
with col1:
    st.markdown(f"### {conf_data['icon']} {team}")
    st.markdown(f"<div style='display:inline-block;padding:4px 12px;border-radius:20px;"
                f"background-color:{conf_data['color']};color:white;font-weight:bold;margin-bottom:15px;'>"
                f"{meta['conf']}</div>", unsafe_allow_html=True)
    st.subheader("⭐ Figuras / Scouting")
    for p in meta.get('players', []):
        st.write(f"- {p}")

with col2:
    st.subheader("📊 Perfil Táctico Dinámico")
    stats = spotlight.fetch_universal_stats(team)
    if stats:
        try:
            fig = spotlight.create_scouting_pizza(f"Análisis: {team}", stats['values'], stats['params'], color=conf_data['color'])
            st.pyplot(fig, use_container_width=True)
            st.download_button("📥 Descargar Pizza Chart", data=fig_to_png_bytes(fig),
                               file_name=f"Pizza_{team}.png", mime="image/png")
            plt.close(fig)
        except Exception as e:
            st.warning(f"No se pudo generar el gráfico: {e}")
    else:
        st.warning("Datos no disponibles.")

st.markdown("---")
st.subheader("📝 Contexto de Confederación")
confederation_context = {
    "UEFA":     "La UEFA alberga las selecciones con mayor inversión en análisis de datos. Alta densidad táctica, presión post-pérdida y juego posicional dominan.",
    "CONMEBOL": "CONMEBOL produce selecciones de alta creatividad individual y transiciones rápidas. El xG ofensivo suele ser superior a la media mundial.",
    "CAF":      "Las selecciones de la CAF destacan por la intensidad física y el contraataque. Creciente adopción de metodologías analíticas modernas.",
    "AFC":      "La AFC tiene en Japón y Corea del Sur sus exponentes más avanzados tácticamente. Alto pressing y disciplina posicional.",
    "CONCACAF": "CONCACAF combina el físico de Norteamérica con la creatividad caribeña. USA es el equipo con mayor presupuesto analítico de la región.",
    "OFC":      "La OFC tiene menor competitividad pero Nueva Zelanda muestra desarrollo constante en métricas de pressing."
}
st.info(confederation_context.get(meta['conf'], "Confederación con alto potencial competitivo."))
