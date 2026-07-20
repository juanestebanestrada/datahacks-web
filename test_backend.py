# -*- coding: utf-8 -*-
"""
test_backend.py — Script de prueba para demostrar el funcionamiento del Back-End.
Muestra el simulador de Poisson, el cálculo de xT y la generación por IA.
"""
import sys
import os
import io

# Configurar salida UTF-8 en consolas Windows para evitar UnicodeEncodeError con emojis
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tactical_models import TacticalExpectedThreat
from core.xpts_simulator import ExpectedPointsSimulator
from core.ai_generator import _generate

def test_tactical_model():
    print("\n" + "="*50)
    print("🎯 DEMOSTRACIÓN 1: MODELO TÁCTICO DE EXPECTED THREAT (xT)")
    print("="*50)
    
    extractor = TacticalExpectedThreat()
    
    # Simular diferentes acciones en el campo
    # Formato: start_x, start_y, end_x, end_y
    # StatsBomb Pitch: 120 x 80
    acciones = [
        ("Pase hacia atrás en defensa", 30, 40, 15, 40),
        ("Pase progresivo de James a Lucho (Entrada a 3/4)", 60, 20, 95, 15),
        ("Pase lateral en mediocampo", 50, 20, 50, 60),
        ("Pase cruzado profundo al área rival", 75, 10, 110, 40)
    ]
    
    for desc, sx, sy, ex, ey in acciones:
        xt_added = extractor.calculate_xt_added(sx, sy, ex, ey)
        status = "🔥 Aumento de Peligro" if xt_added > 0 else "🛡️ Control de Posesión (Negativo)"
        print(f"- {desc}:")
        print(f"  Coords: ({sx}, {sy}) -> ({ex}, {ey})")
        print(f"  xT Añadido: {xt_added:+.5f} | Estado: {status}")

def test_poisson_simulator():
    print("\n" + "="*50)
    print("📈 DEMOSTRACIÓN 2: SIMULADOR DE PUNTOS ESPERADOS (xPts)")
    print("="*50)
    
    sim = ExpectedPointsSimulator(simulations=10000)
    
    # Portugal (Dominante) vs Colombia (Contragolpeador)
    home_xg, away_xg = 2.45, 1.15
    print(f"Partido de Simulación: Portugal ({home_xg} xG) vs Colombia ({away_xg} xG)\n")
    
    # 1. Método Analítico
    print("⏳ Ejecutando Método Analítico Bivariado (Poisson)...")
    res = sim.compute_xpts(home_xg, away_xg)
    probs = res['Win_Probabilities']
    print(f"   - Victoria Portugal: {probs['Home_Win']*100:.2f}%")
    print(f"   - Empate:            {probs['Draw']*100:.2f}%")
    print(f"   - Victoria Colombia: {probs['Away_Win']*100:.2f}%")
    print(f"   - xPts Portugal:     {res['Home_xPts']} pts")
    print(f"   - xPts Colombia:     {res['Away_xPts']} pts\n")
    
    # 2. Método Estocástico (Monte Carlo)
    print("🎲 Ejecutando Simulación de Monte Carlo (10,000 iteraciones)...")
    mc = sim.monte_carlo_xpts(home_xg, away_xg)
    print(f"   - Victoria Portugal (MC): {mc['MC_Home_Win']*100:.2f}%")
    print(f"   - Empate (MC):            {mc['MC_Draw']*100:.2f}%")
    print(f"   - Victoria Colombia (MC): {mc['MC_Away_Win']*100:.2f}%\n")
    
    # 3. Convergencia
    diff = abs(mc['MC_Home_Win'] - probs['Home_Win'])
    print(f"📊 Diferencial de Convergencia (Analítico vs Monte Carlo):")
    print(f"   Δ = {diff:.5f} ({'✅ OK (Convergencia Óptima < 0.01)' if diff < 0.01 else '⚠️ Variación Mayor'})")

def test_ai_integration():
    print("\n" + "="*50)
    print("🧠 DEMOSTRACIÓN 3: PRUEBA DE GATEWAY DE IA (CON FALLBACK)")
    print("="*50)
    
    prompt = "Dame una frase de 10 palabras analizando táctica de fútbol con tono científico."
    print(f"Enviando Prompt a Gateway IA: '{prompt}'\n")
    
    # Llamamos a la función privada _generate que gestiona Gemini -> Grok -> Ollama
    texto, error = _generate(prompt, force_ollama=False)
    
    if error:
        print(f"❌ Error en Gateway de IA: {error}")
    else:
        print(f"🤖 Respuesta de la IA:\n\"{texto.strip()}\"")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_tactical_model()
    test_poisson_simulator()
    test_ai_integration()
