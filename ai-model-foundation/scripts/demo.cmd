@echo off
REM Demo: validate -> train -> eval (run from ai-model-foundation)
cd /d "%~dp0\.."
echo === AI Model Foundation demo (from %CD%) ===
echo.

echo 1. Validate data against contract...
python foundation\cli.py validate --model fraud_detector --data data\train.csv
if errorlevel 1 exit /b 1
echo.

echo 2. Train...
for /f "tokens=2 delims=:," %%a in ('python foundation\cli.py train --model fraud_detector 2^>^&1 ^| findstr "Run ID:"') do set RUN_ID=%%a
set RUN_ID=%RUN_ID: =%
echo    Run ID: %RUN_ID%
echo.

echo 3. Evaluate (gate pass/fail)...
python foundation\cli.py eval --model fraud_detector --run-id %RUN_ID%
echo.

echo 4. Run directory (runs\run_id\...)
dir runs\%RUN_ID%
dir runs\%RUN_ID%\artifact
echo.
echo === Demo done ===
