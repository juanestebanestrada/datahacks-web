"""pages/4_🌍_WC2026_Oficial.py"""
import streamlit as st
import requests
import pandas as pd
from config import API_FOOTBALL_DATA_TOKEN, COMMON_HEADERS
from utils.style_loader import load_css

st.set_page_config(page_title="WC 2026 Oficial · Mundial 2026", page_icon="🌍", layout="wide")
load_css()
st.markdown("""<div class="hero" style="padding:30px;background:linear-gradient(135deg,#1b0033,#3d0075);">
    <h1 class="hero-title" style="font-size:2.5rem;">🌍 Mundial 2026 Oficial</h1>
    <p class="hero-sub">Clasificaciones verificadas · Football-Data.org</p>
</div>""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def get_wc_standings():
    url = "http://api.football-data.org/v4/competitions/2000/standings"
    headers = {**COMMON_HEADERS, "X-Auth-Token": API_FOOTBALL_DATA_TOKEN}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json(), None
        return None, f"Error HTTP {res.status_code}"
    except Exception as e:
        return None, str(e)

with st.spinner("Conectando con Football-Data.org..."):
    data, err = get_wc_standings()

if err:
    st.error(f"⚠️ {err}")
elif data and 'standings' in data:
    st.success("✅ Conectado a Football-Data.org")
    for group_data in data['standings']:
        if group_data.get('type') == 'TOTAL':
            g = group_data.get('group', '').replace('_', ' ')
            st.markdown(f"#### 🏆 {g}")
            filas = []
            for row in group_data.get('table', []):
                t = row['team']
                filas.append({"Pos":row['position'],"Equipo":t['name'],"PJ":row['playedGames'],
                              "G":row['won'],"E":row['draw'],"P":row['lost'],
                              "GF":row['goalsFor'],"GC":row['goalsAgainst'],
                              "DG":row['goalDifference'],"Pts":row['points']})
            if filas:
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
