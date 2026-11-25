import sys
import types
from pathlib import Path

# Resolve current backend directory (on Vercel this is /var/task)
backend_dir = Path(__file__).resolve().parent

# If 'backend' is not already in sys.modules, register it as a virtual package
# pointing to backend_dir. This ensures all 'from backend.app...' absolute imports
# work seamlessly when Vercel isolates root: "backend" into /var/task.
if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    backend_pkg.__file__ = str(backend_dir / "__init__.py")
    sys.modules["backend"] = backend_pkg

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if str(backend_dir.parent) not in sys.path:
    sys.path.insert(0, str(backend_dir.parent))

from backend.app.main import app

# Export ASGI application instance for Vercel FastAPI service
__all__ = ["app"]
