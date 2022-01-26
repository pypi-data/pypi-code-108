#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_astforeachnode.py                                                       #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 AST Node classes instantiated by the parser                                           #
#                                                                                                 #
###################################################################################################

"""Implementation for AST foreach node used and returned by the parser, separate because it requires importing expr"""

from .macal_astnode import AstNode
from .macal_parsernodes import ast_Block
from .macal_parsernodetypes import FOREACH

class ast_Foreach(AstNode):
    """AST Node: ForEach"""
    def __init__(self, lex_token, expression, block: ast_Block):
        """Initializes foreach node type"""
        super().__init__(FOREACH, lex_token)
        self.expr = expression
        self.block = block
        self.iterator_var = None

    def __str__(self):
        return f" FOREACH {self.expr} {self.block}"
