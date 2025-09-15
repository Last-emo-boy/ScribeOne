"""Root launcher for ScribeOne.

Allows running from repo root without installing the package.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add <repo>/src to sys.path so `import scribeone` works without install
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scribeone.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
