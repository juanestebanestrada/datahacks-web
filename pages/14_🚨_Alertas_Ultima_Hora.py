"""pages/14_🚨_Alertas_Ultima_Hora.py"""
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse
import json
from utils.style_loader import load_css
from core.ai_generator import _generate

st.set_page_config(page_title="Alertas de Última Hora · Mundial 2026", page_icon="🚨", layout="wide")
load_css()

# Hero Header
st.markdown("""<div class="hero" style="padding:30px;background:linear-gradient(135deg,#2b0000,#750000);">
    <h1 class="hero-title" style="font-size:2.5rem;">🚨 Centro de Alertas de Última Hora</h1>
    <p class="hero-sub">Ingesta de Google News RSS y clasificación táctica en tiempo real con IA</p>
</div>""", unsafe_allow_html=True)

# Helper function to query Google News RSS for both Spanish and English
def search_google_news(query):
    encoded_query = urllib.parse.quote(query)
    
    # Spanish and English RSS feeds
    url_es = f"https://news.google.com/rss/search?q={encoded_query}&hl=es-419&gl=US&ceid=US:es"
    url_en = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    def fetch_feed(url):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []
            root = ET.fromstring(response.content)
            items = []
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                source = item.find('source').text if item.find('source') is not None else ''
                items.append({
                    'title': title,
                    'link': link,
                    'pubDate': pub_date,
                    'source': source
                })
            return items
        except Exception:
            return []

    # Fetch both feeds
    items_es = fetch_feed(url_es)
    items_en = fetch_feed(url_en)
    
    # Merge and interleave to mix Spanish and English headlines, while deduplicating by title
    articles = []
    seen_titles = set()
    max_len = max(len(items_es), len(items_en))
    
    for i in range(max_len):
        if i < len(items_es):
            art = items_es[i]
            norm_title = art['title'].lower().strip()
            if " - " in norm_title:
                norm_title = norm_title.rsplit(" - ", 1)[0]
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                articles.append(art)
                
        if i < len(items_en):
            art = items_en[i]
            norm_title = art['title'].lower().strip()
            if " - " in norm_title:
                norm_title = norm_title.rsplit(" - ", 1)[0]
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                articles.append(art)
                
    if not articles:
        return None, "No se encontraron noticias ni en español ni en inglés."
    return articles, None

def clean_json_text(text):
    text = text.strip()
    if text.startswith("```"):
        # Split and extract the inner block
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
    return text.strip()

# AI Classification helper
def classify_headlines_ai(headlines):
    headlines_str = "\n".join([f"{idx+1}. {h}" for idx, h in enumerate(headlines)])
    
    prompt = f"""Analiza los siguientes titulares de noticias de fútbol (pueden estar en inglés o español) y clasifícalos.
Categorías válidas: "Lesión", "Convocatoria", "Declaraciones", "Polémica", "Fichaje", "Otros"
Nivel de Urgencia/Gravedad: "Baja", "Media", "Alta"

Titulares:
{headlines_str}

Responde estrictamente con un JSON que tenga esta estructura (sin formato Markdown adicional, solo el JSON). Es sumamente importante que traduzcas y redactes el campo "resumen" siempre en español, incluso si el titular original estaba en inglés:
{{
  "alertas": [
    {{
      "id": 1,
      "titulo_original": "...",
      "categoria": "...",
      "urgencia": "...",
      "figura_afectada": "...",
      "resumen": "resumen en español de la noticia en una frase"
    }},
    ...
  ]
}}
"""
    # Llamamos al motor central que automáticamente usa Ollama (si está marcado en la barra lateral)
    # o Gemini/Grok en la nube.
    res, err = _generate(prompt)
    if err:
        return None, err
    
    try:
        cleaned_res = clean_json_text(res)
        data = json.loads(cleaned_res)
        return data.get('alertas', []), None
    except Exception as e:
        return None, f"Error al parsear respuesta de IA: {e}. Respuesta cruda: {res[:200]}..."

# Stylings for categories
CATEGORY_STYLES = {
    "Lesión": {"bg": "rgba(255, 75, 75, 0.08)", "border": "rgba(255, 75, 75, 0.25)", "left_border": "#FF4B4B", "text": "#FF4B4B", "emoji": "🤕"},
    "Convocatoria": {"bg": "rgba(0, 150, 255, 0.08)", "border": "rgba(0, 150, 255, 0.25)", "left_border": "#0096FF", "text": "#0096FF", "emoji": "📋"},
    "Declaraciones": {"bg": "rgba(0, 200, 150, 0.08)", "border": "rgba(0, 200, 150, 0.25)", "left_border": "#00C896", "text": "#00C896", "emoji": "💬"},
    "Polémica": {"bg": "rgba(255, 150, 0, 0.08)", "border": "rgba(255, 150, 0, 0.25)", "left_border": "#FF9600", "text": "#FF9600", "emoji": "🔥"},
    "Fichaje": {"bg": "rgba(180, 80, 255, 0.08)", "border": "rgba(180, 80, 255, 0.25)", "left_border": "#B450FF", "text": "#B450FF", "emoji": "✈️"},
    "Otros": {"bg": "rgba(255, 255, 255, 0.04)", "border": "rgba(255, 255, 255, 0.1)", "left_border": "#888888", "text": "#888888", "emoji": "📰"}
}

# Main Layout
col_control, col_results = st.columns([1, 2])

with col_control:
    st.subheader("🔍 Panel de Control e Ingesta")
    
    # Predefined suggestions
    sug_term = st.selectbox(
        "💡 Términos Rápidos sugeridos:",
        ["[Escribir manualmente]", "Portugal", "Argentina", "Lionel Messi", "Cristiano Ronaldo", "Luis Díaz", "Mbappé", "Neymar", "España"]
    )
    
    # Manual query input
    if sug_term == "[Escribir manualmente]":
        search_query = st.text_input("Palabra clave / Equipo / Jugador:", "Portugal")
    else:
        search_query = sug_term
        
    limit = st.slider("Cantidad máxima de noticias a analizar:", min_value=3, max_value=15, value=7)
    
    st.write("---")
    st.write("🧪 **Ingreso Manual de Noticias (Simulación)**")
    st.info("¿Quieres probar el clasificador de IA ingresando una noticia específica? Escríbela a continuación.")
    manual_headline = st.text_area("Titular manual:", placeholder="Ej: Confirmado: Luis Díaz tiene un desgarro y se pierde el inicio de la Copa del Mundo.")
    
    # Ingest action
    ingest_button = st.button("🚀 Buscar y Clasificar Noticias", use_container_width=True, type="primary")

with col_results:
    st.subheader("⚡ Feed de Alertas Clasificadas")
    
    # Initialize states to persist alerts
    if "current_alerts" not in st.session_state:
        st.session_state.current_alerts = []
    if "raw_news_found" not in st.session_state:
        st.session_state.raw_news_found = 0

    if ingest_button:
        # 1. Fetching News
        headlines_to_classify = []
        news_metadata = []
        
        if manual_headline.strip():
            # If user typed manual news, analyze it
            headlines_to_classify.append(manual_headline.strip())
            news_metadata.append({
                "link": "#",
                "pubDate": "Hace instantes (Simulación)",
                "source": "Ingreso Manual"
            })
            st.toast("Analizando titular manual...")
        else:
            with st.spinner(f"Ingestando noticias desde Google News RSS (Español e Inglés) para '{search_query}'..."):
                news_items, err = search_google_news(search_query)
                if err:
                    st.error(err)
                elif not news_items:
                    st.warning(f"No se encontraron noticias de última hora para '{search_query}'.")
                else:
                    st.session_state.raw_news_found = len(news_items)
                    # Limit to selected size
                    for item in news_items[:limit]:
                        headlines_to_classify.append(item['title'])
                        news_metadata.append({
                            "link": item['link'],
                            "pubDate": item['pubDate'],
                            "source": item['source']
                        })
        
        # 2. IA Classification
        if headlines_to_classify:
            model_info = "Local (Ollama)" if st.session_state.get('force_ollama') else "Nube (Gemini/Grok)"
            with st.spinner(f"Clasificando {len(headlines_to_classify)} noticias en tiempo real con IA ({model_info})..."):
                alerts, err = classify_headlines_ai(headlines_to_classify)
                if err:
                    st.error(f"Error de IA: {err}")
                else:
                    # Merge metadata
                    final_alerts = []
                    for idx, alert in enumerate(alerts):
                        # Safely map to metadata
                        meta = news_metadata[idx] if idx < len(news_metadata) else {"link": "#", "pubDate": "Desconocida", "source": "Desconocida"}
                        alert['link'] = meta['link']
                        alert['pubDate'] = meta['pubDate']
                        alert['source'] = meta['source']
                        final_alerts.append(alert)
                    
                    st.session_state.current_alerts = final_alerts
                    
                    # Persist alerts to a shared file for the What-If Simulator
                    try:
                        import os
                        os.makedirs("data", exist_ok=True)
                        with open("data/active_alerts.json", "w", encoding="utf-8") as f:
                            json.dump(final_alerts, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        pass
                        
                    st.success(f"✅ ¡Clasificación completada con éxito! Se procesaron {len(final_alerts)} alertas.")

    # Render alerts
    if st.session_state.current_alerts:
        # Display search/filter options
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            cats_available = list(set([a.get('categoria', 'Otros') for a in st.session_state.current_alerts]))
            cat_filter = st.multiselect("Filtrar por Categoría:", cats_available, default=cats_available)
        with filter_col2:
            urg_available = list(set([a.get('urgencia', 'Baja') for a in st.session_state.current_alerts]))
            urg_filter = st.multiselect("Filtrar por Urgencia:", urg_available, default=urg_available)
            
        filtered_alerts = [
            a for a in st.session_state.current_alerts 
            if a.get('categoria', 'Otros') in cat_filter and a.get('urgencia', 'Baja') in urg_filter
        ]
        
        if not filtered_alerts:
            st.info("Ninguna alerta coincide con los filtros aplicados.")
        else:
            for alert in filtered_alerts:
                cat = alert.get('categoria', 'Otros')
                urg = alert.get('urgencia', 'Baja')
                fig = alert.get('figura_afectada', 'Ninguno')
                resumen = alert.get('resumen', '')
                titulo = alert.get('titulo_original', '')
                source = alert.get('source', 'Desconocido')
                pubdate = alert.get('pubDate', 'Fecha desconocida')
                link = alert.get('link', '#')
                
                # Fetch style details
                style = CATEGORY_STYLES.get(cat, CATEGORY_STYLES["Otros"])
                
                urg_badge = f'<span style="background: rgba(255, 75, 75, 0.2); color: #FF4B4B; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">{urg.upper()}</span>' if urg.lower() == 'alta' else \
                            f'<span style="background: rgba(255, 150, 0, 0.2); color: #FF9600; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">{urg.upper()}</span>' if urg.lower() == 'media' else \
                            f'<span style="background: rgba(100, 100, 100, 0.2); color: #AAA; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">{urg.upper()}</span>'
                
                st.markdown(f"""
                <div style="background: {style['bg']}; border: 1px solid {style['border']}; border-radius: 14px; padding: 18px; margin-bottom: 16px; border-left: 6px solid {style['left_border']};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 800; font-size: 0.85rem; color: {style['text']}; text-transform: uppercase;">
                            {style['emoji']} {cat}
                        </span>
                        <div>
                            {urg_badge}
                            <span style="font-size: 0.75rem; color: rgba(255,255,255,0.4); margin-left: 8px;">{pubdate}</span>
                        </div>
                    </div>
                    <h4 style="margin: 0 0 8px 0; color: #FFF; font-size: 1.1rem; line-height: 1.3;">{titulo}</h4>
                    <p style="margin: 0 0 6px 0; color: rgba(255,255,255,0.8); font-size: 0.9rem;">
                        <strong>👤 Figura afectada:</strong> <span style="color: #FFD700;">{fig}</span>
                    </p>
                    <p style="margin: 0; color: rgba(255,255,255,0.65); font-size: 0.88rem; line-height: 1.4; font-style: italic;">
                        "{resumen}"
                    </p>
                    <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
                        <span style="color: rgba(255,255,255,0.45);">Fuente: <strong>{source}</strong></span>
                        <a href="{link}" target="_blank" style="color: #FFD700; font-weight: 700; text-decoration: none; border-bottom: 1px dashed #FFD700;">Ver Noticia Original ↗</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="no-data">
            <span class="no-data-icon">📡</span>
            <div class="no-data-title">Sin alertas en el feed</div>
            <div class="no-data-sub">Selecciona un equipo o ingresa un titular manual a la izquierda y presiona "Buscar y Clasificar".</div>
        </div>
        """, unsafe_allow_html=True)
