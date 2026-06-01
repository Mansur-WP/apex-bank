# Local development server (SQLite, http://127.0.0.1:8000)
$env:LOCAL_DEV = "1"
$env:SESSION_SECRET = "dev-local-secret-change-me"
$env:DEBUG = "True"

Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
