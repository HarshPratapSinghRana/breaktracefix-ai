import sys
import types
from pathlib import Path

# Add project root and backend to python path for Vercel serverless execution
root_path = Path(__file__).resolve().parent.parent
backend_dir = root_path / "backend"

for p in [str(root_path), str(backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    backend_pkg.__file__ = str(backend_dir / "__init__.py")
    sys.modules["backend"] = backend_pkg

from backend.app.main import app

# Vercel serverless function entrypoint handler
__all__ = ["app"]
