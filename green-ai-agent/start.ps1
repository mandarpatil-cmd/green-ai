param(
    [string]$Action = "backend"  # default to backend if no action specified
)

# Set working directory to script location
$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $Root

# Ensure venv exists
if (-not (Test-Path .\.venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate venv
. .\.venv\Scripts\Activate.ps1

# Install package in development mode
Write-Host "Installing package in development mode..."
python -m pip install -e .

# Initialize database
Write-Host "Initializing database..."
$env:PYTHONPATH = $Root
python -c "from backend.main import init_email_db; init_email_db(); print('Database initialized successfully')"

# Start services based on action
switch ($Action) {
    "backend" {
        Write-Host "Starting backend server on http://localhost:8000"
        python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    }
    "dashboard" {
        Write-Host "Starting dashboard on http://localhost:8501"
        streamlit run dashboard/app.py --server.port=8501
    }
    "setup" {
        Write-Host "Setup completed successfully!"
    }
    default {
        Write-Host "Unknown action: $Action. Use 'backend', 'dashboard' or 'setup'."
    }
}
