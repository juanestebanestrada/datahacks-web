#!/bin/bash
# Ir al directorio del proyecto
cd /home/esteban/Documentos/AntigravityPruebas/Mundial2026

# Forzar a Streamlit a usar la configuración local para saltar el prompt de email
export STREAMLIT_CONFIG_DIR="/home/esteban/Documentos/AntigravityPruebas/Mundial2026/.streamlit"

# Ejecutar Streamlit usando el python del entorno virtual
./venv/bin/streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false
