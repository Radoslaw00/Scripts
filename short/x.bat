@echo off
setlocal enabledelayedexpansion
mode con: cols=80 lines=30
color 0A
cls

REM Matrix-style animation header
for /L %%A in (1,1,5) do (
    cls
    echo.
    echo                    ████████╗██╗  ██╗███████╗
    echo                    ╚══██╔══╝██║  ██║██╔════╝
    if %%A gtr 1 echo.                       ██║   ███████║█████╗  
    if %%A gtr 2 echo.                       ██║   ██╔══██║██╔══╝  
    if %%A gtr 3 echo.                       ██║   ██║  ██║███████╗
    if %%A gtr 4 echo.                       ╚═╝   ╚═╝  ╚═╝╚══════╝
    echo.
    echo                    PROCESSOR v1.0
    echo.
    timeout /t 1 /nobreak >nul
)

cls
echo.
echo                    Processing Images...
echo.
echo  [████████████████████████████████████] Stage 1: Converting to WebP
timeout /t 1 /nobreak >nul
echo  [████████████████████████████████████] Stage 2: Sorting by Type
timeout /t 1 /nobreak >nul
echo  [████████████████████████████████████] Stage 3: Resizing
timeout /t 1 /nobreak >nul
echo  [████████████████████████████████████] Stage 4: Optimizing
timeout /t 1 /nobreak >nul
echo  [████████████████████████████████████] Stage 5: Creating Shortcuts
timeout /t 1 /nobreak >nul

python run.py

cls
color 0F
echo.
echo                      ✓ PROCESS COMPLETE ✓
echo.
timeout /t 2 /nobreak >nul
exit
