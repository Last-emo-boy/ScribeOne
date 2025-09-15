from __future__ import annotations

from typing import Literal
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

Choice = Literal["save", "discard", "cancel"]


class UnsavedCloseDialog(QDialog):
    """Modal dialog asking user to save/discard/cancel before closing.

    Meets FR-005 and specs: returns save/discard/cancel and default focus on Save.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("未保存更改")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setModal(True)

        label = QLabel("当前文档有未保存更改，是否保存？")
        label.setWordWrap(True)

        buttons = QDialogButtonBox()
        self.btn_save = buttons.addButton("保存(&S)", QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_discard = buttons.addButton("放弃更改(&D)", QDialogButtonBox.ButtonRole.DestructiveRole)
        self.btn_cancel = buttons.addButton("取消(&C)", QDialogButtonBox.ButtonRole.RejectRole)

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(buttons)

        self.btn_save.setDefault(True)
        self.btn_save.setAutoDefault(True)

        self._choice: Choice = "cancel"

        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self._on_cancel)
        self.btn_discard.clicked.connect(self._on_discard)

    def _on_save(self) -> None:
        self._choice = "save"
        self.accept()

    def _on_discard(self) -> None:
        self._choice = "discard"
        self.accept()

    def _on_cancel(self) -> None:
        self._choice = "cancel"
        self.reject()

    def choice(self) -> Choice:
        return self._choice


def confirm_close_unsaved(parent=None) -> Choice:
    dlg = UnsavedCloseDialog(parent)
    result = dlg.exec()
    # exec() returns QDialog.DialogCode, but we rely on internal _choice to disambiguate
    return dlg.choice()
