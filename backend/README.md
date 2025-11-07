# Backend Quick Start

## Setup

1. Create and activate virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure environment variables in `.env` file

4. Run the server:
```powershell
python main.py
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

To add new endpoints, edit `main.py` or create new route files.

The LangGraph workflows are in `app/workflows/stories/`:
- `nodes.py` - Individual workflow nodes
- `workflows.py` - Complete workflow definitions
