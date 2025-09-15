from scribeone.core.fileio import read_text, write_text
from pathlib import Path


def test_placeholder_fileio_tmp(tmp_path: Path):
    p = tmp_path / "a.txt"
    write_text(str(p), "hello")
    assert read_text(str(p)) == "hello"
