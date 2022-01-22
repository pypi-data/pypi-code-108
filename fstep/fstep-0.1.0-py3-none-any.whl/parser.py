from .lexer import *
from .ast import *

class Parser(object):
    def __init__(self, lexer) -> None:
        self.lexer = lexer
        self.error_num_ = ''
        self.cur_token_ = ''
        self.NextToken()

    def ParseNext(self):
        if self.cur_token_ == Token.End:
            return None
        else:
            return self.ParseFunDef()

    def ExpectId(self):
        return self.cur_token_ == Token.Id

    def NextToken(self):
        self.cur_token_ = self.lexer.NextToken()

    def IsTokenChar(self, chr):
      return self.cur_token_ == Token.Other and self.lexer.other_val_ == chr
      
    def ExpectChar(self, chr):
        if not self.IsTokenChar(chr):
            return False
        self.NextToken()
        return True

    # // check if the current token is the specific operator
    def IsTokenOp(self, op):
        return self.cur_token_ == Token.Operator and self.lexer.op_val_ == op
  
    def ParseBinary(self, parser, ops):
        # // get left-hand side expression
        lhs = parser()
        if lhs == None:
            return None

        def get_op(lhs):
            # // get operator
            op = self.lexer.op_val_
            self.NextToken()
            # // get right-hand side expression
            rhs = parser()
            if rhs == None:
                return None
            # // update lhs
            lhs = BinaryAST(op, lhs, rhs)
            return lhs

        # // get the rest things
        while self.cur_token_ == Token.Operator and self.lexer.op_val_ in ops:
            lhs = get_op(lhs)
            if lhs == None:
                return None
        return lhs

    def ParseFunCall(self):
        # // get function name
        name = self.lexer.id_val_
        # // eat '('
        self.NextToken()
        # // get arguments
        args = []
        if not self.IsTokenChar(')'):
            while True:
                # // get the current argument
                expr = self.ParseExpr()
                if not expr:
                    return None
                args.append(expr)
                # // eat ','
                if not self.IsTokenChar(','):
                    break
                self.NextToken()
        # // check & eat ')'
        if not self.ExpectChar(')'):
            return None

        return FunCallAST(name, args)

    def ParseValue(self):
        if self.cur_token_ == Token.Integer:
            # // get integer literal
            val = self.lexer.int_val_
            self.NextToken()
            return IntAST(val)
        elif self.cur_token_ == Token.Id:
            # // get identifier
            id = self.lexer.id_val_
            self.NextToken()
            # // check if the current token is '('
            return self.ParseFunCall() if self.IsTokenChar('(') else IdAST(id)
        elif self.cur_token_ == Token.Other:
            if self.lexer.other_val_ == '(':
                # // eat '('
                self.NextToken()
                # // get expression
                expr = self.ParseExpr()
                if expr == None:
                    return None
                # // check & eat ')'
                self.ExpectChar(')')
                return expr
        print('# invalid value')
        return None

    def ParseUnaryExpr(self):
        if self.cur_token_ == Token.Operator:
            # // get operator
            op = self.lexer.op_val_
            self.NextToken()
            # // check if is a valid operator
            if op not in [Operator.Sub,Operator.LNot]:
                print(f"invalid unary operator, {op}")
                return None
            # // get operand
            opr = self.ParseValue()
            if opr == None:
                return None
            return UnaryAST(op, opr)
        else:
            return self.ParseValue()

    def ParseMulExpr(self):
        return self.ParseBinary(self.ParseUnaryExpr, [Operator.Mul, Operator.Div, Operator.Mod])

    def ParseAddExpr(self):
        return self.ParseBinary(self.ParseMulExpr, [Operator.Add, Operator.Sub])

    def ParseRelExpr(self):
        return self.ParseBinary(self.ParseAddExpr, [Operator.Less, Operator.LessEq])

    def ParseEqExpr(self):
        return self.ParseBinary(self.ParseRelExpr, [Operator.Eq, Operator.NotEq])

    def ParseLAndExpr(self):
        return self.ParseBinary(self.ParseEqExpr, [Operator.LAnd])

    def ParseExpr(self):
        return self.ParseBinary(self.ParseLAndExpr, [Operator.LOr])

    def ParseDefineAssign(self):
        # // get name of variable
        name = self.lexer.id_val_
        self.NextToken()
        # // check if is a function call
        if self.IsTokenChar('('):
            return self.ParseFunCall()
        # // check if is define/assign
        if not self.IsTokenOp(Operator.Define) and not self.IsTokenOp(Operator.Assign):
            print("# todo")
            return None
        is_define = self.lexer.op_val_ == Operator.Define
        self.NextToken()
        # // get expression
        expr = self.ParseExpr()
        if not expr:
            print("# todo")
            return None
        if is_define:
            return DefineAST(name, expr)
        return AssignAST(name, expr)

    def IsTokenKey(self, key):
        # // check if the current token is the specific keyword
        return  self.cur_token_ == Token.Keyword and self.lexer.key_val_ == key

    def ParseIfElse(self):
        # // eat 'if'
        self.NextToken()
        # // get condition
        cond = self.ParseExpr()
        if cond == None:
            return None
        # // get 'then' body
        then = self.ParseBlock()
        if then == None:
            print('# get then failed todo')
            return None
        # // get 'else-then' body
        else_then = None
        if self.IsTokenKey(Keyword.Else):
            # // eat 'else'
            self.NextToken()
            else_then = self.ParseIfElse() if self.IsTokenKey(Keyword.If) else self.ParseBlock()
            if else_then == None:
                print('# get else_then failed todo')
                return None
        return IfAST(cond, then, else_then)

    def ParseReturn(self):
        # // eat 'return'
        self.NextToken()
        # // get return value
        expr = self.ParseExpr()
        if expr == None:
            print('# ParseReturn failed todo')
            return None
        return ReturnAST(expr)

    def ParseStatement(self):
        if self.cur_token_ == Token.Id:
            return self.ParseDefineAssign()
        elif self.cur_token_ == Token.Keyword:
            if self.lexer.key_val_ == Keyword.If:
                return self.ParseIfElse()
            elif self.lexer.key_val_ == Keyword.Return:
                return self.ParseReturn()
            else:
                print("# fallthrough todo", self.cur_token_, self.lexer.key_val_)                                
        print("# invalid statement todo")
        return None

    def ParseBlock(self):
        # // check & eat '{'
        if not self.ExpectChar('{'):
            assert False, f"{Token.Other}, {self.lexer.other_val_}, {self.lexer.line_no_}"
            return None
        # // get statements
        stmts = []
        while not self.IsTokenChar('}'):
            stmt = self.ParseStatement()
            if stmt == None:
                print('# ParseStatement failed todo')
                return None
            stmts.append(stmt)
        # // eat '}'
        self.NextToken()
        return BlockAST(stmts)

    def ParseFunDef(self):
        # // get function name
        if not self.ExpectId():
            print('# ParseFunDef failed todo')
            return None
        name = self.lexer.id_val_
        self.NextToken()
        # // check & eat '('
        if not self.ExpectChar('('):
            print('# ParseFunDef failed todo')
            return None
        # // get formal arguments
        args = []
        if not self.IsTokenChar(')'):
            while True:
                # // get name of the current argument
                if not self.ExpectId():
                    print('# ParseFunDef failed todo')
                    return None
                args.append(self.lexer.id_val_)
                self.NextToken()
                # // eat ','
                if not self.IsTokenChar(','):
                    break
                self.NextToken()

        # // check & eat ')'
        if not self.ExpectChar(')'):
            print('# ParseFunDef failed todo')
            return None
        # // get function body        
        body = self.ParseBlock()
        if not body:
            print('# ParseFunDef failed todo')
            return None
        return FunDefAST(name, args, body)
