@echo off
REM City tour: validate -> train -> eval -> deploy -> showcase
cd /d "%~dp0\.."
echo === City tour: what this foundation can do ===
echo.

echo 1. Validate (data contracts)...
python foundation\cli.py validate --model fraud_detector --data data\train.csv
if errorlevel 1 exit /b 1
echo.

echo 2. Train (reproducible run)...
for /f "tokens=2 delims=:," %%a in ('python foundation\cli.py train --model fraud_detector --dataset demo 2^>^&1 ^| findstr "Run ID:"') do set RUN_ID=%%a
set RUN_ID=%RUN_ID: =%
if "%RUN_ID%"=="" for /f %%a in ('dir /b /o-d runs 2^>nul') do set RUN_ID=%%a
echo    Run ID: %RUN_ID%
echo.

echo 3. Eval (gates)...
python foundation\cli.py eval --model fraud_detector --run-id %RUN_ID%
if errorlevel 1 exit /b 1
echo.

echo 4. Deploy (embedded_models)...
python foundation\cli.py deploy --model fraud_detector --version %RUN_ID% --stage staging
echo.

echo 5. Showcase (predict from embedded model only)...
python scripts\showcase_embedded.py --model fraud_detector
echo.

echo 6. What's in staging?
type embedded_models\fraud_detector\deploy_meta.json 2>nul
echo.
echo === City tour done ===
