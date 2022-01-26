#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_astselectnode.py                                                        #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 AST Node classes instantiated by the parser                                           #
#                                                                                                 #
###################################################################################################

"""Implementation for AST node select used and returned by the parser, it is separate because it requires importing expr"""

from .macal_parsernodetypes import SELECT
from .macal_expr import Expr
from .macal_astnode import AstNode

class ast_Select(AstNode):
    """AST Node: Select"""
    def __init__(self, lex_token, params: list, pfrom: Expr, into: Expr):
        """Initializes select node type"""
        super().__init__(SELECT, lex_token)
        self.distinct = False
        self.params = params
        #self.from_token = None
        self.sfrom = pfrom
        self.where_token = None
        self.where = None
        self.merge = None
        #self.into_token = None
        self.into = into

    def set_distinct(self, distinct: bool):
        """sets optional distinct flag"""
        self.distinct = distinct

    def set_where(self, where_token, where_value):
        """Sets optional where statement"""
        self.where_token = where_token
        self.where = where_value

    def set_merge(self, merge):
        """sets optional merge statement"""
        self.merge = merge

    def __str__(self):
        """Returns string representation of the node"""
        tstr = f"""SELECT {self.params} FROM {self.sfrom} {self.where if self.where is not None else ""}"""
        if self.merge:
            tstr = f"{tstr} MERGE"
        tstr = f"{tstr} INTO {self.into}"
        return tstr