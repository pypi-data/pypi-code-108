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
        print(f'FunDefAST: {self.name_}')
        print(self.args_)
        print(self.body_)
        return ''

# // define statement
class DefineAST(BaseAST):
    def __init__(self, name, expr) -> None:
        self.name_ = name
        self.expr_ = expr

    def __str__(self):
        print(f'DefineAST: {self.name_}')
        print(self.expr_)
        return ''

# // assign statement
class AssignAST(BaseAST):
    def __init__(self, name, expr) -> None:
        self.name_ = name
        self.expr_ = expr

    def __str__(self):
        print(f'AssignAST:')
        print(self.name_)
        print(self.expr_)
        return ''

# // binary expression
class BinaryAST(BaseAST):
    def __init__(self, op, lhs, rhs) -> None:
        self.op_ = op
        self.lhs_ = lhs
        self.rhs_ = rhs

    def __str__(self):
        print(f'BinaryAST:')
        print(self.op_)
        print(self.lhs_)
        print(self.rhs_)
        return ''

# // unary expression
class UnaryAST(BaseAST):
    def __init__(self, op, opr) -> None:
        self.op_ = op
        self.opr_ = opr

    def __str__(self):
        print(f'UnaryAST:')
        print(self.op_)
        print(self.opr_)
        return ''

# // function call
class FunCallAST(BaseAST):
    def __init__(self, name, args) -> None:
        self.name_ = name
        self.args_ = args

    def __str__(self):
        print(f'FunCallAST: {self.name_}')
        for arg in self.args_:
            print(arg)
        return ''

# // integer literal
class IntAST(BaseAST):
    def __init__(self, val) -> None:
        self.val_ = val

    def __str__(self):
        print(f'IntAST:')
        print(self.val_)
        return ''

# // identifier
class IdAST(BaseAST):
    def __init__(self, id) -> None:
        self.id_ = id

    def __str__(self):
        print(f'IdAST:')
        print(self.id_)
        return ''

# // if-else statement
class IfAST(BaseAST):
    def __init__(self, cond, then, else_then) -> None:
        self.cond_ = cond
        self.then_ = then
        self.else_then_ = else_then

    def __str__(self):
        print(f'IfAST:')
        print(self.cond_)
        print(self.then_)
        print(self.else_then_)
        return ''

# // return statement
class ReturnAST(BaseAST):
    def __init__(self, expr) -> None:
        self.expr_ = expr

    def __str__(self):
        print(f'ReturnAST:')
        print(self.expr_)
        return ''

# // statement block
class BlockAST(BaseAST):
    def __init__(self, stmts) -> None:
        self.stmts_ = stmts

    def __str__(self):
        print(f'BlockAST:')
        for i,stmt in enumerate(self.stmts_):
            print('stmt',i)
            print(stmt)
        return ''
