$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
chcp 65001 > $null
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectRoot

$Python = "D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Fixed Python interpreter not found: $Python"
}

$LogDir = Join-Path $ProjectRoot "pipeline_logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "stage3_descriptive_diagnostics_$Stamp.log"

& $Python "code/src/diagnostics/04_descriptive_diagnostics.py" *> $LogFile
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
    Write-Error "Stage3 failed with exit code $ExitCode. Log: $LogFile"
    exit $ExitCode
}

Write-Host "Stage3 completed. Log: $LogFile"

