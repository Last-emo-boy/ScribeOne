from __future__ import annotations

from typing import Iterable
from PyQt6.QtCore import QSettings

_MAX = 5
_KEY = "recent_files"


def _settings() -> QSettings:
    return QSettings()


def list_recent() -> list[str]:
    settings = _settings()
    vals = settings.value(_KEY, [])
    # QSettings may return list[str] or QStringList; normalize to list[str]
    return [str(x) for x in vals] if isinstance(vals, (list, tuple)) else []


def add_recent(path: str) -> list[str]:
    items = list_recent()
    if path in items:
        items.remove(path)
    items.insert(0, path)
    items = items[:_MAX]
    _settings().setValue(_KEY, items)
    return items


def clear_recent() -> None:
    _settings().remove(_KEY)
