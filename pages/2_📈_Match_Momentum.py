"""
pages/2_📈_Match_Momentum.py
"""
import streamlit as st
import matplotlib.pyplot as plt
from LanusStats import SofaScore, fotmob_match_momentum_plot
from utils.style_loader import load_css

st.set_page_config(page_title="Match Momentum · Mundial 2026", page_icon="📈", layout="wide")
load_css()

st.markdown("""<div class="hero" style="padding:30px;">
    <h1 class="hero-title" style="font-size:2.5rem;">📈 Match Momentum</h1>
    <p class="hero-sub">Intensidad del partido minuto a minuto</p>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    source = st.radio("Fuente:", ["🛡️ FotMob", "📊 SofaScore"], horizontal=True)
    examples_fotmob = {"Brasil vs Argentina": "4196578", "España vs Francia": "4679452", "Colombia vs Chile": "4196582"}
    examples_sofa   = {"Argentina vs Brasil": "12716821", "Colombia vs Chile": "12716823"}
    examples = examples_fotmob if "FotMob" in source else examples_sofa
    sel = st.selectbox("Ejemplos:", list(examples.keys()))
    match_id = st.text_input("ID del Partido:", value=examples[sel])
    if "FotMob" in source:
        st.caption("⚠️ Amistosos suelen carecer de datos. Usa eliminatorias oficiales.")
    else:
        st.caption("💡 IDs de eliminatorias son los más confiables.")
    if st.button("⚡ Generar Momentum", use_container_width=True, type="primary"):
        if match_id.strip().isdigit():
            st.session_state['momentum_id']     = match_id.strip()
            st.session_state['momentum_source'] = source
        else:
            st.error("Ingresa un ID numérico válido.")

with col2:
    if 'momentum_id' in st.session_state:
        with st.spinner("Generando gráfico..."):
            try:
                plt.style.use('dark_background')
                src = st.session_state.get('momentum_source', "🛡️ FotMob")
                if "FotMob" in src:
                    fig, ax = fotmob_match_momentum_plot(st.session_state['momentum_id'], save_fig=False)
                    fig.patch.set_facecolor('#080d1a')
                    ax.set_facecolor('#080d1a')
                else:
                    ss = SofaScore()
                    df = ss.get_match_momentum(st.session_state['momentum_id'])
                    if df is None or df.empty:
                        raise Exception("Sin datos de momentum.")
                    try:
                        md = ss.get_match_data(st.session_state['momentum_id'])
                        home = md['event']['homeTeam']['name']
                        away = md['event']['awayTeam']['name']
                        title = f"{home} vs {away}"
                    except Exception:
                        home, away, title = "Local", "Visitante", "Match Momentum"
                    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#080d1a')
                    ax.set_facecolor('#080d1a')
                    colors = ['#00c2cb' if v > 0 else '#ff4b4b' for v in df['value']]
                    ax.bar(df['minute'], df['value'], color=colors, width=0.8, alpha=0.8)
                    ax.axhline(0, color='white', linewidth=0.5, alpha=0.5)
                    ax.set_title(title, color='white', fontsize=14, pad=20)
                    ax.set_xlabel("Minuto", color='#cccccc')
                    ax.set_ylabel("Intensidad", color='#cccccc')
                    ax.text(0.02, 0.95, f"▲ {home}", transform=ax.transAxes, color='#00c2cb', fontsize=10, fontweight='bold')
                    ax.text(0.02, 0.05, f"▼ {away}", transform=ax.transAxes, color='#ff4b4b', fontsize=10, fontweight='bold')
                    plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
                with st.expander("📚 Interpretación"):
                    st.markdown("**Barras arriba (azul):** Local. **Barras abajo (rojo):** Visitante. Picos sostenidos suelen preceder un gol.")
            except Exception as e:
                err = str(e)
                if "403" in err or "TURNSTILE" in err.upper():
                    st.error("🛡️ Cloudflare bloqueó la conexión. Visita la web en tu navegador y reintenta.")
                elif "'general'" in err:
                    st.error("❌ No hay datos de momentum para este ID de partido.")
                else:
                    st.error(f"Error: {e}")
