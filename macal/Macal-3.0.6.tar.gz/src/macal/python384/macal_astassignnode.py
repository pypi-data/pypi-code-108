#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_astassignnode.py                                                        #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 AST Node classes instantiated by the parser                                           #
#                                                                                                 #
###################################################################################################

"""Implementation for AST Assign node used and returned by the parser"""

from .macal_astnode import AstNode
from .macal_parsernodetypes import ASSIGN
from .macal_lextokentypes import NEW_ARRAY_INDEX
from .macal_astvariablenode import ast_Variable

class ast_Assign(AstNode):
    """AST Node: Assign"""
    def __init__(self, operand, tid: ast_Variable, expression):
        """Initializes assign node type"""
        super().__init__(ASSIGN, tid.token)
        self.operand = operand
        self.ident = tid
        self.expr = expression
        self.ref = False
        self.ref_token = None

    def __str__(self):
        return f""" {"REF " if self.ref is True else ""}{self.ident} {self.operand.token_value} {self.expr}"""
