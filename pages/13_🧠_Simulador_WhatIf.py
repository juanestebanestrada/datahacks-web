import streamlit as st
import pandas as pd
from core.ai_generator import _generate  # Usamos tu motor híbrido existente
from utils.style_loader import load_css

st.set_page_config(page_title="Simulador What-If · Mundial 2026", page_icon="🧠", layout="wide")
load_css()

st.markdown("""<div class="hero" style="padding:30px;background:linear-gradient(135deg,#1b0033,#3d0075);">
    <h1 class="hero-title" style="font-size:2.5rem;">🧠 Simulador de Escenarios Dinámicos</h1>
    <p class="hero-sub">Inyecta variables externas y analiza el impacto táctico con IA Híbrida</p>
</div>""", unsafe_allow_html=True)

st.info("Este módulo utiliza el sistema híbrido Gemini / Grok configurado en tu plataforma.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ Configuración del Partido")
    equipo_a = st.text_input("Selección A", "Argentina")
    equipo_b = st.text_input("Selección B", "Brasil")
    
    opciones_sede = [
        "🏟️ Estadio Neutral (Sin ventaja)",
        f"🏠 Localía para {equipo_a}",
        f"🏠 Localía para {equipo_b}"
    ]
    sede_partido = st.selectbox("Sede del Partido", opciones_sede, index=0)
    
    st.subheader("🚩 Anomalías Predefinidas")
    opciones = [
        "Messi lesionado (Baja de creatividad -25%)",
        "Crisis institucional en la federación visitante",
        "Clima extremo (Lluvia/Calor intenso)",
        "Altitud extrema (+3600m)",
        "Expulsión del arquero titular al minuto 10",
        "Vestuario roto: Conflicto entre estrellas"
    ]
    
    # Cargar alertas en tiempo real desde el Centro de Alertas
    import json
    import os
    dynamic_options = []
    alerts_data = []
    
    # 1. Intentar desde st.session_state
    if "current_alerts" in st.session_state and st.session_state.current_alerts:
        alerts_data = st.session_state.current_alerts
    # 2. Intentar leer desde active_alerts.json
    elif os.path.exists("data/active_alerts.json"):
        try:
            with open("data/active_alerts.json", "r", encoding="utf-8") as f:
                alerts_data = json.load(f)
        except Exception:
            pass
            
    for alert in alerts_data:
        cat = alert.get('categoria', 'Otros')
        if cat in ["Lesión", "Polémica", "Convocatoria", "Fichaje"]:
            fig = alert.get('figura_afectada', 'N/A')
            resumen = alert.get('resumen', '')
            urg = alert.get('urgencia', 'Baja')
            opt_str = f"🚨 [{cat}] {fig} ({urg}): {resumen}"
            dynamic_options.append(opt_str)
            
    if dynamic_options:
        st.caption("📡 *Se detectaron alertas en tiempo real del feed de noticias (disponibles abajo)*")
        
    opciones_totales = opciones + dynamic_options
    anomalias_sel = st.multiselect("Selecciona una o más:", opciones_totales)

with col2:
    st.subheader("✍️ Escenario Personalizado")
    custom = st.text_area("Describe cualquier otra variable (política, social, médica):", 
                          placeholder="Ej: El país local declaró feriado nacional y el estadio es una caldera...")
    
    st.subheader("🔬 Profundidad del Análisis")
    profundidad = st.select_slider("Nivel de detalle de la IA", options=["Rápido", "Estándar", "Profundo"])

st.sidebar.divider()
# Los controles de IA ahora son globales y se cargan desde style_loader.py

if st.button("🚀 Iniciar Simulación Cuántica"):
    todas_anomalias = anomalias_sel + ([custom] if custom else [])
    
    if not todas_anomalias:
        # --- CASO BASE: DATOS REALES ---
        with st.spinner("Extrayendo estadísticas reales del historial..."):
            from core.xpts_simulator import ExpectedPointsSimulator
            from utils.data_loaders import get_team_real_performance_v2
            
            sim = ExpectedPointsSimulator()
            
            # Obtenemos el promedio de gol real del historial de cada equipo
            home_xg_real = get_team_real_performance_v2(equipo_a)
            away_xg_real = get_team_real_performance_v2(equipo_b)
            
            # Ajuste dinámico de localía según la sede elegida
            home_xg = home_xg_real
            away_xg = away_xg_real
            
            if "Neutral" in sede_partido:
                estadio_status_str = "Sin ventaja de localía (Estadio Neutral)"
            elif equipo_a in sede_partido:
                home_xg += 0.15
                estadio_status_str = f"+0.15 xG a {equipo_a} (Ventaja de Local)"
            elif equipo_b in sede_partido:
                away_xg += 0.15
                estadio_status_str = f"+0.15 xG a {equipo_b} (Ventaja de Local)"
            else:
                estadio_status_str = "Sin ventaja de localía (Estadio Neutral)"
            
            res = sim.compute_xpts(home_xg, away_xg)
            probs = res['Win_Probabilities']
            
            st.success(f"📊 Análisis de Caso Base (Historial: {equipo_a} vs {equipo_b})")
            
            # Visualización de Probabilidades
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Victoria {equipo_a}", f"{probs['Home_Win']*100:.1f}%")
            c2.metric("Empate", f"{probs['Draw']*100:.1f}%")
            c3.metric(f"Victoria {equipo_b}", f"{probs['Away_Win']*100:.1f}%")
            
            st.markdown(f"""
            ### 📝 Informe Basado en Datos Reales
            Este análisis se ha generado procesando el historial de goles en el archivo **`fixtures.json`**.
            
            *   **Promedio Histórico {equipo_a}:** {home_xg_real} goles/partido.
            *   **Promedio Histórico {equipo_b}:** {away_xg_real} goles/partido.
            *   **Ajuste de Estadio:** {estadio_status_str}
            *   **Metodología:** Distribución de Poisson Bivariada sobre rendimiento verificado.
            
            > [!IMPORTANT]
            > Los datos mostrados arriba son el **"Estado Base"**. Para ver cómo factores externos (lesiones, clima, etc.) alteran estas probabilidades, selecciona anomalías en el panel lateral.
            """)
    else:
        # --- CASO CON IA: MOTOR HÍBRIDO ---
        with st.spinner("La IA está calculando el impacto de las anomalías..."):
            # Construcción del Prompt Maestro
            anomalias_str = "\n".join([f"- {a}" for a in todas_anomalias])
            prompt = f"""
            ACTÚA COMO UN MOTOR DE SIMULACIÓN TÁCTICA AVANZADA PARA EL MUNDIAL 2026.
            PARTIDO: {equipo_a} vs {equipo_b}
            TIPO DE ENCUENTRO: {sede_partido}
            ANOMALÍAS DETECTADAS:
            {anomalias_str}
            PROFUNDIDAD: {profundidad}
            
            TAREA:
            1. Analiza el impacto táctico y psicológico de estas variables.
            2. Proporciona nuevas PROBABILIDADES de resultado (Victoria A, Empate, Victoria B).
            3. Escribe la 'Narrativa del Caos' (resumen de cómo se daría el partido).
            4. Identifica a los jugadores más afectados.
            
            Formato: Markdown con emojis.
            """
            
            resultado, error = _generate(prompt)
            
            if error:
                st.error(f"❌ Error en la simulación: {error}")
            else:
                st.success("✅ Simulación de Caos completada.")
                st.markdown(resultado)
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar Reporte de Anomalías (MD)",
                    data=resultado,
                    file_name=f"simulacion_caos_{equipo_a}_{equipo_b}.md",
                    mime="text/markdown"
                )
