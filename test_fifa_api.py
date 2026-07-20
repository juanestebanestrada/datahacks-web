# -*- coding: utf-8 -*-
"""
test_fifa_api.py — Script para demostrar en terminal la conexión en vivo con la API del Mundial (Football-Data.org)
Muestra el envío de cabeceras, tiempos de respuesta y datos de grupos en vivo.
"""
import sys
import io
import time
import requests

# Configurar consola de Windows para UTF-8 (evita errores con caracteres especiales)
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Credenciales de la API de Football-Data.org (Servidor oficial de datos del Mundial)
TOKEN = "5acb2fefb13049828c5d34d10fb49850"
HEADERS = {"X-Auth-Token": TOKEN}
URL_WORLD_CUP = "http://api.football-data.org/v4/competitions/2000/standings"

def test_connection():
    print("\n" + "="*70)
    print("📡 PRUEBA DE CONEXIÓN EN VIVO: API OFICIAL MUNDIAL 2026 (Football-Data)")
    print("="*70)
    
    print(f"🔗 URL Objetivo: {URL_WORLD_CUP}")
    print(f"🔑 Cabeceras enviadas: {{'X-Auth-Token': '{TOKEN[:6]}...{TOKEN[-4:]}'}}")
    print("\n⏳ Realizando petición HTTP GET...")
    
    start_time = time.time()
    try:
        response = requests.get(URL_WORLD_CUP, headers=HEADERS, timeout=12)
        latency = (time.time() - start_time) * 1000
        
        print(f"✅ Respuesta recibida en {latency:.2f} ms")
        print(f"📊 Código de Estado HTTP: {response.status_code} ({'OK - Conexión Exitosa' if response.status_code == 200 else 'Error'})")
        
        if response.status_code == 200:
            data = response.json()
            competition = data.get('competition', {})
            season = data.get('season', {})
            
            print("\n" + "-"*40)
            print("🏆 DATOS DE LA COMPETICIÓN RECUPERADOS:")
            print("-"*40)
            print(f"   - Nombre:    {competition.get('name')} ({competition.get('code')})")
            print(f"   - Área/Ente: {competition.get('area', {}).get('name')}")
            print(f"   - Temporada: {season.get('startDate')} hasta {season.get('endDate')}")
            
            standings = data.get('standings', [])
            if standings:
                print("\n" + "-"*40)
                print("👥 MUESTRA DE GRUPOS ACTIVOS DESDE LA API:")
                print("-"*40)
                # Mostrar los primeros 3 grupos como muestra de datos vivos
                for group_data in standings[:3]:
                    group_name = group_data.get('group', 'Grupo Desconocido')
                    # Traducir GROUP_A -> GRUPO A
                    group_display = group_name.replace("GROUP_", "GRUPO ")
                    print(f"\n   📍 {group_display}:")
                    
                    table = group_data.get('table', [])
                    for position, team_entry in enumerate(table[:4], 1):
                        team_name = team_entry.get('team', {}).get('name')
                        played = team_entry.get('playedGames', 0)
                        points = team_entry.get('points', 0)
                        print(f"      {position}. {team_name:<24} | PJ: {played} | Pts: {points}")
            else:
                print("\n⚠️ No se encontraron tablas de posiciones cargadas en esta temporada todavía.")
                
        else:
            print(f"\n❌ Fallo en la respuesta. Contenido del Error:\n{response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Error: La petición excedió el tiempo límite de conexión (Timeout).")
    except Exception as e:
        print(f"\n❌ Error Inesperado al Conectar: {e}")
        
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_connection()
