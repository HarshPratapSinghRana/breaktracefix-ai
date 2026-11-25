import sys
import types
from pathlib import Path

# Auto-register 'backend' in sys.modules if not present
if "backend" not in sys.modules:
    backend_dir = Path(__file__).resolve().parent.parent
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    backend_pkg.__file__ = str(backend_dir / "__init__.py")
    sys.modules["backend"] = backend_pkg
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
