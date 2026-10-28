import numpy as np
import matplotlib.pyplot as plt

def generate_radar_chart():
    categories = ['xG/90\n(Goles)', 'xA/90\n(Asistencias)', 'Pases Clave/90', 'xGChain/90\n(Cadena)', 'xGBuildup/90\n(Construcción)']
    N = len(categories)

    # Values normalized (0 to 1) based on archetype profile
    # Heatmap reference:
    # Finalizador: xG=0.40, xA=0.13, KP=1.05, Chain=0.55, Buildup=0.14
    # Creador: xG=0.23, xA=0.25, KP=1.97, Chain=0.71, Buildup=0.39
    # Distribuidor: xG=0.07, xA=0.09, KP=0.80, Chain=0.52, Buildup=0.43
    # Defensivo: xG=0.04, xA=0.04, KP=0.48, Chain=0.22, Buildup=0.17

    max_vals = [0.40, 0.25, 1.97, 0.71, 0.43]
    
    profiles = {
        'Finalizador (Goleador)': [0.40/max_vals[0], 0.13/max_vals[1], 1.05/max_vals[2], 0.55/max_vals[3], 0.14/max_vals[4]],
        'Creador (Asistidor/Winger)': [0.23/max_vals[0], 0.25/max_vals[1], 1.97/max_vals[2], 0.71/max_vals[3], 0.39/max_vals[4]],
        'Distribuidor (Build-up/Medio)': [0.07/max_vals[0], 0.09/max_vals[1], 0.80/max_vals[2], 0.52/max_vals[3], 0.43/max_vals[4]],
        'Defensivo/Soporte': [0.04/max_vals[0], 0.04/max_vals[1], 0.48/max_vals[2], 0.22/max_vals[3], 0.17/max_vals[4]]
    }

    colors = {
        'Finalizador (Goleador)': '#ff4d6d',
        'Creador (Asistidor/Winger)': '#00d2d3',
        'Distribuidor (Build-up/Medio)': '#feca57',
        'Defensivo/Soporte': '#1dd1a1'
    }

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), facecolor='#0d131f')
    ax.set_facecolor('#0d131f')

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, color='#e2e8f0', size=11, weight='bold')

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="#64748b", size=9)
    plt.ylim(0, 1.05)

    # Grid styling
    ax.spines['polar'].set_color('#1e293b')
    ax.spines['polar'].set_linewidth(1.5)
    ax.grid(color='#334155', linestyle='--', linewidth=0.8, alpha=0.7)

    for name, values in profiles.items():
        vals = values + values[:1]
        ax.plot(angles, vals, linewidth=2.2, linestyle='solid', label=name, color=colors[name], marker='o', markersize=4)
        ax.fill(angles, vals, color=colors[name], alpha=0.18)

    plt.title('Perfil Ideal por Arquetipo (Radar Chart)\nNormalizado La Liga 2023-24', size=14, color='#ffffff', weight='bold', pad=25)
    legend = plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), frameon=True, facecolor='#162032', edgecolor='#334155')
    for text in legend.get_texts():
        text.set_color('#ffffff')
        text.set_fontsize(9)

    plt.tight_layout()
    plt.savefig('assets/caso_radar.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print("Radar chart saved to assets/caso_radar.png")

if __name__ == '__main__':
    generate_radar_chart()
