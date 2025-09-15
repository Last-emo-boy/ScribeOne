from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Document:
    """A minimal single-document model.

    API per specs:
      - path: str | None
      - is_dirty: bool
      - text: str
      - mark_dirty()
      - set_text(text)
      - load_from_path(path, encoding)
      - save_to_path(path | None, encoding)
    """

    path: str | None = None
    is_dirty: bool = False
    text: str = ""

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def set_text(self, text: str) -> None:
        self.text = text
        self.is_dirty = True

    def load_from_path(self, path: str, encoding: str = "utf-8") -> None:
        from .fileio import read_text

        self.text = read_text(path, encoding=encoding)
        self.path = path
        self.is_dirty = False

    def save_to_path(self, path: str | None = None, encoding: str = "utf-8") -> None:
        from .fileio import write_text

        target = path or self.path
        if not target:
            raise ValueError("No path provided for save")
        write_text(target, self.text, encoding=encoding)
        self.path = target
        self.is_dirty = False
