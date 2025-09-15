from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PyQt6.QtWidgets import QLabel, QWidget, QGraphicsDropShadowEffect


class Snackbar(QWidget):
    """A lightweight transient message widget with fade in/out.

    ANM-004: SnackbarFade — windowOpacity fade in/out.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._label = QLabel("", self)
        self._label.setObjectName("snackbarLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            """
            QLabel#snackbarLabel {
                background-color: rgba(20,20,20,220);
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,28);
                font-size: 12px;
            }
            """
        )
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)

        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.hide()

    def show_message(self, text: str, msec: int = 1500) -> None:
        self._label.setText(text)
        self._label.adjustSize()
        self.resize(self._label.size())

        self._place_bottom_center()
        self.setWindowOpacity(0.0)
        self.show()

        # Fade in
        self._anim.stop()
        self._anim.setDuration(150)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

        # Auto fade out after msec
        self._timer.start(max(300, msec))

    def _fade_out(self) -> None:
        self._anim.stop()
        self._anim.setDuration(420)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.start()
        # Ensure hide at end
        self._anim.finished.connect(self.hide)

        # Create a subtle shadow for depth (on create once)
        if not hasattr(self, "_shadow"):
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(24)
            shadow.setOffset(0, 4)
            shadow.setColor(Qt.GlobalColor.black)
            self._label.setGraphicsEffect(shadow)
            self._shadow = shadow

    def _place_bottom_center(self) -> None:
        parent = self.parentWidget()
        if not parent:
            return
        geo = parent.geometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + geo.height() - self.height() - 24
        self.move(x, y)