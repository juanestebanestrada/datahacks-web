"""pages/7_📰_Panel_Informativo.py"""
import streamlit as st
import requests
import pandas as pd
from config import API_FOOTBALL_DATA_TOKEN
from utils.style_loader import load_css

st.set_page_config(page_title="Panel Informativo · Mundial 2026", page_icon="📰", layout="wide")
load_css()

st.markdown("""<div class="hero">
    <div class="hero-tag">API · Football-Data.org</div>
    <h1 class="hero-title">📰 Panel Informativo Global</h1>
    <p class="hero-sub">Resultados · Fixtures · Tablas · Goleadores</p>
</div>""", unsafe_allow_html=True)

competiciones = {
    "Premier League": "PL", "La Liga": "PD", "Serie A": "SA",
    "Bundesliga": "BL1", "Ligue 1": "FL1", "Champions League": "CL", "Mundial 2026": "WC"
}
comp_nombre = st.selectbox("🏆 Competición:", list(competiciones.keys()))
competition_code = competiciones[comp_nombre]

def _fetch(endpoint):
    url = f"https://api.football-data.org/v4/competitions/{competition_code}/{endpoint}"
    try:
        res = requests.get(url, headers={"X-Auth-Token": API_FOOTBALL_DATA_TOKEN}, timeout=15)
        if res.status_code == 200: return res.json(), None
        elif res.status_code == 429: return None, "⚠️ Límite de peticiones alcanzado. Intenta en un minuto."
        elif res.status_code in [400, 404]: return None, "Datos no disponibles para esta competición."
        return None, f"Error HTTP {res.status_code}"
    except Exception as e:
        return None, f"Error de conexión: {e}"

tab_res, tab_fix, tab_table, tab_scorers = st.tabs(["⚽ Resultados", "📅 Próximos Partidos", "🏆 Tabla", "👟 Goleadores"])

with tab_res:
    data, err = _fetch('matches?status=FINISHED')
    if err: st.error(err)
    elif data:
        for m in sorted(data.get('matches', []), key=lambda x: x['utcDate'], reverse=True)[:20]:
            score = f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}"
            st.markdown(f"""<div class="result-card">
                <span style="color:#fff;font-weight:700;">{m['homeTeam']['name']}</span>
                <span class="result-score">{score}</span>
                <span style="color:#fff;font-weight:700;">{m['awayTeam']['name']}</span>
            </div>
            <div class="result-date">{m['utcDate'][:10]}</div>""", unsafe_allow_html=True)

with tab_fix:
    data, err = _fetch('matches?status=IN_PLAY,PAUSED,SCHEDULED,TIMED')
    if err: st.error(err)
    elif data:
        for m in data.get('matches', [])[:20]:
            live = m['status'] in ['IN_PLAY', 'PAUSED']
            h = m.get('score', {}).get('fullTime', {}).get('home', 0) or 0
            a = m.get('score', {}).get('fullTime', {}).get('away', 0) or 0
            badge = f'<span style="color:#ff4b4b;font-weight:900;">🔴 {h} - {a}</span>' if live else '<span style="color:#5badff;">VS</span>'
            st.markdown(f"""<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                border-radius:12px;padding:14px 20px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#fff;font-weight:700;">{m['homeTeam']['name']}</span>
                    {badge}
                    <span style="color:#fff;font-weight:700;">{m['awayTeam']['name']}</span>
                </div>
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);text-align:center;">📅 {m['utcDate'][:10]} {m['utcDate'][11:16]} UTC</div>
            </div>""", unsafe_allow_html=True)

with tab_table:
    data, err = _fetch('standings')
    if err: st.error(err)
    elif data:
        table_data = next((s['table'] for s in data.get('standings', []) if s['type'] == 'TOTAL'), None)
        if table_data:
            rows = [{"Pos":r['position'],"Equipo":r['team']['name'],"PJ":r['playedGames'],
                     "G":r['won'],"E":r['draw'],"P":r['lost'],"GF":r['goalsFor'],
                     "GC":r['goalsAgainst'],"DG":r['goalDifference'],"Pts":r['points']} for r in table_data]
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.info("Tabla no disponible.")

with tab_scorers:
    data, err = _fetch('scorers')
    if err: st.error(err)
    elif data:
        rows = [{"Jugador":s['player']['name'],"Equipo":s['team']['name'],
                 "Goles":s['goals'],"Asistencias":s.get('assists', 0)} for s in data.get('scorers', [])]
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.info("Sin datos de goleadores.")
