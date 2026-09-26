$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $projectPython)) { throw "먼저 .\setup.ps1 -Python <python.exe 경로> 를 실행하세요." }
& $projectPython -m app

