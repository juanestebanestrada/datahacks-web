@echo off
cd /d "d:\AntigravityPruebas\Mundial2026"

echo Cerrando instancias previas de Streamlit...
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq streamlit" >nul 2>&1
timeout /t 1 /nobreak >nul

call .\venv_win\Scripts\activate.bat
echo Lanzando Mundial 2026 App en http://localhost:8501
streamlit run app.py --server.port 8501 --server.headless false
pause
