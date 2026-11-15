@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 -m healthqualify.local_edition_v08
) else (
  where python >nul 2>nul
  if %ERRORLEVEL% EQU 0 (
    python -m healthqualify.local_edition_v08
  ) else (
    echo Python 3.10+ is required. Install Python from python.org, then double-click again.
    pause
    exit /b 1
  )
)
if %ERRORLEVEL% NEQ 0 pause
