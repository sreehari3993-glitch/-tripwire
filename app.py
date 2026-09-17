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
