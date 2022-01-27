# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""Lexer for ASAM ATF using ply"""
import ply.lex as lex
from ply.lex import TOKEN


BOOLEANS = {'TRUE': True, 'FALSE': False}


# Reserved keywords
reserved = {'APPLATTR': 'APPLATTR',
            'APPLELEM': 'APPLELEM',
            'ATF_END': 'ATF_END',
            'ATF_FILE': 'ATF_FILE',
            'BASEATTR': 'BASEATTR',
            'BASETYPE': 'BASETYPE',
            'BLOCKSIZE': 'BLOCKSIZE',
            'CARDINALITY': 'CARDINALITY',
            'COMPONENT': 'COMPONENT',
            'DATATYPE': 'DATATYPE',
            'DESCRIPTION': 'DESCRIPTION',
            'DT_BLOB': 'DT_BLOB',
            'DT_BOOLEAN': 'DT_BOOLEAN',
            'DT_BYTE': 'DT_BYTE',
            'DT_BYTESTR': 'DT_BYTESTR',
            'DT_COMPLEX': 'DT_COMPLEX',
            'DT_DATE': 'DT_DATE',
            'DT_DCOMPLEX': 'DT_DCOMPLEX',
            'DT_DOUBLE': 'DT_DOUBLE',
            'DT_ENUM': 'DT_ENUM',
            'DT_EXTERNALREFERENCE': 'DT_EXTERNALREFERENCE',
            'DT_FLOAT': 'DT_FLOAT',
            'DT_LONG': 'DT_LONG',
            'DT_LONGLONG': 'DT_LONGLONG',
            'DT_SHORT': 'DT_SHORT',
            'DT_STRING': 'DT_STRING',
            'DT_UNKNOWN': 'DT_UNKNOWN',
            'DS_STRING': 'DS_STRING',
            'ENDAPPLELEM': 'ENDAPPLELEM',
            'ENDCOMPONENT': 'ENDCOMPONENT',
            'ENDFILES': 'ENDFILES',
            'ENDINSTELEM': 'ENDINSTELEM',
            'FILES': 'FILES',
            'IEEEFLOAT4': 'IEEEFLOAT4',
            'IEEEFLOAT8': 'IEEEFLOAT8',
            'INCLUDE': 'INCLUDE',
            'INIOFFSET': 'INIOFFSET',
            'INSTELEM': 'INSTELEM',
            'MANY': 'MANY',
            'REF_TO': 'REF_TO',
            'REF_TYPE': 'REF_TYPE',
            'UNDEFINED': 'UNDEFINED',
            'VALOFFSETS': 'VALOFFSETS',
            'VALPERBLOCK': 'VALPERBLOCK'}

# Non reserved keywords
HEX_NUMBERS = r'[0-9A-Fa-f]'
LETTERS = r'[A-Za-z]'
NUMBERS = r'[0-9]'

# Whitespace
CR = r'\r'
FF = r'\f'
LF = r'\n'
SP = r'\s'
VT = r'\t'


VERSION = r'V(%(num)s\.)+%(num)s+' % {'num': NUMBERS}

NEWLINE = r'%s|%s|%s' % (CR + LF, CR, LF)
WHITESPACE = r'%s|%s|%s|%s' % (VT, FF, SP, NEWLINE)

MANY_WHITESPACE = r'[%s]+' % WHITESPACE

COMMA = ','
SEMICOLON = ';'

STRING = r'"(\\\\|\\"|[^"])*"'
IDENTIFIER = r'%(let)s(%(let)s|%(num)s|_)*' % {'let': LETTERS, 'num': NUMBERS}

LINE_END = r'(%s|%s|%s)' % (CR, LF, FF)
LINE_END_SET = r'%s%s%s' % (CR, LF, FF)

LINE_COMMENT = r'//[^%s]*[%s]' % (LINE_END_SET, LINE_END_SET)
MULTI_LINE_COMMENT = r'/\*((.|%s)*?)\*/' % LINE_END

COMMENT = r'/((%s)|(%s))' % (LINE_COMMENT[1:], MULTI_LINE_COMMENT[1:])

DECIMAL = r'(%(num)s+\.%(num)s*)' % {'num': NUMBERS}

INTEGER = r'[-\+]?(%s+|(0x|0X)%s+)' % (NUMBERS, HEX_NUMBERS)

EXP_FLOAT = r'(%(num)s+(\.%(num)s*)?[eE][-\+]?%(num)s+)' % {'num': NUMBERS}

FLOAT = r'%(nan)s|[-\+]?(%(inf)s|%(exp)s|%(dec)s)' % {
    'nan': 'NAN',
    'inf': '(Infinity|INFINITY)',
    'exp': EXP_FLOAT,
    'dec': DECIMAL}

BOOL = '(TRUE|FALSE)'


@TOKEN(VERSION)
def t_VERSION(t):
    return t


t_ASSIGN = r'='
t_COMMA = COMMA


@TOKEN(BOOL)
def t_BOOL(t):
    t.value = BOOLEANS[t.value]
    return t


@TOKEN(COMMENT)
def t_COMMENT(t):
    pass


@TOKEN(FLOAT)
def t_FLOAT(t):
    t.value = float(t.value)
    return t


@TOKEN(IDENTIFIER)
def t_IDENTIFIER(t):
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t


@TOKEN(INTEGER)
def t_INTEGER(t):
    t.value = int(t.value)
    return t


@TOKEN(MANY_WHITESPACE)
def t_WHITESPACE(t):
    pass


@TOKEN(SEMICOLON)
def t_SEMICOLON(t):
    return t


@TOKEN(STRING)
def t_STRING(t):
    t.value = t.value[1:-1]
    return t


tokens = ['VERSION',
          'SEMICOLON',
          'COMMA',
          'IDENTIFIER',
          'INTEGER',
          'STRING',
          'FLOAT',
          'BOOL',
          'ASSIGN'] + list(reserved.values())


def t_error(t):
    """Error handling rule"""
    print("Illegal character '{0}'".format(t.value[0]))
    t.lexer.skip(1)


lexer = lex.lex(debug=0, optimize=0)
