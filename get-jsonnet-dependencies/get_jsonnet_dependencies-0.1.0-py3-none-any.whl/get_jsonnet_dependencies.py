r"""Extracts import dependencies from a Jsonnet file

    > python get_jsonnet_dependencies.py
    > local thing = import "thing.jsonnet";
    thing.jsonnet
    > local amoguise = import @"C:\Users\sus\Documents\amoguise.libsonnet";
    C:\Users\sus\Documents\amoguise.libsonnet
    > local a = import "a.jsonnet"; local b = importstr "b.txt";
    a.jsonnet
    b.txt

Note: Imports spanning multiple lines won't be found by this script.

"""
import sys
import fileinput
import re
from typing import Optional

# - Unescaping escape sequences

ESCAPE_PATTERN = re.compile(
    r'''
    \\["'/\\bfnrt]  # simple escapes
    |\\u[0-9a-fA-F]{4}  # unicode escape
    ''',
    flags=re.VERBOSE,
)

_SIMPLE_ESCAPES = {
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}

def _replace_escape(match):
    string = match[0]
    if string[1] == "u":
        return chr(int(string[2:], base=16))
    return _SIMPLE_ESCAPES.get(string[1], string[1])

# - Extracting import strings

IMPORT_PATTERN = re.compile(
    r'''
        \b
        (?P<func>
            import(?:str)?  # find import or importstr
        )
        \s*
        (?P<at>@)?  # check if verbatim string
        (?P<quote>['"])
        (?P<string>
            (?(at)
                (?:
                    (?P=quote){2}  # doubled quotes get turned into one quote
                    |(?!(?P=quote)).
                )*
                |(?:
                    \\.  # escaped char
                    |(?!\\|(?P=quote)).
                )*
            )
        )
        (?P=quote)
        (?(at)
            (?!(?P=quote))  # makes sure @""" doesnt match
        )
    ''',
    flags=re.VERBOSE,
)

def extract_imports(string: str):
    """Yields all import strings found

    - string is the string to search

        >>> list(extract_imports("import 'sus'"))
        ['sus']
        >>> list(extract_imports("import 'sus' import @'s\e\t''us'"))
        ['sus', "s\\e\t'us"]

    """
    for match in IMPORT_PATTERN.finditer(string):
        string = match["string"]
        if match["at"]:  # Verbatim string
            yield string.replace(match["quote"]*2, match["quote"])
        else:
            yield ESCAPE_PATTERN.sub(_replace_escape, string)

# - Command line

def main(argv: Optional[list[str]] = None):
    """Command line entry point

    - argv => sys.argv[1:]

    """
    if argv is None:
        argv = sys.argv[1:]

    for line in fileinput.input(argv):
        # UX improvement by allowing commented imports during development
        if line.strip().startswith("#") or line.strip().startswith("//"):
            continue
        for string in extract_imports(line):
            print(string)

if __name__ == "__main__":
    main()
