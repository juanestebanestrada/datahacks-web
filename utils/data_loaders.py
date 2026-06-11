"""
utils/data_loaders.py
Funciones de carga de datos de todas las fuentes:
StatsBomb, FotMob, SofaScore, 365Scores.
Con caché, paralelismo y manejo robusto de errores.
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from statsbombpy import sb
from LanusStats import FotMob, ThreeSixFiveScores, SofaScore
from LanusStats.exceptions import MatchDoesntHaveInfo
import json
import os

# ──────────────────────────────────────────────
# STATSBOMB — PARALELO
# ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cargar_tiros(pais: str, comp_id: int, seas_id: int):
    """Carga tiros de StatsBomb Open Data."""
    try:
        partidos = sb.matches(competition_id=comp_id, season_id=seas_id)
        mask = (partidos['home_team'] == pais) | (partidos['away_team'] == pais)
        partidos_equipo = partidos[mask]

        if partidos_equipo.empty:
            return None, f"No se encontraron partidos para '{pais}'."

        match_ids = partidos_equipo['match_id'].tolist()

        def fetch_shots_one(mid):
            try:
                eventos = sb.events(match_id=mid, split=True)
                if 'shots' in eventos:
                    return eventos['shots']
            except Exception:
                pass
            return None

        lista_tiros = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fetch_shots_one, mid): mid for mid in match_ids}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    lista_tiros.append(result)

        if not lista_tiros:
            return None, "No se encontraron datos de tiros."

        tiros = pd.concat(lista_tiros, ignore_index=True)
        tiros = tiros[tiros['team'] == pais].copy()

        if tiros.empty:
            return None, f"No hay tiros registrados para '{pais}'."

        tiros[['x', 'y']] = pd.DataFrame(tiros['location'].tolist(), index=tiros.index)
        tiros['shot_statsbomb_xg'] = tiros['shot_statsbomb_xg'].fillna(0.05)
        return tiros, None

    except Exception as e:
        return None, f"Error al cargar datos: {e}"


@st.cache_data(show_spinner=False)
def cargar_eventos(pais: str, comp_id: int, seas_id: int):
    """Carga TODOS los eventos de StatsBomb para un equipo (paralelo)."""
    try:
        partidos = sb.matches(competition_id=comp_id, season_id=seas_id)
        mask = (partidos['home_team'] == pais) | (partidos['away_team'] == pais)
        partidos_equipo = partidos[mask]

        if partidos_equipo.empty:
            return None, f"No se encontraron partidos para '{pais}'."

        match_ids = partidos_equipo['match_id'].tolist()

        def fetch_events_one(mid):
            try:
                ev = sb.events(match_id=mid)
                return ev[ev['team'] == pais]
            except Exception:
                return None

        lista_eventos = []
        progress = st.progress(0, text=f"Cargando partidos de {pais}...")
        total = len(match_ids)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fetch_events_one, mid): i for i, mid in enumerate(match_ids)}
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                if result is not None and not result.empty:
                    lista_eventos.append(result)
                completed += 1
                progress.progress(completed / total, text=f"Partido {completed}/{total} de {pais}")

        progress.empty()

        if not lista_eventos:
            return None, "No se encontraron eventos completos."

        df_completo = pd.concat(lista_eventos, ignore_index=True)
        df_completo = df_completo.dropna(subset=['location']).copy()
        df_completo[['x', 'y']] = pd.DataFrame(df_completo['location'].tolist(), index=df_completo.index)
        return df_completo, None

    except Exception as e:
        return None, f"Error al extraer eventos: {e}"


# ──────────────────────────────────────────────
# FOTMOB
# ──────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def cargar_tiros_fotmob(team_id: int):
    """Carga tiros de FotMob (últimos 10 partidos). TTL: 30 min."""
    try:
        fotmob = FotMob()
        data = fotmob.fotmob_request(f'teams?id={team_id}').json()
        fixtures_data = data.get('fixtures', {}).get('allFixtures', {}).get('fixtures', [])
        resultados = [f for f in fixtures_data if f.get('status', {}).get('finished')]

        if not resultados:
            return None, "No se encontraron partidos finalizados."

        lista_tiros = []
        for f in resultados[-10:]:
            try:
                sm = fotmob.get_match_shotmap(f['id'])
                if not sm.empty:
                    sm = sm[sm['teamId'] == team_id].copy()
                    if not sm.empty:
                        lista_tiros.append(sm)
            except MatchDoesntHaveInfo:
                continue
            except Exception:
                continue

        if not lista_tiros:
            return pd.DataFrame(), None

        tiros = pd.concat(lista_tiros, ignore_index=True)
        tiros['shot_outcome'] = tiros['eventType'].apply(lambda x: 'Goal' if 'Goal' in str(x) else x)
        tiros['x'] = tiros['x'] * 1.2
        tiros['y'] = tiros['y'] * 0.8
        if 'expectedGoals' in tiros.columns:
            tiros['shot_statsbomb_xg'] = tiros['expectedGoals'].fillna(0.05)
        else:
            tiros['shot_statsbomb_xg'] = 0.05
        return tiros, None

    except Exception as e:
        return None, f"Error FotMob: {e}"


# ──────────────────────────────────────────────
# SOFASCORE
# ──────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def cargar_tiros_sofascore(team_id: int):
    """Carga tiros de SofaScore."""
    try:
        ss = SofaScore()
        res = ss.sofascore_request(f'https://api.sofascore.com/api/v1/team/{team_id}/events/last/0')
        events = res.json().get('events', [])

        lista_tiros = []
        for event in events[:5]:
            mid = event.get('id')
            try:
                sm = ss.get_match_shotmap(mid)
                if not sm.empty:
                    sm = sm[sm['teamId'] == team_id].copy()
                    if not sm.empty:
                        lista_tiros.append(sm)
            except Exception:
                continue

        if not lista_tiros:
            return pd.DataFrame(), None

        tiros = pd.concat(lista_tiros, ignore_index=True)
        tiros['x'] = tiros['x'] * 1.2
        tiros['y'] = tiros['y'] * 0.8
        tiros['shot_outcome'] = tiros['isGoal'].apply(lambda x: 'Goal' if x else 'No Goal')
        tiros['shot_statsbomb_xg'] = tiros['expectedGoals'].fillna(0.05)
        return tiros, None

    except Exception as e:
        return pd.DataFrame(), f"Error SofaScore: {e}"


# ──────────────────────────────────────────────
# 365SCORES — IMPLEMENTACIÓN REAL
# ──────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def cargar_tiros_365scores(team_id: int):
    """Carga tiros de 365Scores."""
    try:
        tsf = ThreeSixFiveScores()
        # Intentar obtener los últimos eventos del equipo
        try:
            events = tsf.get_team_last_events(team_id, count=5) if hasattr(tsf, 'get_team_last_events') else []
        except Exception:
            events = []

        lista_tiros = []
        for ev in events:
            ev_id = ev.get('id') if isinstance(ev, dict) else None
            if ev_id is None:
                continue
            try:
                sm = tsf.get_match_shotmap(ev_id) if hasattr(tsf, 'get_match_shotmap') else pd.DataFrame()
                if not sm.empty:
                    sm = sm[sm.get('teamId', pd.Series()) == team_id].copy() if 'teamId' in sm.columns else sm
                    lista_tiros.append(sm)
            except Exception:
                continue

        if not lista_tiros:
            return pd.DataFrame(), None

        tiros = pd.concat(lista_tiros, ignore_index=True)
        if 'x' in tiros.columns:
            tiros['x'] = tiros['x'] * 1.2
            tiros['y'] = tiros['y'] * 0.8
        if 'isGoal' in tiros.columns:
            tiros['shot_outcome'] = tiros['isGoal'].apply(lambda x: 'Goal' if x else 'No Goal')
        if 'expectedGoals' in tiros.columns:
            tiros['shot_statsbomb_xg'] = pd.to_numeric(tiros['expectedGoals'], errors='coerce').fillna(0.05)
        else:
            tiros['shot_statsbomb_xg'] = 0.05

        return tiros, None

    except Exception as e:
        return pd.DataFrame(), f"Error 365Scores: {e}"


# ──────────────────────────────────────────────
# MÉTRICAS AVANZADAS
# ──────────────────────────────────────────────
def calcular_ppda(df_eventos: pd.DataFrame, equipo: str) -> float | None:
    """
    PPDA = Pases del rival en su propio campo / Acciones defensivas del equipo.
    Cuanto menor, más agresiva es la presión. Elite: <8.0
    """
    try:
        pases_rival = df_eventos[
            (df_eventos['team'] != equipo) &
            (df_eventos['type'] == 'Pass') &
            (df_eventos['x'] < 60)
        ]
        acciones_def = df_eventos[
            (df_eventos['team'] == equipo) &
            (df_eventos['type'].isin(['Pressure', 'Tackle', 'Interception', 'Block']))
        ]
        if len(acciones_def) == 0:
            return None
        return round(len(pases_rival) / len(acciones_def), 2)
    except Exception:
        return None


def calcular_progressive_passes(df_eventos: pd.DataFrame, equipo: str) -> int:
    """
    Pases progresivos: avanzan ≥10m hacia la portería rival (estándar FBref/StatsBomb).
    """
    try:
        pases = df_eventos[
            (df_eventos['team'] == equipo) &
            (df_eventos['type'] == 'Pass')
        ].copy()
        pases = pases.dropna(subset=['location', 'pass_end_location'])
        if pases.empty:
            return 0
        pases['x_start'] = pases['location'].apply(lambda l: l[0] if isinstance(l, list) else 0)
        pases['x_end']   = pases['pass_end_location'].apply(lambda l: l[0] if isinstance(l, list) else 0)
        return int(((pases['x_end'] - pases['x_start']) >= 10).sum())
    except Exception:
        return 0


def calcular_estadisticas_generales(tiros: pd.DataFrame) -> dict:
    """Calcula métricas resumen de un DataFrame de tiros."""
    n_tiros   = len(tiros)
    goles_df  = tiros[tiros.get('shot_outcome', pd.Series()) == 'Goal'] if 'shot_outcome' in tiros.columns else pd.DataFrame()
    n_goles   = len(goles_df)
    xg_total  = float(tiros['shot_statsbomb_xg'].sum()) if 'shot_statsbomb_xg' in tiros.columns else 0.0
    conv_rate = (n_goles / n_tiros * 100) if n_tiros > 0 else 0.0
    return {
        'n_tiros': n_tiros,
        'n_goles': n_goles,
        'xg_total': xg_total,
        'conv_rate': conv_rate,
    }

@st.cache_data(ttl=3600, show_spinner=False)
def get_team_real_performance_v2(team_name: str) -> float:
    """
    Calcula el xG base real de un equipo (V2 - Bypasses old cache).
    1. Normaliza y traduce el nombre del equipo para búsqueda robusta.
    2. Filtra partidos FINALIZADOS en fixtures.json.
    3. Si no hay datos suficientes, usa un mapeo de ranking/jerarquía verificado con las 48 selecciones del Mundial.
    """
    import unicodedata
    
    def normalize_name(name: str) -> str:
        if not name:
            return ""
        # Convertir a minúsculas y quitar acentos
        name = name.strip().lower()
        name = "".join(
            c for c in unicodedata.normalize('NFD', name)
            if unicodedata.category(c) != 'Mn'
        )
        name = name.replace("-", " ").replace("_", " ")
        return " ".join(name.split())

    try:
        # Mapeo de traducciones y sinónimos para asegurar coincidencia
        traducciones = {
            # Grupo A
            "rep checa": "Czech Republic", "czech republic": "Czech Republic", "czechia": "Czech Republic", "republica checa": "Czech Republic",
            "mexico": "Mexico",
            "sudafrica": "South Africa", "south africa": "South Africa",
            "corea del sur": "South Korea", "south korea": "South Korea", "korea republic": "South Korea", "korea": "South Korea",
            # Grupo B
            "bosnia": "Bosnia", "bosnia herzegovina": "Bosnia", "bosnia h": "Bosnia", "bosnia y herzegovina": "Bosnia",
            "canada": "Canada",
            "qatar": "Qatar",
            "suiza": "Switzerland", "switzerland": "Switzerland",
            # Grupo C
            "brasil": "Brazil", "brazil": "Brazil",
            "marruecos": "Morocco", "morocco": "Morocco",
            "haiti": "Haiti",
            "escocia": "Scotland", "scotland": "Scotland",
            # Grupo D
            "turquia": "Turkey", "turkey": "Turkey",
            "usa": "USA", "united states": "USA", "estados unidos": "USA",
            "paraguay": "Paraguay",
            "australia": "Australia",
            # Grupo E
            "alemania": "Germany", "germany": "Germany",
            "curazao": "Curaçao", "curacao": "Curaçao",
            "costa de marfil": "Ivory Coast", "ivory coast": "Ivory Coast",
            "ecuador": "Ecuador",
            # Grupo F
            "suecia": "Sweden", "sweden": "Sweden",
            "paises bajos": "Netherlands", "netherlands": "Netherlands", "holanda": "Netherlands",
            "japon": "Japan", "japan": "Japan",
            "tunez": "Tunisia", "tunisia": "Tunisia",
            # Grupo G
            "belgica": "Belgium", "belgium": "Belgium",
            "egipto": "Egypt", "egypt": "Egypt",
            "iran": "Iran",
            "nueva zelanda": "New Zealand", "new zealand": "New Zealand",
            # Grupo H
            "espana": "Spain", "spain": "Spain",
            "cabo verde": "Cape Verde", "cape verde": "Cape Verde", "cape verde islands": "Cape Verde",
            "arabia saudi": "Saudi Arabia", "arabia saudita": "Saudi Arabia", "saudi arabia": "Saudi Arabia",
            "uruguay": "Uruguay",
            # Grupo I
            "irak": "Iraq", "iraq": "Iraq",
            "francia": "France", "france": "France",
            "senegal": "Senegal",
            "noruega": "Norway", "norway": "Norway",
            # Grupo J
            "argentina": "Argentina",
            "argelia": "Algeria", "algeria": "Algeria",
            "austria": "Austria",
            "jordania": "Jordan", "jordan": "Jordan",
            # Grupo K
            "rd congo": "Congo DR", "congo dr": "Congo DR", "congo": "Congo DR", "republica democratica del congo": "Congo DR", "dr congo": "Congo DR",
            "portugal": "Portugal",
            "uzbekistan": "Uzbekistan",
            "colombia": "Colombia",
            # Grupo L
            "inglaterra": "England", "england": "England",
            "croacia": "Croatia", "croatia": "Croatia",
            "ghana": "Ghana",
            "panama": "Panama",
        }

        # Jerarquía base detallada con todos los 48 equipos (más Italia)
        ranking_jerarquia = {
            "Argentina": 2.20, "France": 2.10, "Spain": 2.10, "England": 2.00, "Brazil": 2.00, "Portugal": 1.95,
            "Germany": 1.90, "Netherlands": 1.90, "Belgium": 1.85, "Colombia": 1.85, "Uruguay": 1.85, "Croatia": 1.80, "Morocco": 1.80, "Italy": 1.80,
            "Switzerland": 1.75, "USA": 1.70, "Mexico": 1.70, "Japan": 1.70, "Senegal": 1.70, "Ecuador": 1.70,
            "Austria": 1.65, "Sweden": 1.65, "Turkey": 1.65, "Norway": 1.65, "South Korea": 1.65, "Czech Republic": 1.60, "Ivory Coast": 1.60, "Algeria": 1.60,
            "Egypt": 1.55, "Iran": 1.55, "Scotland": 1.50, "Paraguay": 1.50, "Australia": 1.50, "Uzbekistan": 1.50, "Bosnia": 1.50, "Canada": 1.50,
            "Qatar": 1.45, "Iraq": 1.45, "Saudi Arabia": 1.45, "Ghana": 1.45,
            "Tunisia": 1.40, "Cape Verde": 1.40, "Congo DR": 1.40, "South Africa": 1.40, "Panama": 1.40,
            "Jordan": 1.30, "Haiti": 1.25, "New Zealand": 1.20, "Curaçao": 1.20
        }

        # Normalizar y traducir la entrada
        norm_input = normalize_name(team_name)
        canonical_name = traducciones.get(norm_input, team_name)

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fixtures_path = os.path.join(base_path, 'fixtures.json')
        
        goles = []
        if os.path.exists(fixtures_path):
            with open(fixtures_path, 'r', encoding='utf-8') as f:
                fixtures = json.load(f)
            
            for match in fixtures:
                status = match.get('status', {})
                if status.get('finished') is True:
                    # Normalizar y traducir nombres en fixtures para comparar con el canonical
                    match_home = match['home']['name']
                    match_away = match['away']['name']
                    
                    canonical_home = traducciones.get(normalize_name(match_home), match_home)
                    canonical_away = traducciones.get(normalize_name(match_away), match_away)
                    
                    if canonical_home == canonical_name:
                        goles.append(match['home'].get('score', 0))
                    elif canonical_away == canonical_name:
                        goles.append(match['away'].get('score', 0))
                
        if len(goles) >= 3:
            return round(sum(goles) / len(goles), 2)
        else:
            # Búsqueda en la jerarquía robusta usando el nombre canónico
            return ranking_jerarquia.get(canonical_name, 1.4)
        
    except Exception:
        return 1.4

def get_team_real_performance(team_name: str) -> float:
    # Wrapper compatible que llama a la V2 para evadir caché vieja
    return get_team_real_performance_v2(team_name)

# ==============================================================================
# FALLBACKS Y CARGA UNIFICADA
# ==============================================================================

FOTMOB_FALLBACK_IDS = {
    "Rep. Checa": 8496,
    "México": 6710,
    "Sudáfrica": 6316,
    "Corea del Sur": 7804,
    "Bosnia": 10106,
    "Canadá": 5810,
    "Qatar": 5902,
    "Suiza": 6717,
    "Brasil": 8256,
    "Marruecos": 6262,
    "Haití": 5934,
    "Escocia": 8498,
    "Turquía": 6595,
    "USA": 6713,
    "Paraguay": 6724,
    "Australia": 6716,
    "Alemania": 8570,
    "Curazao": 287981,
    "Costa de Marfil": 6709,
    "Ecuador": 6707,
    "Suecia": 8520,
    "Países Bajos": 6708,
    "Japón": 6715,
    "Túnez": 6719,
    "Bélgica": 8263,
    "Egipto": 10255,
    "Irán": 6711,
    "Nueva Zelanda": 5820,
    "España": 6720,
    "Cabo Verde": 5888,
    "Arabia Saudí": 7795,
    "Uruguay": 5796,
    "Irak": 5819,
    "Francia": 6723,
    "Senegal": 6395,
    "Noruega": 8492,
    "Argentina": 6706,
    "Argelia": 6317,
    "Austria": 8255,
    "Jordania": 5816,
    "RD Congo": 6321,
    "Portugal": 8361,
    "Uzbekistán": 8700,
    "Colombia": 8258,
    "Inglaterra": 8491,
    "Croacia": 10155,
    "Ghana": 6714,
    "Panamá": 5922
}

STATSBOMB_FALLBACK_CFG = {
    "Rep. Checa": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Czech Republic", "torneo": "Euro 2024"},
    "México": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Mexico", "torneo": "Mundial 2022"},
    "Sudáfrica": {"comp_id": 1267, "seas_id": 107, "statsbomb_name": "South Africa", "torneo": "AFCON 2023"},
    "Corea del Sur": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "South Korea", "torneo": "Mundial 2022"},
    "Canadá": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Canada", "torneo": "Mundial 2022"},
    "Qatar": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Qatar", "torneo": "Mundial 2022"},
    "Suiza": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Switzerland", "torneo": "Euro 2024"},
    "Brasil": {"comp_id": 223, "seas_id": 282, "statsbomb_name": "Brazil", "torneo": "Copa América 2024"},
    "Marruecos": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Morocco", "torneo": "Mundial 2022"},
    "Escocia": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Scotland", "torneo": "Euro 2024"},
    "Turquía": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Turkey", "torneo": "Euro 2024"},
    "USA": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "United States", "torneo": "Mundial 2022"},
    "Paraguay": {"comp_id": 223, "seas_id": 282, "statsbomb_name": "Paraguay", "torneo": "Copa América 2024"},
    "Australia": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Australia", "torneo": "Mundial 2022"},
    "Alemania": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Germany", "torneo": "Euro 2024"},
    "Costa de Marfil": {"comp_id": 1267, "seas_id": 107, "statsbomb_name": "Côte d'Ivoire", "torneo": "AFCON 2023"},
    "Ecuador": {"comp_id": 223, "seas_id": 282, "statsbomb_name": "Ecuador", "torneo": "Copa América 2024"},
    "Suecia": {"comp_id": 55, "seas_id": 43, "statsbomb_name": "Sweden", "torneo": "Euro 2020"},
    "Países Bajos": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Netherlands", "torneo": "Euro 2024"},
    "Japón": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Japan", "torneo": "Mundial 2022"},
    "Túnez": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Tunisia", "torneo": "Mundial 2022"},
    "Bélgica": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Belgium", "torneo": "Euro 2024"},
    "Egipto": {"comp_id": 1267, "seas_id": 107, "statsbomb_name": "Egypt", "torneo": "AFCON 2023"},
    "Irán": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Iran", "torneo": "Mundial 2022"},
    "España": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Spain", "torneo": "Euro 2024"},
    "Cabo Verde": {"comp_id": 1267, "seas_id": 107, "statsbomb_name": "Cape Verde Islands", "torneo": "AFCON 2023"},
    "Arabia Saudí": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Saudi Arabia", "torneo": "Mundial 2022"},
    "Uruguay": {"comp_id": 223, "seas_id": 282, "statsbomb_name": "Uruguay", "torneo": "Copa América 2024"},
    "Francia": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "France", "torneo": "Mundial 2022"},
    "Senegal": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Senegal", "torneo": "Mundial 2022"},
    "Argentina": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Argentina", "torneo": "Mundial 2022"},
    "Argelia": {"comp_id": 1267, "seas_id": 107, "statsbomb_name": "Algeria", "torneo": "AFCON 2023"},
    "Austria": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Austria", "torneo": "Euro 2024"},
    "RD Congo": {"comp_id": 1267, "seas_id": 107, "statsbomb_name": "Congo DR", "torneo": "AFCON 2023"},
    "Portugal": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Portugal", "torneo": "Euro 2024"},
    "Colombia": {"comp_id": 223, "seas_id": 282, "statsbomb_name": "Colombia", "torneo": "Copa América 2024"},
    "Inglaterra": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "England", "torneo": "Euro 2024"},
    "Croacia": {"comp_id": 55, "seas_id": 282, "statsbomb_name": "Croatia", "torneo": "Euro 2024"},
    "Ghana": {"comp_id": 43, "seas_id": 106, "statsbomb_name": "Ghana", "torneo": "Mundial 2022"}
}

def _intentar_cargar_tiros_fuente(fuente: str, pais: str, cfg: dict):
    """Llamador interno para probar fuentes específicas."""
    try:
        if fuente == 'statsbomb':
            comp_id = cfg.get('comp_id')
            seas_id = cfg.get('seas_id')
            sb_name = cfg.get('statsbomb_name')
            if not comp_id or not seas_id or not sb_name:
                fb = STATSBOMB_FALLBACK_CFG.get(pais)
                if fb:
                    comp_id = fb['comp_id']
                    seas_id = fb['seas_id']
                    sb_name = fb['statsbomb_name']
                else:
                    return None, "No hay parámetros de StatsBomb."
            return cargar_tiros(sb_name, comp_id, seas_id)
            
        elif fuente == 'fotmob':
            team_id = cfg.get('team_id')
            if not team_id:
                team_id = FOTMOB_FALLBACK_IDS.get(pais)
            if not team_id:
                return None, "No hay ID de FotMob."
            return cargar_tiros_fotmob(team_id)
            
        elif fuente == 'sofascore':
            team_id = cfg.get('team_id')
            if not team_id:
                return None, "No hay ID de SofaScore."
            return cargar_tiros_sofascore(team_id)
            
        elif fuente == '365scores':
            team_id = cfg.get('team_id')
            if not team_id:
                return None, "No hay ID de 365Scores."
            return cargar_tiros_365scores(team_id)
            
    except Exception as e:
        return None, str(e)
    return None, f"Fuente '{fuente}' no soportada."

def cargar_tiros_unified(pais: str, cfg: dict):
    """
    Carga tiros intentando primero la fuente configurada, y luego hace
    un barrido en cascada de fuentes alternativas hasta obtener datos.
    """
    fuente_principal = cfg.get('fuente', 'statsbomb')
    errors = []
    
    # 1. Intentar fuente principal
    tiros, err = _intentar_cargar_tiros_fuente(fuente_principal, pais, cfg)
    if tiros is not None and not tiros.empty:
        return tiros, None, fuente_principal
    
    if err:
        errors.append(f"{fuente_principal}: {err}")
    else:
        errors.append(f"{fuente_principal}: No se encontraron tiros.")
        
    # 2. Cascada
    fuentes_probar = ['statsbomb', 'fotmob', 'sofascore', '365scores']
    if fuente_principal in fuentes_probar:
        fuentes_probar.remove(fuente_principal)
        
    for f in fuentes_probar:
        tiros, err = _intentar_cargar_tiros_fuente(f, pais, cfg)
        if tiros is not None and not tiros.empty:
            return tiros, None, f
        if err:
            errors.append(f"{f}: {err}")
            
    return None, "Ninguna fuente tiene tiros disponibles. Historial de errores:\n" + "\n".join(errors), None

def cargar_eventos_unified(pais: str, cfg: dict):
    """
    Carga eventos intentando primero con los datos de StatsBomb del torneo principal.
    Si no está configurado, utiliza la configuración histórica de fallback de StatsBomb.
    """
    comp_id = cfg.get('comp_id')
    seas_id = cfg.get('seas_id')
    sb_name = cfg.get('statsbomb_name')
    
    if cfg.get('fuente') != 'statsbomb' or not comp_id or not seas_id or not sb_name:
        fb = STATSBOMB_FALLBACK_CFG.get(pais)
        if fb:
            comp_id = fb['comp_id']
            seas_id = fb['seas_id']
            sb_name = fb['statsbomb_name']
        else:
            return None, f"No hay eventos históricos de StatsBomb disponibles para '{pais}'."
            
    return cargar_eventos(sb_name, comp_id, seas_id)

