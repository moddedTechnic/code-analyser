from dataclasses import dataclass, field
from math import log2
from pathlib import Path

from .languages import detect_language


@dataclass
class AnalysisResults:
    files: int = 0
    loc: int = 0
    operators: list[str] = field(default_factory=list)
    operands: list[str] = field(default_factory=list)

    def __add__(self, other):
        return AnalysisResults(
            files=self.files + other.files,
            loc=self.loc + other.loc,
            operators=self.operators + other.operators,
            operands=self.operands + other.operands
        )

    @property
    def total_operators(self):
        return len(self.operators)

    @property
    def total_operands(self):
        return len(self.operands)

    @property
    def unique_operators(self):
        return len(set(self.operators))

    @property
    def unique_operands(self):
        return len(set(self.operands))

    @property
    def unique_entities(self):
        return self.unique_operators + self.unique_operands

    @property
    def total_entities(self):
        return self.total_operators + self.total_operands

    @property
    def volume(self):
        if self.unique_entities == 0:
            return 0
        return self.total_entities * log2(self.unique_entities)

    @property
    def level(self):
        if self.unique_operators == 0 or self.total_operators == 0:
            return 0
        return (2 / self.unique_operators) * (self.unique_operands / self.total_operands)

    @property
    def intelligence_content(self):
        return self.volume * self.level

    def display(self, verbose: bool = False):
        print(f"Files: {self.files}")
        print(f"Lines of code: {self.loc}")
        print(f"Level: {self.level:.2f}")
        print(f"Volume: {self.volume:.2f}")
        print(f"Intelligence content: {self.intelligence_content:.2f}")

        if verbose:
            print(self.operators)
            print(self.operands)


def analyse_file(file: Path) -> AnalysisResults:
    if file.is_dir():
        return analyse(file)
    results = AnalysisResults()
    language = detect_language(file)
    if language is None:
        return results
    results.files += 1
    results.loc += language.loc(file)
    tokens = language.tokenize(file)
    for token in tokens:
        if token.is_operator:
            results.operators.append(token.text)
        else:
            # print(token.text)
            results.operands.append(token.text)
    return results


def analyse(dirpath: Path) -> AnalysisResults:
    if dirpath.is_file():
        return analyse_file(dirpath)
    results = AnalysisResults()
    for file in dirpath.rglob("*.*"):
        if file.is_dir():
            continue
        results += analyse_file(file)

    return results
