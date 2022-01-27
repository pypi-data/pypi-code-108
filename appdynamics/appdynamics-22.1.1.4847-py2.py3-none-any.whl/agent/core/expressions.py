# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import operator
import re

from appdynamics.lang import filter
from appdynamics.agent.core.conditions import match
from appdynamics.agent.core.logs import setup_logger
from appdynamics.agent.core import pb


logger = setup_logger('appdynamics.agent')

ENTITY_COLLECTORS = {
    # pb.EntityCollector.INVOKED_OBJECT; ,
    # pb.EntityCollector.RETURN_VALUE: ,
    # pb.EntityCollector.PARAMETER: ,
    pb.EntityCollector.IDENTIFYING_PROPERTY: lambda node, ctx: ctx[node.propertyName],
}


class ExpressionNodeEvaluationError(Exception):
    pass


def evaluate_entityValue(node, ctx):
    """Evaluate an EntityCollector.

    """
    entityValue = node.entityValue
    entity_collector = ENTITY_COLLECTORS.get(entityValue.type)
    if entity_collector:
        return entity_collector(entityValue, ctx)
    else:
        raise ExpressionNodeEvaluationError(
            'Cannot evaluate EntityCollector with entityValue type: %d' % entityValue.type)


def evaluate_comparisonOp(node, ctx, operator):
    """Return the result of the comparison operator on the input operands.

    """
    comparisonOp = node.comparisonOp
    lhs = _evaluate(comparisonOp.lhs, ctx)
    rhs = _evaluate(comparisonOp.rhs, ctx)
    return operator(lhs, rhs)


def evaluate_andOp(node, ctx):
    """Return the `and` of the input operands.

    """
    return all(_evaluate(operand, ctx) for operand in node.andOp.operands)


def evaluate_orOp(node, ctx):
    """Return the `or` of the input operands.

    """
    return any(_evaluate(operand, ctx) for operand in node.orOp.operands)


def evaluate_notOp(node, ctx):
    """Return the `not` of the input operand.

    """
    return not _evaluate(node.notOp.operand, ctx)


def evaluate_stringMatchOp(node, ctx):
    """Return True if the input matches the condition, otherwise False.

    """
    stringMatchOp = node.stringMatchOp
    return match(_evaluate(stringMatchOp.input, ctx), stringMatchOp.condition)


def evaluate_mergeOp(node, ctx):
    """Return a string containing the merged inputs.

    """
    mergeOp = node.mergeOp
    return mergeOp.delimiter.join(_evaluate(mergeOp.inputArray, ctx))


def evaluate_splitOp(node, ctx):
    """Return a list of segments of the input.

    """
    splitOp = node.splitOp
    split = _evaluate(splitOp.input, ctx).split(splitOp.delimiter)
    segments = splitOp.segments
    if segments.type == pb.Segments.FIRST:
        return split[:segments.numSegments]
    elif segments.type == pb.Segments.LAST:
        return split[-segments.numSegments:]
    elif segments.type == pb.Segments.SELECTED:
        result = []
        for segment in segments.selectedSegments:
            # Indexing is 1-based...
            result.append(split[segment - 1])
        return result


def evaluate_regexCaptureOp(node, ctx):
    """Return a list of matched regex groups.

    If no match groups are defined, return a list containing the full match.

    """
    regexCaptureOp = node.regexCaptureOp
    match = re.search(regexCaptureOp.regex, _evaluate(regexCaptureOp.input, ctx))

    if not match:
        return []

    # If no regexGroups are defined, return the full match.
    if not regexCaptureOp.regexGroups:
        return [match.group()]

    # Return all matched regexGroups.
    return list(filter(lambda x: x is not None, (match.group(i) for i in regexCaptureOp.regexGroups)))


# def evaluate_getterOp(node, ctx):
#     """Return the specified attribute from the input.

#     """
#     getterOp = node.getterOp
#     return getattr(_evaluate(getterOp.base, ctx), getterOp.field)


# def evaluate_selectOneOp(node, ctx):
#     """Return a single element of the input.

#     """
#     selectOneOp = node.selectOneOp
#     return _evaluate(selectOneOp.input, ctx)[selectOneOp.index]


# def evaluate_selectManyOp(node, ctx):
#     """Return a list of elements of the input.

#     """
#     selectManyOp = node.selectManyOp
#     result = []
#     input_array = _evaluate(selectManyOp.input, ctx)
#     for i in selectManyOp.indices:
#         result.append(input_array[i])
#     return result


OPERATORS = {
    pb.ExpressionNode.EQUALS: lambda node, ctx: evaluate_comparisonOp(node, ctx, operator.eq),
    pb.ExpressionNode.NOT_EQUALS: lambda node, ctx: evaluate_comparisonOp(node, ctx, operator.ne),
    pb.ExpressionNode.LT: lambda node, ctx: evaluate_comparisonOp(node, ctx, operator.lt),
    pb.ExpressionNode.GT: lambda node, ctx: evaluate_comparisonOp(node, ctx, operator.gt),
    pb.ExpressionNode.LE: lambda node, ctx: evaluate_comparisonOp(node, ctx, operator.le),
    pb.ExpressionNode.GE: lambda node, ctx: evaluate_comparisonOp(node, ctx, operator.ge),
    pb.ExpressionNode.NOT: evaluate_notOp,
    pb.ExpressionNode.AND: evaluate_andOp,
    pb.ExpressionNode.OR: evaluate_orOp,
    pb.ExpressionNode.STRINGMATCH: evaluate_stringMatchOp,
    pb.ExpressionNode.MERGE: evaluate_mergeOp,
    pb.ExpressionNode.SPLIT: evaluate_splitOp,
    pb.ExpressionNode.REGEXCAPTURE: evaluate_regexCaptureOp,
    pb.ExpressionNode.ENTITY: evaluate_entityValue,
    pb.ExpressionNode.STRING: lambda node, ctx: node.stringValue,
    pb.ExpressionNode.INTEGER: lambda node, ctx: node.integerValue,
    # pb.ExpressionNode.BOOLEAN: lambda node, ctx: node.booleanValue,
    # pb.ExpressionNode.FLOAT: lambda node, ctx: node.floatValue,
    # pb.ExpressionNode.GETTER: evaluate_getterOp,
    # pb.ExpressionNode.SELECTONE: evaluate_selectOneOp,
    # pb.ExpressionNode.SELECTMANY: evaluate_selectManyOp,
}


def _evaluate(node, ctx):
    # This is a convenience function which does not catch exceptions, so any
    # failed operation in recursive calls to this function will bubble up to
    # `evaluate` and stop the evaluation immediately.
    operator = OPERATORS.get(node.type)
    if operator:
        return operator(node, ctx)
    else:
        raise ExpressionNodeEvaluationError('Cannot evaluate ExpreesionNode with operator type: %d' % node.type)


def evaluate(node, ctx=None):
    """Evaluate an ExpressionNode.

    """
    try:
        return _evaluate(node, ctx)
    except:
        logger.exception('ExpressionNode evaluation failed.')
    return None
