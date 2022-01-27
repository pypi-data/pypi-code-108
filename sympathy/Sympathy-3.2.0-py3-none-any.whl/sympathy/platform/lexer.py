# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
import ply.lex as lex
import os
# Force preload of lexer and parser to avoid warning and regeneration by ply.
try:
    from . import types_lexer as _types_lexer  # NOQA
except ImportError:
    _types_lexer = 'types_lexer'

_outputdir = os.path.dirname(os.path.abspath(__file__))

precedence = ()

reserved = {'sytypealias': 'ALIAS',
            'sytext': 'TEXT',
            'sytable': 'TABLE'}

rreserved = dict(zip(reserved.values(), reserved.keys()))

tokens = ['EOL',
          'EQUALS',
          'LPAREN',
          'RPAREN',
          'COLON',
          'LBRACKET',
          'RBRACKET',
          'LABRACKET',
          'RABRACKET',
          'LBRACE',
          'RBRACE',
          'COMMA',
          'ARROW']

tokens.extend(reserved.values())
tokens.append('IDENTIFIER')

t_ignore = r' '
t_EOL = r'[\n\r]+'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LABRACKET = r'<'
t_RABRACKET = r'>'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COLON = r':'
t_COMMA = r','
t_ARROW = '->'


def t_IDENTIFIER(token):
    r'[A-Za-z][A-Za-z0-9-_]*'
    token.type = reserved.get(token.value, 'IDENTIFIER')
    return token


# Error handling rule
def t_error(token):
    raise TypeError('Illegal character {} at position {} in {}'.format(
        token.value[0], token.lexpos,
        token.lexer.lexdata.strip()))


lexer = lex.lex(debug=0,
                optimize=1,
                lextab=_types_lexer,
                outputdir=_outputdir)
