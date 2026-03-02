@echo off
REM Inicia o Scheduler do BB Controller
REM Este script executa a automação em horários pré-configurados

echo.
echo ========================================
echo   Scheduler BB - Extrato Bancário
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERRO: Python não encontrado no PATH
    echo.
    echo Por favor, instale Python ou adicione-o ao PATH do sistema.
    echo.
    pause
    exit /b 1
)

REM Instala dependências (se necessário)
echo 📦 Verificando dependências...
pip freeze | findstr "openpyxl requests selenium" >nul
if errorlevel 1 (
    echo ⚙️  Instalando dependências...
    pip install -r requirements.txt
)

REM Inicia o scheduler
echo.
echo 🚀 Iniciando Scheduler...
echo.
echo ℹ️  O scheduler permanecerá ativo em background
echo ℹ️  Pressione Ctrl+C para interromper
echo.

python scheduler_bb.py

pause
