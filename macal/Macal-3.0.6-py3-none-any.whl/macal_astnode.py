#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_astnode.py                                                              #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 AstNode base class                                                                    #
#                                                                                                 #
# 3.0.6 26-01-2022: removed list type decorators to remove python version dependancy (>=3.8.4)    
###################################################################################################

"""Base class AstNode used as a base for various ast node types."""

from .macal_lextoken import LexToken

class AstNode:
    """node ancestor for all other node types"""
    def __init__(self, node_type: str, lex_token: LexToken):
        """Base AST node, all other node types inherit this one."""
        self.type : str = node_type
        self.token : LexToken = lex_token

    def name(self):
        """returns token name"""
        return self.token.token_value

    def node_type(self):
        """returns node type"""
        return self.type
