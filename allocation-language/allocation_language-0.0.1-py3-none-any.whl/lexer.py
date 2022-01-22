from rply import LexerGenerator
from rply.lexer import Lexer
from typing import List

lexer_rules = [
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("ALLOC", r"alloc"),
    ("SCOPE", r"scope"),
    ("DISCARD", r"discard"),
    ("ASSESS", r"assess"),
    ("AGGREGATE", r"aggregate"),
    ("SET_VALUE", r"set\_value"),
    ("KEY", r"key"),
    ("EOL", r";"),
    ("PERCENT", r"\%"),
    ("NUMBER", r"(\-)?((\d+\.\d+)|(\.\d+)|(\d+))"),
    ("FIELD_START", r"@'"),
    ("STRING", r"\"(.+?)(?<!\\)(?:(\\\\)*)[\"]"),
    ("FIELD_END", r"(?<!\\)(?:(\\\\)*)[']"), # Lookbehind makes sure we don't match an escaped '
    ("AGG_MODE", r"\:((sum)|(mean)|(median)|(mode)|(max)|(min)|(count))"),
    ("VAR_START", r"\$"),
    ("NAME", r"[A-Za-z]+[0-9A-Za-z]+"),
    ("EXP", r"\^"),
    ("MULT", r"\*"),
    ("DIV", r"\/"),
    ("ADD", r"\+"),
    ("SUB", r"\-"),
    ("AND", r"\&"),
    ("OR", r"\|"),
    ("COMPARATOR", r"(==)|(>=)|(<=)|(>)|(<)")
]

def get_lexer_tokens() -> List[str]:
    return [name for name, _ in lexer_rules]

def make_new_lexer() -> Lexer:
    lg = LexerGenerator()

    lg.ignore(r"\s+")
    lg.ignore(r"\#.*")
    for name, regex in lexer_rules:
        lg.add(name, regex)

    lexer = lg.build()

    return lexer
