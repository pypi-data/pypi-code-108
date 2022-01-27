import hashlib
import sys
import base64

from rox.core.roxx.token_type import TokenType, TokenTypes
from rox.core.utils.time_utils import now_in_unix_milliseconds
from rox.core.utils.type_utils import is_string


def is_undefined(parser, stack, context):
    op1 = stack.pop()
    if not isinstance(op1, TokenType):
        stack.push(False)
    else:
        stack.push(op1 == TokenTypes.UNDEFINED)


def now(parser, stack, context):
    stack.push(now_in_unix_milliseconds())


def and_(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if op1 == TokenTypes.UNDEFINED:
        op1 = False
    if op2 == TokenTypes.UNDEFINED:
        op2 = False
    if not isinstance(op1, bool) or not isinstance(op2, bool):
        raise ValueError
    stack.push(op1 and op2)


def or_(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if op1 == TokenTypes.UNDEFINED:
        op1 = False
    if op2 == TokenTypes.UNDEFINED:
        op2 = False
    if not isinstance(op1, bool) or not isinstance(op2, bool):
        raise ValueError
    stack.push(op1 or op2)


def ne(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if op1 == TokenTypes.UNDEFINED:
        op1 = False
    if op2 == TokenTypes.UNDEFINED:
        op2 = False
    stack.push(op1 != op2)


def eq(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if op1 == TokenTypes.UNDEFINED:
        op1 = False
    if op2 == TokenTypes.UNDEFINED:
        op2 = False
    stack.push(op1 == op2)


def not_(parser, stack, context):
    op1 = stack.pop()
    if op1 == TokenTypes.UNDEFINED:
        op1 = False
    if not isinstance(op1, bool):
        raise ValueError
    stack.push(not op1)


def if_then(parser, stack, context):
    condition_expression = stack.pop()
    true_expression = stack.pop()
    false_expression = stack.pop()
    if not isinstance(condition_expression, bool):
        raise ValueError
    stack.push(true_expression if condition_expression else false_expression)


def in_array(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not isinstance(op2, list):
        stack.push(False)
    else:
        stack.push(op1 in op2)


def md5(parser, stack, context):
    op1 = stack.pop()
    if not is_string(op1):
        stack.push(TokenTypes.UNDEFINED)
        return

    m = hashlib.md5()
    m.update(op1.encode('utf-8'))
    stack.push(m.hexdigest())


def concat(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(TokenTypes.UNDEFINED)
        return

    stack.push('%s%s' % (op1, op2))

def b64d(parser, stack, context):
    op1 = stack.pop()
    if not is_string(op1):
        stack.push(TokenTypes.UNDEFINED)
        return

    if sys.version_info >= (3, 0):
        stack.push(base64.b64decode(op1).decode('utf-8'))
    else:
        stack.push(base64.b64decode(op1))

