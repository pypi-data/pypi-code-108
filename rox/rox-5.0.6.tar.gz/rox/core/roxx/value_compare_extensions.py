import numbers
from distutils.version import LooseVersion

from rox.core.utils.type_utils import is_string
from rox.core.utils.numeric_utils import (is_numeric, convert_to_float)


class ValueCompareExtensions:
    def __init__(self, parser):
        self.parser = parser

    def extend(self):
        self.parser.add_operator('lt', lt)
        self.parser.add_operator('lte', lte)
        self.parser.add_operator('gt', gt)
        self.parser.add_operator('gte', gte)
        self.parser.add_operator('numeq', numeq)
        self.parser.add_operator('numne', numne)
        self.parser.add_operator('semverNe', semver_ne)
        self.parser.add_operator('semverEq', semver_eq)
        self.parser.add_operator('semverLt', semver_lt)
        self.parser.add_operator('semverLte', semver_lte)
        self.parser.add_operator('semverGt', semver_gt)
        self.parser.add_operator('semverGte', semver_gte)


def lt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_numeric(op1) or not is_numeric(op2):
        stack.push(False)
    else:
        stack.push(convert_to_float(op1) < convert_to_float(op2))


def lte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_numeric(op1) or not is_numeric(op2):
        stack.push(False)
    else:
        stack.push(convert_to_float(op1) <= convert_to_float(op2))


def gt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_numeric(op1) or not is_numeric(op2):
        stack.push(False)
    else:
        stack.push(convert_to_float(op1) > convert_to_float(op2))


def gte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_numeric(op1) or not is_numeric(op2):
        stack.push(False)
    else:
        stack.push(convert_to_float(op1) >= convert_to_float(op2))

def numeq(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_numeric(op1) or not is_numeric(op2):
        stack.push(False)
    else:
        stack.push(convert_to_float(op1) == convert_to_float(op2))

def numne(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_numeric(op1) or not is_numeric(op2):
        stack.push(False)
    else:
        stack.push(convert_to_float(op1) != convert_to_float(op2))

def semver_ne(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) != LooseVersion(op2))


def semver_eq(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) == LooseVersion(op2))


def semver_lt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) < LooseVersion(op2))


def semver_lte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) <= LooseVersion(op2))


def semver_gt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) > LooseVersion(op2))


def semver_gte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) >= LooseVersion(op2))
