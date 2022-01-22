from abc import ABC, abstractmethod

# // base class of all ASTs
class BaseAST(ABC):
    @abstractmethod
    def Eval(self):
        pass

    def GenerateIR(self, gen):
        return gen.GenerateOn(self)

    def Eval(self, intp):
        return intp.EvalOn(self)

# // function definition
class FunDefAST(BaseAST):
    def __init__(self, name, args, body) -> None:
        self.name_ = name
        self.args_ = args
        self.body_ = body

    def __str__(self):
        arg_str = ''
        if len(self.args_) > 0:
            for arg in self.args_:
                arg_str += f' {str(arg)} '
        ret = ''
        ret += f'( Func {self.name_} '
        ret += str(arg_str)
        ret += str(self.body_)
        ret += f' )'
        return ret

# // define statement
class DefineAST(BaseAST):
    def __init__(self, name, expr) -> None:
        self.name_ = name
        self.expr_ = expr

    def __str__(self):
        ret = ''
        ret += f'(:= {str(self.name_)} {str(self.expr_)} )'
        return ret

# // assign statement
class AssignAST(BaseAST):
    def __init__(self, name, expr) -> None:
        self.name_ = name
        self.expr_ = expr

    def __str__(self):
        ret = ''
        ret += f'(= {str(self.name_)} {str(self.expr_)} )'
        return ret

# // binary expression
class BinaryAST(BaseAST):
    def __init__(self, op, lhs, rhs) -> None:
        self.op_ = op
        self.lhs_ = lhs
        self.rhs_ = rhs

    def __str__(self):
        ret = ''
        ret += f'( {str(self.op_)} {str(self.lhs_)} {str(self.rhs_)} )'
        return ret

# // unary expression
class UnaryAST(BaseAST):
    def __init__(self, op, opr) -> None:
        self.op_ = op
        self.opr_ = opr

    def __str__(self):
        ret = ''
        ret += f'( {str(self.op_)} {str(self.opr_)} )'
        return ret

# // function call
class FunCallAST(BaseAST):
    def __init__(self, name, args) -> None:
        self.name_ = name
        self.args_ = args

    def __str__(self):
        arg_str = ''
        if len(self.args_) > 0:
            for arg in self.args_:
                arg_str += f' {str(arg)} '
        else:
            arg_str += ' '
        ret = ''
        ret += f'( Call {str(self.name_)}{arg_str})'
        return ret

# // integer literal
class IntAST(BaseAST):
    def __init__(self, val) -> None:
        self.val_ = val

    def __str__(self):
        ret = ''
        # ret += f'( Int {str(self.val_)} )'
        ret += f'{str(self.val_)}'
        return ret

# // identifier
class IdAST(BaseAST):
    def __init__(self, id) -> None:
        self.id_ = id

    def __str__(self):
        ret = ''
        # ret += f'( Id {str(self.id_)} )'
        ret += f'{str(self.id_)}'
        return ret

# // if-else statement
class IfAST(BaseAST):
    def __init__(self, cond, then, else_then) -> None:
        self.cond_ = cond
        self.then_ = then
        self.else_then_ = else_then

    def __str__(self):
        ret = ''
        if self.else_then_ == None:
            ret += f'( If {str(self.cond_)} {str(self.then_)} )'
        else:
            ret += f'( If {str(self.cond_)} {str(self.then_)} {str(self.else_then_)} )'
        return ret

# // return statement
class ReturnAST(BaseAST):
    def __init__(self, expr) -> None:
        self.expr_ = expr

    def __str__(self):
        ret = ''
        ret += f'(Return {str(self.expr_)} )'
        return ret

# // statement block
class BlockAST(BaseAST):
    def __init__(self, stmts) -> None:
        self.stmts_ = stmts

    def __str__(self):
        stmts_str = ''
        for stmt in self.stmts_:
            stmts_str += f' {str(stmt)} '
        ret = ''
        ret += f'( Block{stmts_str})'
        return ret
