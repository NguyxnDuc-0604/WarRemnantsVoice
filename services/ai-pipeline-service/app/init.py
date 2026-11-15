"""Top‑level package for the AI‑pipeline service.

This ``__init__.py`` marks the ``app`` directory as a Python package and can be used
to perform package‑wide initialisation.  For a typical FastAPI/Flask service you
might expose the application instance here so that other modules can simply
import ``app``:

```python
from .main import app  # noqa: F401  (re‑export the FastAPI/Flask app)
```

If the package does not need any special start‑up logic it can stay empty – the
presence of the file is enough for Python to treat the directory as a package.
"""
