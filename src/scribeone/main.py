from __future__ import annotations

import sys

# When run as a module (python -m scribeone.main), relative imports work.
# When run as a script inside the package folder (python main.py), fix sys.path.
try:
    from .app import ScribeApplication  # type: ignore
    from .ui.main_window import MainWindow  # type: ignore
except Exception:  # ImportError in script mode
    if __name__ == "__main__":
        from pathlib import Path

        sys.path.append(str(Path(__file__).resolve().parents[1]))  # add <repo>/src
        from scribeone.app import ScribeApplication  # type: ignore
        from scribeone.ui.main_window import MainWindow  # type: ignore
    else:
        raise


def main() -> int:
    app = ScribeApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
