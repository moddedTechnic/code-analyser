import sys
from pathlib import Path

from code_analyser import analyse


def main():
    if len(sys.argv) < 2:
        print("Usage: code_analyser <dirpath>")
        return 1
    verbose = False
    if len(sys.argv) > 2:
        if sys.argv[2] == "--verbose":
            verbose = True
    dirpath = Path(sys.argv[1])
    if not dirpath.exists():
        print(f"Error: {dirpath} not found")
        return 1
    print(f"Analyzing {dirpath}")
    results = analyse(dirpath)
    results.display(verbose)


if __name__ == '__main__':
    exit(main())
