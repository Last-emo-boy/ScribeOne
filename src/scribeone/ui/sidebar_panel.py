from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, QModelIndex, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QTabWidget,
    QTreeView,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)

# Try to locate QFileSystemModel in available modules
try:  # PyQt6 >= 6.6 typical
    from PyQt6.QtWidgets import QFileSystemModel as _QFileSystemModel  # type: ignore
except Exception:
    try:
        from PyQt6.QtGui import QFileSystemModel as _QFileSystemModel  # type: ignore
    except Exception:
        _QFileSystemModel = None  # type: ignore

from ..utils.recent_files import list_recent


class SidebarPanel(QFrame):
    """Modern left sidebar panel (non-dock) with Explorer + Recent.

    Designed to be embedded inside a layout rather than using QDockWidget to
    allow custom animation, invisible title bar, and gesture / edge reveal.
    """

    fileOpenRequested = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SidebarPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Explorer tab
        self.model = None
        if _QFileSystemModel is not None:
            self.model = _QFileSystemModel(self)
            try:
                self.model.setNameFilters(["*.txt"])
                self.model.setNameFilterDisables(False)
            except Exception:
                pass
            self.tree = QTreeView(self)
            self.tree.setModel(self.model)
            self.tree.setHeaderHidden(True)
            self.tree.doubleClicked.connect(self._open_index)
            self.tabs.addTab(self.tree, "Explorer")
        else:
            self.tree = QLabel("Explorer unavailable", self)
            self.tree.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabs.addTab(self.tree, "Explorer")

        # Recent tab
        self.recent = QListWidget(self)
        self.recent.itemActivated.connect(self._open_recent_item)
        self.tabs.addTab(self.recent, "Recent")

        self.refresh_recent()

        # Subtle shadow for depth when overlaying content (optional)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)

    # ---------------- public API -----------------
    def set_root(self, path: Optional[str]) -> None:
        root = str(path or str(Path.home()))
        if self.model is not None and isinstance(self.tree, QTreeView):
            idx = self.model.setRootPath(root)
            self.tree.setRootIndex(idx)

    def refresh_recent(self) -> None:
        self.recent.clear()
        for p in list_recent():
            item = QListWidgetItem(p)
            item.setToolTip(p)
            self.recent.addItem(item)

    # ---------------- internal handlers -----------------
    def _open_index(self, index: QModelIndex) -> None:
        if self.model is None or not index.isValid():
            return
        path = self.model.filePath(index)
        if Path(path).is_file():
            self.fileOpenRequested.emit(path)

    def _open_recent_item(self, item: QListWidgetItem) -> None:
        if not item:
            return
        self.fileOpenRequested.emit(item.text())
