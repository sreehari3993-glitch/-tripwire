"""
Tripwire ASGI entrypoint alias
Allows running via either `uvicorn main:app` or `uvicorn app:app`.
"""
from main import app
