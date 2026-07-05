# -*- coding: utf-8 -*-
import os
import re
import matplotlib.pyplot as plt

DATA_DIR = r"d:\AntigravityPruebas\Mundial2026\data\analisis_partidos"
OUT_PATH = r"d:\AntigravityPruebas\Mundial2026\website\assets\evolucion_predicciones_dieciseisavos.png"

# 1. Cargar y ordenar cronológicamente los partidos finalizados de Dieciseisavos
matches = []
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".md"):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parsear metadatos rápidos
        meta = {}
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if m:
            for line in m.group(1).split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
                    
        is_finished = meta.get("finalizado", "false").lower() == "true"
        grupo = meta.get("grupo", "")
        
        if is_finished and grupo in ["Dieciseisavos", "Octavos"]:
            fecha = meta.get("fecha", "2026-06-28")
            home_team = meta.get("home_team", "")
            away_team = meta.get("away_team", "")
            g_home_raw = meta.get("goles_home", "0")
            g_away_raw = meta.get("goles_away", "0")
            pronostico = meta.get("pronostico", "0 - 0")
            
            # Limpiar penales del marcador
            g_home = re.sub(r'\(.*?\)', '', str(g_home_raw)).strip()
            g_away = re.sub(r'\(.*?\)', '', str(g_away_raw)).strip()
            
            matches.append({
                "fecha": fecha,
                "id": meta.get("id", filename),
                "g_home": int(g_home) if g_home.isdigit() else 0,
                "g_away": int(g_away) if g_away.isdigit() else 0,
                "pronostico": pronostico
            })

# Ordenar por fecha y luego por ID del partido
matches.sort(key=lambda x: (x["fecha"], x["id"]))

if not matches:
    print("No se encontraron partidos finalizados en Dieciseisavos.")
    exit(0)

# 2. Evaluar cada partido y acumular porcentajes
exact_history = []
tendency_history = []
miss_history = []

exact_count = 0
tendency_count = 0
miss_count = 0

for i, match in enumerate(matches, 1):
    p_clean = match["pronostico"].replace(' ', '')
    r_clean = f"{match['g_home']}-{match['g_away']}".replace(' ', '')
    
    pred_status = "miss"
    if p_clean == r_clean:
        pred_status = "exact"
        exact_count += 1
    else:
        p_parts = p_clean.split('-')
        r_parts = r_clean.split('-')
        if len(p_parts) == 2 and len(r_parts) == 2:
            try:
                p_home, p_away = int(p_parts[0]), int(p_parts[1])
                r_home, r_away = int(r_parts[0]), int(r_parts[1])
                p_diff = p_home - p_away
                r_diff = r_home - r_away
                if (p_diff > 0 and r_diff > 0) or (p_diff < 0 and r_diff < 0) or (p_diff == 0 and r_diff == 0):
                    pred_status = "tendency"
                    tendency_count += 1
                else:
                    miss_count += 1
            except ValueError:
                miss_count += 1
        else:
            miss_count += 1
            
    # Calcular porcentajes acumulados
    exact_history.append((exact_count / i) * 100)
    tendency_history.append((tendency_count / i) * 100)
    miss_history.append((miss_count / i) * 100)

# 3. Dibujar el gráfico con estilo premium oscuro
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0f0c20')
ax.set_facecolor('#0f0c20')

x = range(1, len(matches) + 1)

# Dibujar las líneas
ax.plot(x, exact_history, color='#00e676', marker='o', markersize=4, linewidth=2.0, label='🎯 Predicción Exacta')
ax.plot(x, tendency_history, color='#ffb300', marker='o', markersize=4, linewidth=2.0, label='🔮 Ganador Acertado')
ax.plot(x, miss_history, color='#ff4b4b', marker='o', markersize=4, linewidth=2.0, label='❌ Predicción Fallida')

# Configurar ejes y títulos
ax.set_title('Evolución del Rendimiento del Algoritmo (Fase Eliminatoria)', color='white', fontsize=11, fontweight='bold', pad=15)
ax.set_xlabel('Partidos Jugados', color='#888888', fontsize=9)
ax.set_ylabel('Porcentaje Acumulado (%)', color='#888888', fontsize=9)

ax.set_xlim(0.8, len(matches) + 0.2)
ax.set_xticks(range(1, len(matches) + 1))
ax.set_ylim(-5, 105)
ax.grid(True, color='#26223d', linestyle=':', linewidth=0.5)

# Remover bordes innecesarios
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#26223d')
ax.spines['bottom'].set_color('#26223d')

# Leyenda
ax.legend(loc='lower left', framealpha=0.1, facecolor='#fff', edgecolor='#555', fontsize=8.5)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

print(f"Gráfico de evolución guardado en: {OUT_PATH}")
print(f"Total partidos analizados en Dieciseisavos: {len(matches)} (Exactas: {exact_count}, Tendencias: {tendency_count}, Fallidas: {miss_count})")
