#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_parser.py                                                               #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 3.0 Language Parser                                                                       #
#                                                                                                 #
###################################################################################################

"""macal Language parser implementation"""

from .macal_lextoken import LexToken, SelectParam
from .macal_lextokentypes import (OP_AND, OP_OR, OP_NOTEQUAL, OP_EQUAL, OP_GT, OP_GTEQUAL,
    OP_LT, OP_LTEQUAL, OP_SUB, OP_ADD, OP_DIV, OP_MUL, OP_ASSIGN , OP_NOT, REF, FSTR,
    LPAREN, RPAREN, IDENTIFIER, KEYWORD, LINDEX, RINDEX, NEW_ARRAY_INDEX, COMMA, SEMICOLON,
    OP_DEFINE, LBRACKET, RBRACKET, COMMENT)

from .macal_keywords import (KW_ARRAY, NIL, KW_FOREACH, KW_ELIF, KW_ELSE, KW_IF, KW_BREAK, KW_HALT,
                            KW_RETURN, KW_AS, KW_DISTINCT, KW_SELECT, KW_FROM, KW_MERGE, KW_WHERE, 
                            KW_INTO, KW_RECORD, TRUE)

from .macal_variable_types import ARRAY, BOOL, FLOAT, INT, STRING, RECORD
from .macal_expr import Expr
from .macal_expritem import ExpressionItem
from .macal_parsernodes import (ast_list_Index, ast_function_Param_list,
                              ast_Block, ast_Halt, ast_Break, ast_Return)

from .macal_astifnode import ast_If, ast_Elif_branch, ast_Else_branch
from .macal_astselectnode import ast_Select
from .macal_astforeachnode import ast_Foreach
from .macal_astvariablenode import ast_Variable
from .macal_astfunctionnode import ast_Function_definition
from .macal_astcallfunctionnode import ast_Call_function
from .macal_astassignnode import ast_Assign

#expression     → literal
#               | unary
#               | binary
#               | grouping ;

#literal        → NUMBER | STRING | "true" | "false" | "nil" ;
#grouping       → "(" expression ")" ;
#unary          → ( "-" | "!" ) expression ;
#binary         → expression operator expression ;
#operator       → "==" | "!=" | "<" | "<=" | ">" | ">="
#               | "+"  | "-"  | "*" | "/" ;

#expression     → equality ;
#equality       → comparison ( ( "!=" | "==" ) comparison )* ;
#comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
#term           → factor ( ( "-" | "+" ) factor )* ;
#factor         → unary ( ( "/" | "*" ) unary )* ;
#unary          → ( "!" | "-" ) unary
#               | primary ;
#primary        → NUMBER | STRING | "true" | "false" | "nil"
#               | "(" expression ")" ;

#Name	        Operators	    Associates
#Equality	    == !=	        Left
#Comparison	    > >= < <=	    Left
#Term	        - +	            Left
#Factor	        / *	            Left
#Unary	        ! -	            Right

class MacalParser:
    """macal Parser class"""
    def __init__(self):
        """Initializes language parser for macal"""
        self.tokens: list(LexToken) = []
        self.length: int = 0
        self.nodes: list = []
        self.pos: int = -1
        self.version: str = "3.0.1"

    def reset(self):
        """resets the current state, do not use!
       This is here for the linter only"""
        self.tokens = []
        self.length = 0
        self.nodes = []
        self.pos = -1

    def _peek(self, look_ahead_count=0):
        if self.pos >= 0 and self.pos < self.length - look_ahead_count:
            return self.tokens[self.pos + look_ahead_count]
        return None

    def _chk(self, ttype):
        peek = self._peek()
        if peek is not None and peek.token_type == ttype:
            return True
        return False

    def _check(self, ttype):
        return not self._eof() and self._chk(ttype)

    def _eof(self):
        return self.pos >= self.length

    def _match(self, *args):
        if self._eof():
            return False
        if self._peek().token_type in args:
            self._advance()
            return True
        return False

    def _match_kw(self, *args):
        tkwd = self._peek().token_value
        if tkwd in args:
            self._advance()
            return True
        return False
    
    def _advance(self):
        if not self._eof():
            self.pos += 1
        return self._previous()

    def _previous(self):
        if self.pos > 0:
            return self.tokens[self.pos -1]
        return None

    def _expression(self):
        return self._boolean()

    def _boolean(self):
        expr = self._equality()
        while self._match(OP_AND, OP_OR):
            operator = self._previous().token_value
            right = self._equality()
            expr = Expr(self._previous()).binary(expr, operator, right)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match(OP_NOTEQUAL, OP_EQUAL):
            operator = self._previous().token_value
            right = self._comparison()
            expr = Expr(self._previous()).binary(expr, operator, right)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match(OP_GT, OP_GTEQUAL, OP_LT, OP_LTEQUAL):
            operator = self._previous().token_value
            right = self._term()
            expr = Expr(self._previous()).binary(expr, operator, right)
        return expr

    def _term(self):
        expr = self._factor()
        while self._match(OP_SUB, OP_ADD):
            operator = self._previous().token_value
            right = self._factor()
            expr = Expr(self._previous()).binary(expr, operator, right)
        return expr

    def _factor(self):
        expr = self._unary()
        if self._match(OP_ASSIGN):
            raise Exception("Invalid assignment, expected ==");
        while self._match(OP_DIV, OP_MUL):
            operator = self._previous().token_value
            right = self._unary()
            expr = Expr(self._previous()).binary(expr, operator, right)
        return expr

    def _unary(self):
        if self._match(OP_NOT, OP_SUB, REF, FSTR):
            operator = self._previous().token_value
            right = self._primary()
            return Expr(self._previous()).unary(operator, right)
        return self._primary()

    def _primary(self):
        result = None
        if self._match(BOOL):
            result = Expr(self._previous()).literal(ExpressionItem(self._previous().token_value == TRUE, self._previous().token_type))
        elif self._match(STRING, INT, FLOAT):
            result = Expr(self._previous()).literal(ExpressionItem(self._previous().token_value, self._previous().token_type))
        elif self._match(NIL):
            result = Expr(self._previous()).literal(ExpressionItem(None, NIL))
        elif self._match(IDENTIFIER):
            result = self._variable_or_function()
        elif self._match(LPAREN):
            result = self._grouping()
        elif self._match_kw(KW_ARRAY):
            result = Expr(self._previous()).literal(ExpressionItem([], ARRAY))
        elif self._match_kw(KW_RECORD):
            result = Expr(self._previous()).literal(ExpressionItem({}, RECORD))
        if result is None:
            self._raise_error("unknown token in expression")
        return result

    def _variable_or_function(self):
        expr = None
        if self._check(LPAREN):
            call = ast_Call_function(self._variable(self._previous()), self._param_list())
            expr = Expr(self._previous()).function(call)
        else:
            expr = self._variable(self._previous())
        return expr

    def _grouping(self):
        expr = self._expression()
        self._consume(RPAREN, "Expect ')' after expression.")
        return Expr(self._previous()).grouping(expr)

    @staticmethod
    def _format_error(token, message):
        if token is None:
            fmt_msg = "Syntax Error: {}".format(message)
        else:
            fmt_msg = "Syntax Error: {} @{},{} ({})".format(message, token.token_line,
                                                            token.token_offset, token.token_value)
        return fmt_msg

    def _raise_error(self, message):
        raise Exception(self._format_error(self._peek(), message))

    def _consume(self, ttype, message: str):
        if self._check(ttype):
            validated = self._advance()
            if validated is not None:
                return validated
        self._raise_error(message)
        return None

    def _consume_keyword(self, kwd, message):
        if self._check(KEYWORD) and self._peek().token_value == kwd:
            return self._advance()
        self._raise_error(message)
        return None

    def _parse_variable_array_index(self, node: ast_Variable):
        while self._check(LINDEX):
            index_token = self._advance()
            if self._check(RINDEX):
                expr = Expr(self._previous()).literal(ExpressionItem(NEW_ARRAY_INDEX, ARRAY))
            else:
                expr = self._expression()
            node.add_index(ast_list_Index(index_token, expr,
                            self._consume(RINDEX, "Expected ']'")))

    def _variable(self, tid):
        node = ast_Variable(tid)
        if self._check(LINDEX):
            self._parse_variable_array_index(node)
        return node

    def _param_list(self):
        node = ast_function_Param_list(self._consume(LPAREN, "Expected '(' before parameter list"))
        if self._check(RPAREN):
            node.close(self._advance())
            return node
        expr = self._expression()
        if expr is None:
            self._raise_error("Expected parameter(expression)")
        node.add_parameter(expr)
        while self._check(COMMA):
            self._advance()
            nexpr = self._expression()
            if nexpr is None:
                self._raise_error("Expected parameter(expression)")
            node.add_parameter(nexpr)
        node.close(self._consume(RPAREN, "Expected ')' after parameter list"))
        return node

    def _parse_function_call(self, tid):
        node = ast_Call_function(tid, self._param_list())
        self._consume(SEMICOLON, "Expected ';'")
        return node

    def _parse_function_definition(self, tid):
        oplex = self._consume(OP_DEFINE, "Expected '=>'")
        node = ast_Function_definition(tid, oplex, self._param_list(), self._parse_block())
        return node

    def _parse_assign(self, tid):
        node = ast_Assign(self._consume(OP_ASSIGN, "Expected '='"), tid,  self._expression())
        self._consume(SEMICOLON, "Expected ';'")
        return node

    def _parse_assign_ref(self):
        ref = self._consume(REF, "Expected '&'")
        tid = self._variable(self._consume(IDENTIFIER, "identifier expected in instruction"))
        node = self._parse_assign(tid)
        node.ref = True
        node.ref_token = ref
        return node

    def _parse_block(self):
        node = ast_Block(self._consume(LBRACKET, "{ expected"))
        while not self._check(RBRACKET) and not self._eof():
            instr = self._parse_instruction()
            if instr is None:
                self._raise_error("Syntax Error: Instruction returned None")
            if instr != COMMENT:
                node.add_instruction(instr)
        node.close(self._consume(RBRACKET, "} expected"))
        return node

    def _parse_identifier(self):
        tid = self._variable(self._consume(IDENTIFIER, "identifier expected in instruction"))
        result = None
        peek = self._peek()
        if peek.token_type == LPAREN:
            result = self._parse_function_call(tid)
        elif peek.token_type == OP_ASSIGN:
            result = self._parse_assign(tid)
        elif peek.token_type == OP_DEFINE:
            result = self._parse_function_definition(tid)
        if result is None:
            self._raise_error(f"Unexpected token after identifier ({tid.token.token_value}) ")
        return result

    def _parse_instruction(self):
        result = None
        if self._eof():
            return result
        peek = self._peek()
        if peek.token_type == IDENTIFIER:
            result = self._parse_identifier()
        elif peek.token_type == REF:
            result = self._parse_assign_ref()
        elif peek.token_type == LBRACKET:
            result = self._parse_block()
        elif peek.token_type == KEYWORD:
            result = self._parse_keyword()
        elif peek.token_type == COMMENT:
            self._consume(COMMENT, "") # We skip comments
            result = COMMENT # still we have to signal our caller we did encounter one.
        if result is None:
            self._raise_error("Unknown character")
        return result

    def _parse_if(self):
        keyword = self._consume_keyword(KW_IF, "Expected 'if'")
        expr = self._expression()
        if expr is None:
            self._raise_error("Expected parameter(expression)")
            return None
        node = ast_If(keyword, expr, self._parse_block())
        while not self._eof() and self._peek().token_value == KW_ELIF:
            kwei = self._advance()
            expr = self._expression()
            if expr is None:
                self._raise_error("Expected parameter(expression)")
                return None
            node.add_elif(ast_Elif_branch(kwei, expr, self._parse_block()))
        if not self._eof() and self._peek().token_value == KW_ELSE:
            node.add_else(ast_Else_branch(self._advance(), self._parse_block()))
        return node

    def _parse_foreach(self):
        keyword = self._consume_keyword(KW_FOREACH, "Expected 'foreach'")
        expr = self._expression()
        if expr is None:
            self._raise_error("Expected parameter(expression)")
        node = ast_Foreach(keyword, expr, self._parse_block())
        return node

    def _parse_break(self):
        node = ast_Break(self._consume_keyword(KW_BREAK, "Expected 'break'"))
        self._consume(SEMICOLON, "Expected ';'")
        return node

    def _parse_halt(self):
        keyword = self._consume_keyword(KW_HALT, "Expected 'halt'")
        expr = self._expression()
        if expr is None:
            self._raise_error("Expected parameter(expression)")
        node = ast_Halt(keyword, expr)
        self._consume(SEMICOLON, "Expected ';'")
        return node

    def _parse_return(self):
        keyword = self._consume_keyword(KW_RETURN, "Expected 'return'")
        expr = self._expression()
        if expr is None:
            self._raise_error("Expected parameter(expression)")
        node = ast_Return(keyword, expr)
        self._consume(SEMICOLON, "Expected ';'")
        return node

    def _parse_select_param(self):
        token = self._advance()
        astok = None
        asv = None
        if self._peek().token_value == KW_AS:
            astok = self._consume_keyword(KW_AS, "Expected 'as'")
            asv = self._advance()
        return SelectParam(token, astok, asv)

    def _parse_select(self):
        keyword = self._consume_keyword(KW_SELECT, "Expected 'select'")
        distinct = False
        peek = self._peek()
        if peek.token_value == KW_DISTINCT:
            self._advance()# skip distinct kw
            distinct = True
        params = []
        param = self._parse_select_param()
        params.append(param)
        while not self._eof() and self._check(COMMA):
            self._advance() # skip ,
            wparam = self._parse_select_param()
            params.append(wparam)
        _ = self._consume_keyword(KW_FROM, "Expected 'from'")
        sfrom = self._expression()
        wheretoken = None
        swhere = None
        if self._peek().token_value == KW_WHERE:
            wheretoken = self._consume_keyword(KW_WHERE, "Expected 'where'")
            swhere = self._expression()
        smerge = False
        if self._peek().token_value == KW_MERGE:
            smerge = True
            self._advance() # skip merge keyword
        _ = self._consume_keyword(KW_INTO, "Expected 'into'")
        sinto = self._expression()
        self._consume(SEMICOLON, "Expected ';'")
        node = ast_Select(keyword, params, sfrom, sinto)
        #node.set_tokens(fromtoken, intotoken)
        node.set_distinct(distinct)
        node.set_where(wheretoken, swhere)
        node.set_merge(smerge)
        return node

    def _parse_keyword(self):
        name = self._peek().token_value
        result = None
        if name == KW_IF:
            result = self._parse_if()
        elif name == KW_FOREACH:
            result = self._parse_foreach()
        elif name == KW_HALT:
            result = self._parse_halt()
        elif name == KW_BREAK:
            result = self._parse_break()
        elif name == KW_SELECT:
            result = self._parse_select()
        elif name == KW_RETURN:
            result = self._parse_return()
        if result is None:
            raise Exception(self._format_error(self._peek(), "Unknown keyword"))
        return result

    def parse(self, tokens):
        """Parses the given list of tokens into an AST tree and returns that."""
        if tokens is None:
            raise Exception("Sytax Error: Unexpected EOF.")
        self.tokens = tokens
        self.length = len(tokens)
        self.pos = 0
        root = ast_Block(None)
        while not self._eof():
            instr = self._parse_instruction()
            if instr != COMMENT:
                root.add_instruction(instr)
        return root
