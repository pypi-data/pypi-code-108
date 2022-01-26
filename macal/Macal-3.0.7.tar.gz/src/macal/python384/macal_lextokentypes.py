#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_lexertokentypes.py                                                      #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Lexer tokentypes                                                                      #
#                                                                                                 #
###################################################################################################

"""Token type names for the Lexer output"""

from .macal_lextoken import SingleToken

LPAREN      = 'LPAREN'
RPAREN      = 'RPAREN'
LINDEX      = 'LINDEX'
RINDEX      = 'RINDEX'
LBRACKET    = 'LBRACKET'
RBRACKET    = 'RBRACKET'
SEMICOLON   = 'SEMICOLON'
COLON       = 'COLON'
COMMA       = 'COMMA'
FSTR        = 'FSTR'
REF         = 'REF'

OP_ADD      = 'OP_ADD'
OP_SUB      = 'OP_SUB'
OP_MUL      = 'OP_MUL'
OP_DIV      = 'OP_DIV'
OP_PWR      = 'OP_PWR'
OP_EQUAL    = 'OP_EQUAL'
OP_ASSIGN   = 'OP_ASSIGN'
OP_LT       = 'OP_LT'
OP_GT       = 'OP_GT'
OP_NOT      = 'OP_NOT'
OP_NOTEQUAL = 'OP_NOTEQUAL'
OP_LTEQUAL  = 'OP_LTEQUAL'
OP_GTEQUAL  =  'OP_GTEQUAL'
OP_DEFINE   = 'OP_DEFINE'
OP_AND      = 'AND'
OP_OR       = 'OR'

IDENTIFIER  = 'IDENTIFIER'

KEYWORD     = 'KEYWORD'

NEW_ARRAY_INDEX  = 'x?[_NEW_ARRAY_INDEX_]?x'
NEW_RECORD_INDEX = 'x?[_NEW_RECORD_INDEX_]?x'

COMMENT     = 'COMMENT'

EOF         = 'EOF'

ERROR       = 'ERROR'

SINGLETOKENS = [SingleToken('(',LPAREN), SingleToken(')',RPAREN), SingleToken('[',LINDEX),
                SingleToken(']',RINDEX) , SingleToken('{',LBRACKET), SingleToken('}',RBRACKET),
                SingleToken(';',SEMICOLON), SingleToken(',',COMMA), SingleToken('+',OP_ADD),
                SingleToken('-',OP_SUB), SingleToken('*',OP_MUL), SingleToken('^',OP_PWR),
                SingleToken('$', FSTR), SingleToken('&', REF), SingleToken(':', COLON)]

SINGLE_TOKENS = {'(' : LPAREN, ')' : RPAREN, '[' : LINDEX, ']' : RINDEX, 
                 '{': LBRACKET, '}': RBRACKET, ';': SEMICOLON, ',' : COMMA, 
                 '+' : OP_ADD, '-' : OP_SUB, '*' : OP_MUL, '^' : OP_PWR, 
                 '$' :  FSTR, '&' :  REF, ':' : COLON}

DOUBLE_TOKENS = {'==' : OP_EQUAL, '=': OP_ASSIGN, '>=' : OP_GTEQUAL, '>': OP_GT, 
                 '<=' : OP_LTEQUAL, '<' : OP_LT, '!=' : OP_NOTEQUAL, '!' : OP_NOT, 
                 '//' : COMMENT, '/' : OP_DIV, '=>' : OP_DEFINE}