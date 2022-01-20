from .token import TokenType

# GRAMMAR of our simple expression language
# AutomationEdge Technologies
# yogesh.ketkar@automationedge.com
################################################################################
# expression  := bexpression
#                | icomparison
#                | expression (( AND | OR | EQ | NOTEQ ) expression)+
#                | NOT expression
#                | LPAREN expression RPAREN
#
# bconstant   := TRUE | FALSE
# bfunction   := contains | startswith | endswith
# bexpression := bconstant | bfunction
#
# identifier  := STRING | NUMBER | VARIABLE
# ifunction   := upper | lower
# iexpression := identifier | ifunction
# icomparison := iexpression ( EQ | NOTEQ | LT | LTEQ | GT | GTEQ ) iexpression
################################################################################

# - expression which is the top-level production can be one of the following
#   - bexpression
#     True or False or any of the functions which return True or False
#     examples: True, False, contains("foobar", "foo"), startswith("foobar", "foo")
#   - icomparison
#     is any expression which involves comparison of two iexpressions
#     examples: 10 <= 20, lower("FOO") == "foo"
#   - expression ((AND, OR, EQ, NOTEQ) expression)+
#     One of the above expressions followed by zero or more AND, OR, EQ, NOTEQ expressions
#   - NOT expression
#     not of one of the above expressions
#   - ( expression )
#     an expression which can be one of the above expressions enclosed in parentheses


# Below are some of the examples of the expressions and resulting evaluation tree
# (1) "True and False"
#     and
#       True
#       False
#
# (2) "False and False or True"  (evaluates to True)
#     or
#       and
#         False
#         False
#       True
#     Note that, by default, evaluation is eager or left to right. So 'and' operator
#     gets evaluated first and then 'or'. If you want to change the order, you can
#     use parentheses to explicitly specify the order as shown in the next example.
#
# (3) "False and (False or True)" (evaluates to False)
#     and
#       False
#       or
#         False
#         True
#
# (4) 'not not False and contains("ab", "b") or 21 > 20' (evaluates to True)
#     or
#       and
#         not
#           not
#             False
#         contains
#           ab
#           b
#       >
#         21
#         20
#
# (5) 'not not False and (contains("ab", "b") or 21 > 20)' (evaluates to False)
#     and
#       not
#         not
#           False
#       or
#         contains
#           ab
#           b
#         >
#           21
#           20

class TreeNode:
    def __init__(self, token):
        self.token = token
        self.children = []

    def evaluate(self, var_dict={}):
        if self.token.ttype == TokenType.AND:
            return self.children[0].evaluate(var_dict) and self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.OR:
            return self.children[0].evaluate(var_dict) or self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.NOT:
            return not self.children[0].evaluate(var_dict)
        elif self.token.ttype == TokenType.TRUE:
            return True
        elif self.token.ttype == TokenType.FALSE:
            return False
        elif self.token.ttype == TokenType.CONTAINS:
            return self.children[1].evaluate(var_dict) in self.children[0].evaluate(var_dict)
        elif self.token.ttype == TokenType.STARTSWITH:
            return self.children[0].evaluate(var_dict).startswith(self.children[1].evaluate(var_dict))
        elif self.token.ttype == TokenType.ENDSWITH:
            return self.children[0].evaluate(var_dict).endswith(self.children[1].evaluate(var_dict))
        elif self.token.ttype == TokenType.LOWER:
            return self.children[0].evaluate(var_dict).lower()
        elif self.token.ttype == TokenType.UPPER:
            return self.children[0].evaluate(var_dict).upper()
        elif self.token.ttype == TokenType.LEN:
            return len(self.children[0].evaluate(var_dict))
        elif self.token.ttype == TokenType.EQ:
            return self.children[0].evaluate(var_dict) == self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.NOTEQ:
            return self.children[0].evaluate(var_dict) != self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.LT:
            return self.children[0].evaluate(var_dict) < self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.LTEQ:
            return self.children[0].evaluate(var_dict) <= self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.GT:
            return self.children[0].evaluate(var_dict) > self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.GTEQ:
            return self.children[0].evaluate(var_dict) >= self.children[1].evaluate(var_dict)
        elif self.token.ttype == TokenType.NUMBER:
            return self.numeric_value(self.token.ttext)
        elif self.token.ttype == TokenType.STRING:
            return self.token.ttext
        elif self.token.ttype == TokenType.VARIABLE:
            if self.token.ttext not in var_dict:
                raise ValueError(f"Variable {self.token.ttext} not found in dictionary.")
            return var_dict[self.token.ttext]

    # method to print the tree
    def traverse(self, level=0):
        x = ""
        for i in range(0, level):
            x += "  "
        print(f"{x}{self.token.ttext}")
        for child in self.children:
            child.traverse(level + 1)

    def numeric_value(self, s):
        try:
            return int(s)
        except ValueError:
            # Not an integer, try with float
            return float(s)


class DDParser:
    def __init__(self, ddlexer):
        self.ddlexer = ddlexer
        self.variables = set()
        self.current_token = None
        self.next_token()

    def next_token(self):
        self.current_token = self.ddlexer.get_token()

    # returns result of matching current token type with the passed token type
    def check_token(self, ttype):
        return ttype == self.current_token.ttype

    def match(self, ttypes):
        m = False
        for ttype in ttypes:
            if self.check_token(ttype):
                m = True
                break
        if not m:
            error = ttypes[0].name
            for i in range(1, len(ttypes)):
                error += " or " + ttypes[i].name
            self.abort(f"Expected {error}, got {self.token_error()}")

    def match_and_next(self, ttypes):
        self.match(ttypes)
        self.next_token()

    def parse(self):
        node = self.expression(None)
        # Below code is there only to check excess right parentheses(')')
        # 1. Lexical analysis can potentially detect mismatch in parentheses by using a stack.
        #    But for that, we will have to go through all the tokens once before semantic parsing
        #    (basically parsing) starts, i.e., will have do one pass through the tokens.
        #    But we don't want an extra pass for this. We don't get all lexical tokens upfront,
        #    but get them one by one during parsing itself.
        # 2. When parsing 'True)', True evaluates to an expression and then we call method
        #    continue_expression(). Method 'continue_expression' is called after you have consumed
        #    a legitimate sub-expression but your overall expression may not be complete.
        #    Basically, it gets called
        #      1) when you are done with 'not expression'
        #      2) or when you are done with bexpression or icomparison
        #      3) or when you are done with an expression within parenthesis
        #    When evaluating '(True)', continue_expression is called after True is evaluated to be
        #    a legitimate expression. continue_expression ignores the right parenthesis. The check if every
        #    left parenthesis has a matching right parenthesis happens at a place where new expression
        #    stating with left parenthesis starts getting evaluated.
        #    If input expression 'True)' which doesn't start with a left parenthesis, there is no question
        #    of matching ')' check at the end of '('. This results in extra right parentheses tokens lingering
        #    at the end.
        # 3. Ideally, after self.expression() is called, we should have consumed all the tokens.
        #    If not, first one remaining should be ')'.
        if not self.check_token(TokenType.END_OF_EXPRESSION):
            self.abort(f"Expected END_OF_EXPRESSION, got {self.current_token.ttext}")
        return node

    # Comment put in function 'parse' gives some idea about how parsing works, some more details.
    # When expression is
    # = 'False and False or True'
    #   You start with an empty (None) parse tree and after False has been processed, parse tree
    #   has one node with type FALSE. Next continue_expression() is called which creates a new node
    #   for AND operation and adds node passed as argument to continue_expression() as its first child.
    #   This new AND node is passed further to expression() function as its the new top-level parse
    #   tree node. expression() again processed False, but as this time, node passed to it isn't null
    #   adds it as child of the top-leve node passed to it. So now AND node has two children.
    #   Again continue_expression() is called, which this time, creates a OR node and adds AND
    #   node as its first child and the process continues.
    #   If you call traverse() on the tree returned by parse(), you will see that it looks like
    #   or
    #     and
    #       False
    #       False
    #     True
    #
    # = 'False and (False or True)'
    #   As explained above, after 'False and' have been parsed, you have AND top-level node with
    #   False as its first child. But '(' starts a new expression tree. When new tree ends up having
    #   or as the top-level node with False and True as its children and this node goes as the second
    #   child of AND node.
    #   If you call traverse() on the tree returned by parse(), you will see that it looks like
    #   and
    #     False
    #     or
    #       False
    #       True
    #
    # = 'False and not True'
    #   As explained above, after 'False and' have been parsed, you have AND top-level node with
    #   False as its first child. Now 'not' operation creates a new node, add True as its first child
    #   and 'not' node in turns becomes second child of AND node. This results in having below parse tree.
    #   and
    #     True
    #     not
    #       True
    #
    #   Now consider a tricky scenario with 'not's
    # 1 'not not True'
    #   If after a top-level node created for first 'not' tokens, if you just pass that along in two
    #   recursive expression() calls, one for next 'not' and one for 'True', parse tree would end-up looking
    #   lik this. This is a problem, there can only be one child to 'not' node.
    #   not
    #     not
    #     True
    #   To fix this problem, you have to pass most recently created 'not' node to expression(). But now there
    #   is another problem, if we pass that node to expression(), parse tree will look like this.
    #   not
    #     True
    #   Last True node does attach to the right 'not' node, but that 'not' node is the one returned
    #   ultimately and we have lost the top-level 'not' node.
    #   As explained above, after 'False and' have been parsed, you have AND top-level node with
    #   False as its first child. Now 'not' operation creates a new node, add True as its first child
    #   and 'not' node in turns becomes second child of AND node.
    def expression(self, node, top=None):
        if self.check_token(TokenType.NOT):
            opnot = TreeNode(self.current_token)
            self.next_token()

            if node is None:
                node = opnot
            else:
                node.children.append(opnot)
            c = self.expression(opnot, node if top is None else top)
            node = self.continue_expression(c)
        elif self.is_boolean_expression() or self.is_identifier_expression():
            if self.is_boolean_expression():
                c = self.bexpression()
            else:
                c = self.icomparison()
            if node is None:
                node = c
            else:
                node.children.append(c)
            node = self.continue_expression(node if top is None else top)
        elif self.check_token(TokenType.LPAREN):
            self.next_token()
            c = self.expression(None)
            if node is not None:
                node.children.append(c)
            else:
                node = c
            self.match_and_next([TokenType.RPAREN])
            # For an expression similar to 'True or not(True)', if we just 'pass node'
            # to continue_expression(), what would end up getting returned is parse tree
            # only for not(True), though top-level node is correctly representing
            # 'True or not(True)'.
            node = self.continue_expression(node if top is None else top)
        else:
            self.abort(f"Unexpected {self.token_error()}")

        return node

    def continue_expression(self, node):
        if not self.check_token(TokenType.END_OF_EXPRESSION):
            if self.check_token(TokenType.RPAREN):
                pass
            elif self.is_equal_not_equal() or self.is_logical_operator():
                op = TreeNode(self.current_token)
                op.children.append(node)
                self.next_token()
                node = self.expression(op)
            else:
                self.abort(f"Expected or, and, == or !=, got {self.token_error()}")
        return node

    def bexpression(self):
        node = None
        if self.is_boolean_constant():
            node = TreeNode(self.current_token)
            self.next_token()
        elif self.is_boolean_function():
            node = TreeNode(self.current_token)
            self.next_token()
            # All boolean functions (contains, startswith and endswith) take two arguments.
            # Hence we can just match '(', iexpression, ',', iexpression, ')'
            # If in future, we start having boolean functions with arguments NOT EQUAL to two,
            # code below will change. Will have to do token matching based on the function names.
            # Possibly, we can maintain dictionary of function names and number of arguments.
            self.match_and_next([TokenType.LPAREN])
            p1 = self.iexpression()
            node.children.append(p1)
            self.match_and_next([TokenType.COMMA])
            p2 = self.iexpression()
            node.children.append(p2)
            self.match_and_next([TokenType.RPAREN])
        else:
            self.abort(f"Unexpected {self.current_token.ttext}")

        return node

    def get_variables(self):
        return self.variables

    def add_to_variables(self):
        if self.current_token.ttype == TokenType.VARIABLE:
            self.variables.add(self.current_token.ttext)

    def iexpression(self):
        node = None
        if self.is_identifier():
            node = TreeNode(self.current_token)
            self.add_to_variables()
            self.next_token()
        elif self.is_identifier_function():
            node = TreeNode(self.current_token)
            self.next_token()
            # Identifier functions are the ones which don't return a boolean value.
            # All identifier functions (lower, upper) take only one argument.
            # Hence we can just match '(', iexpression, ')'
            # If in future, we start having identifier functions with arguments NOT EQUAL to one,
            # code below will change. Will have to do token matching based on the function names.
            # Possibly, we can maintain dictionary of function names and number of arguments.
            self.match_and_next([TokenType.LPAREN])
            p1 = self.iexpression()
            node.children.append(p1)
            self.match_and_next([TokenType.RPAREN])
        else:
            self.abort(f"Unexpected {self.current_token.ttext}")

        return node

    def is_logical_operator(self):
        return self.check_token(TokenType.AND)\
            or self.check_token(TokenType.OR)

    def is_boolean_expression(self):
        return self.is_boolean_constant()\
            or self.is_boolean_function()

    def is_boolean_constant(self):
        return self.check_token(TokenType.TRUE)\
            or self.check_token(TokenType.FALSE)

    def is_boolean_function(self):
        return self.check_token(TokenType.CONTAINS)\
            or self.check_token(TokenType.STARTSWITH)\
            or self.check_token(TokenType.ENDSWITH)

    def is_identifier_expression(self):
        return self.is_identifier()\
            or self.is_identifier_function()

    def is_identifier(self):
        return self.check_token(TokenType.VARIABLE)\
            or self.check_token(TokenType.STRING)\
            or self.check_token(TokenType.NUMBER)

    def is_identifier_function(self):
        return self.check_token(TokenType.LOWER)\
            or self.check_token(TokenType.UPPER)\
            or self.check_token(TokenType.LEN)

    def is_equal_not_equal(self):
        return self.check_token(TokenType.EQ)\
            or self.check_token(TokenType.NOTEQ)

    def is_comparison_operator(self):
        return self.check_token(TokenType.EQ)\
            or self.check_token(TokenType.NOTEQ)\
            or self.check_token(TokenType.LT)\
            or self.check_token(TokenType.LTEQ)\
            or self.check_token(TokenType.GT)\
            or self.check_token(TokenType.GTEQ)

    def token_error(self):
        if self.current_token.ttype == TokenType.END_OF_EXPRESSION:
            return TokenType.END_OF_EXPRESSION.name
        else:
            return self.current_token.ttext

    def icomparison(self):
        node = None
        c1 = self.iexpression()
        if self.is_comparison_operator():
            node = TreeNode(self.current_token)
            self.next_token()
            if self.is_identifier_expression():
                c2 = self.iexpression()
            else:
                self.abort(f"Expected number, string, variable or identifier function, got {self.token_error()}")
        else:
            self.abort("Expected comparison operator, got " + self.token_error())

        node.children.append(c1)
        node.children.append(c2)
        return node

    # error during parsing, raise an error
    def abort(self, message):
        raise ValueError(f"Error during parsing: {message}")
