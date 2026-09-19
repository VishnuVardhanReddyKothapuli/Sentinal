.\.venv\Scripts\pip.exe install -r requirements-ai.txt
Get-Process python | Where-Object { $_.MainWindowTitle -notlike "*pip*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000
