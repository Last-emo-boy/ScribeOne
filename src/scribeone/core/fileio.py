from __future__ import annotations

from pathlib import Path


def read_text(path: str, encoding: str = "utf-8") -> str:
    p = Path(path)
    try:
        return p.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        # Bubble up for the UI layer to handle encoding retries
        raise e
    except OSError as e:
        raise e


essential_newline = "\n"


def write_text(path: str, text: str, encoding: str = "utf-8") -> None:
    p = Path(path)
    # Normalize newlines to \n when writing; OS will handle conversions if needed
    content = text.replace("\r\n", essential_newline).replace("\r", essential_newline)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)
