from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QSettings, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QRect
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QPlainTextEdit,
    QStatusBar,
    QMenuBar,
    QMenu,
    QGraphicsOpacityEffect,
    QToolBar,
    QLabel,
)

from ..core.document import Document
from .dialogs import confirm_close_unsaved
from .encoding_prompt import choose_encoding
from ..utils.recent_files import add_recent, list_recent
from .snackbar import Snackbar
from .about import AboutDialog
from .theme_manager import ThemeManager
# from .sidebar import SidebarDock  # deprecated dock version
from .sidebar_panel import SidebarPanel
from .messages import MSG_SAVED, ERR_OPEN_FAILED, ERR_SAVE_FAILED, WARN_OVERWRITE


class MainWindow(QMainWindow):
    # Declare attribute types for analyzers
    sidebar: SidebarPanel
    _sidebar_effect: QGraphicsOpacityEffect
    _sidebar_target_width: int
    _sidebar_anim: QParallelAnimationGroup | None
    _sidebar_visible: bool
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ScribeOne — untitled [○]")
        self.resize(900, 640)

        # Document model
        self.doc = Document()

        # Editor
        self.editor = QPlainTextEdit(self)
        self.editor.setTabStopDistance(4 * self.editor.fontMetrics().horizontalAdvance(" "))
        self.editor.textChanged.connect(self._on_text_changed)
        self.setCentralWidget(self.editor)

        # Actions and Menus
        self._build_actions()
        self._build_menu()

        # Status bar + indicators
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self._pos_label = QLabel("Ln 1, Col 1", self)
        self._wrap_label = QLabel("Wrap: On", self)
        self.status.addPermanentWidget(self._pos_label)
        self.status.addPermanentWidget(self._wrap_label)
        self.editor.cursorPositionChanged.connect(self._update_cursor_pos)
        self._update_chrome()

        # Preferences and helpers
        self._restore_prefs()
        self._snackbar = Snackbar(self)
        self._theme_manager = ThemeManager(QApplication.instance())
        self._theme_manager.restore()

        # Sidebar panel (non-dock overlay)
        self.sidebar = SidebarPanel(self)
        self.sidebar.set_root(str(Path.home()))
        self.sidebar.fileOpenRequested.connect(self._open_path)
        self._sidebar_effect = QGraphicsOpacityEffect(self.sidebar)
        self.sidebar.setGraphicsEffect(self._sidebar_effect)
        self._sidebar_target_width = 260
        self._sidebar_visible = True
        self._install_sidebar_overlay()
        self._init_sidebar_state()


    # ----- UI Build -----
    def _build_actions(self) -> None:
        self.act_new = QAction("New", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self._new_file)

        self.act_open = QAction("Open…", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self._open_file)

        self.act_save = QAction("Save", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self._save_file)

        self.act_save_as = QAction("Save As…", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self._save_file_as)

        self.act_exit = QAction("Exit", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)

        # View / Options
        self.act_toggle_wrap = QAction("Toggle Wrap", self)
        self.act_toggle_wrap.setCheckable(True)
        self.act_toggle_wrap.setShortcut("Alt+Z")
        self.act_toggle_wrap.toggled.connect(self._toggle_wrap)

        # Help and Theme
        self.act_about = QAction("About", self)
        self.act_about.setShortcut("F1")
        self.act_about.triggered.connect(self._show_about)

        self.act_theme_light = QAction("Light Theme", self)
        self.act_theme_dark = QAction("Dark Theme", self)
        self.act_theme_light.triggered.connect(lambda: self._apply_theme("light"))
        self.act_theme_dark.triggered.connect(lambda: self._apply_theme("dark"))

        # Sidebar toggle
        self.act_toggle_sidebar = QAction("Toggle Sidebar", self)
        self.act_toggle_sidebar.setCheckable(True)
        self.act_toggle_sidebar.setShortcut("Ctrl+B")
        self.act_toggle_sidebar.toggled.connect(self._toggle_sidebar)

    

    def _build_menu(self) -> None:
        # Toolbar (modern quick access)
        tb = QToolBar("Main", self)
        tb.setMovable(False)
        tb.setIconSize(tb.iconSize())
        tb.addAction(self.act_new)
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_toggle_wrap)
        tb.addAction(self.act_toggle_sidebar)
        tb.addSeparator()
        tb.addAction(self.act_theme_light)
        tb.addAction(self.act_theme_dark)
        tb.addSeparator()
        tb.addAction(self.act_about)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)


    # ----- Events -----
    def closeEvent(self, event) -> None:  # noqa: N802
        if self.doc.is_dirty:
            choice = confirm_close_unsaved(self)
            if choice == "save":
                if not self._ensure_saved():
                    event.ignore()
                    return
            elif choice == "cancel":
                event.ignore()
                return
            # discard → accept
        # Persist sidebar state
        s = QSettings()
        s.setValue("ui/sidebarVisible", self.sidebar.isVisible())
        s.setValue("ui/sidebarWidth", max(0, self.sidebar.width()))
        event.accept()

    # ----- Slots -----
    def _on_text_changed(self) -> None:
        current = self.editor.toPlainText()
        if current != self.doc.text:
            self.doc.set_text(current)
            self._update_chrome()

    # ----- Helpers -----
    def _update_chrome(self) -> None:
        name = Path(self.doc.path).name if self.doc.path else "untitled"
        dot = "●" if self.doc.is_dirty else "○"
        self.setWindowTitle(f"ScribeOne — {name} [{dot}]")
        self.status.showMessage(self.doc.path or "(unsaved)")

    def _new_file(self) -> None:
        if self.doc.is_dirty:
            choice = confirm_close_unsaved(self)
            if choice == "save" and not self._ensure_saved():
                return
            if choice == "cancel":
                return
        self.doc = Document()
        self.editor.blockSignals(True)
        self.editor.setPlainText("")
        self.editor.blockSignals(False)
        self._update_chrome()

    def _open_file(self) -> None:
        # FR-002: open with encoding retry
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        self._open_path(path)

    def _open_path(self, path: str) -> None:
        if not path:
            return
        try:
            self.doc.load_from_path(path)
        except UnicodeDecodeError as e:
            enc = choose_encoding(self, path, e)
            if not enc:
                return
            try:
                self.doc.load_from_path(path, encoding=enc)
            except Exception as e2:
                self.status.showMessage(ERR_OPEN_FAILED.format(path=path), 5000)
                return
        except Exception as e:
            self.status.showMessage(ERR_OPEN_FAILED.format(path=path), 5000)
            return
        self.editor.blockSignals(True)
        self.editor.setPlainText(self.doc.text)
        self.editor.blockSignals(False)
        self._update_chrome()
        add_recent(path)
        self._rebuild_recent_menu()
        self._snackbar.show_message("已打开")
        if hasattr(self, "sidebar"):
            self.sidebar.refresh_recent()

    def _ensure_saved(self) -> bool:
        if not self.doc.path:
            return self._save_file_as()
        try:
            self.doc.save_to_path()
            self._update_chrome()
            self._snackbar.show_message("已保存")
            return True
        except Exception as e:
            self.status.showMessage(ERR_SAVE_FAILED.format(path=self.doc.path or ""), 5000)
            return False

    def _save_file(self) -> None:
        if not self._ensure_saved():
            return

    def _save_file_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(self, "Save As", self.doc.path or "untitled.txt", "Text Files (*.txt);;All Files (*)")
        if not path:
            return False
        # Overwrite confirm
        if Path(path).exists() and Path(path) != Path(self.doc.path or ""):
            from PyQt6.QtWidgets import QMessageBox
            res = QMessageBox.question(self, "Confirm Overwrite", WARN_OVERWRITE)
            if res != QMessageBox.StandardButton.Yes:
                return False
        try:
            self.doc.save_to_path(path)
            self._update_chrome()
            add_recent(path)
            self._rebuild_recent_menu()
            self._snackbar.show_message("已保存")
            if hasattr(self, "sidebar"):
                self.sidebar.refresh_recent()
            return True
        except Exception as e:
            self.status.showMessage(ERR_SAVE_FAILED.format(path=path), 5000)
            return False

    # ----- Preferences -----
    def _restore_prefs(self) -> None:
        s = QSettings()
        wrap = s.value("editor/wordWrap", True, type=bool)
        self.act_toggle_wrap.setChecked(bool(wrap))
        self._apply_wrap(bool(wrap))

    def _toggle_wrap(self, checked: bool) -> None:
        self._apply_wrap(checked)
        QSettings().setValue("editor/wordWrap", bool(checked))

    def _apply_wrap(self, enabled: bool) -> None:
        mode = QPlainTextEdit.LineWrapMode.WidgetWidth if enabled else QPlainTextEdit.LineWrapMode.NoWrap
        self.editor.setLineWrapMode(mode)
        self._wrap_label.setText(f"Wrap: {'On' if enabled else 'Off'}")

    def _apply_theme(self, name: str) -> None:
        self._theme_manager.apply(name)

    def _show_about(self) -> None:
        AboutDialog(self).exec()

    def _rebuild_recent_menu(self) -> None:
        # Menu bar removed; keep stub to avoid call sites breaking
        return

    def _open_recent(self, path: str) -> None:
        self._open_path(path)

    def _update_cursor_pos(self) -> None:
        cur = self.editor.textCursor()
        # PyQt6 positions are 0-based; show as 1-based
        line = cur.blockNumber() + 1
        col = cur.columnNumber() + 1
        self._pos_label.setText(f"Ln {line}, Col {col}")

    # ----- Sidebar visibility + animation -----
    def _init_sidebar_state(self) -> None:
        s = QSettings()
        default_width = int(s.value("ui/sidebarWidth", 260))
        visible = bool(s.value("ui/sidebarVisible", True, type=bool))
        self._sidebar_target_width = max(180, int(default_width))
        self.act_toggle_sidebar.setChecked(visible)
        self._sidebar_visible = visible
        if not visible:
            self.sidebar.hide()
            self._sidebar_effect.setOpacity(0.0)
        else:
            self.sidebar.show()
            self.sidebar.resize(self._sidebar_target_width, self.height())

    def _toggle_sidebar(self, checked: bool) -> None:
        self._animate_sidebar(show=checked)
        self._sidebar_visible = checked

    def _animate_sidebar(self, show: bool) -> None:
        current_w = self.sidebar.width() if self.sidebar.isVisible() else 0
        target_w = self._sidebar_target_width if show else 0

        # Prepare conditions
        if show and not self.sidebar.isVisible():
            self.sidebar.show()
            self.sidebar.raise_()
        op_from = self._sidebar_effect.opacity()
        op_to = 1.0 if show else 0.0

        fade = QPropertyAnimation(self._sidebar_effect, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(op_from)
        fade.setEndValue(op_to)
        fade.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Animate geometry width for overlay panel
        start_rect = QRect(0, 0, current_w, self.height())
        end_rect = QRect(0, 0, target_w, self.height())
        width_anim = QPropertyAnimation(self.sidebar, b"geometry", self)
        width_anim.setDuration(240)
        width_anim.setStartValue(start_rect)
        width_anim.setEndValue(end_rect)
        width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade)
        group.addAnimation(width_anim)

        def _on_finished() -> None:
            if not show:
                self.sidebar.hide()
                QSettings().setValue("ui/sidebarWidth", max(180, current_w))
            else:
                QSettings().setValue("ui/sidebarWidth", max(180, self.sidebar.width()))
            QSettings().setValue("ui/sidebarVisible", show)

        group.finished.connect(_on_finished)
        self._sidebar_anim = group
        group.start()

    # ----- Overlay install & edge gesture -----
    def _install_sidebar_overlay(self) -> None:
        # Place sidebar manually; mimic overlay by moving/reshaping on resize
        self.sidebar.setParent(self)
        self.sidebar.move(0, 0)
        self.sidebar.resize(self._sidebar_target_width, self.height())
        self.sidebar.setObjectName("SidebarPanel")
        self.sidebar.setStyleSheet("#SidebarPanel { background: rgba(15,17,21,0.92); }")
        self.installEventFilter(self)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self.sidebar.isVisible():
            self.sidebar.resize(self._sidebar_target_width, self.height())

    def eventFilter(self, obj, ev):  # simplified hover edge reveal
        from PyQt6.QtCore import QEvent
        if ev.type() == QEvent.Type.MouseMove:
            pos = self.mapFromGlobal(ev.globalPosition().toPoint()) if hasattr(ev, 'globalPosition') else self.mapFromGlobal(ev.globalPos())
            if pos.x() < 6 and not self._sidebar_visible:
                self.act_toggle_sidebar.setChecked(True)
            elif pos.x() > self._sidebar_target_width + 40 and self._sidebar_visible:
                # auto hide when cursor far from edge
                self.act_toggle_sidebar.setChecked(False)
        return super().eventFilter(obj, ev)
