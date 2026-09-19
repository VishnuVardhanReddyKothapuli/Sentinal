$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Create backend/.venv and install backend/requirements.txt first. See README.md.'
}
Push-Location (Join-Path $projectRoot 'backend')
try {
    & $pythonPath -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend verification failed.' }
} finally { Pop-Location }
Push-Location (Join-Path $projectRoot 'frontend')
try {
    & npm.cmd test
    if ($LASTEXITCODE -ne 0) { throw 'Result display verification failed.' }
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
