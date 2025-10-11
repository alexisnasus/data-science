"""
EJECUTAR_SCRAPER.bat
Script ejecutable para Windows - Menú interactivo
"""

@echo off
chcp 65001 > nul
cls

:MENU
echo ══════════════════════════════════════════════════════════════
echo  🏠 SISTEMA DE SCRAPING PORTAL INMOBILIARIO
echo ══════════════════════════════════════════════════════════════
echo.
echo  Selecciona una opción:
echo.
echo  [1] 🚀 Scraper Simple (5 páginas, rápido)
echo  [2] ⚙️  Scraper Configurable (personalizado)
echo  [3] 📊 Scraper Incremental (actualizar histórico)
echo  [4] 🗺️  Scraper Multi-Región (nacional)
echo  [5] 🔍 Validar datos existentes
echo  [6] ❌ Salir
echo.
echo ══════════════════════════════════════════════════════════════
echo.

set /p opcion="Ingresa opción (1-6): "

if "%opcion%"=="1" goto SIMPLE
if "%opcion%"=="2" goto CONFIGURABLE
if "%opcion%"=="3" goto INCREMENTAL
if "%opcion%"=="4" goto MULTIREGION
if "%opcion%"=="5" goto VALIDAR
if "%opcion%"=="6" goto SALIR

echo.
echo ❌ Opción inválida
pause
goto MENU

:SIMPLE
cls
echo ══════════════════════════════════════════════════════════════
echo  🚀 EJECUTANDO SCRAPER SIMPLE
echo ══════════════════════════════════════════════════════════════
echo.
python 01_scraper_simple.py
echo.
pause
goto MENU

:CONFIGURABLE
cls
echo ══════════════════════════════════════════════════════════════
echo  ⚙️  SCRAPER CONFIGURABLE
echo ══════════════════════════════════════════════════════════════
echo.
echo Opciones disponibles:
echo   --tipo: casa ^| departamento ^| oficina ^| local
echo   --region: metropolitana ^| valparaiso ^| biobio ^| maule
echo   --paginas: número de páginas
echo.
set /p params="Ingresa parámetros (o Enter para defaults): "
python 02_scraper_configurable.py %params%
echo.
pause
goto MENU

:INCREMENTAL
cls
echo ══════════════════════════════════════════════════════════════
echo  📊 SCRAPER INCREMENTAL
echo ══════════════════════════════════════════════════════════════
echo.
python 03_scraper_incremental.py
echo.
pause
goto MENU

:MULTIREGION
cls
echo ══════════════════════════════════════════════════════════════
echo  🗺️  SCRAPER MULTI-REGIÓN
echo ══════════════════════════════════════════════════════════════
echo.
python 04_scraper_multiples_regiones.py
echo.
pause
goto MENU

:VALIDAR
cls
echo ══════════════════════════════════════════════════════════════
echo  🔍 VALIDAR DATOS
echo ══════════════════════════════════════════════════════════════
echo.
echo Archivos CSV disponibles:
dir /b *.csv 2>nul
echo.
set /p archivo="Ingresa el nombre del archivo a validar: "
python 05_validar_datos.py %archivo%
echo.
pause
goto MENU

:SALIR
cls
echo.
echo ✅ ¡Hasta luego!
echo.
timeout /t 2 >nul
exit
