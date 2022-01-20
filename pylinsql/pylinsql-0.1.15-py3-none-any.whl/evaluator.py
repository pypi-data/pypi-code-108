"""
Builds a symbolic expression by evaluating low-level instructions.

This module is used internally.
"""

import builtins
import dis
import sys
from dataclasses import dataclass
from dis import Instruction
from types import CodeType
from typing import Optional

from .ast import *


class JumpResolver:
    # each instruction is 2 bytes
    INST_SIZE: ClassVar[int] = 2

    _next: int

    def process(self, instr: dis.Instruction) -> Tuple[int, int]:
        # automatically fall through to subsequent block
        self._next = instr.offset + __class__.INST_SIZE

        fn = getattr(self, instr.opname, None)
        if fn is not None:
            return fn(instr.arg)
        elif self.test(instr):
            raise NotImplementedError(
                f"jump instruction {instr.opname} is not recognized"
            )
        else:
            return self._next, self._next

    def test(self, instr: dis.Instruction) -> bool:
        "True if the Python instruction involves a jump with a target, e.g. JUMP_ABSOLUTE or POP_JUMP_IF_TRUE."

        return instr.opcode in dis.hasjabs or instr.opcode in dis.hasjrel

    def JUMP_ABSOLUTE(self, target):
        addr = self._abs(target)
        return addr, addr

    def JUMP_FORWARD(self, delta):
        addr = self._rel(delta)
        return addr, addr

    def JUMP_IF_FALSE_OR_POP(self, target):
        return self._next, self._abs(target)

    def JUMP_IF_TRUE_OR_POP(self, target):
        return self._abs(target), self._next

    def POP_JUMP_IF_FALSE(self, target):
        return self._next, self._abs(target)

    def POP_JUMP_IF_TRUE(self, target):
        return self._abs(target), self._next

    def FOR_ITER(self, delta):
        return self._next, self._rel(delta)

    def RETURN_VALUE(self, _):
        return None, None

    def _abs(self, target):
        if sys.version_info >= (3, 10):
            return __class__.INST_SIZE * target
        else:
            return target

    def _rel(self, delta):
        if sys.version_info >= (3, 10):
            return self._next + __class__.INST_SIZE * delta
        else:
            return self._next + delta


@dataclass(frozen=True)
class _IteratorValue:
    "Placeholder for iterator value pushed to the stack by the FOR_ITER instruction."

    pass


@dataclass
class BasicBlockResult:
    stack: Stack = None
    # expression on which the final jump instruction in the block is evaluated
    jump_expr: Optional[Expression] = None
    # expression that is produced by a YIELD_VALUE instruction
    yield_expr: Optional[Expression] = None
    # expression that is returned by a RETURN_VALUE instruction
    return_expr: Optional[Expression] = None


class Evaluator:
    codeobject: CodeType
    stack: Stack
    variables: List[str]

    _expr: BasicBlockResult
    _jump_cond: bool

    def __init__(self, codeobject):
        self.codeobject = codeobject
        self.stack = []
        self.variables = []

    def _reset(self):
        self._expr = BasicBlockResult()

    def process_block(
        self, instructions: List[Instruction], stack: Stack, jump_cond: bool
    ) -> BasicBlockResult:
        "Process a single basic block, ending with a (conditional) jump."

        self.stack = stack.copy()
        self._jump_cond = jump_cond
        self._reset()
        for instruction in instructions:
            fn = getattr(self, instruction.opname)
            fn(instruction.arg)

        # includes fall-through case from this block to the following block
        self._expr.stack = self.stack

        result = self._expr
        self._reset()
        return result

    def LOAD_ATTR(self, name_index):
        base = self.stack.pop()
        self.stack.append(AttributeAccess(base, self.codeobject.co_names[name_index]))

    def LOAD_CONST(self, const_index):
        self.stack.append(Constant(self.codeobject.co_consts[const_index]))

    def LOAD_FAST(self, var_num):
        self.stack.append(LocalRef(self.codeobject.co_varnames[var_num]))

    def LOAD_GLOBAL(self, name_index):
        self.stack.append(GlobalRef(self.codeobject.co_names[name_index]))

    def LOAD_DEREF(self, i):
        if i < len(self.codeobject.co_cellvars):
            name = self.codeobject.co_cellvars[i]
        else:
            name = self.codeobject.co_freevars[i - len(self.codeobject.co_cellvars)]
        self.stack.append(ClosureRef(name))

    def STORE_FAST(self, var_num):
        self.stack.pop()
        var_name = self.codeobject.co_varnames[var_num]
        if var_name not in self.variables:
            self.variables.append(var_name)

    def _pop_func_args(self, argc: int) -> List[Expression]:
        args = []
        for _ in range(argc):
            args.append(self.stack.pop())
        args.reverse()
        return args

    def CALL_FUNCTION(self, argc):
        args = self._pop_func_args(argc)
        func = self.stack.pop()
        self.stack.append(FunctionCall(func, args))

    def CALL_FUNCTION_KW(self, argc):
        # keyword arguments with keyword names supplied in a tuple
        const: Constant = self.stack.pop()
        if not isinstance(const.value, tuple):
            raise RuntimeError("keyword argument names must be supplied in a tuple")
        names: Tuple[str, ...] = const.value
        values = self._pop_func_args(len(names))
        kwargs = {name: value for name, value in zip(names, values)}

        # positional arguments in reverse order
        pargs = []
        for _ in range(argc - len(names)):
            pargs.append(self.stack.pop())
        pargs.reverse()

        func = self.stack.pop()
        self.stack.append(FunctionCall(func, pargs, kwargs))

    def _unary_op(self, cls):
        expr = self.stack.pop()
        self.stack.append(cls(expr))

    UNARY_POSITIVE = lambda self, _: self._unary_op(UnaryPlus)
    UNARY_NEGATIVE = lambda self, _: self._unary_op(UnaryMinus)
    UNARY_INVERT = lambda self, _: self._unary_op(BitwiseNot)
    UNARY_NOT = lambda self, _: self._unary_op(Negation)

    def _binary_op(self, cls):
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(cls(left, right))

    BINARY_POWER = lambda self, _: self._binary_op(Exponentiation)
    BINARY_MULTIPLY = lambda self, _: self._binary_op(Multiplication)
    BINARY_TRUE_DIVIDE = lambda self, _: self._binary_op(Division)
    BINARY_ADD = lambda self, _: self._binary_op(Addition)
    BINARY_SUBTRACT = lambda self, _: self._binary_op(Subtraction)
    BINARY_LSHIFT = lambda self, _: self._binary_op(BitwiseLeftShift)
    BINARY_RSHIFT = lambda self, _: self._binary_op(BitwiseRightShift)
    BINARY_AND = lambda self, _: self._binary_op(BitwiseAnd)
    BINARY_XOR = lambda self, _: self._binary_op(BitwiseXor)
    BINARY_OR = lambda self, _: self._binary_op(BitwiseOr)

    def _compare_op(self, op: str, invert: bool):
        right = self.stack.pop()
        left = self.stack.pop()
        comp = Comparison(op, left, right)
        if invert:
            self.stack.append(comp.negate())
        else:
            self.stack.append(comp)

    COMPARE_OP = lambda self, opname: self._compare_op(dis.cmp_op[opname], False)

    # new in version 3.9
    CONTAINS_OP = lambda self, invert: self._compare_op("in", invert)
    IS_OP = lambda self, invert: self._compare_op("is", invert)

    # new in version 3.10
    def GEN_START(self, kind):
        pass

    def GET_LEN(self, _):
        self.stack.append(FunctionCall(builtins.len, [self.stack[-1]]))

    def JUMP_ABSOLUTE(self, target):
        pass

    def JUMP_FORWARD(self, delta):
        pass

    def JUMP_IF_FALSE_OR_POP(self, target):
        if self._jump_cond:
            self._expr.jump_expr = self.stack[-1]
            self._expr.stack = self.stack
        else:
            self._expr.jump_expr = self.stack.pop()
            self._expr.stack = self.stack

    def JUMP_IF_TRUE_OR_POP(self, target):
        if self._jump_cond:
            self._expr.jump_expr = self.stack[-1]
            self._expr.stack = self.stack
        else:
            self._expr.jump_expr = self.stack.pop()
            self._expr.stack = self.stack

    def _pop_jump(self):
        self._expr.jump_expr = self.stack.pop()
        self._expr.stack = self.stack

    POP_JUMP_IF_FALSE = lambda self, target: self._pop_jump()
    POP_JUMP_IF_TRUE = lambda self, target: self._pop_jump()

    def DUP_TOP(self, _):
        self.stack.append(self.stack[-1])

    def DUP_TOP_TWO(self, _):
        item1 = self.stack[-1]
        item2 = self.stack[-2]
        self.stack.extend([item2, item1])

    def POP_TOP(self, _):
        self.stack.pop()

    def ROT_TWO(self, _):
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

    def ROT_THREE(self, _):
        self.stack[-1], self.stack[-2], self.stack[-3] = (
            self.stack[-2],
            self.stack[-3],
            self.stack[-1],
        )

    def ROT_FOUR(self, _):
        self.stack[-1], self.stack[-2], self.stack[-3], self.stack[-4] = (
            self.stack[-2],
            self.stack[-3],
            self.stack[-4],
            self.stack[-1],
        )

    def FOR_ITER(self, _):
        if self._jump_cond:
            self.stack.append(_IteratorValue())
        self._expr.stack = self.stack

    def _sequence_op(self, count, cls):
        values = []
        for _ in range(count):
            values.append(self.stack.pop())
        values.reverse()
        self.stack.append(cls(values))

    BUILD_TUPLE = lambda self, count: self._sequence_op(count, TupleExpression)
    BUILD_LIST = lambda self, count: self._sequence_op(count, ListExpression)

    def UNPACK_SEQUENCE(self, count):
        value = self.stack.pop()
        for index in range(count - 1, -1, -1):
            self.stack.append(IndexAccess(value, index))

    def RETURN_VALUE(self, _):
        self._expr.return_expr = self.stack.pop()

    def YIELD_VALUE(self, _):
        self._expr.yield_expr = self.stack.pop()
