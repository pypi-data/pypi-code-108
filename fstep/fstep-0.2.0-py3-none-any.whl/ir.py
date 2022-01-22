from abc import ABC, abstractmethod
from .lexer import *

# // base class of all ASTs
class BaseAST(ABC):
    @abstractmethod
    def Eval(self):
        pass

    @abstractmethod
    def GenerateIR(self):
        pass

# // base class of all instructions
class InstBase(ABC):
    # // dump RISC-V assembly of the current instruction
    @abstractmethod
    def Dump(self):
        pass

# // base class of all values
class ValueBase(ABC):
    # // dump RISC-V assembly of read operation
    @abstractmethod
    def DumpRead(self):
        pass
    # // dump RISC-V assembly of write operation
    @abstractmethod
    def DumpWrite(self):
        pass

# // register for storing the intermediate results
kResultReg = "t0"
# // register for storing the temporary data
kTempReg = "t1"

# // function definition
class FunctionDef(object):
    def __init__(self, name, arg_num) -> None:
        self.name_ = name
        self.arg_num_ = arg_num
        self.slot_num_ = 0
        self.insts_ = []

    # // create & push instruction to current function
    def PushInst(self, inst):
        # print('PushInst', inst.__class__.__name__)
        self.insts_.append(inst)

    # // create a new stack slot definition
    def AddSlot(self):
        slot = SlotVal(self.slot_num_)
        self.slot_num_ += 1
        return slot

    #// dump RISC-V assembly of the current function
    def Dump(self, os):
        # // dump header
        os.write("  .text\n")
        os.write(f"  .globl {self.name_}\n")
        os.write(f"{self.name_}:\n")
        # // dump prologue
        os.write(f"  addi sp, sp, -{int(self.slot_offset())}\n")
        os.write(f"  sw ra, {int(self.slot_offset() - 4)}(sp)\n")
        assert(self.arg_num_ <= 8 and "argument count is greater than 8")
        for i in range(0,self.arg_num_):
            os.write(f"  sw s{i}, {int(self.slot_offset() - 4 * (i + 2))}(sp)\n")
            os.write(f"  mv s{i}, a{i}\n")
        # // dump instructions
        for inst in self.insts_:
            inst.Dump(os, self)
        os.write('\n')

    def __str__(self):
        print('FunctionDef')
        print(self.name_, self.arg_num_, self.slot_num_)
        # import pdb;pdb.set_trace()
        for inst in self.insts_:
            print(inst)
        return ''

    #// getters
    def name(self):
        return self.name_
    def arg_num(self):
        return self.arg_num_
    def slot_offset(self):
        return ((self.arg_num_ + self.slot_num_) // 4 + 1) * 16

# // assignment
class AssignInst(InstBase):
    def __init__(self, dest, val) -> None:
        self.dest_ = dest
        self.val_ = val

    def Dump(self, os, func):
        self.val_.DumpRead(os)
        self.dest_.DumpWrite(os)

    def __str__(self):
        print('AssignInst')
        print(self.dest_)
        print(self.val_)
        return ''

# // conditional branch
class BranchInst(InstBase):
    def __init__(self, bnez, cond, label) -> None:
        self.bnez_ = bnez
        self.cond_ = cond
        self.label_ = label

    def Dump(self, os, func):
        self.cond_.DumpRead(os)
        os.write(f"  {'bnez' if self.bnez_ else 'beqz'} {kResultReg}, ")
        self.label_.DumpRead(os)
        os.write('\n')

    def __str__(self):
        print('BranchInst')
        print(self.bnez_)
        print(self.cond_)
        print(self.label_)
        return ''

# // unconditional jump
class JumpInst(InstBase):
    def __init__(self, label) -> None:
        self.label_ = label

    def Dump(self, os, func):
        os.write("  j ")
        self.label_.DumpRead(os)
        os.write('\n')

    def __str__(self):
        print('JumpInst')
        print(self.label_)
        return ''

# // label definition
class LabelInst(InstBase):
    def __init__(self, label) -> None:
        self.label_ = label

    def Dump(self, os, func):
        self.label_.DumpRead(os)
        os.write(':\n')

    def __str__(self):
        print('LabelInst')
        print(self.label_)
        return ''

# // function call
class CallInst(InstBase):
    def __init__(self, dest, func, args) -> None:
        self.dest_ = dest
        self.func_ = func
        self.args_ = args

    def Dump(self, os, func):
        # // generate arguments
        # assert(args_.size() <= 8 && "argument count is greater than 8");
        for i in range(0,len(self.args_)):
            self.args_[i].DumpRead(os)
            os.write(f"  mv a{i}, {kResultReg}\n")
        # // generate function call
        os.write(f"  call {self.func_.name()}\n")
        os.write(f"  mv {kResultReg}, a0\n")
        self.dest_.DumpWrite(os)

    def __str__(self):
        print('CallInst')
        print(self.dest_)
        print(self.func_.name())
        for arg in self.args_:
            print(arg)
        return ''

# // function return
class ReturnInst(InstBase):
    def __init__(self, val) -> None:
        self.val_ = val

    def Dump(self, os, func):
        # // dump return value
        self.val_.DumpRead(os)
        os.write(f"  mv a0, {kResultReg}\n")
        # // dump epilogue
        # assert(func.arg_num() <= 8 && "argument count is greater than 8");
        for i in range(func.arg_num()):
            os.write(f"  lw s{i}, {int(func.slot_offset() - 4 * (i + 2))}(sp)\n")
        os.write(f"  lw ra, {int(func.slot_offset() - 4)}(sp)\n")
        os.write(f"  addi sp, sp, {int(func.slot_offset())}\n")
        os.write("  ret\n")

    def __str__(self):
        print('ReturnInst')
        print(self.val_)
        return ''

# // binary operation
class BinaryInst(InstBase):
    def __init__(self, op, dest, lhs, rhs) -> None:
        self.op_ = op
        self.dest_ = dest
        self.lhs_ = lhs
        self.rhs_ = rhs

    def Dump(self, os, func):
        #// dump lhs & rhs
        self.lhs_.DumpRead(os)
        os.write(f"  mv {kTempReg}, {kResultReg}\n")
        self.rhs_.DumpRead(os)
        # // perform binary operation
        if self.op_ == Operator.LessEq:
            os.write(f"  sgt {kResultReg}, {kTempReg}, {kResultReg}\n")
            os.write(f"  seqz {kResultReg}, {kResultReg}\n")
        elif self.op_ == Operator.Eq or self.op_ == Operator.NotEq:
            os.write(f"  xor {kResultReg}, {kTempReg}, {kResultReg}\n")
            os.write(f"  {'seqz' if self.op_ == Operator.Eq else 'snez'} {kResultReg}, {kResultReg}\n")
        else:
            os.write(f"  ")
            if self.op_ == Operator.Add: 
                os.write(f"add")
            elif self.op_ == Operator.Sub:
                os.write(f"sub")
            elif self.op_ == Operator.Mul:
                os.write(f"mul")
            elif self.op_ == Operator.Div:
                os.write(f"div")
            elif self.op_ == Operator.Mod:
                os.write(f"rem")
            elif self.op_ == Operator.Less:
                os.write(f"slt")
            else:
                assert False and "unknown binary operator"
            os.write(f' {kResultReg}, {kTempReg}, {kResultReg}\n')
        # // store the result to dest
        self.dest_.DumpWrite(os)

    def __str__(self):
        print('BinaryInst')
        print(self.op_)
        print(self.dest_)
        print(self.lhs_)
        print(self.rhs_)
        return ''

# // unary operation
class UnaryInst(InstBase):
    def __init__(self, op, dest, opr) -> None:
        self.op_ = op
        self.dest_ = dest
        self.opr_ = opr

    def Dump(self, os, func):
        # // generate operand
        self.opr_.DumpRead(os)
        # // perform unary operation
        os.write(f"  ")
        if self.op_ == Operator.Sub: 
            os.write(f"neg")
        elif self.op_ == Operator.LNot:
            os.write(f"seqz")
        else:
            assert False and "unknown unary operator"
        os.write(f' {kResultReg}, {kResultReg}\n')
        # // store the result to dest
        self.dest_.DumpWrite(os)

    def __str__(self):
        print('UnaryInst')
        print(self.op_)
        print(self.dest_)
        print(self.opr_)
        return ''

# // stack slot
class SlotVal(ValueBase):
    def __init__(self, id) -> None:
        self.id_ = id

    def DumpRead(self, os):
        os.write(f"  lw {kResultReg}, {self.id_ * 4}(sp)\n")

    def DumpWrite(self, os):
        os.write(f"  sw {kResultReg}, {self.id_ * 4}(sp)\n")

    def __str__(self):
        print('SlotVal')
        print(self.id_)
        return ''

# // argument reference
class ArgRefVal(ValueBase):
    def __init__(self, id) -> None:
        self.id_ = id

    def DumpRead(self, os):
        os.write(f"  mv {kResultReg}, s{self.id_}\n")

    def DumpWrite(self, os):
        os.write(f"  mv s{self.id_}, {kResultReg}\n")

    def __str__(self):
        print('ArgRefVal')
        print(self.id_)
        return ''

# // label
class LabelVal(ValueBase):
    next_id_ = 0
    def __init__(self) -> None:
        self.id_ = LabelVal.next_id_
        LabelVal.next_id_ += 1

    def DumpRead(self, os):
        os.write(f".label{self.id_}")

    def DumpWrite(self, os):
        assert False and "writing a label"

    def __str__(self):
        print('LabelVal')
        print(self.id_)
        return ''

# // integer
class IntVal(ValueBase):
    def __init__(self, val) -> None:
        self.val_ = val

    def DumpRead(self, os):
        os.write(f"  li {kResultReg}, {self.val_}\n")

    def DumpWrite(self, os):
        assert False and "writing an integer"

    def __str__(self):
        print('IntVal')
        print(self.val_)
        return ''