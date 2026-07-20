# -*- coding: utf-8 -*-
"""
utils/visualization.py
Funciones de visualización: Shot Map, KDE Heatmap,
Pass Network, K-Means Clusters. Todas con manejo robusto de figuras.
"""
import io
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from mplsoccer import Pitch, VerticalPitch
from sklearn.cluster import KMeans

BG = '#0d1e35'


def fig_to_png_bytes(fig: plt.Figure) -> bytes:
    """Exporta una figura a bytes PNG de alta resolución."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.read()


def _crear_lienzo(formato: str, half: bool = False, pitch_color: str = BG, line_color: str = '#2a5fa5') -> tuple[Pitch, plt.Figure, plt.Axes]:
    """Crea el objeto Pitch y la figura Matplotlib ajustada al formato de red social."""
    if formato == "vertical":  # 9:16 TikTok / Reels
        pitch = VerticalPitch(
            pitch_type='statsbomb', half=half,
            pitch_color=pitch_color, line_color=line_color, goal_type='box', linewidth=1.8, pad_top=15
        )
        fig, ax = pitch.draw(figsize=(9, 16))
    elif formato == "cuadrado":  # 1:1 X / Instagram
        pitch = Pitch(
            pitch_type='statsbomb', half=half,
            pitch_color=pitch_color, line_color=line_color, goal_type='box', linewidth=1.5, pad_top=10
        )
        fig, ax = pitch.draw(figsize=(10, 10))
    else:  # horizontal (Estándar Web / 13:9)
        pitch = Pitch(
            pitch_type='statsbomb', half=half,
            pitch_color=pitch_color, line_color=line_color, goal_type='box', linewidth=1.5, pad_top=10
        )
        fig, ax = pitch.draw(figsize=(13, 9))
    
    fig.set_facecolor(pitch_color)
    return pitch, fig, ax


def generar_mapa(tiros: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """Mapa de tiros con xG visualizado por tamaño, optimizado para redes sociales."""
    goles    = tiros[tiros['shot_outcome'] == 'Goal']
    no_goles = tiros[tiros['shot_outcome'] != 'Goal']

    pitch, fig, ax = _crear_lienzo(formato, half=True)

    if not no_goles.empty:
        pitch.scatter(
            no_goles.x, no_goles.y,
            s=np.clip(no_goles.shot_statsbomb_xg * 1200, 60, 800),
            edgecolors='#5badff', c='#1e66c8', alpha=0.65, linewidth=1.2, zorder=3, ax=ax
        )

    if not goles.empty:
        pitch.scatter(
            goles.x, goles.y,
            s=np.clip(goles.shot_statsbomb_xg * 1500, 200, 1000),
            marker='*', edgecolors='#cc7700', c='#FFD700', linewidth=0.8, zorder=4, ax=ax
        )

    patch_no_gol = mpatches.Patch(color='#1e66c8', label=f'Disparo  · {len(no_goles)}')
    patch_gol    = mpatches.Patch(color='#FFD700', label=f'Gol ★  · {len(goles)}')
    
    # Ajustar leyendas según el formato
    if formato == "vertical":
        leg1 = ax.legend(handles=[patch_no_gol, patch_gol], loc='upper left', frameon=False,
                         fontsize=10, labelcolor='white', bbox_to_anchor=(0.01, -0.01))
        for xg_val in [0.05, 0.15, 0.35]:
            ax.scatter([], [], s=xg_val * 1200, facecolor='white', edgecolor='grey', alpha=0.5, label=f'xG ≈ {xg_val}')
        leg2 = ax.legend(loc='upper right', title='Tamaño = xG', title_fontsize=9, frameon=False,
                         fontsize=9, labelcolor='white', bbox_to_anchor=(0.99, -0.01))
    else:
        leg1 = ax.legend(handles=[patch_no_gol, patch_gol], loc='lower left', frameon=False,
                         fontsize=11, labelcolor='white', bbox_to_anchor=(0.01, 0.01))
        for xg_val in [0.05, 0.15, 0.35]:
            ax.scatter([], [], s=xg_val * 1200, facecolor='white', edgecolor='grey', alpha=0.5, label=f'xG ≈ {xg_val}')
        leg2 = ax.legend(loc='lower right', title='Tamaño = xG', title_fontsize=10, frameon=False,
                         fontsize=9, labelcolor='white', bbox_to_anchor=(0.99, 0.01))
        
    leg2.get_title().set_color('#aaaaaa')
    ax.add_artist(leg1)

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.02 if formato != "vertical" else 0.04

    fig.text(0.5, y_title, f'{bandera}  {pais}', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, torneo, ha='center', va='top', fontsize=12, color='#888888')
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    
    if formato == "vertical":
        plt.tight_layout(rect=[0, 0.08, 1, 0.92])
    else:
        plt.tight_layout(rect=[0, 0.05, 1, 0.93])
    return fig


def generar_mapa_calor(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """KDE Heatmap de densidad de acciones."""
    pitch, fig, ax = _crear_lienzo(formato, half=False)

    pitch.kdeplot(
        df_eventos['x'], df_eventos['y'], ax=ax,
        levels=50, fill=True, zorder=-1, cmap='hot', alpha=0.6
    )

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93

    fig.text(0.5, y_title, f'{bandera}  {pais} (Mapa de Calor)', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, torneo, ha='center', va='top', fontsize=12, color='#888888')
    
    if formato == "vertical":
        plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    else:
        plt.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def generar_mapa_pases(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """Red de pases del último partido."""
    match_ids = df_eventos['match_id'].unique()
    eventos = df_eventos[df_eventos['match_id'] == match_ids[-1]].copy() if len(match_ids) > 0 else df_eventos.copy()

    pases = eventos[(eventos['type'] == 'Pass') & (eventos['team'] == pais)].copy()
    pases_completados = pases[pases['pass_outcome'].isnull()].copy()
    pases_completados['pasador'] = pases_completados['player']
    pases_completados['receptor'] = pases_completados['pass_recipient']

    posiciones_promedio = pases_completados.groupby('pasador')[['x', 'y']].mean().reset_index()
    posiciones_promedio.rename(columns={'x': 'x_promedio', 'y': 'y_promedio'}, inplace=True)
    toques = pases_completados.groupby('pasador').size().reset_index(name='toques')
    posiciones_promedio = posiciones_promedio.merge(toques, on='pasador')

    conexiones = pases_completados.groupby(['pasador', 'receptor']).size().reset_index(name='pass_count')
    conexiones = conexiones[conexiones['pass_count'] > 3]
    conexiones = conexiones.merge(posiciones_promedio, on='pasador', how='left')
    conexiones = conexiones.merge(posiciones_promedio, left_on='receptor', right_on='pasador', suffixes=('', '_receptor'), how='left')

    pitch, fig, ax = _crear_lienzo(formato, half=False, line_color='#c7d5cc')

    if not conexiones.empty:
        pitch.arrows(conexiones['x_promedio'], conexiones['y_promedio'],
                     conexiones['x_promedio_receptor'], conexiones['y_promedio_receptor'],
                     lw=conexiones['pass_count'] * 0.4, color='#ad993c', zorder=1, ax=ax, alpha=0.7)

    if not posiciones_promedio.empty:
        pitch.scatter(posiciones_promedio['x_promedio'], posiciones_promedio['y_promedio'],
                      s=posiciones_promedio['toques'] * 20, color='#e74c3c', edgecolors='white', linewidth=2, alpha=1, ax=ax, zorder=2)
        for _, row in posiciones_promedio.iterrows():
            apellido = str(row['pasador']).split()[-1]
            offset_y = 2 if formato != "vertical" else 0
            offset_x = 0 if formato != "vertical" else -2
            pitch.annotate(apellido, xy=(row['x_promedio'] - offset_x, row['y_promedio'] - offset_y),
                           c='white', va='center', ha='center', size=10, weight='bold', ax=ax, zorder=3)

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93

    fig.text(0.5, y_title, f'{bandera}  {pais} (Red de Pases)', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} - Partido Más Reciente", ha='center', va='top', fontsize=12, color='#888888')
    
    if formato == "vertical":
        plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    else:
        plt.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def generar_mapa_clusters(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, player_name: str = None, formato: str = "horizontal") -> plt.Figure:
    """ADN Táctico via K-Means clustering de pases."""
    pases = df_eventos[(df_eventos['type'] == 'Pass') & (df_eventos['team'] == pais)].copy()
    if pases.empty:
        fig, ax = plt.subplots(figsize=(9, 16) if formato == "vertical" else (13, 9))
        ax.set_facecolor(BG)
        fig.set_facecolor(BG)
        fig.text(0.5, 0.5, "Sin pases registrados", color="white", ha="center", fontsize=20)
        return fig

    if player_name is None:
        player_name = pases['player'].value_counts().idxmax()

    pases_jugador = pases[pases['player'] == player_name].copy()
    pases_jugador = pases_jugador.dropna(subset=['location', 'pass_end_location'])

    if pases_jugador.empty:
        fig, ax = plt.subplots(figsize=(9, 16) if formato == "vertical" else (13, 9))
        ax.set_facecolor(BG)
        fig.set_facecolor(BG)
        fig.text(0.5, 0.5, f"Sin coordenadas para {player_name}", color="white", ha="center", fontsize=20)
        return fig

    x1, y1 = np.array(pases_jugador['location'].tolist()).T
    x2, y2 = np.array(pases_jugador['pass_end_location'].tolist()).T
    coords = np.vstack((x1, y1, x2, y2)).T

    n_clusters = min(30, len(coords))
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    model.fit(coords)

    pitch, fig, ax = _crear_lienzo(formato, half=False, line_color='#c7d5cc')

    centers = model.cluster_centers_
    for i, center in enumerate(centers):
        cluster_size = np.sum(model.labels_ == i)
        lw    = np.clip(cluster_size * 0.5, 1, 10)
        alpha = np.clip(cluster_size * 0.1 + 0.3, 0.4, 0.9)
        pitch.arrows(center[0], center[1], center[2], center[3],
                     width=lw, color='#FFD700', zorder=2, ax=ax, alpha=alpha, headwidth=5, headlength=5)
        pitch.scatter(center[0], center[1], color='#e74c3c', edgecolors='white', s=cluster_size * 20, zorder=3, ax=ax)

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.015 if formato != "vertical" else 0.03
    
    fig.text(0.5, y_title, f'{bandera} {pais} - ADN Táctico: {player_name}', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} | Patrones de Pases (K-Means)", ha='center', va='top', fontsize=12, color='#888888')
    
    # Posicionar leyenda de K-Means según el formato
    if formato == "vertical":
        fig.text(0.1, 0.09, "LEYENDA:", color='white', weight='bold', size=10)
        fig.text(0.1, 0.075, "• Flecha: Dirección promedio del patrón", color='#aaaaaa', size=9)
        fig.text(0.1, 0.06, "• Grosor: Volumen de pases en ese patrón", color='#aaaaaa', size=9)
        fig.text(0.1, 0.045, "• Punto Rojo: Punto de origen del pase", color='#aaaaaa', size=9)
        plt.tight_layout(rect=[0, 0.12, 1, 0.92])
    else:
        fig.text(0.1, 0.08, "LEYENDA:", color='white', weight='bold', size=10)
        fig.text(0.1, 0.055, "• Flecha: Dirección promedio del patrón", color='#aaaaaa', size=9)
        fig.text(0.35, 0.055, "• Grosor: Volumen de pases en ese patrón", color='#aaaaaa', size=9)
        fig.text(0.65, 0.055, "• Punto Rojo: Punto de origen del pase", color='#aaaaaa', size=9)
        plt.tight_layout(rect=[0, 0.1, 1, 0.93])
        
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    return fig


# ──────────────────────────────────────────────
# NUEVAS VISUALIZACIONES TÁCTICAS AVANZADAS
# ──────────────────────────────────────────────

XT_GRID = np.array([
    [0.00638303, 0.00779616, 0.00844854, 0.00977659, 0.01126267, 0.01248344, 0.01473596, 0.0174506, 0.02122129, 0.02756312, 0.03485072, 0.0379259],
    [0.00750072, 0.00878589, 0.00942382, 0.0105949,  0.01214719, 0.0138454,  0.01611813, 0.01870347, 0.02401521, 0.02953272, 0.04066992, 0.04647721],
    [0.0088799,  0.00977745, 0.01001304, 0.01110462, 0.01269174, 0.01429128, 0.01685596, 0.01935132, 0.0241224,  0.02855202, 0.05491138, 0.06442595],
    [0.00941056, 0.01082722, 0.01016549, 0.01132376, 0.01262646, 0.01484598, 0.01689528, 0.0199707,  0.02385149, 0.03511326, 0.10805102, 0.25745362],
    [0.00941056, 0.01082722, 0.01016549, 0.01132376, 0.01262646, 0.01484598, 0.01689528, 0.0199707,  0.02385149, 0.03511326, 0.10805102, 0.25745362],
    [0.0088799,  0.00977745, 0.01001304, 0.01110462, 0.01269174, 0.01429128, 0.01685596, 0.01935132, 0.0241224,  0.02855202, 0.05491138, 0.06442595],
    [0.00750072, 0.00878589, 0.00942382, 0.0105949,  0.01214719, 0.0138454,  0.01611813, 0.01870347, 0.02401521, 0.02953272, 0.04066992, 0.04647721],
    [0.00638303, 0.00779616, 0.00844854, 0.00977659, 0.01126267, 0.01248344, 0.01473596, 0.0174506,  0.02122129, 0.02756312, 0.03485072, 0.0379259]
])


def generar_mapa_xt(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """Generación de Amenaza (xT - Expected Threat) acumulada por zonas."""
    pases = df_eventos[(df_eventos['type'] == 'Pass') & (df_eventos['team'] == pais) & (df_eventos['pass_outcome'].isna())].copy()
    carries = df_eventos[(df_eventos['type'] == 'Carry') & (df_eventos['team'] == pais)].copy()
    
    pases = pases.dropna(subset=['location', 'pass_end_location'])
    carries = carries.dropna(subset=['location', 'carry_end_location'])
    
    if pases.empty and carries.empty:
        fig, ax = plt.subplots(figsize=(9, 16) if formato == "vertical" else (13, 9))
        ax.set_facecolor(BG)
        fig.set_facecolor(BG)
        fig.text(0.5, 0.5, "Sin pases/conducciones registrados", color="white", ha="center", fontsize=20)
        return fig
        
    p_x1 = pases['x'].values if not pases.empty else np.array([])
    p_y1 = pases['y'].values if not pases.empty else np.array([])
    p_x2 = np.array([loc[0] for loc in pases['pass_end_location']]) if not pases.empty else np.array([])
    p_y2 = np.array([loc[1] for loc in pases['pass_end_location']]) if not pases.empty else np.array([])
    
    c_x1 = carries['x'].values if not carries.empty else np.array([])
    c_y1 = carries['y'].values if not carries.empty else np.array([])
    c_x2 = np.array([loc[0] for loc in carries['carry_end_location']]) if not carries.empty else np.array([])
    c_y2 = np.array([loc[1] for loc in carries['carry_end_location']]) if not carries.empty else np.array([])
    
    all_x1 = np.concatenate([p_x1, c_x1])
    all_y1 = np.concatenate([p_y1, c_y1])
    all_x2 = np.concatenate([p_x2, c_x2])
    all_y2 = np.concatenate([p_y2, c_y2])
    
    xt_sum = np.zeros((8, 12))
    for x1, y1, x2, y2 in zip(all_x1, all_y1, all_x2, all_y2):
        c1 = int(np.clip(x1 / 10.0, 0, 11))
        r1 = int(np.clip(y1 / 10.0, 0, 7))
        c2 = int(np.clip(x2 / 10.0, 0, 11))
        r2 = int(np.clip(y2 / 10.0, 0, 7))
        val = XT_GRID[r2, c2] - XT_GRID[r1, c1]
        if val > 0:
            xt_sum[r1, c1] += val
            
    pitch, fig, ax = _crear_lienzo(formato, half=False)
    
    bin_statistic = {
        'statistic': xt_sum,
        'x_grid': np.linspace(0, 120, 13),
        'y_grid': np.linspace(0, 80, 9),
        'cx': np.linspace(5, 115, 12),
        'cy': np.linspace(5, 75, 8)
    }
    
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='inferno', edgecolors='#1e2b3c', alpha=0.85)
    
    # label_heatmap omitido: requiere bin_statistic en formato meshgrid 2D generado por pitch.bin_statistic()
                            
    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.02 if formato != "vertical" else 0.04
    
    fig.text(0.5, y_title, f'{bandera} {pais} (Amenaza Esperada - xT)', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} | Peligro Generado (Pases y Conducciones)", ha='center', va='top', fontsize=12, color='#888888')
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    
    cbar = plt.colorbar(heatmap, ax=ax, shrink=0.6, orientation='horizontal', pad=0.05)
    cbar.set_label('xT Acumulado', color='white', size=10)
    cbar.ax.xaxis.set_tick_params(color='white')
    cbar.ax.tick_params(labelcolor='white')
    
    if formato == "vertical":
        plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    else:
        plt.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def generar_mapa_sonar(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, player_name: str = None, formato: str = "horizontal") -> plt.Figure:
    """Sonar de Pases: Direcciones predominantes, precisión y volumen."""
    pases = df_eventos[(df_eventos['type'] == 'Pass') & (df_eventos['team'] == pais)].copy()
    if pases.empty:
        fig, ax = plt.subplots(figsize=(9, 16) if formato == "vertical" else (13, 9))
        ax.set_facecolor(BG)
        fig.set_facecolor(BG)
        fig.text(0.5, 0.5, "Sin pases registrados", color="white", ha="center", fontsize=20)
        return fig

    if player_name is None:
        player_name = pases['player'].value_counts().idxmax()

    pases_jugador = pases[pases['player'] == player_name].copy()
    pases_jugador = pases_jugador.dropna(subset=['location', 'pass_end_location'])

    if pases_jugador.empty:
        fig, ax = plt.subplots(figsize=(9, 16) if formato == "vertical" else (13, 9))
        ax.set_facecolor(BG)
        fig.set_facecolor(BG)
        fig.text(0.5, 0.5, f"Sin coordenadas para {player_name}", color="white", ha="center", fontsize=20)
        return fig

    x1 = pases_jugador['x'].values
    y1 = pases_jugador['y'].values
    x2 = np.array([loc[0] for loc in pases_jugador['pass_end_location']])
    y2 = np.array([loc[1] for loc in pases_jugador['pass_end_location']])

    dx = x2 - x1
    dy = y2 - y1
    angles = np.arctan2(dy, dx)
    lengths = np.sqrt(dx**2 + dy**2)
    completados = pases_jugador['pass_outcome'].isna().values

    avg_x = x1.mean()
    avg_y = y1.mean()

    n_bins = 16
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    bin_indices = np.digitize(angles, bins) - 1

    sonar_x = []
    sonar_y = []
    sonar_dx = []
    sonar_dy = []
    colors = []
    widths = []

    for b in range(n_bins):
        mask = bin_indices == b
        count = mask.sum()
        if count == 0:
            continue
        
        theta = (bins[b] + bins[b+1]) / 2.0
        avg_len = lengths[mask].mean()
        acc = completados[mask].mean()
        
        ray_len = np.clip(count * 1.5, 3, 20)
        v_dx = ray_len * np.cos(theta)
        v_dy = ray_len * np.sin(theta)
        
        sonar_x.append(avg_x)
        sonar_y.append(avg_y)
        sonar_dx.append(v_dx)
        sonar_dy.append(v_dy)
        colors.append(acc)
        widths.append(np.clip(avg_len / 4, 1.2, 5.0))

    pitch, fig, ax = _crear_lienzo(formato, half=False, line_color='#c7d5cc')
    
    pitch.scatter(avg_x, avg_y, color='#e74c3c', edgecolors='white', s=250, zorder=3, ax=ax)
    
    if sonar_x:
        cmap = plt.get_cmap('RdYlGn')
        # Dibujamos cada rayo individualmente con ancho escalar para evitar
        # el error de broadcasting de quiver cuando width es un array.
        for sx, sy, sdx, sdy, acc, w in zip(sonar_x, sonar_y, sonar_dx, sonar_dy, colors, widths):
            c = cmap(acc)
            pitch.arrows([sx], [sy],
                         [sx + sdx], [sy + sdy],
                         width=float(w), color=[c],
                         headwidth=4, headlength=4, zorder=2, ax=ax)

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.02 if formato != "vertical" else 0.04

    fig.text(0.5, y_title, f'{bandera} {pais} - Sonar de Pases: {player_name}', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} | Dirección y Precisión de Pases", ha='center', va='top', fontsize=12, color='#888888')
    
    if formato == "vertical":
        fig.text(0.1, 0.09, "LEYENDA:", color='white', weight='bold', size=10)
        fig.text(0.1, 0.075, "• Dirección: Hacia dónde van los pases", color='#aaaaaa', size=9)
        fig.text(0.1, 0.06, "• Largo: Volumen de pases en ese ángulo", color='#aaaaaa', size=9)
        fig.text(0.1, 0.045, "• Color: Precisión (Rojo = Baja, Verde = 100%)", color='#aaaaaa', size=9)
        plt.tight_layout(rect=[0, 0.12, 1, 0.92])
    else:
        fig.text(0.1, 0.08, "LEYENDA:", color='white', weight='bold', size=10)
        fig.text(0.1, 0.055, "• Dirección: Orientación de las flechas", color='#aaaaaa', size=9)
        fig.text(0.4, 0.055, "• Largo: Volumen de pases", color='#aaaaaa', size=9)
        fig.text(0.65, 0.055, "• Color: Precisión (Rojo a Verde)", color='#aaaaaa', size=9)
        plt.tight_layout(rect=[0, 0.1, 1, 0.93])
        
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    return fig


def generar_mapa_defensivo(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """Mapa de Acciones Defensivas con densidad en background."""
    def_types = ['Ball Recovery', 'Duel', 'Interception', 'Tackle', 'Block', 'Foul Committed', 'Pressure']
    df_def = df_eventos[(df_eventos['team'] == pais) & (df_eventos['type'].isin(def_types))].copy()
    
    pitch, fig, ax = _crear_lienzo(formato, half=False)
    
    if df_def.empty:
        ax.text(60, 40, "Sin acciones defensivas registradas", color="white", ha="center", va="center", fontsize=16)
        return fig
        
    if len(df_def) >= 10:
        pitch.kdeplot(df_def['x'], df_def['y'], ax=ax, levels=20, fill=True, cmap='Blues', alpha=0.3, zorder=1)
        
    colors = {
        'Pressure': '#f1c40f',
        'Tackle': '#e74c3c',
        'Interception': '#2ecc71',
        'Block': '#3498db',
        'Ball Recovery': '#9b59b6',
        'Foul Committed': '#e67e22',
        'Duel': '#1abc9c'
    }
    
    for dtype, group in df_def.groupby('type'):
        pitch.scatter(group['x'], group['y'], color=colors.get(dtype, '#95a5a6'), 
                      edgecolors='white', s=80, alpha=0.8, label=dtype, ax=ax, zorder=2)
                      
    if formato == "vertical":
        ax.legend(loc='upper left', frameon=True, facecolor=BG, edgecolor='#2a5fa5',
                  fontsize=8, labelcolor='white', bbox_to_anchor=(0.01, -0.01))
        plt.tight_layout(rect=[0, 0.08, 1, 0.92])
    else:
        ax.legend(loc='lower left', frameon=True, facecolor=BG, edgecolor='#2a5fa5',
                  fontsize=10, labelcolor='white', bbox_to_anchor=(0.01, 0.01))
        plt.tight_layout(rect=[0, 0, 1, 0.93])

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.02 if formato != "vertical" else 0.04
    
    fig.text(0.5, y_title, f'{bandera} {pais} (Mapa de Acciones Defensivas)', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} | Presiones, Recuperaciones y Bloqueos", ha='center', va='top', fontsize=12, color='#888888')
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    
    return fig


def generar_mapa_carries(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """Mapa de Conducciones Progresivas (avances de balón >= 10 metros)."""
    carries = df_eventos[(df_eventos['type'] == 'Carry') & (df_eventos['team'] == pais)].copy()
    
    pitch, fig, ax = _crear_lienzo(formato, half=False)
    
    if carries.empty:
        ax.text(60, 40, "Sin conducciones registradas", color="white", ha="center", va="center", fontsize=16)
        return fig
        
    carries = carries.dropna(subset=['location', 'carry_end_location'])
    if carries.empty:
        ax.text(60, 40, "Sin coordenadas para conducciones", color="white", ha="center", va="center", fontsize=16)
        return fig
        
    carries['x_start'] = carries['x']
    carries['y_start'] = carries['y']
    carries['x_end'] = np.array([loc[0] for loc in carries['carry_end_location']])
    carries['y_end'] = np.array([loc[1] for loc in carries['carry_end_location']])
    
    prog_carries = carries[(carries['x_end'] - carries['x_start']) >= 10].copy()
    
    if prog_carries.empty:
        ax.text(60, 40, "Sin conducciones progresivas (>= 10m)", color="white", ha="center", va="center", fontsize=16)
        return fig
        
    cmap = plt.get_cmap('YlOrRd')
    colors = cmap(np.clip(prog_carries['x_end'] / 120, 0.4, 1.0))
    
    pitch.arrows(prog_carries['x_start'], prog_carries['y_start'],
                 prog_carries['x_end'], prog_carries['y_end'],
                 width=2, color=colors, headwidth=4, headlength=4, zorder=2, ax=ax)
                 
    pitch.scatter(prog_carries['x_start'], prog_carries['y_start'], color='#3498db', edgecolors='white', s=30, zorder=3, ax=ax)

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.02 if formato != "vertical" else 0.04
    
    fig.text(0.5, y_title, f'{bandera} {pais} (Conducciones Progresivas)', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} | Carreras con balón que avanzan >= 10m", ha='center', va='top', fontsize=12, color='#888888')
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    
    if formato == "vertical":
        plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    else:
        plt.tight_layout(rect=[0, 0, 1, 0.93])
        
    return fig


def generar_mapa_asistencias(df_eventos: pd.DataFrame, pais: str, torneo: str, bandera: str, formato: str = "horizontal") -> plt.Figure:
    """Mapa de asistencias a tiros y pases clave."""
    pases_asistencias = df_eventos[
        (df_eventos['team'] == pais) & 
        (df_eventos['type'] == 'Pass') & 
        (df_eventos['pass_assisted_shot_id'].notna())
    ].copy()
    
    pitch, fig, ax = _crear_lienzo(formato, half=True)
    
    if pases_asistencias.empty:
        ax.text(60, 40, "Sin asistencias a tiro registradas", color="white", ha="center", va="center", fontsize=16)
        return fig
        
    pases_asistencias = pases_asistencias.dropna(subset=['location', 'pass_end_location'])
    if pases_asistencias.empty:
        ax.text(60, 40, "Sin coordenadas para las asistencias", color="white", ha="center", va="center", fontsize=16)
        return fig
        
    tiros = df_eventos[
        (df_eventos['team'] == pais) & 
        (df_eventos['type'] == 'Shot')
    ].copy()
    
    p_x1 = pases_asistencias['x'].values
    p_y1 = pases_asistencias['y'].values
    p_x2 = np.array([loc[0] for loc in pases_asistencias['pass_end_location']])
    p_y2 = np.array([loc[1] for loc in pases_asistencias['pass_end_location']])
    
    pitch.arrows(p_x1, p_y1, p_x2, p_y2, width=1.5, color='#2ecc71', headwidth=3, headlength=3, zorder=2, ax=ax)
    pitch.scatter(p_x1, p_y1, color='#27ae60', edgecolors='white', s=50, zorder=3, ax=ax)
    
    for idx, row in pases_asistencias.iterrows():
        shot_id = row['pass_assisted_shot_id']
        shot_match = tiros[tiros['id'] == shot_id]
        
        is_goal = False
        if not shot_match.empty:
            is_goal = shot_match.iloc[0].get('shot_outcome') == 'Goal'
            
        end_x = row['pass_end_location'][0]
        end_y = row['pass_end_location'][1]
        
        if is_goal:
            pitch.scatter(end_x, end_y, s=150, marker='*', color='#FFD700', edgecolors='#cc7700', zorder=4, ax=ax)
        else:
            pitch.scatter(end_x, end_y, s=80, color='#e74c3c', edgecolors='white', zorder=4, ax=ax)
            
    patch_pases = mpatches.Patch(color='#2ecc71', label='Pase Asistidor')
    patch_gol = mpatches.Patch(color='#FFD700', label='Gol ★')
    patch_tiro = mpatches.Patch(color='#e74c3c', label='Tiro (No Gol)')
    
    if formato == "vertical":
        ax.legend(handles=[patch_pases, patch_gol, patch_tiro], loc='upper left', frameon=False,
                  fontsize=9, labelcolor='white', bbox_to_anchor=(0.01, -0.01))
        plt.tight_layout(rect=[0, 0.08, 1, 0.92])
    else:
        ax.legend(handles=[patch_pases, patch_gol, patch_tiro], loc='lower left', frameon=False,
                  fontsize=10, labelcolor='white', bbox_to_anchor=(0.01, 0.01))
        plt.tight_layout(rect=[0, 0.05, 1, 0.93])

    y_title = 0.98 if formato != "vertical" else 0.96
    y_sub = 0.935 if formato != "vertical" else 0.93
    y_brand = 0.02 if formato != "vertical" else 0.04
    
    fig.text(0.5, y_title, f'{bandera} {pais} (Asistencias y Tiros)', ha='center', va='top', fontsize=22, fontweight='bold', color='white')
    fig.text(0.5, y_sub, f"{torneo} | Ubicación de pases clave y remates", ha='center', va='top', fontsize=12, color='#888888')
    fig.text(0.5, y_brand, "© @ScoutingMundial2026 | Powered by AI", ha="center", fontsize=10, color="gray", alpha=0.7)
    
    return fig
