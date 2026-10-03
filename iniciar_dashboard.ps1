# ETAPA 9: iniciador local del dashboard.
# ARCHIVO: iniciar_dashboard.ps1; activa las dependencias locales y abre Streamlit.
$RaizProyecto = Split-Path -Parent $MyInvocation.MyCommand.Path  # Localiza el proyecto.
$PythonProyecto = 'C:/Users/franz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'  # Define el intérprete comprobado.
$env:PYTHONPATH = Join-Path $RaizProyecto '.runtime'  # Activa las bibliotecas aisladas.
Set-Location -LiteralPath $RaizProyecto  # Sitúa la ejecución en el proyecto.
& $PythonProyecto -m streamlit run 'dashboard/app.py'  # Inicia el observatorio en el navegador.
