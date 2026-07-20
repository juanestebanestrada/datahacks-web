"""pages/8_🧠_NotebookLM_AI.py — Con Gemini API real"""
import streamlit as st
from utils.style_loader import load_css
from utils.registry import load_registry, save_to_registry
from core.ai_generator import generar_podcast, generar_hilo_x, generar_dossier_scouting, generar_blog_seo, generar_trivia
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Inteligencia IA · Mundial 2026", page_icon="🧠", layout="wide")
load_css()

# Init session state
for key in ['gen_podcast','gen_dossier','gen_trivia']:
    if key not in st.session_state:
        st.session_state[key] = None

NOTEBOOK_ID = "a68a9047-1447-4685-befa-a4f1c928da8f"

st.sidebar.markdown("### 🧬 NotebookLM")
st.sidebar.info(f"📚 **Libreta:** Mundial2026\nID: `{NOTEBOOK_ID}`")

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#1A73E8,#0D47A1);
margin-bottom:20px;border-radius:12px;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">🧠 Inteligencia IA</h1>
    <p style="margin:0;color:#E8F0FE;">Powered by Gemini 2.0 Flash × NotebookLM</p>
</div>""", unsafe_allow_html=True)

with st.expander("🚀 GENERAR CON GEMINI AI", expanded=True):
    col_gen1, col_gen2 = st.columns([3, 1])
    with col_gen1:
        tema_ia = st.text_input("Tema para análisis con IA:", placeholder="Ej: Debilidades defensivas de Portugal o El ADN de Luis Díaz")
    with col_gen2:
        st.write("")
        st.write("")
        if st.button("⚡ Generar Todo", use_container_width=True, type="primary"):
            if tema_ia:
                with st.spinner("Gemini generando análisis real..."):
                    st.session_state['gen_podcast'], _ = generar_podcast(tema_ia)
                    st.session_state['gen_dossier'], _ = generar_dossier_scouting(tema_ia)
                    st.session_state['gen_trivia'],  _ = generar_trivia(tema_ia, n_preguntas=3)
                st.success("✅ ¡Contenido generado con IA real!")
                st.rerun()
            else:
                st.warning("Escribe un tema primero.")

tab1, tab2, tab3 = st.tabs(["🎙️ Pódcast Táctico", "📋 Dosier de Scouting", "🎮 Trivia Interactiva"])

with tab1:
    st.markdown("### 🎙️ Pódcast Táctico")
    if st.session_state.get('gen_podcast'):
        st.success("✨ Generado con Gemini AI")
        st.markdown(st.session_state['gen_podcast'])
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 Archivar Podcast"):
                save_to_registry("Podcast", f"Pódcast IA - {datetime.now().strftime('%d/%m/%Y')}", st.session_state['gen_podcast'])
                st.toast("¡Archivado!")
        with col_b:
            st.download_button("📥 Descargar .txt", data=st.session_state['gen_podcast'],
                               file_name=f"podcast_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
    st.markdown("---")
    st.write("**Podcast Original (NotebookLM):**")
    AUDIO_URL = "https://lh3.googleusercontent.com/notebooklm/AKXwDQFFuzKx7dbrHJrujMj36MvzL2eCoyse5p_hoSN4LjrMjpHOmZN9n-JLp-ScFJIYEq7k4_k6wL3dkP7fBIw4veFSea701LSYR3md4QT3ENCSwTaH9xHpYmmh436-E223TKURCKqOLzJH3a7zwtIwzl1mynwBqA=m140-dv"
    st.audio(AUDIO_URL, format="audio/wav")

with tab2:
    st.markdown("### 📋 Dosier de Scouting")
    if st.session_state.get('gen_dossier'):
        st.success("✨ Generado con Gemini AI")
        st.markdown(st.session_state['gen_dossier'])
        if st.button("💾 Archivar Dosier"):
            save_to_registry("Dosier", f"Dosier IA - {datetime.now().strftime('%d/%m/%Y')}", st.session_state['gen_dossier'])
            st.toast("¡Archivado!")
    else:
        st.info("Genera contenido con el panel de arriba para activar esta sección.")

with tab3:
    st.markdown("### 🎮 Trivia Interactiva")
    trivia_data = st.session_state.get('gen_trivia') or []
    if not trivia_data:
        st.info("Genera contenido arriba para activar la trivia con IA.")
    else:
        for idx, item in enumerate(trivia_data, 1):
            with st.expander(f"Pregunta {idx}: {item.get('pregunta', '')}"):
                ans = st.radio("Tu respuesta:", item.get("opciones", []), key=f"trivia_{idx}", index=None)
                if ans:
                    if ans == item.get("correcta"):
                        st.success("¡CORRECTO! 🎉")
                    else:
                        st.error(f"Incorrecto. La respuesta era: {item.get('correcta')}")
                    st.info(f"💡 {item.get('explicacion', '')}")

st.markdown("---")
with st.expander("🗄️ Historial de Contenido"):
    history = load_registry()
    if history:
        df = pd.DataFrame(history)[['timestamp', 'tipo', 'titulo']]
        df.columns = ['Fecha', 'Tipo', 'Título']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay contenido archivado.")
