"""pages/12_🔍_Explorador_Datos.py"""
import streamlit as st
import soccerdata as sd
import unicodedata
from utils.style_loader import load_css

st.set_page_config(page_title="Explorador · Mundial 2026", page_icon="🔍", layout="wide")
load_css()

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#00B4DB,#0083B0);
margin-bottom:20px;border-radius:12px;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">🔍 Explorador de Datos Universal</h1>
    <p style="margin:0;color:#E0F7FA;">Localiza Jugadores y Equipos en FBref</p>
</div>""", unsafe_allow_html=True)

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn')

@st.cache_data(show_spinner="Descargando datos de FBref...")
def fetch_fbref_players(leagues, seasons='2324'):
    fb = sd.FBref(leagues=list(leagues), seasons=seasons)
    return fb.read_player_season_stats(stat_type='standard')

@st.cache_data(show_spinner="Descargando datos de equipos...")
def fetch_fbref_teams(leagues, seasons='2324'):
    fb = sd.FBref(leagues=list(leagues), seasons=seasons)
    return fb.read_team_season_stats()

query = st.text_input("Jugador o Equipo:", placeholder="Ej: Luis Diaz, Portugal, Real Madrid")
valid_leagues = ["Big 5 European Leagues Combined","ENG-Premier League","ESP-La Liga",
                 "FRA-Ligue 1","GER-Bundesliga","ITA-Serie A","INT-World Cup","INT-European Championship"]

col1, col2 = st.columns([2, 1])
with col1:
    league_scope = st.multiselect("Ligas:", valid_leagues, default=["ENG-Premier League","ESP-La Liga","INT-World Cup"])
with col2:
    search_type = st.radio("Tipo:", ["Jugador", "Equipo"], horizontal=True)

for k in ['df_search_results', 'df_search_type']:
    if k not in st.session_state:
        st.session_state[k] = None

if st.button("🚀 Escaneo Profundo", use_container_width=True, type="primary"):
    if not query:
        st.warning("Ingresa un término.")
    else:
        with st.spinner("Buscando en FBref..."):
            try:
                q_norm = strip_accents(query).lower()
                if search_type == "Jugador":
                    data = fetch_fbref_players(tuple(league_scope))
                    mask = data.index.get_level_values('player').map(lambda x: q_norm in strip_accents(x).lower())
                    st.session_state.df_search_results = data[mask]
                else:
                    data = fetch_fbref_teams(tuple(league_scope))
                    mask = data.index.get_level_values('team').map(lambda x: q_norm in strip_accents(x).lower())
                    st.session_state.df_search_results = data[mask]
                st.session_state.df_search_type = search_type
            except Exception as e:
                st.error(f"Error: {e}")

results = st.session_state.df_search_results
if results is not None and not results.empty:
    st.success(f"✅ {len(results)} resultado(s) encontrado(s)")
    for idx, row in results.iterrows():
        if st.session_state.df_search_type == "Jugador":
            league, season, team, player = idx
            with st.expander(f"👤 {player} · {team}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Goles", row.get(('Performance', 'Gls'), "N/A"),
                          help="Goles marcados en la temporada seleccionada.")
                c2.metric("Asistencias", row.get(('Performance', 'Ast'), "N/A"),
                          help="Asistencias de gol en la temporada seleccionada.")
                c3.metric("xG", row.get(('Expected', 'xG'), "N/A"),
                          help="Expected Goals: calidad de las ocasiones generadas. >0.5/partido = atacante élite.")
        else:
            league, _, team = idx
            with st.expander(f"🛡️ {team} · {league}", expanded=True):
                st.info(f"Datos de {team} en {league}.")
elif results is not None:
    st.error("No se encontraron coincidencias.")
