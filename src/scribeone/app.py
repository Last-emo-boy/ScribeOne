from __future__ import annotations

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication


class ScribeApplication(QApplication):
    """QApplication wrapper to centralize theme loading and app-wide settings.

    TODO: Wire light/dark theme switching and persisted settings.
    """

    ORGANIZATION = "ScribeOne"
    APPLICATION = "ScribeOne"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        QCoreApplication.setOrganizationName(self.ORGANIZATION)
        QCoreApplication.setApplicationName(self.APPLICATION)
        # Future: load settings, apply theme, fonts, translations
