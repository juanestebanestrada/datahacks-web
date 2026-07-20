"""pages/6_📡_ESPN_Live.py"""
import streamlit as st
import requests
from utils.style_loader import load_css

st.set_page_config(page_title="ESPN Live · Mundial 2026", page_icon="📡", layout="wide")
load_css()

st.markdown("""<div class="hero" style="padding:30px;background:linear-gradient(135deg,#cc0000,#330000);">
    <h1 class="hero-title" style="font-size:2.5rem;">📡 ESPN Live Predictor</h1>
    <p class="hero-sub">Probabilidades Algorítmicas · API Oculta ESPN</p>
</div>""", unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
def get_espn_scoreboard(slug):
    try:
        res = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard", timeout=10)
        return (res.json(), None) if res.status_code == 200 else (None, f"Error {res.status_code}")
    except Exception as e:
        return None, str(e)

def parse_american_odds(val):
    try:
        v = float(val)
        return 100/(v+100) if v > 0 else (-v/(-v+100) if v < 0 else 0)
    except Exception:
        return 0

col_menu, _ = st.columns([1, 2])
with col_menu:
    league = st.selectbox("Torneo en Vivo", [
        ("Premier League", "eng.1"),("LaLiga", "esp.1"),
        ("Clasificatorias Conmebol", "conmebol.worldq.conmebol"),
        ("Champions League", "uefa.champions"),("Mundial FIFA", "fifa.world")
    ], format_func=lambda x: x[0])

data, err = get_espn_scoreboard(league[1])
if err:
    st.error(f"Error ESPN: {err}")
else:
    events = data.get("events", [])
    if not events:
        st.info("No hay partidos en vivo o programados actualmente.")
    else:
        st.markdown(f"### {len(events)} Evento(s)")
        for event in events:
            status = event.get('status', {}).get('type', {}).get('description', '')
            clock  = event.get('status', {}).get('displayClock', '')
            comp   = event.get('competitions', [{}])[0]
            home_team, away_team = {}, {}
            for c in comp.get('competitors', []):
                t = {"name": c.get('team', {}).get('displayName', ''),
                     "logo": c.get('team', {}).get('logo', ''),
                     "score": c.get('score', '0')}
                if c.get('homeAway') == 'home': home_team = t
                else: away_team = t
            st.markdown(f"""
            <div style="background:#111827;padding:20px;border-radius:12px;border:1px solid #374151;margin-bottom:20px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:15px;">
                    <span style="color:#9CA3AF;">{status} {clock}</span>
                    <span style="color:#9CA3AF;">ESPN</span>
                </div>
                <div style="display:flex;justify-content:space-around;align-items:center;">
                    <div style="text-align:center;width:33%;">
                        <img src="{home_team.get('logo','')}" width="60" style="margin-bottom:10px;">
                        <h3 style="margin:0;">{home_team.get('name','')}</h3>
                        <h2 style="margin:0;font-size:3rem;">{home_team.get('score','')}</h2>
                    </div>
                    <div style="text-align:center;width:33%;color:#6B7280;font-size:1.5rem;font-weight:bold;">VS</div>
                    <div style="text-align:center;width:33%;">
                        <img src="{away_team.get('logo','')}" width="60" style="margin-bottom:10px;">
                        <h3 style="margin:0;">{away_team.get('name','')}</h3>
                        <h2 style="margin:0;font-size:3rem;">{away_team.get('score','')}</h2>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
