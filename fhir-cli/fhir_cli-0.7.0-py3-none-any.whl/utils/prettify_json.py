from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer


def prettify_json(raw_json: str):
    return highlight(
        raw_json,
        lexer=JsonLexer(),
        formatter=Terminal256Formatter(style="monokai"),
    )
