from __future__ import annotations

from pathlib import Path
from PyQt6.QtCore import QSettings


class ThemeManager:
    def __init__(self, app) -> None:
        self.app = app

    def apply(self, name: str) -> None:
        qss_path = self._theme_path(name)
        if qss_path and qss_path.exists():
            self.app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
            QSettings().setValue("ui/theme", name)

    def restore(self) -> None:
        name = QSettings().value("ui/theme", "dark")
        name = str(name) if name else "dark"
        self.apply(name)

    @staticmethod
    def _theme_path(name: str) -> Path | None:
        base = Path(__file__).resolve().parents[1] / "theme"
        fn = f"{name}.qss"
        p = base / fn
        return p