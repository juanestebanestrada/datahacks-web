def safe_show_screenshot(path, caption=""):
    """Muestra un screenshot solo si es un archivo de imagen válido y no vacío."""
    import os
    from PIL import Image
    if not path or not os.path.exists(path):
        return
    try:
        with Image.open(path) as img:
            w, h = img.size
            if w > 0 and h > 0:
                import streamlit as st
                st.image(path, caption=caption)
            else:
                import streamlit as st
                st.warning(f"Screenshot capturado pero con dimensiones inválidas ({w}x{h}). El navegador puede no haber renderizado a tiempo.")
    except Exception as e:
        import streamlit as st
        st.warning(f"No se pudo mostrar el screenshot: {e}")
