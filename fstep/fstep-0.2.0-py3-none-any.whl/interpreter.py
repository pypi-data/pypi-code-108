import sys
from .lexer import *

# // environments
class Environment(dict):
    current = None

    def __enter__(self):
        self._old_scope = Environment.current
        Environment.current = self
        return self

    def __exit__(self, ptype, value, trace):
        Environment.current = self._old_scope

    def get_item(self, k, recursive=True):
        ret = self.get(k, None)
        if ret == None and recursive and self._old_scope != None:
            return self._old_scope.get_item(k)
        return ret

    # // update item
    # // returns true if the update operation takes effect
    def update_item(self, k, v, recursive=True):
        it = self.get(k, None)
        if it != None:
            self[k] = v
            return True
        elif it == None and recursive and self._old_scope != None:
            return self._old_scope.update_item(k,v)
        return False

def getstring():
    buff = ''
    while True:
        chr = sys.stdin.read(1)
        # print(chr)
        if chr in ' \n\r\t':
            break
        buff += chr
    return buff

class Interpreter(object):
    # // name of return value
    kRetVal = "$ret"

    def __init__(self) -> None:
        self.error_num_ = 0
        # // name of the current function
        self.func_name_ = ''

        # // all function definitions
        self.funcs_ = {}
        # // environments
        self.envs_ = None

    # // count of error
    def error_num(self):
        return self.error_num_

    # // add the specific function definition to interpreter
    # // returns false if failed
    def AddFunctionDef(self, func):
        # // check redefinition
        # if (funcs_.count(func_name_)) {
        # LogError("function has already been defined");
        # return false;
        # }
        # // add to function map
        self.funcs_.update({func.name_:func})
        return True

    # // perform library function call
    def CallLibFunction(self, name, args):
        if name == "input":
            # // check arguments
            if len(args) != 0:
                print("argument count mismatch")
                return None
            # // read an integer from stdin
            # ret = input()
            ret = getstring()
            return int(ret)
        elif name == "print":
            # // check arguments
            if len(args) != 1:
                print("argument count mismatch")
                return None
            # // evaluate argument
            arg = args[0].Eval(self)
            # import pdb;pdb.set_trace()
            if arg == None:
                return None
            # // print to stdout
            print(arg)
            return 0
        else:
            # // not a library function call
            return None

    # // evaluate the current program
    # // returns return value of 'main' function, or 'nullopt' if failed
    def Eval(self):
        # // find the 'main' function
        it = self.funcs_.get("main", None)
        if it == None:
            print("'main' function not found")
            return None
        # // initialize the root environment
        with Environment() as envs:
            # self.envs_ = envs
            # // evaluate 'main' function
            return it.Eval(self)

    # // visitor methods
    def EvalOn(self, ast):
        # print('EvalOn'+ast.__class__.__name__)
        # return getattr(self, 'GenerateOn'+ast.__class__.__name__)(ast)
        m = getattr(self, 'EvalOn'+ast.__class__.__name__)
        r = m(ast)
        return r
        
    def EvalOnFunDefAST(self, ast):
        # // set up return value
        # self.envs_.update({self.kRetVal:{}})
        Environment.current.update({self.kRetVal:{}})
        # // evaluate function body
        ast.body_.Eval(self)
        # // get & check return value
        # ret_val = self.envs_.get_item(self.kRetVal, False)
        ret_val = Environment.current.get_item(self.kRetVal, False)
        if ret_val in [None, {}]:
            print("function has no return value")
            return None
        return ret_val

    def EvalOnBlockAST(self, ast):
        # // enter a new environment
        with Environment() as envs:
            # // evaluate all statements in block
            for stmt in ast.stmts_:
                stmt.Eval(self)
                # // stop if there is an error
                if self.error_num_:
                    print('EvalOnBlockAST error todo')
                    return None
                # // stop if return
                if Environment.current.get_item(self.kRetVal) not in [None,{}]:
                    return None
            return None
    
    def EvalOnDefineAST(self, ast):
        # // evaluate the expression
        expr = ast.expr_.Eval(self)
        if expr == None:
            return None
        # // update the current environment
        if ast.name_ in Environment.current:
            print("symbol has already been defined")
            return None
        Environment.current.update({ast.name_:expr})
        return None

    def EvalOnAssignAST(self, ast):
        # // evaluate the expression
        expr = ast.expr_.Eval(self)
        if expr == None:
            return None
        # // update value of the symbol
        envs = Environment.current
        succ = False
        while envs != None:
            # // try to update the value
            if envs.update_item(ast.name_, expr, False):
                succ = True
                break
            # // do not cross the boundary of function
            if envs.get_item(self.kRetVal, False):
                break
            envs = envs._old_scope
        # // check if success
        if not succ:
            import pdb;pdb.set_trace()
            print("symbol has not been defined")
            return None

    def EvalOnIfAST(self, ast):
        # // evaluate the condition
        cond = ast.cond_.Eval(self)
        if cond == None:
            return None
        if cond:
            # // evaluate the true branch
            ast.then_.Eval(self)
        elif ast.else_then_:
            # // evaluate the false branch
            ast.else_then_.Eval(self)
        return None

    def EvalOnReturnAST(self, ast):
        # // evaluate the return value
        expr = ast.expr_.Eval(self)
        if expr == None:
            return None
        # // update the current return value
        # succ = self.envs_.update_item(self.kRetVal, expr)
        succ = Environment.current.update_item(self.kRetVal, expr)
        assert succ and "environment corrupted"
        return None

    def EvalOnBinaryAST(self, ast):
        # // check if is logical operator
        if ast.op_ == Operator.LAnd or ast.op_ == Operator.LOr:
            # // evaluate lhs first
            lhs = ast.lhs_.Eval(self)
            # assert lhs != None
            if  lhs == None or (ast.op_ == Operator.LAnd and not lhs) or (ast.op_ == Operator.LOr and lhs):
                return lhs
            # // then evaluate rhs
            return ast.rhs_.Eval(self)
        else:
            # // evaluate the lhs & rhs
            lhs = ast.lhs_.Eval(self)
            rhs = ast.rhs_.Eval(self)
            if lhs == None or rhs == None:
                return None
            # // perform binary operation
            if ast.op_ == Operator.Add:
                return lhs + rhs
            elif ast.op_ == Operator.Sub: 
                return lhs - rhs
            elif ast.op_ == Operator.Mul: 
                return lhs * rhs
            elif ast.op_ == Operator.Div: 
                return lhs // rhs
            elif ast.op_ == Operator.Mod: 
                return lhs % rhs
            elif ast.op_ == Operator.Less: 
                return lhs < rhs
            elif ast.op_ == Operator.LessEq: 
                return lhs <= rhs
            elif ast.op_ == Operator.Eq: 
                return int(lhs) == int(rhs)
            elif ast.op_ == Operator.NotEq: 
                return int(lhs) != int(rhs)
            else:
                assert False and "unknown binary operator"

            return None

    def EvalOnUnaryAST(self, ast):
        #   // evaluate the operand
        opr = ast.opr_.Eval(self)
        if opr == None:
            return None
        #   // perform unary operation
        if ast.op_ == Operator.Sub: 
            return -opr
        elif ast.op_ == Operator.LNot: 
            return not opr
        else:
            assert False and "unknown unary operator"
        return None

    def EvalOnFunCallAST(self, ast):
        # // handle library function call
        ret = self.CallLibFunction(ast.name_, ast.args_)
        # if self.error_num_ or ret:
        if ret != None:
            # print(f'EvalOnFunCallAST {ast.name_} {ret} {self.error_num_}')
            return ret
        # // find the specific function
        it = self.funcs_.get(ast.name_, None)
        if it == None:
            print(f"{ast.name_} function not found")
            return None
        # // make a new environment for arguments
        with Environment() as envs:
            # // evaluate arguments
            func_args = it.args_
            if len(ast.args_) != len(func_args):
                print("argument count mismatch")
                return None
            for i in range(len(func_args)):
                # // evaluate the current argument
                arg = ast.args_[i].Eval(self)
                if arg == None:
                    return None
                # // add to environment
                if func_args[i] in envs:
                    print("redifinition of argument")
                    return None
                envs.update({func_args[i]:arg})
            # // call the specific function
            return it.Eval(self)

    def EvalOnIntAST(self, ast):
        return ast.val_

    def EvalOnIdAST(self, ast):
        # // find in the current environment
        val = Environment.current.get_item(ast.id_)
        if val == None:
            print("symbol has not been defined")
            return None
        return val

