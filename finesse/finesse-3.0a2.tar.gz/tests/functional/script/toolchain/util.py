from finesse.script.containers import (
    KatMetaToken,
    KatToken,
    KatNumberToken,
    KatStringToken,
    KatNoneToken,
    KatReferenceToken,
    KatBooleanToken,
    KatWhitespaceToken,
)

# Tokens.
NEWLINE = lambda lineno, index: KatToken(lineno, index, index + 1, "NEWLINE", "\n")
SPACE = lambda lineno, start, length=1: KatWhitespaceToken(
    lineno, start, start + length, "WHITESPACE", " " * length
)
COMMENT = lambda lineno, start, value: KatToken(
    lineno, start, start + len(value), "COMMENT", value
)
LINEEND = lambda lineno, start: KatToken(lineno, start, start + 1, "NEWLINE", "\n")
NAME = lambda lineno, start, value: KatToken(
    lineno, start, start + len(value), "NAME", value
)
NUMBER = lambda lineno, start, value: KatNumberToken(
    lineno, start, start + len(value), "NUMBER", value
)
STRING = lambda lineno, start, value: KatStringToken(
    lineno, start, start + len(value), "STRING", value
)
NONE = lambda lineno, start: KatNoneToken(
    lineno, start, start + len("none"), "NONE", "none"
)
REFERENCE = lambda lineno, start, value: KatReferenceToken(
    lineno, start, start + len(value), "REFERENCE", value
)
BOOLEAN = lambda lineno, start, value: KatBooleanToken(
    lineno, start, start + len(str(value)), "BOOLEAN", value
)
LBRACKET = lambda lineno, start: KatToken(lineno, start, start + 1, "LBRACKET", "[")
RBRACKET = lambda lineno, start: KatToken(lineno, start, start + 1, "RBRACKET", "]")
LPAREN = lambda lineno, start: KatToken(lineno, start, start + 1, "LPAREN", "(")
RPAREN = lambda lineno, start: KatToken(lineno, start, start + 1, "RPAREN", ")")
COMMA = lambda lineno, start: KatToken(lineno, start, start + 1, "COMMA", ",")
PLUS = lambda lineno, start: KatToken(lineno, start, start + 1, "PLUS", "+")
MINUS = lambda lineno, start: KatToken(lineno, start, start + 1, "MINUS", "-")
TIMES = lambda lineno, start: KatToken(lineno, start, start + 1, "TIMES", "*")
DIVIDE = lambda lineno, start: KatToken(lineno, start, start + 1, "DIVIDE", "/")
FLOORDIVIDE = lambda lineno, start: KatToken(
    lineno, start, start + 2, "FLOORDIVIDE", "//"
)
POWER = lambda lineno, start: KatToken(lineno, start, start + 2, "POWER", "**")
EQUALS = lambda lineno, start: KatToken(lineno, start, start + 1, "EQUALS", "=")

# Meta tokens.
IMPLICITLINEEND = lambda lineno, start: KatMetaToken(lineno, start, start, "NEWLINE")
ENDMARKER = lambda lineno: KatMetaToken(lineno, 1, 1, "ENDMARKER")
