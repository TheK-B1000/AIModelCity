# Demo: validate -> train -> eval (run from repo root)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..")

Write-Host "=== AI Model Foundation demo (from $(Get-Location)) ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Validate data against contract..." -ForegroundColor Yellow
python foundation/cli.py validate --model fraud_detector --data data/train.csv
Write-Host ""

Write-Host "2. Train..." -ForegroundColor Yellow
$trainOut = python foundation/cli.py train --model fraud_detector 2>&1
Write-Host $trainOut
if ($trainOut -match "Run ID: ([a-f0-9]+)") { $RUN_ID = $Matches[1] }
if (-not $RUN_ID) {
    $RUN_ID = (Get-ChildItem runs -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
}
Write-Host "   Run ID: $RUN_ID"
Write-Host ""

Write-Host "3. Evaluate (gate pass/fail)..." -ForegroundColor Yellow
python foundation/cli.py eval --model fraud_detector --run-id $RUN_ID
Write-Host ""

Write-Host "4. Run directory (runs/<run_id>/...):" -ForegroundColor Yellow
Get-ChildItem "runs/$RUN_ID" -ErrorAction SilentlyContinue
Get-ChildItem "runs/$RUN_ID/artifact" -ErrorAction SilentlyContinue
Write-Host ""
Write-Host "=== Demo done ===" -ForegroundColor Cyan
