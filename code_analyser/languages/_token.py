from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Token:
    text: str
    is_operator: bool


class _File:
    def __init__(self, file: Path):
        self.file = file
        self._handle = None

    def __enter__(self):
        self._handle = self.file.open('r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._handle.close()

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self._handle is None:
            raise RuntimeError("I/O operation on closed file")
        char = self._handle.read(1)
        if not char:
            raise StopIteration
        return char

    def read_line(self) -> str:
        return self._handle.readline()
