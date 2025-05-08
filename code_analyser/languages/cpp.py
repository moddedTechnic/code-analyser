from pathlib import Path
from typing import Generator

from ._token import Token, _File

KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern',
    'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
    'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while',
    'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'int8_t', 'int16_t', 'int32_t', 'int64_t',
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
        in_multiline_comment = False
        for line in f:
            line = line.strip()
            if in_multiline_comment:
                if '*/' in line:
                    in_multiline_comment = False
                if line.endswith('*/'):
                    continue
            if not line:
                continue
            if line.startswith('//'):
                continue
            if '/*' in line:
                in_multiline_comment = True
                if '*/' in line:
                    in_multiline_comment = False
                if line.startswith('/*'):
                    if '*/' in line and not line.endswith('*/'):
                        pass
                    else:
                        continue
            count += 1
    return count


def tokenize(file: Path) -> Generator[Token, None, None]:
    return _tokenize_pass2(file)


def _tokenize_pass2(file: Path) -> Generator[Token, None, None]:
    tokens = _tokenize_pass1(file)
    for token in tokens:
        if token.is_operator:
            yield token
            continue
        t1 = next(tokens, None)
        t2 = next(tokens, None)
        if t1 and t2 and t1.text == '::' and not t2.is_operator:
            yield Token(token.text + t1.text + t2.text, is_operator=False)
        else:
            yield token
            if t1:
                yield t1
            if t2:
                yield t2


def _tokenize_pass1(file: Path) -> Generator[Token, None, None]:
    tokens = _tokenize_raw(file)
    for token in tokens:
        if token.text == ':':
            next_token = next(tokens, None)
            if next_token and next_token.text == ':':
                yield Token('::', is_operator=True)
            else:
                yield token
                if next_token:
                    yield next_token
            continue
        if token.text == '-':
            next_token = next(tokens, None)
            if next_token is None:
                yield token
                return
            if next_token.text == '>':
                yield Token('->', is_operator=True)
                continue
            if next_token.text == '-':
                yield Token('--', is_operator=True)
                continue
            yield token
            if next_token:
                yield next_token
            continue
        if token.text == '+':
            next_token = next(tokens, None)
            if next_token is None:
                yield token
                return
            if next_token.text == '+':
                yield Token('++', is_operator=True)
                continue
            if next_token.text == '=':
                yield Token('+=', is_operator=True)
                continue
            yield token
            if next_token:
                yield next_token
            continue
        yield token


def _tokenize_raw(file: Path) -> Generator[Token, None, None]:
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
        line = f.read_line()
        if line.startswith('include'):
            _, target = line.split(' ')
            yield Token('#include', is_operator=True)
            yield Token(target.strip(), is_operator=False)
            return
        if line.startswith('endif'):
            yield Token('#endif', is_operator=True)
            return
        if line.startswith('else'):
            yield Token('#else', is_operator=True)
            return
    if char == '/':
        c = next(f)
        if c == '/':
            f.read_line()
            return
        yield Token(char, is_operator=True)
        yield from handle_char(c, f)
    if char in SYMBOLS:
        yield Token(char, is_operator=True)
    if char == '"':
        token = char
        for c in f:
            token += c
            if c == '"':
                break
        yield Token(token, is_operator=False)
    if char.isalnum():
        token = char
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
