"""pages/16_🏆_Visual_Bracket.py — Bracket Completo Mundial 2026 · 32 Equipos"""
import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import os, json, io
from utils.style_loader import load_css

st.set_page_config(page_title="Bracket Mundial 2026 · 32 Equipos", page_icon="🏆", layout="wide")
load_css()

# ──────────────────────────────────────────────────────────────────────────────
# CSS PREMIUM
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
.stApp {
    background: radial-gradient(ellipse at center, #6B0D20 0%, #3A060F 60%, #1A0207 100%) !important;
    color: white !important;
}
button[data-baseweb="tab"] { color: #FFD700 !important; font-weight: 800 !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #FFD700 !important; color: #FFD700 !important;
}
.round-title {
    font-size: 0.58rem; font-weight: 900; color: #FFD700; text-align: center;
    text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px;
    padding: 3px 2px; border-bottom: 1.5px solid rgba(255,215,0,0.25);
}
div.stButton > button {
    width: 100% !important; border-radius: 3px !important; font-weight: 700 !important;
    font-size: 0.63rem !important; text-transform: uppercase !important;
    letter-spacing: 0.3px !important; height: 28px !important;
    transition: all 0.12s ease !important; border-width: 1.5px !important;
    white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
}
div.stButton > button[kind="secondary"] {
    background: #FFFFFF !important; color: #3A060F !important;
    border-color: #CCCCCC !important; box-shadow: 0 2px 5px rgba(0,0,0,0.25) !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #FFD700 !important; box-shadow: 0 3px 10px rgba(255,215,0,0.3) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FFD700, #FFA800) !important;
    color: #1A0207 !important; border-color: #FFD700 !important;
    box-shadow: 0 0 10px rgba(255,215,0,0.55) !important;
}
.match-box {
    background: rgba(0,0,0,0.28); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 4px; padding: 3px 3px 5px; margin-bottom: 3px;
}
.match-label {
    font-size: 0.5rem; font-weight: bold; color: rgba(255,215,0,0.6);
    text-align: center; display: block; margin-bottom: 2px;
    text-transform: uppercase; letter-spacing: 0.8px;
}
.slot-empty {
    background: rgba(255,255,255,0.03); border: 1px dashed rgba(255,255,255,0.12);
    border-radius: 3px; height: 28px; display: flex; align-items: center;
    justify-content: center; font-size: 0.55rem; color: rgba(255,255,255,0.18);
    margin-bottom: 2px;
}
.champion-box {
    background: linear-gradient(135deg, rgba(255,215,0,0.18), rgba(255,140,0,0.08));
    border: 2px solid #FFD700; border-radius: 10px; text-align: center;
    padding: 10px 6px; box-shadow: 0 0 22px rgba(255,215,0,0.35); margin-top:6px;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #FFD700, #FF8C00) !important;
    color: #1A0207 !important; border: none !important; font-weight: 900 !important;
    font-size: 0.85rem !important; letter-spacing: 1px !important;
    border-radius: 8px !important; box-shadow: 0 4px 20px rgba(255,215,0,0.5) !important;
    width: 100% !important;
}
</style>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""<div style="text-align:center; padding:14px 0 4px;">
    <h1 style="color:#FFD700; font-size:2rem; font-weight:900; text-transform:uppercase;
               letter-spacing:3px; margin:0; text-shadow: 0 0 20px rgba(255,215,0,0.4);">
        🏆 Bracket Mundial 2026 — 32 Equipos
    </h1>
    <p style="color:rgba(255,255,255,0.5); font-size:0.8rem; margin-top:4px; letter-spacing:1px;">
        R32 · Octavos · Cuartos · Semis · Final · Campeón del Mundo
    </p>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, 'data', 'grupos.json')
    flags = {}
    grupo_teams = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            grupos = json.load(f)
        for g_name, g_teams in grupos.items():
            letter = g_name.split(" ")[-1]
            grupo_teams[letter] = list(g_teams.keys())
            for tname, tinfo in g_teams.items():
                flags[tname] = tinfo.get("bandera", "⚽")
    return flags, grupo_teams

teams_data, GRUPO_TEAMS = load_data()
all_teams = sorted(list(teams_data.keys()))
GRUPOS    = ["A","B","C","D","E","F","G","H","I","J","K","L"]

def get_flag(n): return teams_data.get(n, "⚽")
def fmt(n):
    if not n: return ""
    s = n if len(n) <= 13 else n[:12] + "…"
    return f"{get_flag(n)} {s}"

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────────────────────────
for g in GRUPOS:
    gt = GRUPO_TEAMS.get(g, [])
    if f"vb2_g{g}_1st" not in st.session_state:
        st.session_state[f"vb2_g{g}_1st"] = gt[0] if gt else None
    if f"vb2_g{g}_2nd" not in st.session_state:
        st.session_state[f"vb2_g{g}_2nd"] = gt[1] if len(gt) > 1 else None

for i in range(1, 9):
    if f"vb2_best3_{i}" not in st.session_state:
        st.session_state[f"vb2_best3_{i}"] = None

for i in range(1, 17):
    for s in ["t1", "t2"]:
        if f"vb2_r32_{i}_{s}" not in st.session_state:
            st.session_state[f"vb2_r32_{i}_{s}"] = None

WIN_KEYS = (
    [f"vb2_w_r32_{i}" for i in range(1, 17)] +
    [f"vb2_w_r16_{i}" for i in range(1, 9)]  +
    [f"vb2_w_qf_{i}"  for i in range(1, 5)]  +
    [f"vb2_w_sf_{i}"  for i in range(1, 3)]  +
    ["vb2_champion"]
)
for k in WIN_KEYS:
    if k not in st.session_state:
        st.session_state[k] = None

# ──────────────────────────────────────────────────────────────────────────────
# CASCADE INVALIDATION
# ──────────────────────────────────────────────────────────────────────────────
def inval(key, opts):
    if st.session_state.get(key) not in (opts or []):
        st.session_state[key] = None

def cascade():
    for i in range(1, 17):
        inval(f"vb2_w_r32_{i}",
              [st.session_state.get(f"vb2_r32_{i}_t1"),
               st.session_state.get(f"vb2_r32_{i}_t2")])
    for j in range(1, 9):
        inval(f"vb2_w_r16_{j}",
              [st.session_state.get(f"vb2_w_r32_{2*j-1}"),
               st.session_state.get(f"vb2_w_r32_{2*j}")])
    for j in range(1, 5):
        inval(f"vb2_w_qf_{j}",
              [st.session_state.get(f"vb2_w_r16_{2*j-1}"),
               st.session_state.get(f"vb2_w_r16_{2*j}")])
    for j in range(1, 3):
        inval(f"vb2_w_sf_{j}",
              [st.session_state.get(f"vb2_w_qf_{2*j-1}"),
               st.session_state.get(f"vb2_w_qf_{2*j}")])
    inval("vb2_champion",
          [st.session_state.get("vb2_w_sf_1"),
           st.session_state.get("vb2_w_sf_2")])

cascade()

# ──────────────────────────────────────────────────────────────────────────────
# PROGRESS INDICATOR
# ──────────────────────────────────────────────────────────────────────────────
def _bracket_progress():
    r32_filled  = sum(1 for i in range(1,17)
                      if st.session_state.get(f"vb2_r32_{i}_t1")
                      and st.session_state.get(f"vb2_r32_{i}_t2"))
    r32_winners = sum(1 for i in range(1,17) if st.session_state.get(f"vb2_w_r32_{i}"))
    r16_winners = sum(1 for i in range(1, 9) if st.session_state.get(f"vb2_w_r16_{i}"))
    qf_winners  = sum(1 for i in range(1, 5) if st.session_state.get(f"vb2_w_qf_{i}"))
    sf_winners  = sum(1 for i in range(1, 3) if st.session_state.get(f"vb2_w_sf_{i}"))
    champion    = 1 if st.session_state.get("vb2_champion") else 0
    steps = [
        (r32_filled,  16, "Cruces R32"),
        (r32_winners, 16, "Ganadores R32"),
        (r16_winners,  8, "Octavos"),
        (qf_winners,   4, "Cuartos"),
        (sf_winners,   2, "Semis"),
        (champion,     1, "Final"),
    ]
    done  = sum(d for d,_,_ in steps)
    total = sum(t for _,t,_ in steps)
    pct   = int(done / total * 100)
    labels = [f"✅ {n}" if d == t else (f"🟡 {d}/{t} {n}" if d > 0 else f"○ {n}")
              for d, t, n in steps]
    return labels, pct

# ──────────────────────────────────────────────────────────────────────────────
# IMAGE BUILDER (works at any fill level)
# ──────────────────────────────────────────────────────────────────────────────
def build_full_bracket_image():
    """Genera el bracket con el estado actual — funciona parcialmente lleno."""
    FW, FH = 36, 17
    fig, ax = plt.subplots(figsize=(FW, FH), facecolor='#2A0508')
    ax.set_xlim(0, FW)
    ax.set_ylim(0, FH)
    ax.axis('off')

    for xi in range(380):
        t = xi / 380
        r = 0.17 - 0.10 * t
        ax.axvline(x=xi * FW / 380, color=(r, 0.02, 0.04), lw=FW/380, alpha=0.6, zorder=0)

    GOLD = '#FFD700'
    DARK = '#1A0207'
    CW   = 3.2
    CH   = 0.65
    GAP  = 0.70

    def draw_card(cx, cy, team, winner=False, fs=8.5):
        bg = '#FFD700' if winner else ('#E8E8E8' if team else '#2A0810')
        tc = '#1A0207' if winner else ('#2A0508' if team else '#555555')
        ec = GOLD if winner else ('#BBBBBB' if team else (1.0, 1.0, 1.0, 0.1))
        rect = mpatches.FancyBboxPatch(
            (cx - CW/2, cy - CH/2), CW, CH,
            boxstyle="round,pad=0.04", lw=1.5 if winner else 1.0,
            edgecolor=ec, facecolor=bg, zorder=3
        )
        ax.add_patch(rect)
        if winner:
            glow = mpatches.FancyBboxPatch(
                (cx - CW/2 - 0.08, cy - CH/2 - 0.08), CW + 0.16, CH + 0.16,
                boxstyle="round,pad=0.1", lw=0,
                edgecolor='none', facecolor=GOLD, alpha=0.15, zorder=2
            )
            ax.add_patch(glow)
        if team:
            label = team if len(team) <= 14 else f"{team[:13]}…"
        else:
            label = "—"
        ax.text(cx, cy, label, ha='center', va='center', fontsize=fs,
                fontweight='bold' if winner else 'normal',
                color=tc, zorder=4, clip_on=True)

    def line_h(x1, y, x2):
        ax.plot([x1, x2], [y, y], color=GOLD, lw=0.9, alpha=0.35, zorder=1)

    def line_v(x, y1, y2):
        ax.plot([x, x], [y1, y2], color=GOLD, lw=0.7, alpha=0.28, zorder=1)

    def round_lbl(cx, y, txt):
        ax.text(cx, y, txt, ha='center', va='bottom', fontsize=8,
                fontweight='bold', color=GOLD, alpha=0.9,
                path_effects=[pe.withStroke(linewidth=2.5, foreground=DARK)])

    XR32L, XR16L, XQF_L, XSF_L = 2.0, 6.2, 10.4, 14.6
    XCEN                        = 18.0
    XSF_R, XQF_R, XR16R, XR32R = 21.4, 25.6, 29.8, 34.0

    Y_BASE = 15.6
    Y_STEP = 1.9
    Y_R32  = [Y_BASE - i * Y_STEP for i in range(8)]
    Y_R16  = [(Y_R32[2*j] + Y_R32[2*j+1]) / 2 for j in range(4)]
    Y_QF   = [(Y_R16[2*j] + Y_R16[2*j+1]) / 2 for j in range(2)]
    Y_SF   = (Y_QF[0] + Y_QF[1]) / 2
    Y_FIN  = Y_SF

    round_lbl(XR32L, Y_BASE + 0.55, "DIECISEISAVOS")
    round_lbl(XR16L, Y_BASE + 0.55, "OCTAVOS")
    round_lbl(XQF_L, Y_BASE + 0.55, "CUARTOS")
    round_lbl(XSF_L, Y_BASE + 0.55, "SEMIFINAL")
    round_lbl(XCEN,  Y_BASE + 0.55, "🏆  GRAN FINAL  🏆")
    round_lbl(XSF_R, Y_BASE + 0.55, "SEMIFINAL")
    round_lbl(XQF_R, Y_BASE + 0.55, "CUARTOS")
    round_lbl(XR16R, Y_BASE + 0.55, "OCTAVOS")
    round_lbl(XR32R, Y_BASE + 0.55, "DIECISEISAVOS")

    w = {}
    for i in range(1, 17): w[f"r32_{i}"] = st.session_state.get(f"vb2_w_r32_{i}") or ""
    for i in range(1,  9): w[f"r16_{i}"] = st.session_state.get(f"vb2_w_r16_{i}") or ""
    for i in range(1,  5): w[f"qf_{i}"]  = st.session_state.get(f"vb2_w_qf_{i}")  or ""
    for i in range(1,  3): w[f"sf_{i}"]  = st.session_state.get(f"vb2_w_sf_{i}")  or ""
    w["champ"] = st.session_state.get("vb2_champion") or ""

    # R32 LEFT (M1–M8)
    for i in range(8):
        mi = i + 1
        yc = Y_R32[i]
        t1 = st.session_state.get(f"vb2_r32_{mi}_t1") or ""
        t2 = st.session_state.get(f"vb2_r32_{mi}_t2") or ""
        wk = w[f"r32_{mi}"]
        draw_card(XR32L, yc + GAP/2, t1, winner=(wk == t1 and t1 != ""))
        draw_card(XR32L, yc - GAP/2, t2, winner=(wk == t2 and t2 != ""))
        line_v(XR32L - CW/2, yc - GAP/2, yc + GAP/2)
        if wk:
            mid_y = yc + GAP/2 if wk == t1 else yc - GAP/2
            line_h(XR32L + CW/2, mid_y, XR16L - CW/2)

    # R32 RIGHT (M9–M16)
    for i in range(8):
        mi = i + 9
        yc = Y_R32[i]
        t1 = st.session_state.get(f"vb2_r32_{mi}_t1") or ""
        t2 = st.session_state.get(f"vb2_r32_{mi}_t2") or ""
        wk = w[f"r32_{mi}"]
        draw_card(XR32R, yc + GAP/2, t1, winner=(wk == t1 and t1 != ""))
        draw_card(XR32R, yc - GAP/2, t2, winner=(wk == t2 and t2 != ""))
        line_v(XR32R + CW/2, yc - GAP/2, yc + GAP/2)
        if wk:
            mid_y = yc + GAP/2 if wk == t1 else yc - GAP/2
            line_h(XR16R + CW/2, mid_y, XR32R - CW/2)

    # R16 LEFT (j=1..4)
    for j in range(4):
        rj = j + 1
        yc = Y_R16[j]
        t1 = w[f"r32_{2*j+1}"]
        t2 = w[f"r32_{2*j+2}"]
        wk = w[f"r16_{rj}"]
        draw_card(XR16L, yc + GAP/2, t1, winner=(wk == t1 and t1 != ""))
        draw_card(XR16L, yc - GAP/2, t2, winner=(wk == t2 and t2 != ""))
        line_v(XR16L - CW/2, yc - GAP/2, yc + GAP/2)
        if t1: line_v(XR32L + CW/2, Y_R32[2*j] + GAP/2, Y_R16[j] + GAP/2)
        if t2: line_v(XR32L + CW/2, Y_R32[2*j+1] - GAP/2, Y_R16[j] - GAP/2)
        if wk:
            mid_y = yc + GAP/2 if wk == t1 else yc - GAP/2
            line_h(XR16L + CW/2, mid_y, XQF_L - CW/2)

    # R16 RIGHT (j=5..8)
    for j in range(4):
        rj = j + 5
        yc = Y_R16[j]
        t1 = w[f"r32_{2*j+9}"]
        t2 = w[f"r32_{2*j+10}"]
        wk = w[f"r16_{rj}"]
        draw_card(XR16R, yc + GAP/2, t1, winner=(wk == t1 and t1 != ""))
        draw_card(XR16R, yc - GAP/2, t2, winner=(wk == t2 and t2 != ""))
        line_v(XR16R + CW/2, yc - GAP/2, yc + GAP/2)
        if wk:
            mid_y = yc + GAP/2 if wk == t1 else yc - GAP/2
            line_h(XQF_R + CW/2, mid_y, XR16R - CW/2)

    # QF LEFT (j=1..2)
    for j in range(2):
        qj = j + 1
        yc = Y_QF[j]
        t1 = w[f"r16_{2*j+1}"]
        t2 = w[f"r16_{2*j+2}"]
        wk = w[f"qf_{qj}"]
        draw_card(XQF_L, yc + GAP/2, t1, winner=(wk == t1 and t1 != ""))
        draw_card(XQF_L, yc - GAP/2, t2, winner=(wk == t2 and t2 != ""))
        line_v(XQF_L - CW/2, yc - GAP/2, yc + GAP/2)
        if wk:
            mid_y = yc + GAP/2 if wk == t1 else yc - GAP/2
            line_h(XQF_L + CW/2, mid_y, XSF_L - CW/2)

    # QF RIGHT (j=3..4)
    for j in range(2):
        qj = j + 3
        yc = Y_QF[j]
        t1 = w[f"r16_{2*j+5}"]
        t2 = w[f"r16_{2*j+6}"]
        wk = w[f"qf_{qj}"]
        draw_card(XQF_R, yc + GAP/2, t1, winner=(wk == t1 and t1 != ""))
        draw_card(XQF_R, yc - GAP/2, t2, winner=(wk == t2 and t2 != ""))
        line_v(XQF_R + CW/2, yc - GAP/2, yc + GAP/2)
        if wk:
            mid_y = yc + GAP/2 if wk == t1 else yc - GAP/2
            line_h(XSF_R + CW/2, mid_y, XQF_R - CW/2)

    # SF LEFT
    t1_sf1, t2_sf1, wk_sf1 = w["qf_1"], w["qf_2"], w["sf_1"]
    draw_card(XSF_L, Y_SF + GAP/2, t1_sf1, winner=(wk_sf1 == t1_sf1 and t1_sf1 != ""))
    draw_card(XSF_L, Y_SF - GAP/2, t2_sf1, winner=(wk_sf1 == t2_sf1 and t2_sf1 != ""))
    line_v(XSF_L - CW/2, Y_SF - GAP/2, Y_SF + GAP/2)
    if wk_sf1:
        line_h(XSF_L + CW/2, Y_SF + GAP/2 if wk_sf1 == t1_sf1 else Y_SF - GAP/2, XCEN - CW/2)

    # SF RIGHT
    t1_sf2, t2_sf2, wk_sf2 = w["qf_3"], w["qf_4"], w["sf_2"]
    draw_card(XSF_R, Y_SF + GAP/2, t1_sf2, winner=(wk_sf2 == t1_sf2 and t1_sf2 != ""))
    draw_card(XSF_R, Y_SF - GAP/2, t2_sf2, winner=(wk_sf2 == t2_sf2 and t2_sf2 != ""))
    line_v(XSF_R + CW/2, Y_SF - GAP/2, Y_SF + GAP/2)
    if wk_sf2:
        line_h(XCEN + CW/2, Y_SF + GAP/2 if wk_sf2 == t1_sf2 else Y_SF - GAP/2, XSF_R - CW/2)

    # GRAN FINAL
    fin_t1, fin_t2 = w["sf_1"], w["sf_2"]
    fin_y1 = Y_FIN + GAP/2 + 0.15
    fin_y2 = Y_FIN - GAP/2 - 0.15
    champ  = w["champ"]
    final_bg = mpatches.FancyBboxPatch(
        (XCEN - CW/2 - 0.3, fin_y2 - 0.4), CW + 0.6,
        (fin_y1 - fin_y2) + CH + 0.8,
        boxstyle="round,pad=0.12", lw=2.2,
        edgecolor=GOLD, facecolor='#160305', zorder=2
    )
    ax.add_patch(final_bg)
    ax.text(XCEN, (fin_y1 + fin_y2)/2 + 0.9, "G R A N   F I N A L",
            ha='center', va='center', fontsize=9, fontweight='bold',
            color=GOLD, path_effects=[pe.withStroke(linewidth=3, foreground=DARK)])
    draw_card(XCEN, fin_y1, fin_t1, winner=(champ == fin_t1 and fin_t1 != ""), fs=9.5)
    draw_card(XCEN, fin_y2, fin_t2, winner=(champ == fin_t2 and fin_t2 != ""), fs=9.5)

    # CHAMPION
    if champ:
        y_c = fin_y2 - 1.6
        ax.add_patch(mpatches.FancyBboxPatch(
            (XCEN - CW/2 - 0.4, y_c - 0.6), CW + 0.8, 1.2,
            boxstyle="round,pad=0.12", lw=2.5,
            edgecolor=GOLD, facecolor='#250608', zorder=4
        ))
        ax.text(XCEN, y_c, f"👑 {champ} 👑",
                ha='center', va='center', fontsize=12, fontweight='bold',
                color=GOLD, zorder=5)
        ax.text(XCEN, y_c - 0.45, "CAMPEÓN DEL MUNDO",
                ha='center', va='center', fontsize=8, fontweight='bold',
                color=GOLD, alpha=0.9, zorder=5)

    # BRANDING
    ax.text(FW/2, 0.4, "FIFA WORLD CUP 2026  ·  USA | CANADA | MEXICO",
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=GOLD, alpha=0.6)
    ax.text(FW/2, 0.15, "© @ScoutingMundial2026  ·  Generado con IA",
            ha='center', va='center', fontsize=8.5, color='#888888', alpha=0.7)

    plt.tight_layout(pad=0.3)
    return fig


def _gen_and_store():
    """Genera y almacena el PNG en session_state."""
    fig_img = build_full_bracket_image()
    buf = io.BytesIO()
    fig_img.savefig(buf, format='png', dpi=180, bbox_inches='tight',
                    facecolor='#2A0508', edgecolor='none')
    buf.seek(0)
    st.session_state["vb2_bracket_img"] = buf.read()
    plt.close(fig_img)


# ──────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def slot_btn(team, btn_key, sel_key):
    if not team:
        st.markdown('<div class="slot-empty">—</div>', unsafe_allow_html=True)
        return
    is_sel = st.session_state.get(sel_key) == team
    if st.button(fmt(team), key=btn_key, type="primary" if is_sel else "secondary",
                 use_container_width=True):
        st.session_state[sel_key] = team
        st.rerun()

def match_box(label, t1, t2, k1, k2, sel_key):
    st.markdown(f'<div class="match-box"><span class="match-label">{label}</span>',
                unsafe_allow_html=True)
    slot_btn(t1, k1, sel_key)
    slot_btn(t2, k2, sel_key)
    st.markdown('</div>', unsafe_allow_html=True)

def SP(h):
    st.markdown(f'<div style="height:{h}px;"></div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────────────────
tab_cfg, tab_bracket, tab_export = st.tabs([
    "⚙️ 1. Clasificados & Cruces",
    "🏆 2. Bracket Interactivo",
    "📸 3. Vista Previa & Descarga"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CLASIFICADOS & CRUCES
# ══════════════════════════════════════════════════════════════════════════════
with tab_cfg:
    st.markdown("#### 🗂️ Paso 1 — 1° y 2° de cada Grupo (según tu simulación WhatIf)")
    def update_g(g, pos):
        val = st.session_state.get(f"sel_g{g}_{pos}")
        if val is not None:
            st.session_state[f"vb2_g{g}_{pos}"] = val

    c1, c2, c3, c4 = st.columns(4)
    cols = [c1, c2, c3, c4]
    
    for idx, g in enumerate(GRUPOS):
        gt = GRUPO_TEAMS.get(g, all_teams)
        with cols[idx % 4]:
            st.markdown(f"**🏷️ Grupo {g}**")
            cur1 = st.session_state.get(f"vb2_g{g}_1st")
            idx1 = gt.index(cur1) if cur1 in gt else 0
            st.selectbox(f"1° Grupo {g}", gt, index=idx1,
                         key=f"sel_g{g}_1st", format_func=fmt,
                         label_visibility="collapsed",
                         on_change=update_g, args=(g, "1st"))
            
            curr_1st = st.session_state.get(f"vb2_g{g}_1st")
            rem  = [t for t in gt if t != curr_1st]
            cur2 = st.session_state.get(f"vb2_g{g}_2nd")
            idx2 = rem.index(cur2) if cur2 in rem else 0
            st.selectbox(f"2° Grupo {g}", rem, index=idx2,
                         key=f"sel_g{g}_2nd", format_func=fmt,
                         label_visibility="collapsed",
                         on_change=update_g, args=(g, "2nd"))
        if (idx + 1) % 4 == 0 and idx < len(GRUPOS) - 1:
            st.markdown("---")

    st.markdown("---")
    st.markdown("#### 🥉 Paso 2 — Los 8 Mejores Terceros")
    st.caption("Selecciona los 8 equipos que, aunque quedaron 3°, avanzan por mejor rendimiento.")

    firsts  = [st.session_state.get(f"vb2_g{g}_1st") for g in GRUPOS]
    seconds = [st.session_state.get(f"vb2_g{g}_2nd") for g in GRUPOS]
    possible_thirds = [t for g in GRUPOS
                       for t in GRUPO_TEAMS.get(g, [])
                       if t not in firsts and t not in seconds]

    def update_b3(i):
        val = st.session_state.get(f"sel_best3_{i}")
        if val is not None:
            st.session_state[f"vb2_best3_{i}"] = val

    b3_cols = st.columns(4)
    for i in range(1, 9):
        with b3_cols[(i-1) % 4]:
            opts  = [None] + possible_thirds + [t for t in all_teams
                     if t not in possible_thirds + firsts + seconds]
            cur   = st.session_state.get(f"vb2_best3_{i}")
            idx_b = opts.index(cur) if cur in opts else 0
            st.selectbox(f"Mejor 3° #{i}", opts, index=idx_b,
                         key=f"sel_best3_{i}",
                         format_func=lambda x: "— Ninguno —" if x is None else fmt(x),
                         on_change=update_b3, args=(i,))

    st.markdown("---")
    st.markdown("#### ⚔️ Paso 3 — Los 16 Partidos de Dieciseisavos (Ronda de 32)")
    st.caption("**M1–M8** → Llave Izquierda &nbsp;|&nbsp; **M9–M16** → Llave Derecha")

    if st.button("🪄 Generar Cruces Automáticamente (Según Paso 1 y 2)", type="primary"):
        f_list = [st.session_state.get(f"vb2_g{g}_1st") for g in GRUPOS]
        f_list = [t for t in f_list if t]
        s_list = [st.session_state.get(f"vb2_g{g}_2nd") for g in GRUPOS]
        s_list = [t for t in s_list if t]
        t_list = [st.session_state.get(f"vb2_best3_{i}") for i in range(1, 9)]
        t_list = [t for t in t_list if t]
        
        # M1-M8: 8 Primeros vs 8 Terceros
        for i in range(8):
            t1 = f_list[i] if i < len(f_list) else None
            t2 = t_list[i] if i < len(t_list) else None
            st.session_state[f"vb2_r32_{i+1}_t1"] = t1
            st.session_state[f"vb2_r32_{i+1}_t2"] = t2
        
        # M9-M12: Restantes 4 Primeros vs 4 Segundos
        for i in range(4):
            t1 = f_list[8+i] if (8+i) < len(f_list) else None
            t2 = s_list[i] if i < len(s_list) else None
            st.session_state[f"vb2_r32_{9+i}_t1"] = t1
            st.session_state[f"vb2_r32_{9+i}_t2"] = t2
            
        # M13-M16: Restantes 8 Segundos vs 8 Segundos
        for i in range(4):
            t1 = s_list[4+i] if (4+i) < len(s_list) else None
            t2 = s_list[8+i] if (8+i) < len(s_list) else None
            st.session_state[f"vb2_r32_{13+i}_t1"] = t1
            st.session_state[f"vb2_r32_{13+i}_t2"] = t2
            
        # Limpiar keys de selectbox para forzar refresco
        for i in range(1, 17):
            if f"sel_r32_{i}_t1" in st.session_state: del st.session_state[f"sel_r32_{i}_t1"]
            if f"sel_r32_{i}_t2" in st.session_state: del st.session_state[f"sel_r32_{i}_t2"]
        
        # Limpiar ganadores
        for k in WIN_KEYS: st.session_state[k] = None
        st.rerun()

    def update_r32(i, slot_s):
        val = st.session_state.get(f"sel_r32_{i}_{slot_s}")
        if val is not None:
            st.session_state[f"vb2_r32_{i}_{slot_s}"] = val

    r32_left, r32_right = st.columns(2)
    for i in range(1, 17):
        col = r32_left if i <= 8 else r32_right
        with col:
            st.markdown(f"**⚔️ M{i}** — *Llave {'Izquierda' if i <= 8 else 'Derecha'}*")
            mc1, mc2 = st.columns(2)
            for slot_col, slot_s in [(mc1, "t1"), (mc2, "t2")]:
                with slot_col:
                    opts = [None] + all_teams
                    cur  = st.session_state.get(f"vb2_r32_{i}_{slot_s}")
                    idxv = opts.index(cur) if cur in opts else 0
                    st.selectbox(
                        f"{'A' if slot_s=='t1' else 'B'} M{i}",
                        opts, index=idxv, key=f"sel_r32_{i}_{slot_s}",
                        format_func=lambda x: "— —" if x is None else fmt(x),
                        label_visibility="collapsed",
                        on_change=update_r32,
                        args=(i, slot_s)
                    )
            SP(4)

    st.markdown("---")
    rc1, rc2, _ = st.columns([1.5, 1.5, 4])
    with rc2:
        if st.button("🔄 Reiniciar bracket completo", type="secondary"):
            for k in WIN_KEYS:
                st.session_state[k] = None
            for i in range(1, 17):
                st.session_state[f"vb2_r32_{i}_t1"] = None
                st.session_state[f"vb2_r32_{i}_t2"] = None
                if f"sel_r32_{i}_t1" in st.session_state:
                    del st.session_state[f"sel_r32_{i}_t1"]
                if f"sel_r32_{i}_t2" in st.session_state:
                    del st.session_state[f"sel_r32_{i}_t2"]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BRACKET INTERACTIVO
# ══════════════════════════════════════════════════════════════════════════════
with tab_bracket:
    st.caption("💡 Haz clic en un equipo para que avance. "
               "**Genera y descarga la imagen en cualquier momento** — no necesitas llenarlo todo.")

    def r32t(i, s): return st.session_state.get(f"vb2_r32_{i}_{s}")
    def wr32(i):    return st.session_state.get(f"vb2_w_r32_{i}")
    def wr16(i):    return st.session_state.get(f"vb2_w_r16_{i}")
    def wqf(i):     return st.session_state.get(f"vb2_w_qf_{i}")
    def wsf(i):     return st.session_state.get(f"vb2_w_sf_{i}")

    C = st.columns([1.05, 1.05, 1.05, 1.05, 1.5, 1.05, 1.05, 1.05, 1.05])

    with C[0]:
        st.markdown('<div class="round-title">R32 · Izq</div>', unsafe_allow_html=True)
        for i in range(1, 9):
            match_box(f"M{i}", r32t(i,"t1"), r32t(i,"t2"),
                      f"br_r32_{i}_t1", f"br_r32_{i}_t2", f"vb2_w_r32_{i}")
            if i < 8: SP(4)

    with C[1]:
        st.markdown('<div class="round-title">Octavos · Izq</div>', unsafe_allow_html=True)
        for j in range(1, 5):
            SP([44, 96, 96, 96][j-1])
            match_box(f"Oct {j}", wr32(2*j-1), wr32(2*j),
                      f"br_r16_{j}_t1", f"br_r16_{j}_t2", f"vb2_w_r16_{j}")

    with C[2]:
        st.markdown('<div class="round-title">Cuartos · Izq</div>', unsafe_allow_html=True)
        SP(120)
        match_box("QF 1", wr16(1), wr16(2), "br_qf1_t1", "br_qf1_t2", "vb2_w_qf_1")
        SP(280)
        match_box("QF 2", wr16(3), wr16(4), "br_qf2_t1", "br_qf2_t2", "vb2_w_qf_2")

    with C[3]:
        st.markdown('<div class="round-title">Semifinal · Izq</div>', unsafe_allow_html=True)
        SP(290)
        match_box("SF 1", wqf(1), wqf(2), "br_sf1_t1", "br_sf1_t2", "vb2_w_sf_1")

    with C[4]:
        st.markdown('<div class="round-title" style="color:#FFD700;font-size:0.65rem;">🏆 Gran Final</div>',
                    unsafe_allow_html=True)
        SP(190)
        st.markdown("""<div class="match-box" style="border:1.5px solid rgba(255,215,0,0.45);">
            <span class="match-label" style="color:#FFD700; font-size:0.6rem;">⚡ FINAL MUNDIAL</span>""",
            unsafe_allow_html=True)
        slot_btn(wsf(1), "br_fin_t1", "vb2_champion")
        slot_btn(wsf(2), "br_fin_t2", "vb2_champion")
        st.markdown('</div>', unsafe_allow_html=True)
        SP(8)
        champ = st.session_state.get("vb2_champion")
        if champ:
            sub = wsf(2) if champ == wsf(1) else wsf(1)
            st.markdown(f"""<div class="champion-box">
                <div style="font-size:1.8rem;">👑</div>
                <div style="font-size:0.58rem; color:#FFD700; font-weight:900;
                            text-transform:uppercase; letter-spacing:2px;">Campeón del Mundo</div>
                <div style="font-size:1rem; font-weight:900; color:#fff; margin:4px 0;">
                    {fmt(champ)}</div>
                <div style="font-size:0.62rem; color:rgba(255,255,255,0.45);">
                    🥈 {fmt(sub)}</div>
            </div>""", unsafe_allow_html=True)
            if st.session_state.get("_vb2_last_champ") != champ:
                st.session_state["_vb2_last_champ"] = champ
                st.balloons()
        else:
            st.markdown("""<div class="champion-box" style="border-style:dashed;
                              border-color:rgba(255,215,0,0.3);">
                <span style="color:rgba(255,255,255,0.2); font-size:0.65rem;
                             text-transform:uppercase; letter-spacing:1px;">
                    Esperando al Campeón</span>
            </div>""", unsafe_allow_html=True)

    with C[5]:
        st.markdown('<div class="round-title">Semifinal · Der</div>', unsafe_allow_html=True)
        SP(290)
        match_box("SF 2", wqf(3), wqf(4), "br_sf2_t1", "br_sf2_t2", "vb2_w_sf_2")

    with C[6]:
        st.markdown('<div class="round-title">Cuartos · Der</div>', unsafe_allow_html=True)
        SP(120)
        match_box("QF 3", wr16(5), wr16(6), "br_qf3_t1", "br_qf3_t2", "vb2_w_qf_3")
        SP(280)
        match_box("QF 4", wr16(7), wr16(8), "br_qf4_t1", "br_qf4_t2", "vb2_w_qf_4")

    with C[7]:
        st.markdown('<div class="round-title">Octavos · Der</div>', unsafe_allow_html=True)
        for j in range(5, 9):
            SP([44, 96, 96, 96][j-5])
            match_box(f"Oct {j}", wr32(2*j-1), wr32(2*j),
                      f"br_r16_{j}_t1", f"br_r16_{j}_t2", f"vb2_w_r16_{j}")

    with C[8]:
        st.markdown('<div class="round-title">R32 · Der</div>', unsafe_allow_html=True)
        for i in range(9, 17):
            match_box(f"M{i}", r32t(i,"t1"), r32t(i,"t2"),
                      f"br_r32_{i}_t1", f"br_r32_{i}_t2", f"vb2_w_r32_{i}")
            if i < 16: SP(4)

    # ── ZONA DE EXPORTACIÓN DIRECTA AL PIE DEL BRACKET ───────────────────────
    SP(20)
    st.markdown('<hr style="border-color:rgba(255,215,0,0.2);">', unsafe_allow_html=True)

    prog_labels, prog_pct = _bracket_progress()
    export_l, export_r = st.columns([3, 2])

    with export_l:
        st.markdown(
            '<div style="font-size:0.75rem; color:rgba(255,255,255,0.5); margin-bottom:4px;">'
            + "  ·  ".join(prog_labels) + '</div>',
            unsafe_allow_html=True
        )
        st.progress(prog_pct, text=f"🟡 Progreso: {prog_pct}% completado")

    with export_r:
        st.markdown(
            '<p style="color:rgba(255,255,255,0.4); font-size:0.73rem; margin:0 0 6px;">'
            '💡 Genera la imagen en <strong>cualquier momento</strong> — '
            'incluso con solo los dieciseisavos definidos.</p>',
            unsafe_allow_html=True
        )
        btn_gen, btn_dl = st.columns(2)
        with btn_gen:
            if st.button("🎨 Generar Imagen", type="primary",
                         use_container_width=True, key="gen_tab2"):
                with st.spinner("🏗️ Generando..."):
                    _gen_and_store()
                st.success("✅ Lista")
                st.rerun()
        with btn_dl:
            img_b = st.session_state.get("vb2_bracket_img")
            if img_b:
                st.download_button(
                    label="📥 Descargar PNG",
                    data=img_b,
                    file_name="bracket_mundial_2026.png",
                    mime="image/png",
                    use_container_width=True,
                    type="primary",
                    key="dl_tab2"
                )
            else:
                st.button("📥 Descargar PNG", disabled=True,
                          use_container_width=True, key="dl_tab2_disabled")

    if st.session_state.get("vb2_bracket_img"):
        with st.expander("🖼️ Vista previa de la última imagen generada", expanded=False):
            st.image(st.session_state["vb2_bracket_img"], use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VISTA PREVIA & DESCARGA
# ══════════════════════════════════════════════════════════════════════════════
with tab_export:
    st.markdown("""<div style="text-align:center; margin-bottom:12px;">
        <h3 style="color:#FFD700; font-size:1.15rem; margin:0;">
            📸 Vista Previa & Descarga</h3>
        <p style="color:rgba(255,255,255,0.45); font-size:0.8rem; margin-top:4px;">
            Puedes generar la imagen en <strong style="color:#FFD700;">cualquier momento</strong>
            — sin necesidad de llenar todo el bracket.
        </p></div>""", unsafe_allow_html=True)

    exp_l, exp_c, exp_r = st.columns([1, 2.5, 1])
    with exp_c:
        prog_labels3, prog_pct3 = _bracket_progress()
        st.progress(prog_pct3, text=f"Progreso del bracket: {prog_pct3}%")
        st.markdown(
            '<div style="font-size:0.72rem; color:rgba(255,255,255,0.4); margin-bottom:10px;">'
            + "  ·  ".join(prog_labels3) + '</div>',
            unsafe_allow_html=True
        )
        if st.button("🎨  Generar / Actualizar Imagen",
                     type="primary", use_container_width=True, key="gen_tab3"):
            with st.spinner("🏗️ Renderizando en alta resolución..."):
                _gen_and_store()
            st.success("✅ Imagen generada — desplázate para verla y descargarla")

    if st.session_state.get("vb2_bracket_img"):
        st.image(st.session_state["vb2_bracket_img"], use_container_width=True)
        SP(10)
        dl_l, dl_c, dl_r = st.columns([1, 2.5, 1])
        with dl_c:
            st.download_button(
                label="📥  DESCARGAR BRACKET PNG · Alta Resolución",
                data=st.session_state["vb2_bracket_img"],
                file_name="bracket_mundial_2026_32equipos.png",
                mime="image/png",
                use_container_width=True,
                type="primary",
                key="dl_tab3"
            )
    else:
        st.info("💡 Aún no has generado ninguna imagen. "
                "Usa el botón de arriba o el de la pestaña 🏆 Bracket Interactivo.")
