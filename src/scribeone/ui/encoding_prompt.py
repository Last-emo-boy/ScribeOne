from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QInputDialog


COMMON_ENCODINGS = [
    "utf-8",
    "gbk",
    "gb2312",
    "big5",
    "shift_jis",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
    "iso-8859-1",
]


def choose_encoding(parent=None, path: str | None = None, error: Exception | None = None) -> Optional[str]:
    title = "选择编码以重新打开"
    msg = "无法以 UTF-8 打开文件，选择其他编码后重试："
    if path:
        msg = f"无法以 UTF-8 打开文件:\n{path}\n\n请选择编码后重试："
    enc, ok = QInputDialog.getItem(parent, title, msg, COMMON_ENCODINGS, 0, False)
    if ok and enc:
        return str(enc)
    return None
