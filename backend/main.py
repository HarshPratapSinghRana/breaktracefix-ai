import sys
from pathlib import Path

# Add project root and backend directory to sys.path so both
# 'backend.app...' and local module imports resolve cleanly when
# deployed as a dedicated Vercel service with root: "backend".
root_path = Path(__file__).resolve().parent.parent
backend_path = Path(__file__).resolve().parent

for p in [str(root_path), str(backend_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.app.main import app

# Export ASGI application instance for Vercel
__all__ = ["app"]
