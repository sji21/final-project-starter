param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
& $Python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 이상을 지정하세요." }
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.lock
if ($LASTEXITCODE -ne 0) { throw "의존성 설치에 실패했습니다." }
Write-Output "완료: .\start.ps1 로 실행하세요."

