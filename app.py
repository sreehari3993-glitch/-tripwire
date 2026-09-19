"""
Root ASGI entrypoint alias
Supports running from repository root or backend directory.
"""
import sys
import os

backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app

if __name__ == "__main__":
    import uvicorn
    print("\n=======================================================")
    print("  TRIPWIRE FastAPI Backend Starting...")
    print("  URL:           http://127.0.0.1:8000 (or http://localhost:8000)")
    print("  API Docs:      http://127.0.0.1:8000/docs")
    print("  Frontend UI:   http://127.0.0.1:5173")
    print("=======================================================\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=[backend_dir])
