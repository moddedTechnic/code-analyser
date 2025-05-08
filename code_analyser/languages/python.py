from pathlib import Path
from typing import Generator

from ._token import Token, _File

KEYWORDS = {
    'for', 'while', 'if', 'elif', 'else', 'try', 'except', 'finally',
    'with', 'as', 'def', 'class', 'return', 'import', 'from', 'in',
    'is', 'not', 'and', 'or', 'break', 'continue', 'pass', 'raise',
    'lambda', 'yield', 'async', 'await', 'global', 'nonlocal',
    'del', 'assert', 'True', 'False', 'None', 'self', 'print',
    'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set',
    'tuple', 'bool', 'complex', 'enumerate', 'zip', 'map', 'filter',
    'sorted', 'reversed', 'sum', 'any', 'all', 'max', 'min',
}

SYMBOLS = {
    '(', '{', '[', ';', ',', '.', ':', '?', '*', '+', '-', '/', '%', '&', '|', '^', '~', '=', '<', '>',
}

IGNORED = {
    ')', '}', ']',
}


def loc(file: Path) -> int:
    # TODO: ignore inactive preprocessor directives
    count = 0
    with file.open('r') as f:
        in_multiline = False
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            if line.startswith('"""') or line.startswith("'''"):
                in_multiline = not in_multiline
                continue
            if line.endswith('"""') or line.endswith("'''"):
                in_multiline = False
                continue
            if in_multiline:
                continue
            if not line:
                continue
            count += 1
    return count


def tokenize(file: Path) -> Generator[Token, None, None]:
    with _File(file) as f:
        for char in f:
            yield from handle_char(char, f)


def handle_char(char: str, f: _File):
    # TODO: ignore inactive preprocessor directives
    if char.isspace():
        return
    if char in IGNORED:
        return
    if char == '#':
        f.read_line()
        return
    if char in SYMBOLS:
        yield Token(char, is_operator=True)
        return
    if char == '"' or char == "'":
        yield handle_string(f, char)
        return
    if char.isalnum():
        token = char
        if char in {'f', 'b', 'r', 'u'}:
            c = next(f)
            token += c
            if c == '"' or c == "'":
                t = handle_string(f, c)
                yield Token(char + t.text, is_operator=False)
                return
        for c in f:
            if c.isalnum() or c == '_' or c == '.':
                token += c
            else:
                break
        if token in KEYWORDS:
            yield Token(token, is_operator=True)
        else:
            yield Token(token, is_operator=False)
        yield from handle_char(c, f)


def handle_string(f, end):
    token = end
    for c in f:
        token += c
        if c == end:
            break
    return Token(token, is_operator=False)
