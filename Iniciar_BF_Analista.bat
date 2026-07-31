@echo off
title BF Analista de Futebol - Launcher Automático
color 0A
echo =================================================================
echo           ⚽ INICIANDO BF ANALISTA DE FUTEBOL
echo =================================================================
echo.
echo  🌐 Acesso Local:  http://localhost:8501
echo  🚀 Acesso Remoto: https://blot-sandbag-wildcat.ngrok-free.dev/
echo.
echo =================================================================
cd /d "%~dp0"
python run.py
pause
