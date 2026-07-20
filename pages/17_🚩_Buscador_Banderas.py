"""pages/17_🚩_Buscador_Banderas.py — Generador de Banderas y Grupos"""
import streamlit as st
import pandas as pd
import json
import os
import unicodedata
from utils.style_loader import load_css

st.set_page_config(page_title="Generador de Banderas · Mundial 2026", page_icon="🚩", layout="wide")
load_css()

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#11998e,#38ef7d);
margin-bottom:20px;border-radius:12px;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">🚩 Generador y Mapeador de Banderas Visuales</h1>
    <p style="margin:0;color:#E0F7FA;">Introduce un listado de grupos y equipos para generar automáticamente una tabla con sus banderas nacionales reales en imagen.</p>
</div>""", unsafe_allow_html=True)

def normalize_text(text):
    """Normaliza texto eliminando acentos, caracteres especiales y espacios raros."""
    if not text:
        return ""
    text = str(text).replace('\xa0', ' ').strip().lower()
    # Eliminar acentos/diacríticos
    text = "".join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text

def get_iso_mapping():
    # Mapeo de nombres normalizados a códigos ISO 3166-1 alpha-2 para FlagCDN
    base_iso = {
        "mexico": "mx", "corea del sur": "kr", "south korea": "kr",
        "rep checa": "cz", "republica checa": "cz", "czech republic": "cz",
        "suiza": "ch", "switzerland": "ch",
        "canada": "ca",
        "bosnia": "ba", "bosnia y herzegovina": "ba", "bosnia & herzegovina": "ba",
        "brasil": "br", "brazil": "br",
        "marruecos": "ma", "morocco": "ma",
        "usa": "us", "estados unidos": "us", "united states": "us",
        "turquia": "tr", "turkey": "tr",
        "paraguay": "py",
        "alemania": "de", "germany": "de",
        "ecuador": "ec",
        "costa de marfil": "ci", "ivory coast": "ci",
        "paises bajos": "nl", "netherlands": "nl", "holanda": "nl",
        "japon": "jp", "japan": "jp",
        "belgica": "be", "belgium": "be",
        "iran": "ir",
        "egipto": "eg", "egypt": "eg",
        "espana": "es", "spain": "es",
        "uruguay": "uy",
        "francia": "fr", "france": "fr",
        "senegal": "sn",
        "noruega": "no", "norway": "no",
        "argentina": "ar",
        "austria": "at",
        "argelia": "dz", "algeria": "dz",
        "portugal": "pt",
        "colombia": "co",
        "inglaterra": "gb-eng", "england": "gb-eng",
        "croacia": "hr", "croatia": "hr",
        "ghana": "gh",
        "haiti": "ht",
        "escocia": "gb-sct", "scotland": "gb-sct",
        "australia": "au",
        "curazao": "cw", "curacao": "cw",
        "suecia": "se", "sweden": "se",
        "tunez": "tn", "tunisia": "tn",
        "nueva zelanda": "nz", "new zealand": "nz",
        "cabo verde": "cv", "cape verde": "cv",
        "arabia saudi": "sa", "saudi arabia": "sa",
        "irak": "iq", "iraq": "iq",
        "jordania": "jo", "jordan": "jo",
        "rd congo": "cd", "congo dr": "cd", "congo": "cd",
        "uzbekistan": "uz",
        "panama": "pa"
    }
    
    # Crear mapeo normalizado
    normalized_mapping = {normalize_text(k): v for k, v in base_iso.items()}
    
    # Mapeo invertido de ISO a Emojis para cuando el usuario copie texto plano
    emoji_flags = {
        "mx": "🇲🇽", "kr": "🇰🇷", "cz": "🇨🇿", "ch": "🇨🇭", "ca": "🇨🇦", "ba": "🇧🇦",
        "br": "🇧🇷", "ma": "🇲🇦", "us": "🇺🇸", "tr": "🇹🇷", "py": "🇵🇾", "de": "🇩🇪",
        "ec": "🇪🇨", "ci": "🇨🇮", "nl": "🇳🇱", "jp": "🇯🇵", "be": "🇧🇪", "ir": "🇮🇷",
        "eg": "🇪🇬", "es": "🇪🇸", "uy": "🇺🇾", "fr": "🇫🇷", "sn": "🇸🇳", "no": "🇳🇴",
        "ar": "🇦🇷", "at": "🇦🇹", "dz": "🇩🇿", "pt": "🇵🇹", "co": "🇨🇴", "gb-eng": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "hr": "🇭🇷", "gh": "🇬🇭", "ht": "🇭🇹", "gb-sct": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "au": "🇦🇺",
        "cw": "🇨🇼", "se": "🇸🇪", "tn": "🇹🇳", "nz": "🇳🇿", "cv": "🇨🇻", "sa": "🇸🇦",
        "iq": "🇮🇶", "jo": "🇯🇴", "cd": "🇨🇩", "uz": "🇺🇿", "pa": "🇵🇦"
    }
    
    # Fusionar desde grupos.json
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root_dir, "data", "grupos.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                grupos = json.load(f)
                for g_name, teams in grupos.items():
                    for t_name, t_info in teams.items():
                        name_norm = normalize_text(t_name)
                        if name_norm not in normalized_mapping:
                            if "statsbomb_name" in t_info:
                                sb_name = normalize_text(t_info["statsbomb_name"])
                                if sb_name in normalized_mapping:
                                    normalized_mapping[name_norm] = normalized_mapping[sb_name]
    except Exception:
        pass
        
    return normalized_mapping, emoji_flags

# Input area
default_text = """A
México
Corea del Sur
Rep. Checa

B
Suiza
Canadá
Bosnia

C
Brasil	
Marruecos

D
USA
Turquía
Paraguay"""

st.markdown("### 📝 Pega tu lista abajo")
st.caption("Tip: Las letras solas definen el grupo. Los nombres de países siguientes se asignarán a ese grupo.")
raw_input = st.text_area("Listado de equipos:", value=default_text, height=200)

if st.button("⚡ Generar Tabla con Banderas", use_container_width=True, type="primary"):
    lines = [line.strip() for line in raw_input.split("\n")]
    parsed_data = []
    current_group = "Desconocido"
    iso_mapping, emoji_flags = get_iso_mapping()

    for line in lines:
        if not line:
            continue
        
        cleaned_line = line.strip()
        if len(cleaned_line) == 1 and cleaned_line.isalpha() and cleaned_line.isupper():
            current_group = f"Grupo {cleaned_line}"
        elif cleaned_line.lower().startswith("grupo "):
            current_group = cleaned_line.title()
        else:
            team_line = cleaned_line.replace("\t", " ")
            parts = [p.strip() for p in team_line.split(" ") if p.strip()]
            
            if not parts:
                continue
                
            iso_code = None
            matched_name = " ".join(parts)
            found = False
            
            # Buscar coincidencia
            for i in range(len(parts), 0, -1):
                candidate = " ".join(parts[:i])
                norm_candidate = normalize_text(candidate)
                if norm_candidate in iso_mapping:
                    iso_code = iso_mapping[norm_candidate]
                    matched_name = candidate
                    found = True
                    break
            
            # Búsqueda parcial
            if not found:
                norm_full = normalize_text(" ".join(parts))
                for key, val in iso_mapping.items():
                    if key in norm_full or norm_full in key:
                        iso_code = val
                        matched_name = " ".join(parts)
                        found = True
                        break
            
            flag_url = None
            emoji_fallback = "❓"
            if iso_code:
                flag_url = f"https://flagcdn.com/w80/{iso_code}.png"
                emoji_fallback = emoji_flags.get(iso_code, "❓")
            else:
                flag_url = "https://flagcdn.com/w80/un.png"
                
            parsed_data.append({
                "Grupo": current_group,
                "Equipo": matched_name.title(),
                "Bandera": flag_url,
                "Emoji": emoji_fallback
            })
            
    if parsed_data:
        df = pd.DataFrame(parsed_data)
        st.success(f"¡Procesados {len(df)} equipos con éxito!")
        
        # 1. Mostrar la tabla interactiva
        st.markdown("### 📊 Vista previa interactiva")
        st.dataframe(df[["Grupo", "Equipo", "Bandera"]], use_container_width=True, column_config={
            "Bandera": st.column_config.ImageColumn("Bandera (Imagen)", help="Bandera oficial"),
            "Grupo": st.column_config.TextColumn("Grupo", width="medium"),
            "Equipo": st.column_config.TextColumn("Equipo", width="large")
        })
        
        # 2. Copia rápida para Word / Excel
        st.markdown("### 📋 Copiar y Pegar Directo (Word, Excel, Google Docs)")
        st.caption("Selecciona el contenido de la tabla de abajo con tu mouse, cópialo con Ctrl+C y pégalo directamente en Word o Excel. Las imágenes de las banderas se transferirán automáticamente.")
        
        # Construir una tabla HTML nativa para que sea perfectamente seleccionable
        html_table = """
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #ddd; overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; color: #333;">
                <thead>
                    <tr style="background-color: #f2f2f2; border-bottom: 2px solid #ddd;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Grupo</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Equipo</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd; width: 100px;">Bandera</th>
                    </tr>
                </thead>
                <tbody>
        """
        for item in parsed_data:
            html_table += f"""
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 8px; border: 1px solid #ddd;">{item['Grupo']}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{item['Equipo']}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                            <img src="{item['Bandera']}" width="40" height="25" style="border: 1px solid #ccc; display: block; margin: 0 auto;" />
                        </td>
                    </tr>
            """
        html_table += """
                </tbody>
            </table>
        </div>
        """
        st.write(html_table, unsafe_allow_html=True)
        
        # 3. Formato Texto / Markdown
        st.markdown("### ✏️ Copiar como Texto / Markdown")
        st.caption("Usa el botón de la esquina superior derecha del cuadro para copiar la tabla completa formateada.")
        
        # Generar formato Markdown para copiar como texto plano
        markdown_text = "| Grupo | Equipo | Bandera |\n| :--- | :--- | :---: |\n"
        for item in parsed_data:
            markdown_text += f"| {item['Grupo']} | {item['Equipo']} | {item['Emoji']} |\n"
            
        st.code(markdown_text, language="markdown")
        
        # 4. Descarga física
        st.markdown("### 📥 Descargar Archivo")
        csv = df[["Grupo", "Equipo", "Emoji"]].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar tabla como CSV",
            data=csv,
            file_name="tabla_banderas_mundial.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.error("No se pudo procesar ningún equipo. Revisa el formato de entrada.")
