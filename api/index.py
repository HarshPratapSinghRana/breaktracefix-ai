import sys
from pathlib import Path

# Add project root and backend to python path for Vercel serverless execution
root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.main import app

# Vercel serverless function entrypoint handler
# Exposes standard ASGI app instance

