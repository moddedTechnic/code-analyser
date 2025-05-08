# Code Analyser

Simple program to compute code metrics about Python and C++ code.

Metrics supported:
- File count
- Lines of Code
- Code level
- Code volume
- Intelligence Content

The latter three are as defined by Halstead, M.H. (Maurice H. (1977) Elements of software science. New York : Elsevier. Available at: http://archive.org/details/elementsofsoftwa0000hals (Accessed: 25 February 2025).

To run, first initialise Poetry:

```sh
poetry install
poetry shell
```

Then run

```sh
python3 code_analyser <PATH/TO/PROGRAM/SOURCE>
```

