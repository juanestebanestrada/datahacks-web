"""pages/9_📱_Content_Factory.py — Con Gemini API real"""
import streamlit as st
from datetime import datetime
import pandas as pd
from utils.style_loader import load_css
from utils.registry import load_registry, save_to_registry
from core.ai_generator import generar_hilo_x, generar_blog_seo, generar_guion_tiktok, generar_guion_youtube

st.set_page_config(page_title="Content Factory · Mundial 2026", page_icon="📱", layout="wide")
load_css()

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#FF4B2B,#FF416C);
margin-bottom:20px;border-radius:12px;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">📱 Content Factory</h1>
    <p style="margin:0;color:#FFE3E3;">Material viral para X, YouTube y Blog — Gemini AI</p>
</div>""", unsafe_allow_html=True)

for k in ['cf_x', 'cf_blog', 'cf_tiktok', 'cf_youtube', 'cf_error']:
    if k not in st.session_state:
        st.session_state[k] = None

# Generador central
st.subheader("⚡ Generar Nuevo Contenido")
col_t, col_tone, col_b = st.columns([3, 2, 1.2])
with col_t:
    topic = st.text_area("Tema:", placeholder="Ej: El impacto de Luis Díaz en la ofensiva de Colombia", key="cf_topic")
with col_tone:
    tono_seleccionado = st.selectbox(
        "Tono Editorial:",
        ["Científico (Montecarlo)", "El Villano (Polémico)", "Sleepy Giant (Gemas de Datos)", "Betting & Value (Especulador)"],
        index=0,
        help="Adapta el estilo de redacción e intención de los contenidos generados."
    )
with col_b:
    st.write("")
    st.write("")
    if st.button("🚀 Generar Todo", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("Gemini generando contenido (Blog, X, TikTok, YouTube)..."):
                st.session_state['cf_x'],       err_x = generar_hilo_x(topic, tono=tono_seleccionado)
                st.session_state['cf_blog'],    err_b = generar_blog_seo(topic, "Mundial 2026", tono=tono_seleccionado)
                st.session_state['cf_tiktok'],  err_t = generar_guion_tiktok(topic, tono=tono_seleccionado)
                st.session_state['cf_youtube'], err_y = generar_guion_youtube(topic, tono=tono_seleccionado)
                
                errores = [e for e in [err_x, err_b, err_t, err_y] if e]
                if errores:
                    st.session_state['cf_error'] = errores[0]
                else:
                    st.session_state['cf_error'] = None
                    save_to_registry("Generación CF", f"CF ({tono_seleccionado}) - {topic[:30]}", f"Paquete completo generado")
            
            st.rerun()
        else:
            st.warning("Escribe un tema.")

tab_x, tab_blog, tab_tiktok, tab_youtube, tab_hist = st.tabs(["🐦 Hilo X", "📰 Blog SEO", "🎬 TikTok (60s)", "🎥 YouTube (3-5m)", "🗄️ Historial"])

if st.session_state.get('cf_error'):
    st.error(f"🚨 Falla en los motores de IA:\n\n{st.session_state['cf_error']}")

with tab_x:
    st.write("Hilo viral con ganchos emocionales y hashtags optimizados.")
    x_text = st.session_state.get('cf_x')
    if x_text:
        st.success("✨ Generado con Gemini/Grok AI")
        st.code(x_text, language="markdown")
        col1, col2 = st.columns(2)
        with col1: st.info("Copia el texto y pégalo en X.")
        with col2:
            if st.button("💾 Archivar Hilo", key="save_x"):
                save_to_registry("X Thread", f"Hilo - {datetime.now().strftime('%d/%m/%Y')}", x_text)
                st.toast("¡Hilo guardado!")
    else:
        st.info("Genera contenido con el panel de arriba.")

with tab_blog:
    st.write("Post 600-800 palabras estructurado para WordPress.")
    blog_text = st.session_state.get('cf_blog')
    if blog_text:
        st.success("✨ Generado con Gemini/Grok AI")
        with st.expander("👁️ Vista Previa", expanded=True):
            st.markdown(blog_text)
        st.code(blog_text, language="markdown")
        if st.button("💾 Archivar Blog", key="save_blog"):
            save_to_registry("Blog SEO", f"Blog - {datetime.now().strftime('%d/%m/%Y')}", blog_text)
            st.toast("¡Blog guardado!")
    else:
        st.info("Genera contenido con el panel de arriba.")

with tab_tiktok:
    st.write("Guión de 60 segundos enfocado en alta retención (Ganchos y CTA rápidos).")
    tiktok_text = st.session_state.get('cf_tiktok')
    if tiktok_text:
        st.success("✨ Generado automáticamente por Gemini/Grok")
        st.markdown(tiktok_text)
        if st.button("💾 Archivar TikTok", key="save_tiktok"):
            save_to_registry("TikTok Script", f"TikTok - {datetime.now().strftime('%d/%m/%Y')}", tiktok_text)
            st.toast("¡Guión de TikTok guardado!")
    else:
        st.info("Genera contenido con el panel de arriba.")

with tab_youtube:
    st.write("Guión largo (3 a 5 min) para análisis profundo, indicando visuales de la app.")
    youtube_text = st.session_state.get('cf_youtube')
    if youtube_text:
        st.success("✨ Generado automáticamente por Gemini/Grok")
        st.markdown(youtube_text)
        if st.button("💾 Archivar YouTube", key="save_youtube"):
            save_to_registry("YouTube Script", f"YouTube - {datetime.now().strftime('%d/%m/%Y')}", youtube_text)
            st.toast("¡Guión de YouTube guardado!")
    else:
        st.info("Genera contenido con el panel de arriba.")

with tab_hist:
    st.write("Historial de todo el contenido generado.")
    history = load_registry()
    if history:
        df = pd.DataFrame(history)[['timestamp', 'tipo', 'titulo']]
        df.columns = ['Fecha', 'Tipo', 'Título']
        st.dataframe(df, use_container_width=True, hide_index=True)
        sel = st.selectbox("Ver contenido:", [f"[{h['tipo']}] {h['titulo']}" for h in history])
        if sel:
            idx = [f"[{h['tipo']}] {h['titulo']}" for h in history].index(sel)
            st.code(history[idx]['contenido'], language="markdown")
    else:
        st.info("No hay contenido archivado aún.")
