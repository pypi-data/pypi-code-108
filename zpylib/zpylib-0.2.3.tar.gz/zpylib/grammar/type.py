# Lexer 需要用到的 token 类型对应的正则

from .keyword import zpy_RESERVED, py_RESERVED

t_NUMBER = r'-?(\d*\.)?\d+([eE][+\-]?\d+)?[jJ]?[lL]?'
t_HEX = r'-?0x([abcdef]|[ABCDEF]|\d)+[lL]?'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_DELIMITER = r'[.,:;]'
t_COMMENT = r'\#.*'
t_STRING = r'(?:\'.*\'|".*"|\'\'\'.*\'\'\'|""".*""")'

t_ignore = " \t"


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in py_RESERVED:
        t.type = py_RESERVED[t.value]
    return t


def t_ZNAME(t):
    r'[\u4e00-\u9fa5_]+[a-zA-Z0-9_\u4e00-\u9fa5]*'
    if t.value in zpy_RESERVED:
        t.type = zpy_RESERVED[t.value]
    return t


def t_line(t):
    r'\n'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)