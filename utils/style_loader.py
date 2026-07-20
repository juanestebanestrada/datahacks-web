"""
utils/style_loader.py — Carga el CSS global una sola vez.
"""
import streamlit as st
import os

_CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')

def load_css():
    """Inyecta el CSS global de la app. Llamar una vez al inicio de cada página."""
    try:
        with open(_CSS_PATH, 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Si no existe el archivo, continuar sin estilos personalizados
    
    # Llamar al centro de control de IA
    load_ai_sidebar()

def load_ai_sidebar():
    """Dibuja el centro de control de IA en la barra lateral."""
    st.sidebar.divider()
    st.sidebar.subheader("🤖 Centro de Control IA")
    
    from core.ai_generator import get_ollama_models
    
    # Inicializar estados si no existen
    if 'force_ollama' not in st.session_state:
        st.session_state.force_ollama = False
    
    # Obtener lista de modelos reales instalados
    lista_modelos = get_ollama_models()
    
    st.session_state.force_ollama = st.sidebar.toggle(
        "Modo Local (Ollama)", 
        value=st.session_state.force_ollama,
        help="Usa tu GPU (RTX 3060/4060 Ti) en lugar de la nube."
    )
    
    st.session_state.model_ollama = st.sidebar.selectbox(
        "Seleccionar Modelo Local", 
        options=lista_modelos,
        index=0
    )
    
    if st.session_state.force_ollama:
        st.sidebar.success(f"⚡ Corriendo en local: {st.session_state.model_ollama}")
    else:
        st.sidebar.info("☁️ Corriendo en la nube (Gemini/Grok)")


def copyable_dataframe(df, label: str = "tabla", key: str = "copy", styled=None,
                       use_container_width: bool = True, hide_index: bool = True):
    """
    Muestra un dataframe con botones de descarga CSV y copiado rápido.
    Úsalo en cualquier página de la app en lugar de st.dataframe() cuando
    quieras que el usuario pueda copiar o exportar los datos fácilmente.

    Parámetros
    ----------
    df          : pd.DataFrame  — datos a mostrar
    label       : str           — nombre del archivo CSV de descarga
    key         : str           — clave única para evitar colisiones de widgets
    styled      : Styler | None — si se pasa un Styler de Pandas, se usa para el dataframe
    use_container_width : bool
    hide_index  : bool
    """
    import pandas as pd
    import io

    col_csv, col_excel, col_cp, col_spacer = st.columns([1.4, 1.4, 1.4, 3.8])

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    with col_csv:
        st.download_button(
            label="📥 Descargar CSV",
            data=csv_bytes,
            file_name=f"{label}.csv",
            mime="text/csv",
            key=f"dl_{key}",
            use_container_width=True,
        )

    # Generar bytes de Excel en memoria
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_bytes = excel_buffer.getvalue()
    
    with col_excel:
        st.download_button(
            label="📊 Descargar Excel",
            data=excel_bytes,
            file_name=f"{label}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_excel_{key}",
            use_container_width=True,
        )

    show_text = st.session_state.get(f"show_text_{key}", False)
    with col_cp:
        if st.button("📋 Copiar tabla", key=f"cp_{key}", use_container_width=True):
            st.session_state[f"show_text_{key}"] = not show_text
            show_text = not show_text

    # Render del dataframe
    if styled is not None:
        st.dataframe(styled, use_container_width=use_container_width, hide_index=hide_index)
    else:
        st.dataframe(df, use_container_width=use_container_width, hide_index=hide_index)

    # Panel de texto copiable (se activa con el botón)
    if show_text:
        tsv_text = df.to_csv(sep="\t", index=False)
        st.code(tsv_text, language=None)
        st.caption("☝️ Haz clic en el icono de copiar (arriba a la derecha del recuadro) para copiar todo al portapapeles.")
