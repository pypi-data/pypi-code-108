#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_expr.py                                                                 #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Expression node class                                                                 #
#                                                                                                 #
###################################################################################################

"""Expression class implementation, this class is used by the parser."""

from .macal_lextokentypes import IDENTIFIER
from .macal_lextoken      import Token
from .macal_exprtypes import BINARY, UNARY, LITERAL, GROUPING, VARIABLE, INDEX, FUNCTION, PARAMS
from .macal_parsernodetypes import CALL
from .macal_keywords import NIL
from .macal_expritem import ExpressionItem

class Expr:
    """Expression class with static methods to instantiate specific expr node types."""
    def __init__(self, token: Token):
        """Base initializer for Expr class"""
        self.expr_type  = None
        self.left       = ExpressionItem(None, NIL)
        self.operator   = None
        self.right      = ExpressionItem(None, NIL)
        self.token      = token

    def set_right(self, value):
        """set right parameter"""
        self.right = value

    def binary(self, left, operator, right):
        """Instantiates Expr node of type binary"""
        instance = self
        instance.expr_type = BINARY
        instance.left = ExpressionItem(left, Expr)
        instance.operator = operator
        instance.right = ExpressionItem(right, Expr)
        return instance

    def unary(self, operator, right):
        """Instantiates Expr node of type unary"""
        instance = self
        instance.expr_type = UNARY
        instance.operator = operator
        instance.right = ExpressionItem(right, Expr)
        return instance
    
    def literal(self, left):
        """Instantiates Expr node of type literal"""
        instance = self
        instance.expr_type = LITERAL
        instance.left = left
        return instance

    def grouping(self, grouping):
        """Instantiates Expr node of type grouping"""
        instance = self
        instance.expr_type = GROUPING
        instance.left = ExpressionItem(grouping, GROUPING)
        return instance
    
    def variable(self, var):
        """Instantiates Expr node of type variable"""
        instance = self
        instance.expr_type = VARIABLE
        instance.left = ExpressionItem(var, VARIABLE)
        return instance

    def index(self, index):
        """Instantiates Expr node of type variableindex"""
        instance = self
        instance.expr_type = INDEX
        instance.left = ExpressionItem(index, INDEX)
        return instance

    def function(self, fun):
        """Instantiates Expr node of type function call"""
        instance = self
        instance.expr_type = FUNCTION
        instance.left = ExpressionItem(fun, CALL)
        instance.operator = CALL
        return instance

    def param_list(self):
        """Instantiates Expr node of type parameter list."""
        instance = self
        instance.expr_type = PARAMS
        instance.left = ExpressionItem([], PARAMS)
        return instance
    
    def print(self, expr):
        """Recursive printing function to display the entire expression"""
        if expr is None:
            return ""
        result = ""
        if isinstance(expr, tuple):
            if expr[0] == IDENTIFIER:
                result = expr[1]
            else:
                result = "Unknown {}".format(expr[0])
        elif not isinstance(expr, Expr) and expr is not None:
            result = expr.print("")
        elif expr.expr_type == BINARY:
            result = "( {} op: {} {})".format(self.print(expr.left.value),
                                              expr.operator, self.print(expr.right.value))
        elif expr.expr_type == UNARY:
            uop = expr.operator
            uright = expr.right.value
            result = "(unop: {} {})".format(uop, self.print(uright))
        elif expr.expr_type == LITERAL:
            result = repr("literal {}: {}".format(expr.left.item_type, expr.left.value))
        elif expr.expr_type == GROUPING:
            result = "( {} )".format(self.print(expr.left.value))
        elif expr.expr_type == INDEX:
            result = "Index [ {} ]".format(expr.left.value)
        elif expr.expr_type == FUNCTION:
            result =self.print(expr.left.value)
        #elif (expr.expr_type == VARIABLE):
        #    result = expr.print()
        #elif (expr.expr_type == PARAMS):
        #    result = expr.print()
        else:
            result = "Unknown {}".format(expr.expr_type)
        return result

    def __str__(self):
        result = ""
        if self.expr_type is None:
            return result
        if self.expr_type == BINARY:
            result = f"{self.left.value} {self.operator} {self.right.value}"
        elif self.expr_type == UNARY:
            result = f"{self.operator}{self.right.value}"
        elif self.expr_type == LITERAL:
            result = f"{self.left.value} ({self.left.item_type})"
        elif self.expr_type == GROUPING:
            result = f"({self.left.value})"
        elif self.expr_type == INDEX:
            result = f"[{self.left.value}]"
        elif self.expr_type == FUNCTION:
            result = f"{self.left.value}"
        elif self.expr_type == VARIABLE:
            result = f"{self.left.value}"
        else:
            result = f"unhandled expr type {self.expr_type}"
        return result
