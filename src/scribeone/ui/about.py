from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("关于 ScribeOne")
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                """
                <b>ScribeOne</b><br/>
                Minimal, modern single‑document editor<br/>
                <br/>
                © 2025 ScribeOne Authors<br/>
                License: AGPL-3.0-or-laterz
                """
            )
        )