@echo off
title DarelyTopic - BERTopic Web Hub
echo ========================================================
echo   Iniciando DarelyTopic (BERTopic Web Hub)...
echo ========================================================
cd /d "C:\dixsys\darelytopic"

if not exist "venv\Scripts\streamlit.exe" (
    echo [ERROR] No se encontro el entorno virtual en C:\dixsys\darelytopic\venv
    echo Por favor asegurate de que la carpeta venv exista.
    pause
    exit /b
)

echo Abriendo navegador en http://localhost:8501 ...
start "" "http://localhost:8501"

echo Ejecutando aplicacion Streamlit...
".\venv\Scripts\streamlit.exe" run app.py --server.port=8501 --browser.gatherUsageStats=false

pause
