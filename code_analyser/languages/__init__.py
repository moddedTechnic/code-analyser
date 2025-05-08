from pathlib import Path

from . import cpp, python


def detect_language(file: Path):
    if file.suffix in {'.c', '.cpp', '.h', '.hpp'}:
        return cpp
    if file.suffix in {'.py'}:
        return python
    return None
