"""
utils/build_match_pages.py
Compila los análisis en formato Markdown (.md) a páginas HTML estáticas
y actualiza dinámicamente tanto las páginas de grupo como el widget Multi-Match de la home page.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'analisis_partidos')
WEBSITE_DIR = os.path.join(BASE_DIR, 'website')
ANALISIS_DIR = os.path.join(WEBSITE_DIR, 'analisis')

GROUP_PAGES = {
    "Grupo A": "grupo_a.html",
    "Grupo B": "grupo_b.html",
    "Grupo C": "grupo_c.html",
    "Grupo D": "grupo_d.html",
    "Grupo E": "grupo_e.html",
    "Grupo F": "grupo_f.html",
    "Grupo G": "grupo_g.html",
    "Grupo H": "grupo_h.html",
    "Grupo I": "grupo_i.html",
    "Grupo J": "grupo_j.html",
    "Grupo K": "grupo_k.html",
    "Grupo L": "grupo_l.html",
}

FLAGS_MAP = {
    "México": "mx", "Sudáfrica": "za", "Rep. Checa": "cz", "Corea del Sur": "kr",
    "Suiza": "ch", "Canadá": "ca", "Qatar": "qa", "Bosnia": "ba",
    "Brasil": "br", "Marruecos": "ma", "Haití": "ht", "Escocia": "gb-sct",
    "Turquía": "tr", "USA": "us", "Paraguay": "py", "Australia": "au",
    "Alemania": "de", "Curazao": "cw", "Costa de Marfil": "ci", "Ecuador": "ec",
    "Suecia": "se", "Países Bajos": "nl", "Japón": "jp", "Túnez": "tn",
    "Bélgica": "be", "Egipto": "eg", "Irán": "ir", "Nueva Zelanda": "nz",
    "España": "es", "Cabo Verde": "cv", "Arabia Saudí": "sa", "Uruguay": "uy",
    "Irak": "iq", "Francia": "fr", "Senegal": "sn", "Noruega": "no",
    "Argentina": "ar", "Argelia": "dz", "Austria": "at", "Jordania": "jo",
    "RD Congo": "cd", "Portugal": "pt", "Uzbekistán": "uz", "Colombia": "co",
    "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa"
}

# Plantilla HTML para una página de partido individual
TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{titulo} // DataHacks</title>
  <meta name="description" content="Análisis táctico detallado del partido {home_team} vs {away_team} del Mundial 2026." />
  <link rel="stylesheet" href="../css/main.css" />
  <style>
    .match-header {{
      padding: 140px 0 60px;
      text-align: center;
      position: relative;
      background: linear-gradient(135deg, #0f0c20 0%, #15102a 100%);
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .back-btn-wrap {{
      display: flex;
      justify-content: flex-start;
      margin-bottom: 24px;
    }}
    .back-link {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--cyan);
      font-family: var(--font-head);
      font-weight: 700;
      font-size: 0.9rem;
      transition: all 0.3s;
    }}
    .back-link:hover {{
      color: var(--white);
      transform: translateX(-4px);
    }}
    .match-container {{
      max-width: 850px;
      margin: 40px auto 80px;
      padding: 32px;
      background: var(--bg-card);
      backdrop-filter: blur(25px);
      border: 1px solid var(--border);
      border-radius: var(--r-lg);
      box-shadow: 0 15px 35px rgba(0,0,0,0.3);
      color: #fff;
      line-height: 1.8;
    }}
    .match-container h1, .match-container h2, .match-container h3 {{
      font-family: var(--font-head);
      color: var(--cyan);
      margin-top: 28px;
      margin-bottom: 12px;
    }}
    .match-container h1 {{ font-size: 2rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 10px; }}
    .match-container h2 {{ font-size: 1.5rem; color: var(--green); }}
    .match-container h3 {{ font-size: 1.2rem; }}
    .match-container p {{ margin-bottom: 16px; color: #e0e6ed; }}
    .match-container ul {{ margin-bottom: 20px; padding-left: 20px; list-style-type: square; }}
    .match-container li {{ margin-bottom: 8px; color: #e0e6ed; }}
    .scoreboard {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 30px;
      margin: 25px 0;
      font-family: var(--font-head);
    }}
    .score-team {{
      font-size: 1.8rem;
      font-weight: 900;
      color: #fff;
    }}
    .score-box {{
      background: rgba(0, 149, 255, 0.15);
      color: var(--cyan);
      border: 1px solid rgba(0, 149, 255, 0.3);
      font-size: 2.2rem;
      font-weight: 900;
      padding: 10px 24px;
      border-radius: 12px;
      min-width: 100px;
      text-align: center;
    }}
    .tactical-visuals {{
      margin-top: 35px;
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 25px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      align-items: center;
    }}
    .tactical-visuals h4 {{
      font-family: var(--font-head);
      color: var(--green);
      margin: 0 0 10px;
    }}
    .tactical-visuals img {{
      max-width: 100%;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.08);
    }}
    @media (max-width: 600px) {{
      .scoreboard {{
        flex-direction: column;
        gap: 12px;
        margin: 15px 0;
      }}
      .score-team {{
        font-size: 1.4rem;
        text-align: center;
        justify-content: center !important;
      }}
      .score-box {{
        font-size: 1.8rem;
        padding: 8px 20px;
        min-width: 80px;
      }}
      .match-container {{
        padding: 20px 14px;
        margin: 20px auto 40px;
        border-radius: var(--r);
      }}
      .match-container h1 {{
        font-size: 1.5rem;
      }}
      .match-container h2 {{
        font-size: 1.25rem;
      }}
      .match-container h3 {{
        font-size: 1.1rem;
      }}
      .match-container p, .match-container li {{
        font-size: 0.88rem;
        line-height: 1.6;
      }}
      .match-header {{
        padding: 110px 0 40px;
      }}
      .match-header h2 {{
        font-size: 1.8rem;
      }}
    }}
  </style>
</head>
<body>

<nav class="navbar scrolled" id="navbar">
  <div class="container">
    <div class="nav-inner">
      <a href="../index.html" class="nav-logo">
        <img src="../assets/logo_datahacks.jpg" alt="DataHacks" style="height:48px;">
      </a>
      <ul class="nav-links">
        <li><a href="../index.html#plataforma">Plataforma</a></li>
        <li><a href="../index.html#mundial2026">Mundial 2026</a></li>
        <li><a href="../index.html#contenido">Contenido</a></li>
        <li><a href="../index.html#social">Social</a></li>
      </ul>
      <div class="nav-cta">
        <a href="../index.html#newsletter" class="btn btn-primary">Suscribirme →</a>
      </div>
    </div>
  </div>
</nav>

<section class="match-header">
  <div class="container">
    <div class="back-btn-wrap">
      <a href="../{grupo_page}" class="back-link">← Volver al {grupo}</a>
    </div>
    <span class="badge" style="margin-bottom:16px">{grupo}</span>
    <h2>{home_team} vs {away_team}</h2>
    <p style="color: var(--muted); font-size: 1rem;">📅 {fecha} · 🕒 {hora} (Local)</p>
    
    <div class="scoreboard">
      <div class="score-team" style="display: flex; align-items: center; gap: 12px; justify-content: flex-end; flex: 1;">
        <span>{home_team}</span>
        <img src="https://flagcdn.com/w80/{code_home}.png" alt="{home_team}" style="height: 28px; width: auto; border-radius: 4px; border: 1px solid rgba(255,255,255,0.15); flex-shrink: 0;">
      </div>
      <div style="display:flex; flex-direction:column; align-items:center; flex-shrink: 0;">
        <div class="score-box">{display_score}</div>
        {score_label}
      </div>
      <div class="score-team" style="display: flex; align-items: center; gap: 12px; justify-content: flex-start; flex: 1;">
        <img src="https://flagcdn.com/w80/{code_away}.png" alt="{away_team}" style="height: 28px; width: auto; border-radius: 4px; border: 1px solid rgba(255,255,255,0.15); flex-shrink: 0;">
        <span>{away_team}</span>
      </div>
    </div>
  </div>
</section>

<div class="container">
  <div class="match-container">
    {body_html}
    
    {visuals_html}
  </div>
</div>

<footer>
  <div class="container">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="data">Data</span><span class="hack">Hacks</span>
        <div style="font-size:0.72rem;color:var(--muted);font-weight:400;letter-spacing:1px;text-transform:uppercase;margin-top:4px">Sports Data Analytics // Football Metrics</div>
        <div style="font-size:0.78rem;margin-top:10px;color:rgba(255,255,255,0.7);font-family:var(--font-body);"><span style="color:var(--cyan);font-weight:600">Contacto:</span> <a href="mailto:data.hacks.sports@gmail.com" style="transition:color 0.2s;text-decoration:none;color:#fff;border-bottom:1px dashed rgba(0,212,255,0.4);padding-bottom:1px" onmouseover="this.style.borderColor='var(--cyan)'; this.style.color='var(--cyan)';" onmouseout="this.style.borderColor='rgba(0,212,255,0.4)'; this.style.color='#fff';">data.hacks.sports@gmail.com</a></div>
      </div>
      <div class="footer-links">
        <a href="../index.html#plataforma">Plataforma</a>
        <a href="../index.html#mundial2026">Mundial</a>
        <a href="../index.html#contenido">Contenido</a>
      </div>
      <div class="footer-domains">
        Mundial 2026 · Analizado por <span>DataHacks IA</span>
      </div>
    </div>
  </div>
</footer>

</body>
</html>
"""

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            body = parts[2]
            
            metadata = {}
            for line in frontmatter_text.strip().split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    metadata[k.strip()] = v.strip().strip('"').strip("'")
            return metadata, body
    return {}, content

def parse_bold(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

def md_to_html(md_text):
    html = []
    in_list = False
    
    for line in md_text.split('\n'):
        line = line.strip()
        
        if not line:
            if in_list:
                html.append('</ul>')
                in_list = False
            continue
            
        if line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html.append('<ul>')
                in_list = True
            content = parse_bold(line[2:])
            html.append(f'<li>{content}</li>')
            continue
        elif re.match(r'^\d+\.\s', line):
            if in_list:
                html.append('</ul>')
                in_list = False
            match = re.match(r'^(\d+)\.\s(.*)', line)
            content = parse_bold(match.group(2))
            html.append(f'<p><strong>{match.group(1)}.</strong> {content}</p>')
            continue
        else:
            if in_list:
                html.append('</ul>')
                in_list = False

        if line.startswith('### '):
            html.append(f'<h3>{parse_bold(line[4:])}</h3>')
        elif line.startswith('## '):
            html.append(f'<h2>{parse_bold(line[3:])}</h2>')
        elif line.startswith('# '):
            html.append(f'<h1>{parse_bold(line[2:])}</h1>')
        elif line == '---':
            html.append('<hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 24px 0;">')
        else:
            html.append(f'<p>{parse_bold(line)}</p>')
            
    if in_list:
        html.append('</ul>')
        
    return '\n'.join(html)

def get_mini_pitch_svg(team_name, color_theme):
    if team_name == "México":
        nodes = [(48, 25), (28, 30), (42, 65), (60, 42), (45, 48)]
        links = [(1, 0), (0, 3), (3, 2), (2, 1), (1, 4), (0, 4), (2, 4), (3, 4)]
    elif team_name == "Sudáfrica":
        nodes = [(72, 25), (55, 40), (88, 35), (78, 62), (70, 48), (82, 28), (60, 50)]
        links = [(0, 5), (5, 2), (2, 3), (3, 4), (4, 1), (1, 6), (6, 3), (1, 0), (2, 4)]
    elif team_name == "Rep. Checa":
        nodes = [(50, 20), (30, 25), (35, 55), (55, 60), (45, 40)]
        links = [(1, 0), (0, 4), (1, 4), (2, 4), (3, 4), (2, 3), (1, 2), (0, 3)]
    elif team_name == "Corea del Sur":
        nodes = [(70, 20), (90, 25), (85, 55), (65, 60), (75, 40)]
        links = [(0, 1), (1, 4), (0, 4), (2, 4), (3, 4), (2, 3), (1, 2), (0, 3)]
    else:
        if color_theme == 'cyan':
            nodes = [(45, 25), (30, 35), (40, 55), (55, 45), (42, 40)]
            links = [(1, 0), (0, 3), (3, 2), (2, 1), (4, 0), (4, 1), (4, 2), (4, 3)]
        else:
            nodes = [(75, 25), (90, 35), (80, 55), (65, 45), (78, 40)]
            links = [(1, 0), (0, 3), (3, 2), (2, 1), (4, 0), (4, 1), (4, 2), (4, 3)]
            
    line_color = "rgba(255, 255, 255, 0.12)"
    node_color = "#00f0ff" if color_theme == "cyan" else "#00ff66"
    glow_filter_id = f"glow-{color_theme}-{team_name.lower().replace(' ', '_').replace('.', '')}"
    
    svg = f"""<svg viewBox="0 0 120 80" class="mini-pitch-svg" style="width: 100px; height: 75px; opacity: 0.85;">
      <defs>
        <filter id="{glow_filter_id}" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="1.5" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <!-- Pitch outline -->
      <rect x="2" y="2" width="116" height="76" rx="4" fill="none" stroke="{line_color}" stroke-width="0.8"/>
      <!-- Midfield line -->
      <line x1="60" y1="2" x2="60" y2="78" stroke="{line_color}" stroke-width="0.8"/>
      <!-- Center circle -->
      <circle cx="60" cy="40" r="14" fill="none" stroke="{line_color}" stroke-width="0.8"/>
      <!-- Penalty Area Left -->
      <rect x="2" y="18" width="18" height="44" fill="none" stroke="{line_color}" stroke-width="0.8"/>
      <!-- Penalty Area Right -->
      <rect x="100" y="18" width="18" height="44" fill="none" stroke="{line_color}" stroke-width="0.8"/>
      <!-- Goal Area Left -->
      <rect x="2" y="28" width="6" height="24" fill="none" stroke="{line_color}" stroke-width="0.8"/>
      <!-- Goal Area Right -->
      <rect x="112" y="28" width="6" height="24" fill="none" stroke="{line_color}" stroke-width="0.8"/>
      
      <!-- Links (Passing Lines) -->
    """
    for l in links:
        n1 = nodes[l[0]]
        n2 = nodes[l[1]]
        svg += f'  <line x1="{n1[0]}" y1="{n1[1]}" x2="{n2[0]}" y2="{n2[1]}" stroke="{node_color}" stroke-opacity="0.45" stroke-width="0.7"/>\n'
        
    for n in nodes:
        svg += f'  <circle cx="{n[0]}" cy="{n[1]}" r="2.5" fill="{node_color}" filter="url(#{glow_filter_id})"/>\n'
        
    svg += "</svg>"
    return svg

def build_all_pages():
    print("Iniciando compilación de crónicas...")
    os.makedirs(ANALISIS_DIR, exist_ok=True)
    
    all_compiled_matches = []
    
    if not os.path.exists(DATA_DIR):
        print(f"Directorio de datos {DATA_DIR} no existe.")
        return False
        
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.md'):
            file_path = os.path.join(DATA_DIR, filename)
            meta, body = parse_markdown_file(file_path)
            
            if not meta:
                print(f"Ignorando {filename}: Falta frontmatter.")
                continue
                
            slug = meta.get('slug', meta.get('id', filename.replace('.md', '')))
            grupo = meta.get('grupo', 'Grupo A')
            home_team = meta.get('home_team', '')
            away_team = meta.get('away_team', '')
            fecha = meta.get('fecha', '')
            hora = meta.get('hora', '')
            goles_home = meta.get('goles_home', '0')
            goles_away = meta.get('goles_away', '0')
            pronostico_val = meta.get('pronostico', '0 - 0')
            is_finished = meta.get('finalizado', 'false').lower() == 'true'
            
            body_html = md_to_html(body)
            
            # Reubicar clasificación de predicción en el análisis posterior (dentro del cuerpo)
            if is_finished:
                pred_status = "miss"
                try:
                    p_clean = pronostico_val.replace(' ', '')
                    r_clean = f"{goles_home}-{goles_away}".replace(' ', '')
                    if p_clean == r_clean:
                        pred_status = "exact"
                    else:
                        p_parts = p_clean.split('-')
                        r_parts = r_clean.split('-')
                        if len(p_parts) == 2 and len(r_parts) == 2:
                            p_home, p_away = int(p_parts[0]), int(p_parts[1])
                            r_home, r_away = int(r_parts[0]), int(r_parts[1])
                            p_diff = p_home - p_away
                            r_diff = r_home - r_away
                            if (p_diff > 0 and r_diff > 0) or (p_diff < 0 and r_diff < 0) or (p_diff == 0 and r_diff == 0):
                                pred_status = "tendency"
                except Exception:
                    pass
                
                if pred_status == "exact":
                    label = "🎯 PREDICCIÓN EXACTA"
                    color = "#00e676"
                    bg = "rgba(0, 230, 118, 0.1)"
                    border = "rgba(0, 230, 118, 0.25)"
                elif pred_status == "tendency":
                    label = "🔮 GANADOR ACERTADO"
                    color = "#ffb300"
                    bg = "rgba(255, 179, 0, 0.1)"
                    border = "rgba(255, 179, 0, 0.25)"
                else:
                    label = "❌ PREDICCIÓN FALLIDA"
                    color = "#ff4b4b"
                    bg = "rgba(255, 75, 75, 0.1)"
                    border = "rgba(255, 75, 75, 0.25)"
                
                prediction_result_html = f"""
                <div style="margin: 16px 0; padding: 12px 16px; border-radius: 8px; background: {bg}; border: 1px solid {border}; display: inline-flex; align-items: center; gap: 8px; color: {color}; font-family: var(--font-head); font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;">
                  {label}
                </div>
                """
                
                # Inyectar inmediatamente después del encabezado de análisis posterior
                heading_pattern = r'(<h2>📝 Crónica y Análisis Posterior \(Post-Partido\)</h2>)'
                if re.search(heading_pattern, body_html):
                    body_html = re.sub(heading_pattern, r'\1\n' + prediction_result_html, body_html)
                else:
                    body_html = re.sub(r'(<h2>.*?Crónica.*?</h2>)', r'\1\n' + prediction_result_html, body_html)
            
            # Determinar qué marcador mostrar (Real o Proyectado)
            if is_finished:
                display_score = f"{goles_home} - {goles_away}"
                score_label = '<div style="font-size:0.75rem; color:rgba(255,255,255,0.4); margin-top:5px; font-weight:700;">FINALIZADO</div>'
            else:
                display_score = pronostico_val
                score_label = '<div style="font-size:0.75rem; color:var(--cyan); margin-top:5px; font-weight:700;">PRONÓSTICO IA</div>'
            
            # Incorporación dinámica de imágenes tácticas de forma escalable
            images_list = []
            if 'imagenes' in meta and meta['imagenes'].strip():
                img_items = meta['imagenes'].split(',')
                for item in img_items:
                    if ':' in item:
                        filename, caption = item.split(':', 1)
                        images_list.append((filename.strip(), caption.strip()))
            
            visuals_html = ""
            if images_list:
                def get_clean_key(filename):
                    name = filename.lower()
                    if 'defensivo' in name:
                        return 'mapadefensivo'
                    if 'expectedthreatxt' in name or 'xt' in name:
                        return 'xt'
                    if 'calor' in name:
                        return 'calor'
                    if 'shotmap' in name or 'tiro' in name:
                        return 'shotmap'
                    if 'reddepases' in name or 'pases' in name:
                        return 'pases'
                    if 'conducciones' in name:
                        return 'conducciones'
                    if 'asistencias' in name:
                        return 'asistencias'
                    return name.strip()

                # Agrupar en parejas
                grouped_visuals = []
                used_indices = set()
                for i in range(len(images_list)):
                    if i in used_indices:
                        continue
                    filename_i, caption_i = images_list[i]
                    key_i = get_clean_key(filename_i)
                    
                    paired = False
                    for j in range(i + 1, len(images_list)):
                        if j in used_indices:
                            continue
                        filename_j, caption_j = images_list[j]
                        key_j = get_clean_key(filename_j)
                        
                        if key_i == key_j:
                            grouped_visuals.append(('pair', (filename_i, caption_i), (filename_j, caption_j)))
                            used_indices.add(i)
                            used_indices.add(j)
                            paired = True
                            break
                    
                    if not paired:
                        grouped_visuals.append(('single', (filename_i, caption_i)))
                        used_indices.add(i)

                visual_blocks = []
                for item in grouped_visuals:
                    if item[0] == 'pair':
                        img1, cap1 = item[1]
                        img2, cap2 = item[2]
                        img_file_clean_1 = img1.replace('.jpg', '.png')
                        img_file_clean_2 = img2.replace('.jpg', '.png')
                        block = f"""
                  <div class="tactical-pair" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; width: 100%; margin-bottom: 24px;">
                    <div style="background: rgba(15, 12, 32, 0.35); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                      <h4 style="color: var(--cyan); font-size: 0.85rem; margin: 0 0 12px; font-family: var(--font-head); font-weight: 700;">{cap1}</h4>
                      <img src="../assets/{img_file_clean_1}" alt="{cap1}" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                    </div>
                    <div style="background: rgba(15, 12, 32, 0.35); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                      <h4 style="color: var(--cyan); font-size: 0.85rem; margin: 0 0 12px; font-family: var(--font-head); font-weight: 700;">{cap2}</h4>
                      <img src="../assets/{img_file_clean_2}" alt="{cap2}" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                    </div>
                  </div>
"""
                        visual_blocks.append(block)
                    else:
                        img, cap = item[1]
                        img_file_clean = img.replace('.jpg', '.png')
                        block = f"""
                  <div class="tactical-single" style="width: 100%; max-width: 500px; margin: 0 auto 24px; background: rgba(15, 12, 32, 0.35); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                    <h4 style="color: var(--cyan); font-size: 0.85rem; margin: 0 0 12px; font-family: var(--font-head); font-weight: 700;">{cap}</h4>
                    <img src="../assets/{img_file_clean}" alt="{cap}" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                  </div>
"""
                        visual_blocks.append(block)

                visuals_html = f"""
                <div class="tactical-visuals" style="margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 30px; width: 100%;">
                  <h3 style="font-family: var(--font-head); color: var(--green); text-align: center; margin-bottom: 25px;">📊 Pizarras y Gráficos Tácticos</h3>
                  <div style="width: 100%;">
                    {"".join(visual_blocks)}
                  </div>
                </div>
                """
            
            grupo_page = GROUP_PAGES.get(grupo, "grupo_a.html")
            code_home = FLAGS_MAP.get(home_team, 'un')
            code_away = FLAGS_MAP.get(away_team, 'un')
            
            match_html = TEMPLATE_HTML.format(
                titulo=meta.get('titulo', f"{home_team} vs {away_team}"),
                home_team=home_team,
                away_team=away_team,
                code_home=code_home,
                code_away=code_away,
                grupo=grupo,
                grupo_page=grupo_page,
                fecha=fecha,
                hora=hora,
                display_score=display_score,
                score_label=score_label,
                body_html=body_html,
                visuals_html=visuals_html
            )
            
            output_file = os.path.join(ANALISIS_DIR, f"{slug}.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(match_html)
            print(f"Generada crónica: website/analisis/{slug}.html")
            
            match_data = {
                "slug": slug,
                "home": home_team,
                "away": away_team,
                "fecha": fecha,
                "hora": hora,
                "titulo": meta.get('titulo', ''),
                "link": f"analisis/{slug}.html",
                "display_score": display_score,
                "pronostico": pronostico_val,
                "is_finished": is_finished,
                "grupo": grupo,
                "poisson": meta.get('poisson', '58-26-16')
            }
            
            all_compiled_matches.append(match_data)
            
    # --- CALCULAR STANDINGS DE LOS GRUPOS ---
    standings = {}
    grupos_path = os.path.join(BASE_DIR, 'data', 'grupos.json')
    if os.path.exists(grupos_path):
        try:
            import json
            with open(grupos_path, 'r', encoding='utf-8') as f:
                grupos_dict = json.load(f)
            for grupo, teams in grupos_dict.items():
                standings[grupo] = {}
                for team_name in teams.keys():
                    standings[grupo][team_name] = {
                        "PJ": 0, "G": 0, "E": 0, "P": 0,
                        "GF": 0, "GC": 0, "DG": 0, "Pts": 0
                    }
            for m in all_compiled_matches:
                if m['is_finished']:
                    grupo = m['grupo']
                    home = m['home']
                    away = m['away']
                    if grupo in standings and home in standings[grupo] and away in standings[grupo]:
                        score_str = m['display_score']
                        if '-' in score_str:
                            parts = score_str.split('-')
                            if len(parts) == 2:
                                try:
                                    gh = int(parts[0].strip())
                                    ga = int(parts[1].strip())
                                    h_stats = standings[grupo][home]
                                    a_stats = standings[grupo][away]
                                    h_stats["PJ"] += 1
                                    a_stats["PJ"] += 1
                                    h_stats["GF"] += gh
                                    h_stats["GC"] += ga
                                    a_stats["GF"] += ga
                                    a_stats["GC"] += gh
                                    h_stats["DG"] = h_stats["GF"] - h_stats["GC"]
                                    a_stats["DG"] = a_stats["GF"] - a_stats["GC"]
                                    if gh > ga:
                                        h_stats["G"] += 1
                                        h_stats["Pts"] += 3
                                        a_stats["P"] += 1
                                    elif ga > gh:
                                        a_stats["G"] += 1
                                        a_stats["Pts"] += 3
                                        h_stats["P"] += 1
                                    else:
                                        h_stats["E"] += 1
                                        h_stats["Pts"] += 1
                                        a_stats["E"] += 1
                                        a_stats["Pts"] += 1
                                except ValueError:
                                    pass
        except Exception as e:
            print(f"Error al calcular standings: {e}")

    # --- ACTUALIZACIÓN DE LA HOME PAGE (index.html) ---
    index_path = os.path.join(WEBSITE_DIR, 'index.html')
    if os.path.exists(index_path) and all_compiled_matches:
        # Agrupar por fecha y seleccionar la fecha más reciente que tenga partidos
        by_date = {}
        for m in all_compiled_matches:
            d = m['fecha']
            if d not in by_date: by_date[d] = []
            by_date[d].append(m)
            
        latest_date = sorted(by_date.keys(), reverse=True)[0]
        # Filtrar para mostrar solo partidos NO finalizados en el Live Match Center
        active_today_matches = [m for m in by_date[latest_date] if not m['is_finished']]
        today_matches = sorted(active_today_matches, key=lambda x: x['hora'])
        
        # Generar Tarjetas HTML
        cards_list = []
        for idx, m in enumerate(today_matches):
            # Obtener códigos de bandera FlagCDN
            code_home = FLAGS_MAP.get(m['home'], 'un')
            code_away = FLAGS_MAP.get(m['away'], 'un')
            
            # Porcentajes del modelo Poisson
            poisson_str = m.get('poisson', '58-26-16')
            try:
                parts_p = poisson_str.split('-')
                prob_home = int(parts_p[0].strip())
                prob_draw = int(parts_p[1].strip())
                prob_away = int(parts_p[2].strip())
            except:
                prob_home, prob_draw, prob_away = 58, 26, 16
            
            # Decidir si lleva la etiqueta superior "DOSSIER TÁCTICO"
            badge_html = ""
            if idx == 0:
                badge_html = '<div class="match-widget-badge-top">DOSSIER TÁCTICO</div>'
                
            # Separar goles de goles proyectados/reales
            score_home = "0"
            score_away = "0"
            if '-' in m['display_score']:
                score_parts = m['display_score'].split('-')
                if len(score_parts) == 2:
                    score_home = score_parts[0].strip()
                    score_away = score_parts[1].strip()
            
            # Generar mini pitches
            pitch_svg_home = get_mini_pitch_svg(m['home'], 'cyan')
            pitch_svg_away = get_mini_pitch_svg(m['away'], 'green')
            
            card_html = f"""
      <div id="widget-{m['slug']}" class="match-widget-card">
        {badge_html}
        
        <div class="match-widget-header-row">
          <div class="team-block local">
            <span class="team-name">{m['home']}</span>
            <img src="https://flagcdn.com/w80/{code_home}.png" alt="{m['home']}" class="team-flag">
          </div>
          
          <div class="digital-scoreboard">
            <div class="score-box local">{score_home}</div>
            <div class="score-divider">-</div>
            <div class="score-box visitor">{score_away}</div>
          </div>
          
          <div class="team-block visitor">
            <img src="https://flagcdn.com/w80/{code_away}.png" alt="{m['away']}" class="team-flag">
            <span class="team-name">{m['away']}</span>
          </div>
        </div>
        
        <div class="match-middle-row">
          <div class="tactical-field local">
            {pitch_svg_home}
          </div>
          
          <div class="poisson-section">
            <div class="poisson-title">Poisson probabilities</div>
            <div class="poisson-bar">
              <div class="bar-segment local" style="width: {prob_home}%" title="{m['home']}: {prob_home}%"></div>
              <div class="bar-segment draw" style="width: {prob_draw}%" title="Empate: {prob_draw}%"></div>
              <div class="bar-segment visitor" style="width: {prob_away}%" title="{m['away']}: {prob_away}%"></div>
            </div>
            <div class="poisson-labels">
              <span class="label-local">{prob_home}%</span>
              <span class="label-draw">Draw {prob_draw}%</span>
              <span class="label-visitor">{prob_away}%</span>
            </div>
          </div>
          
          <div class="tactical-field visitor">
            {pitch_svg_away}
          </div>
        </div>
        
        <div class="match-widget-footer" style="display: flex; justify-content: flex-end; width: 100%; margin-top: 5px;">
          <a href="{m['link']}" class="btn-glow-cyan">Ver Análisis Táctico</a>
        </div>
      </div>
"""
            cards_list.append(card_html)
            
        cards_html = "\n        ".join(cards_list)
        
        # Generar Tarjetas de Historial HTML
        history_cards = []
        finished_matches = [m for m in all_compiled_matches if m['is_finished']]
        sorted_matches = sorted(finished_matches, key=lambda x: (x['fecha'], x['hora']), reverse=True)
        
        for m in sorted_matches:
            code_home = FLAGS_MAP.get(m['home'], 'un')
            code_away = FLAGS_MAP.get(m['away'], 'un')
            real_score = m['display_score']
            pronostico = m['pronostico']
            
            # Mostrar marcador predicho y real de forma sencilla sin cruces ni badges
            score_display_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; gap: 2px;">
              <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4);" title="Pronóstico del partido">
                Predicho: {pronostico}
              </div>
              <div style="background: rgba(255, 255, 255, 0.04); padding: 3px 8px; border-radius: 6px; color: var(--cyan); font-size: 0.95rem; font-weight: 900; border: 1px solid rgba(255,255,255,0.06);" title="Resultado Real">
                {real_score}
              </div>
            </div>
            """
            prediction_badge = ""
            
            card_hist_html = f"""
      <div class="history-card" style="background: rgba(15, 12, 32, 0.25); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 12px; transition: all 0.3s; height: 100%;" onmouseover="this.style.borderColor='var(--cyan)'; this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.06)'; this.style.transform='translateY(0)'">
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: var(--muted);">
          <span class="badge" style="background: rgba(0, 240, 255, 0.08); color: var(--cyan); border: none; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;">{m['grupo']}</span>
          <span>📅 {m['fecha']}</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; font-family: var(--font-head); font-weight: 700; color: #fff;">
          <div style="display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0;">
            <img src="https://flagcdn.com/w40/{code_home}.png" alt="{m['home']}" style="width: 20px; height: auto; border-radius: 2px;">
            <span style="font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{m['home']}</span>
          </div>
          {score_display_html}
          <div style="display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0; justify-content: flex-end;">
            <span style="font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: right;">{m['away']}</span>
            <img src="https://flagcdn.com/w40/{code_away}.png" alt="{m['away']}" style="width: 20px; height: auto; border-radius: 2px;">
          </div>
        </div>
        <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; gap: 8px;">
          {prediction_badge}
          <a href="{m['link']}" style="color: var(--cyan); text-decoration: none; font-size: 0.8rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; transition: color 0.2s;" onmouseover="this.style.color='var(--white)'" onmouseout="this.style.color='var(--cyan)'">Ver Análisis →</a>
        </div>
      </div>
"""
            history_cards.append(card_hist_html)
            
        history_html = "\n        ".join(history_cards)
        
        # Generar Widget de Standings Dinámico para la Home Page
        standings_widget_html = ""
        if standings:
            widget_html_parts = []
            widget_html_parts.append("""
<style>
  .standings-section {
    margin: 40px 0;
    padding: 24px;
    background: rgba(15, 12, 32, 0.45);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
  }
  .standings-tabs-container {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 12px;
  }
  .standings-tab-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.6);
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-family: var(--font-head);
    font-size: 0.85rem;
    font-weight: 700;
    transition: all 0.2s ease;
  }
  .standings-tab-btn:hover {
    background: rgba(0, 149, 255, 0.1);
    border-color: rgba(0, 149, 255, 0.3);
    color: var(--cyan);
  }
  .standings-tab-btn.active {
    background: rgba(0, 149, 255, 0.2);
    border-color: var(--cyan);
    color: #fff;
    box-shadow: 0 0 10px rgba(0, 149, 255, 0.25);
  }
  .standings-tab-content {
    display: none;
    animation: fadeInStandings 0.4s ease;
  }
  @keyframes fadeInStandings {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>

<div class="standings-section">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
    <h3 style="font-family: var(--font-head); font-size: 1.3rem; color: #fff; margin: 0; display: flex; align-items: center; gap: 8px;">
      🏆 Tabla de Posiciones Mundial 2026
    </h3>
    <span class="badge" style="background: rgba(0, 240, 255, 0.08); color: var(--cyan); border: none; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">
      Simulación Local (Resultados Oficiales)
    </span>
  </div>
  
  <div class="standings-tabs-container">""")

            group_keys = sorted(standings.keys())
            for idx, g in enumerate(group_keys):
                active_class = " active" if idx == 0 else ""
                tab_id = f"std-tab-{g.lower().replace(' ', '-')}"
                widget_html_parts.append(f'    <button class="standings-tab-btn{active_class}" onclick="switchStandingsTab(event, \'{tab_id}\')">{g}</button>')
                
            widget_html_parts.append('  </div>')

            for idx, g in enumerate(group_keys):
                display_style = "display: block;" if idx == 0 else "display: none;"
                tab_id = f"std-tab-{g.lower().replace(' ', '-')}"
                
                sorted_teams = sorted(
                    standings[g].items(),
                    key=lambda x: (x[1]['Pts'], x[1]['DG'], x[1]['GF'], x[0]),
                    reverse=True
                )
                
                rows_list = []
                for pos, (team_name, stats) in enumerate(sorted_teams, 1):
                    flag_code = FLAGS_MAP.get(team_name, 'un')
                    row_html = f"""
          <tr style="text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td style="text-align: center; font-weight: bold; padding: 12px 8px; width: 50px;">{pos}</td>
            <td style="text-align: left; padding: 12px 8px; display: flex; align-items: center; gap: 8px;">
              <img src="https://flagcdn.com/w40/{flag_code}.png" alt="{team_name}" style="width: 20px; height: auto; border-radius: 2px;">
              <span style="font-weight: 600;">{team_name}</span>
            </td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['PJ']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['G']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['E']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['P']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['GF']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['GC']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 50px;">{stats['DG']}</td>
            <td style="text-align: center; padding: 12px 8px; width: 70px; font-weight: 900; color: var(--cyan);">{stats['Pts']}</td>
          </tr>"""
                    rows_list.append(row_html)
                    
                rows_html = "".join(rows_list)
                
                widget_html_parts.append(f"""
  <div id="{tab_id}" class="standings-tab-content" style="{display_style}">
    <div style="overflow-x: auto; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 10px;">
      <table style="width: 100%; border-collapse: collapse; font-family: var(--font-body); color: #fff; font-size: 0.9rem;">
        <thead>
          <tr style="border-bottom: 2px solid var(--border);">
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">Pos</th>
            <th style="text-align: left; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">Equipo</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">PJ</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">G</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">E</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">P</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">GF</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">GC</th>
            <th style="width: 50px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">DG</th>
            <th style="width: 70px; text-align: center; padding: 12px 8px; color: var(--cyan); font-family: var(--font-head); font-weight: 900;">Pts</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
  </div>""")
                
            widget_html_parts.append("""
</div>

<script>
function switchStandingsTab(evt, tabId) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("standings-tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("standings-tab-btn");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }
  document.getElementById(tabId).style.display = "block";
  evt.currentTarget.classList.add("active");
}
</script>""")
            standings_widget_html = "".join(widget_html_parts)
            
        # Inyectar en index.html
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
            
        # Remplazar tarjetas del Live Match Center
        pattern_cards = r'(<!-- ANALISIS_CARDS_START -->)(.*?)(<!-- ANALISIS_CARDS_END -->)'
        replacement_cards = f'\\1\n        {cards_html}\n        \\3'
        index_content = re.sub(pattern_cards, replacement_cards, index_content, flags=re.DOTALL)
        
        # Remplazar tarjetas de Historial
        pattern_history = r'(<!-- HISTORIAL_CARDS_START -->)(.*?)(<!-- HISTORIAL_CARDS_END -->)'
        replacement_history = f'\\1\n        {history_html}\n        \\3'
        index_content = re.sub(pattern_history, replacement_history, index_content, flags=re.DOTALL)
        
        # Remplazar el widget de Standings
        if standings_widget_html:
            pattern_standings = r'(<!-- STANDINGS_WIDGET_START -->)(.*?)(<!-- STANDINGS_WIDGET_END -->)'
            replacement_standings = f'\\1\n        {standings_widget_html}\n        \\3'
            index_content = re.sub(pattern_standings, replacement_standings, index_content, flags=re.DOTALL)
            
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"Actualizado index.html: Live Match Center ({len(today_matches)} partidos), Historial ({len(sorted_matches)} partidos) y Tabla de Posiciones")
        
    # --- ACTUALIZACIÓN DE LAS TABLAS DE POSICIONES DE LOS GRUPOS (grupo_a.html a grupo_l.html) ---
    if standings:
        try:
            # Para cada grupo, ordenar standings, generar HTML e inyectar en el respectivo archivo
            for grupo, table_data in standings.items():
                grupo_file_name = GROUP_PAGES.get(grupo)
                if not grupo_file_name:
                    continue
                
                grupo_file_path = os.path.join(WEBSITE_DIR, grupo_file_name)
                if os.path.exists(grupo_file_path):
                    with open(grupo_file_path, 'r', encoding='utf-8') as f:
                        grupo_html_content = f.read()
                    
                    # Ordenar equipos: Pts -> DG -> GF -> Nombre
                    sorted_teams = sorted(
                        table_data.items(),
                        key=lambda x: (x[1]['Pts'], x[1]['DG'], x[1]['GF'], x[0]),
                        reverse=True
                    )
                    
                    # Generar filas de la tabla
                    rows_list = []
                    for pos, (team_name, stats) in enumerate(sorted_teams, 1):
                        flag_code = FLAGS_MAP.get(team_name, 'un')
                        row_html = f"""
          <tr style="text-align: center;">
            <td style="text-align: center; font-weight: bold; width: 60px;">{pos}</td>
            <td style="text-align: left; display: flex; align-items: center; gap: 8px;">
              <img src="https://flagcdn.com/w40/{flag_code}.png" alt="{team_name}" style="width: 20px; height: auto; border-radius: 2px;">
              <span>{team_name}</span>
            </td>
            <td style="text-align: center; width: 60px;">{stats['PJ']}</td>
            <td style="text-align: center; width: 60px;">{stats['G']}</td>
            <td style="text-align: center; width: 60px;">{stats['E']}</td>
            <td style="text-align: center; width: 60px;">{stats['P']}</td>
            <td style="text-align: center; width: 60px;">{stats['GF']}</td>
            <td style="text-align: center; width: 60px;">{stats['GC']}</td>
            <td style="text-align: center; width: 60px;">{stats['DG']}</td>
            <td style="text-align: center; width: 80px; font-weight: 900; color: var(--cyan);">{stats['Pts']}</td>
          </tr>"""
                        rows_list.append(row_html)
                    
                    rows_html = "".join(rows_list)
                    
                    # Generar bloque de standings
                    placeholder_start = "<!-- STANDINGS_START -->"
                    placeholder_end = "<!-- STANDINGS_END -->"
                    
                    standings_html_block = f"""<!-- STANDINGS_START -->
  <div class="container" style="margin-bottom: 40px;">
    <h3 style="font-family: var(--font-head); color: var(--white); margin-bottom: 20px; font-size: 1.5rem; text-align: left;">🏆 Tabla de Posiciones</h3>
    <div class="comparison-container" style="padding: 20px; margin-bottom: 0px; border-radius: 12px; background: var(--bg-card); border: 1px solid var(--border); box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow-x: auto;">
      <table class="comp-table" style="width: 100%; border-collapse: collapse; font-family: var(--font-body); color: #fff;">
        <thead>
          <tr style="border-bottom: 2px solid var(--border);">
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">Pos</th>
            <th style="text-align: left; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">Equipo</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">PJ</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">G</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">E</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">P</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">GF</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">GC</th>
            <th style="width: 60px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 700;">DG</th>
            <th style="width: 80px; text-align: center; padding: 14px 16px; color: var(--cyan); font-family: var(--font-head); font-weight: 900;">Pts</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
  </div>
  <!-- STANDINGS_END -->"""
                    
                    # Inyectar el bloque de standings
                    if placeholder_start in grupo_html_content:
                        pattern = re.escape(placeholder_start) + r".*?" + re.escape(placeholder_end)
                        grupo_html_content = re.sub(pattern, standings_html_block, grupo_html_content, flags=re.DOTALL)
                    else:
                        target = '<div class="tactical-grid">'
                        if target in grupo_html_content:
                            grupo_html_content = grupo_html_content.replace(target, standings_html_block + '\n\n  ' + target)
                    
                    with open(grupo_file_path, 'w', encoding='utf-8') as f:
                        f.write(grupo_html_content)
                    print(f"   [OK] Tabla de posiciones inyectada en: website/{grupo_file_name}")
        except Exception as e:
            print(f"Error al actualizar tablas de posiciones de los grupos: {e}")
            
    print("Compilación finalizada exitosamente.")
    return True

if __name__ == '__main__':
    build_all_pages()
