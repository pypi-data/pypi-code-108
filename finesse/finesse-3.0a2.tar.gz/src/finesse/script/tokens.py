"""Regular expressions for matching tokens of different types in kat script.

Any new token types added here should be added to `tokenizer.py` and `highlighter.py` as
well.
"""

# NOTE: do not run black on this file!


def group(*choices):
    """Match any of the specified choices."""
    return f"({'|'.join(choices)})"


def any(*choices):
    """Specify that there should be zero or more of the specified choices."""
    return f"{group(*choices)}*"


def maybe(*choices):
    """Specify that there should be zero or one of the specified choices."""
    return f"{group(*choices)}?"


WHITESPACE = r"[ \f\t]+"
NEWLINE = r"\r?\n+"
COMMENT = r"#[^\r\n]*"
NONE = group(r"None", r"none")
BOOLEAN = group(r"True", r"true", r"False", r"false")
REFERENCE = r"&[a-zA-Z_][a-zA-Z0-9_.]*"  # Reference to element name or property.
NAME = r"[a-zA-Z_][a-zA-Z0-9_.]*"  # Element name or property.

# Most of these are based on those in the Python `tokenize` module.
_INTEGER_NUMBER = r"(?:0(?:_?0)*|[1-9](?:_?[0-9])*)"
_EXPONENT = r"[eE][-+]?[0-9](?:_?[0-9])*"
_POINT_FLOAT = group(r"[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?", r"\.[0-9](?:_?[0-9])*") + maybe(_EXPONENT)
_EXPONENT_FLOAT = r"[0-9](?:_?[0-9])*" + _EXPONENT
_FLOAT_NUMBER = group(_POINT_FLOAT, _EXPONENT_FLOAT)
_SI_NUMBER = group(_INTEGER_NUMBER, _POINT_FLOAT) + r"[pnumkMGT]"
_INFINITY = r"inf"
_IMAGINARY_NUMBER = group(_INFINITY + r"[jJ]", r"[0-9](?:_?[0-9])*[jJ]", _FLOAT_NUMBER + r"[jJ]")
NUMBER = group(_IMAGINARY_NUMBER, _SI_NUMBER, _FLOAT_NUMBER, _INTEGER_NUMBER, _INFINITY)

_SINGLE_QUOTED_STRING = r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'"
_DOUBLE_QUOTED_STRING = r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"'
STRING = group(_SINGLE_QUOTED_STRING, _DOUBLE_QUOTED_STRING)

# Types that only take one form. The order here is important (highest priority first).
LITERALS = {
    "EQUALS": "=",
    "PLUS": "+",
    "MINUS": "-",
    "POWER": "**",  # Has to be above TIMES.
    "TIMES": "*",
    "FLOORDIVIDE": "//",  # Has to be above DIVIDE.
    "DIVIDE": "/",
    "COMMA": ",",
    "LBRACKET": "[",
    "RBRACKET": "]",
    "LPAREN": "(",
    "RPAREN": ")",
}
