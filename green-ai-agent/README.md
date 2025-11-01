# Green AI Email Classification Agent

An intelligent email classification system with energy-usage awareness.

## Setup

1. Clone the repository
2. Run the setup script:
```powershell
.\start.ps1 -Action setup
```

## Running the Services

### Backend API
```powershell
.\start.ps1 -Action backend
```
The API will be available at http://localhost:8000

### Dashboard
```powershell
.\start.ps1 -Action dashboard
```
The dashboard will be available at http://localhost:8501

## Project Structure

- `backend/`: FastAPI backend service
- `dashboard/`: Streamlit dashboard
- `models/`: Trained model files
- `data/`: Training and sample data
- `docs/`: Documentation
- `Scripts/`: Utility scripts
- `test_/`: Test files

## Configuration

Main configuration files:
- `backend/config.py`: Core configuration
- `backend/config_prod.py`: Production overrides

## API Endpoints

- `/classify-email`: Main classification endpoint
- `/health`: Health check
- `/agent-stats`: Usage statistics
- `/runs/recent`: Recent classifications
- More endpoints documented in the API docs (http://localhost:8000/docs)

## Environment Variables

- `PYTHONPATH`: Set to the project root directory
- Database file: `green_metrics.sqlite3`

## Development

To install in development mode:
```powershell
python -m pip install -e .
```