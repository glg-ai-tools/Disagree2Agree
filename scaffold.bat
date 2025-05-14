@echo off
REM ===================================================================
REM Green Light Go AI Go/No-Go Assistant Project Scaffold
REM Run this in the parent folder where you want the repo to live.
REM ===================================================================

set ROOT=green-light-go-AI-go-nogo-assistant

if exist "%ROOT%" (
  echo ERROR: "%ROOT%" already exists. Please remove or choose another location.
  pause
  exit /b 1
)

echo Creating project root "%ROOT%"...
mkdir "%ROOT%"

echo Creating glg module...
mkdir "%ROOT%\glg"
type nul > "%ROOT%\glg\__init__.py"
type nul > "%ROOT%\glg\core.py"

echo Creating agents...
mkdir "%ROOT%\glg\agents"
type nul > "%ROOT%\glg\agents\__init__.py"
type nul > "%ROOT%\glg\agents\luminary.py"
type nul > "%ROOT%\glg\agents\anchor.py"
type nul > "%ROOT%\glg\agents\navigator.py"
type nul > "%ROOT%\glg\agents\catalyst.py"
type nul > "%ROOT%\glg\agents\scribe.py"
type nul > "%ROOT%\glg\agents\auditor.py"

echo Creating utils...
mkdir "%ROOT%\glg\utils"
type nul > "%ROOT%\glg\utils\prompts.py"

echo Creating config folder...
mkdir "%ROOT%\config"
type nul > "%ROOT%\config\secrets_template.json"

echo Touching top-level files...
type nul > "%ROOT%\main.py"
type nul > "%ROOT%\requirements.txt"
type nul > "%ROOT%\README.md"
type nul > "%ROOT%\.gitignore"

echo.
echo Scaffold complete!  
echo Next steps:
echo  1. cd %ROOT%
echo  2. python -m venv .venv
echo  3. .venv\Scripts\activate
echo  4. pip install -r requirements.txt
echo.
pause
