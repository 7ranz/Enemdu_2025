@echo off
REM ETAPA 9: iniciador de doble clic para el dashboard.
REM ARCHIVO: iniciar_dashboard.bat; carga las dependencias locales y abre Streamlit.
set "RAIZ_PROYECTO=%~dp0"
set "PYTHONPATH=%RAIZ_PROYECTO%.runtime"
cd /d "%RAIZ_PROYECTO%"
"C:\Users\franz\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m streamlit run dashboard\app.py
pause
