from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, QModelIndex
from PyQt6.QtWidgets import (
    QDockWidget,
    QTreeView,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QLabel,
)

# QFileSystemModel lives in QtWidgets for some builds, and in QtGui for others; try both.
try:  # PyQt6 >= 6.6 often provides it here
    from PyQt6.QtWidgets import QFileSystemModel as _QFileSystemModel  # type: ignore
except Exception:  # fallback path on certain PyQt6 builds
    try:
        from PyQt6.QtGui import QFileSystemModel as _QFileSystemModel  # type: ignore
    except Exception:  # last resort: disable Explorer
        _QFileSystemModel = None  # type: ignore

from ..utils.recent_files import list_recent


class SidebarDock(QDockWidget):
    """Left sidebar with Explorer and Recent lists (txt-focused).

    - Explorer: QFileSystemModel filtered to *.txt
    - Recent: last 5 recent files from settings
    """

    fileOpenRequested = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__("Sidebar", parent)
        self.setObjectName("SidebarDock")
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        self.tabs = QTabWidget(self)
        self.setWidget(self.tabs)

        # Explorer
        self.model = None
        if _QFileSystemModel is not None:
            self.model = _QFileSystemModel(self)
            try:
                self.model.setNameFilters(["*.txt"])  # txt-only focus
                self.model.setNameFilterDisables(False)
            except Exception:
                pass
            self.tree = QTreeView(self)
            self.tree.setModel(self.model)
            self.tree.doubleClicked.connect(self._open_index)
            self.tabs.addTab(self.tree, "Explorer")
        else:
            # Fallback when QFileSystemModel isn't available
            self.tree = QLabel("Explorer unavailable (QFileSystemModel missing)", self)
            self.tabs.addTab(self.tree, "Explorer")

        # Recent
        self.recent = QListWidget(self)
        self.recent.itemActivated.connect(self._open_recent_item)
        self.tabs.addTab(self.recent, "Recent")

        self._refresh_recent()

    def set_root(self, path: Optional[str]) -> None:
        root = str(path or str(Path.home()))
        if self.model is not None and isinstance(self.tree, QTreeView):
            idx = self.model.setRootPath(root)
            self.tree.setRootIndex(idx)

    def _open_index(self, index: QModelIndex) -> None:
        if self.model is None or not index.isValid():
            return
        path = self.model.filePath(index)
        if Path(path).is_file():
            self.fileOpenRequested.emit(path)

    def _refresh_recent(self) -> None:
        self.recent.clear()
        for p in list_recent():
            item = QListWidgetItem(p)
            item.setToolTip(p)
            self.recent.addItem(item)

    def refresh_recent(self) -> None:
        self._refresh_recent()

    def _open_recent_item(self, item: QListWidgetItem) -> None:
        if not item:
            return
        self.fileOpenRequested.emit(item.text())
