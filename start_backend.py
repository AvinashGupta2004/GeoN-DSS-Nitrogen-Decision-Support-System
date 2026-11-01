"""
Convenience launcher for GeoN-DSS FastAPI Backend
Usage: python start_backend.py
"""
import sys
from pathlib import Path
import uvicorn

# Ensure backend directory is in python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 Starting GeoN-DSS FastAPI Backend")
    print("📍 Interactive API Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
