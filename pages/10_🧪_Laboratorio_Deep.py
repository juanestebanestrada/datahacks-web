"""pages/10_🧪_Laboratorio_Deep.py — Monte Carlo + Similitud Vectorial"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.style_loader import load_css, copyable_dataframe
from core.xpts_simulator import ExpectedPointsSimulator
from core.player_similarity import ScoutingGenerativeSimilarity
from core.ai_generator import generar_dossier_scouting

st.set_page_config(page_title="Laboratorio Deep · Mundial 2026", page_icon="🧪", layout="wide")
load_css()

st.markdown("""<div style="padding:20px;background:linear-gradient(135deg,#4A00E0,#8E2DE2);
margin-bottom:20px;border-radius:12px;">
    <h1 style="margin:0;font-size:2rem;color:#fff;">🧪 Laboratorio Deep Analytics</h1>
    <p style="margin:0;color:#E8F0FE;">Poisson Bivariada + Similitud Coseno + IA Generativa</p>
</div>""", unsafe_allow_html=True)

tab_xpts, tab_scouting = st.tabs(["📊 Simulador xPts (Justicia Matemática)", "🔍 Scouting Generativo (Z-Score)"])

# ── SIMULADOR XPTS ──
with tab_xpts:
    st.write("**Simulación de Poisson Bivariada:** matriz de probabilidades cruzadas para calcular los puntos que cada equipo *matemáticamente merece* según su xG.")

    sim = ExpectedPointsSimulator(simulations=10000)
    st.subheader("Datos de Fase de Grupos en Tiempo Real")
    
    # Cargar los grupos reales
    import json
    import os
    
    grupos_dict = {}
    grupos_path = "data/grupos.json"
    if os.path.exists(grupos_path):
        try:
            with open(grupos_path, "r", encoding="utf-8") as f:
                grupos_dict = json.load(f)
        except Exception:
            pass
            
    if not grupos_dict:
        # Fallback en caso de que no se pueda leer
        grupos_dict = {
            "Grupo K": {
                "RD Congo": {}, "Portugal": {}, "Uzbekistán": {}, "Colombia": {}
            }
        }
        
    lista_grupos = list(grupos_dict.keys())
    
    grupo_seleccionado = st.selectbox(
        "Selecciona un Grupo para Simular:", 
        lista_grupos, 
        index=lista_grupos.index("Grupo K") if "Grupo K" in lista_grupos else 0
    )
    
    # Limpiar resultados si cambia el grupo
    if 'last_selected_group' not in st.session_state:
        st.session_state['last_selected_group'] = grupo_seleccionado
    elif st.session_state['last_selected_group'] != grupo_seleccionado:
        st.session_state['last_selected_group'] = grupo_seleccionado
        if 'justice_table' in st.session_state:
            del st.session_state['justice_table']
        if 'mc_validation' in st.session_state:
            del st.session_state['mc_validation']
            
    equipos_grupo = list(grupos_dict[grupo_seleccionado].keys())
    
    # Generar todos los partidos (round-robin: 6 partidos para 4 equipos)
    pairings = [
        (equipos_grupo[0], equipos_grupo[1]),
        (equipos_grupo[2], equipos_grupo[3]),
        (equipos_grupo[0], equipos_grupo[2]),
        (equipos_grupo[1], equipos_grupo[3]),
        (equipos_grupo[0], equipos_grupo[3]),
        (equipos_grupo[1], equipos_grupo[2])
    ]
    
    from utils.data_loaders import get_team_real_performance_v2
    
    matches_list = []
    for home, away in pairings:
        xg_home = get_team_real_performance_v2(home)
        xg_away = get_team_real_performance_v2(away)
        matches_list.append({
            'Team_Home': home,
            'Team_Away': away,
            'xG_Home': xg_home,
            'xG_Away': xg_away
        })
        
    df_matches = pd.DataFrame(matches_list)
    
    st.info("💡 Puedes editar los valores de xG directamente haciendo doble clic en las celdas de la tabla.")
    
    edited_df = st.data_editor(
        df_matches,
        column_config={
            "Team_Home": st.column_config.TextColumn("Local", disabled=True),
            "Team_Away": st.column_config.TextColumn("Visitante", disabled=True),
            "xG_Home": st.column_config.NumberColumn("xG Local", min_value=0.0, max_value=10.0, step=0.1, format="%.2f"),
            "xG_Away": st.column_config.NumberColumn("xG Visitante", min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_{grupo_seleccionado}"
    )

    col_sim1, col_sim2 = st.columns([2, 1])
    with col_sim2:
        if st.button("🎲 Ejecutar Simulación", use_container_width=True, type="primary"):
            with st.spinner("Calculando matriz de Poisson..."):
                justice_table = sim.generate_justice_table(edited_df)
                st.session_state['justice_table'] = justice_table

                # Validación Monte Carlo
                st.session_state['mc_validation'] = []
                for _, row in edited_df.iterrows():
                    mc = sim.monte_carlo_xpts(row['xG_Home'], row['xG_Away'])
                    analytical = sim.compute_xpts(row['xG_Home'], row['xG_Away'])
                    diff = abs(mc['MC_Home_Win'] - analytical['Win_Probabilities']['Home_Win'])
                    st.session_state['mc_validation'].append({
                        'Partido': f"{row['Team_Home']} vs {row['Team_Away']}",
                        'P(Local) Analítico': f"{analytical['Win_Probabilities']['Home_Win']:.3f}",
                        'P(Local) MC': f"{mc['MC_Home_Win']:.3f}",
                        'Convergencia (Δ)': f"{diff:.4f}"
                    })

    with col_sim1:
        if 'justice_table' in st.session_state:
            st.success("¡Justicia Matemática Aplicada!")
            jt = st.session_state['justice_table']
            copyable_dataframe(
                jt,
                label="justicia_matematica",
                key="justice_table",
                styled=jt.style.format({"Expected_Points": "{:.2f}"}).background_gradient(cmap='Purples')
            )

    if st.session_state.get('mc_validation'):
        with st.expander("🔬 Validación Monte Carlo (10k iteraciones)"):
            df_val = pd.DataFrame(st.session_state['mc_validation'])
            copyable_dataframe(df_val, label="validacion_montecarlo", key="mc_val")
            st.caption("Δ < 0.005 confirma que el método analítico de Poisson converge con la simulación estocástica.")

# ── SCOUTING GENERATIVO ──
with tab_scouting:
    st.write("**Motor Coseno Vectorial:** normalización Z-Score + distancia coseno para encontrar gemelos tácticos.")

    mock_scouting = pd.DataFrame({
        'player_name':    ['James Rodriguez','Bruno Fernandes','Abbosbek Fayzullaev','Chancel Mbemba','Pepe','Cristiano Ronaldo','Luis Diaz'],
        'xA_p90':         [0.40, 0.42, 0.10, 0.05, 0.02, 0.15, 0.30],
        'key_passes_p90': [3.10, 3.20, 0.50, 0.20, 0.10, 1.20, 2.50],
        'tackles_p90':    [0.50, 0.80, 3.00, 4.50, 4.80, 0.20, 1.50],
        'xg_p90':         [0.20, 0.25, 0.15, 0.05, 0.08, 0.90, 0.45],
    })
    copyable_dataframe(mock_scouting, label="base_scouting", key="scouting_base")

    scout_engine = ScoutingGenerativeSimilarity(mock_scouting)
    col1, col2 = st.columns(2)
    with col1:
        selected_player = st.selectbox("Jugador a Analizar:", mock_scouting['player_name'].values)
    with col2:
        st.write("")
        st.write("")
        btn_scout = st.button("🔍 Escanear Perfil Z-Score", type="primary")

    if btn_scout:
        with st.spinner("Calculando similitud coseno..."):
            prompt_res = scout_engine.find_most_similar(selected_player, top_n=2)
        st.subheader("Gemelos Tácticos Detectados:")
        st.text_area("Prompt para NotebookLM:", prompt_res, height=150)

        # Llamar a Gemini para explicación automática
        with st.spinner("Gemini generando análisis táctico..."):
            dossier, error = generar_dossier_scouting(selected_player, {"Tipo": "Análisis vectorial", "Similitud": "Top 2 detectados"})
        st.markdown("### 🤖 Análisis Generativo:")
        st.markdown(dossier)
        if error:
            st.error(f"Error de IA: {error}")
