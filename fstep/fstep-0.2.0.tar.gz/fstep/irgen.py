from .ir import *
from .lexer import *

# // all defined variables (stack slots)
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

class IRGenerator(object):

    def __init__(self) -> None:
        # // current function
        self.func_ = None
        # // all defined functions
        self.funcs_ = {}
        # // all predefined library functions
        self.lib_funcs_ = {}

        self.error_num_ = 0
        # // register all of the library functions
        self.lib_funcs_.update({"input":FunctionDef("input", 0)})
        self.lib_funcs_.update({"print":FunctionDef("print", 1)})

    # // print error message to stderr
    # ValPtr LogError(std::string_view message);
    # // count of error
    def error_num(self):
        return self.error_num_

    # // dump RISC-V assembly of all generated IRs
    def Dump(self, os):
        for it in self.funcs_.values():
            it.Dump(os)

    def __str__(self):
        for it in self.funcs_.values():
            print(it)
        return ''

    # // visitor methods
    def GenerateOn(self, ast):
        # print('GenerateOn'+ast.__class__.__name__)
        # return getattr(self, 'GenerateOn'+ast.__class__.__name__)(ast)
        m = getattr(self, 'GenerateOn'+ast.__class__.__name__)
        r = m(ast)
        return r

    def GenerateOnFunDefAST(self, ast):
        # // check argument count
        if len(ast.args_) > 8:
            print("argument count must be less than or equal to 8")
            return None
        # // create function definition IR
        self.func_ = FunctionDef(ast.name_, len(ast.args_))
        # // add to function map
        if self.func_.name_ in self.funcs_:
            print('function has already been defined')
            return None
        self.funcs_[self.func_.name_] = self.func_
        # // enter argument environment
        with Environment() as vars:
            # // add definitions of arguments
            for i in range(len(ast.args_)):
                vars.update({ast.args_[i]:ArgRefVal(i)})
            # // generate body
            ast.body_.GenerateIR(self)
        return None
    
    def GenerateOnBlockAST(self, ast):
        # // enter a new environment
        with Environment() as vars:
            # // generate on all statements
            for stmt in ast.stmts_:
                stmt.GenerateIR(self)
                # if self.error_num_:  # todo
                #     return None
        return None

    def GenerateOnDefineAST(self, ast):
        # // generate expression
        expr = ast.expr_.GenerateIR(self)
        if not expr:
            return None
        # // add symbol definition
        slot = self.func_.AddSlot()
        if ast.name_ in Environment.current:
            print("symbol has already been defined")
            return None
        Environment.current.update({ast.name_:slot})
        # // generate assign instruction
        self.func_.PushInst(AssignInst(slot, expr))
        return None

    def GenerateOnAssignAST(self, ast):
        # // generate expression
        expr = ast.expr_.GenerateIR(self)
        if not expr:
            return None
        # // get stack slot of the symbol
        slot = Environment.current.get_item(ast.name_)
        if slot == None:
            print("symbol has not been defined")
            return None
        # // generate assign instruction
        self.func_.PushInst(AssignInst(slot, expr))
        return None

    def GenerateOnIfAST(self, ast):
        # // generate condition
        cond = ast.cond_.GenerateIR(self)
        if cond == None:
            return None
        # // create labels
        false_branch = LabelVal()
        end_if = LabelVal() if ast.else_then_ else None
        #// generate contional branch
        self.func_.PushInst(BranchInst(False, cond, false_branch))
        # // generate the true branch
        ast.then_.GenerateIR(self)
        if ast.else_then_:
            self.func_.PushInst(JumpInst(end_if))
        # // generate the false branch
        self.func_.PushInst(LabelInst(false_branch))
        if ast.else_then_:
            ast.else_then_.GenerateIR(self)
            self.func_.PushInst(LabelInst(end_if))
        return None

    def GenerateOnReturnAST(self, ast):
        # // generate return value
        expr = ast.expr_.GenerateIR(self)
        if expr == None:
            return None
        # // generate return instruction
        self.func_.PushInst(ReturnInst(expr))
        return None

    def GenerateOnBinaryAST(self, ast):
        # // check if is logical operator
        if ast.op_ == Operator.LAnd or ast.op_ == Operator.LOr:
            # // logical AND operation, generate labels
            end_logic = LabelVal()
            # // generate lhs first
            lhs = ast.lhs_.GenerateIR(self)
            if lhs == None:
                return None
            # // generate conditional branch
            self.func_.PushInst(BranchInst(ast.op_ == Operator.LOr, lhs, end_logic))
            # // generate rhs
            rhs = ast.rhs_.GenerateIR(self)
            if rhs == None:
                return None
            self.func_.PushInst(AssignInst(lhs, rhs))
            # // generate label definition
            self.func_.PushInst(LabelInst(end_logic))
            return lhs
        else:
            # // generate lhs & rhs
            lhs = ast.lhs_.GenerateIR(self)
            rhs = ast.rhs_.GenerateIR(self)
            if lhs == None or rhs == None:
                return None
            # // generate binary operation
            dest = self.func_.AddSlot()
            self.func_.PushInst(BinaryInst(ast.op_, dest, lhs, rhs))
            return dest

    def GenerateOnUnaryAST(self, ast):
        # // generate operand
        opr = ast.opr_.GenerateIR(self)
        if opr == None:
            return None
        # // generate unary operation
        dest = self.func_.AddSlot()
        self.func_.PushInst(UnaryInst(ast.op_, dest, opr))
        return dest
        
    def GenerateOnFunCallAST(self, ast):
        # // get the function definition
        if ast.name_ not in self.funcs_:
            if ast.name_ not in self.lib_funcs_:
                print('function not found')
                return None
            else:
                it = self.lib_funcs_[ast.name_]                    
        else:
            it = self.funcs_[ast.name_]
        # // check argument count
        if len(ast.args_) != it.arg_num_:
            print("argument count mismatch")
            return None
        # // generate arguments
        args = []
        for i in ast.args_:
            arg = i.GenerateIR(self)
            if arg == None:
                return None
            args.append(arg)
        # // generate function call
        dest = self.func_.AddSlot()
        self.func_.PushInst(CallInst(dest, it, args))
        return dest
        
    def GenerateOnIntAST(self, ast):
        return IntVal(ast.val_)

    def GenerateOnIdAST(self, ast):
        # // get stack slot of the symbol
        slot = Environment.current.get_item(ast.id_)
        if slot == None:
            print("symbol has not been defined")
            return None
        return slot

