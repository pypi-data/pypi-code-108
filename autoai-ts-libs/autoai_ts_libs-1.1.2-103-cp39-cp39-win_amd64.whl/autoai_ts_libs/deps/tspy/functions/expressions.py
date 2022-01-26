"""
main entry point for all time-series expressions (fast lambdas)
"""


#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

def id(key=None):
    return None, key

def logical_not(exp):
        
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()  
    return getattr(tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions, 'not')(exp)

def logical_and(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return getattr(tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions, 'and')(
        left_exp,
        right_exp
    )

def logical_or(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return getattr(tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions, 'or')(
        left_exp,
        right_exp
    )

def lt(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.lessThan(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def lte(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.lessThanOrEqual(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def gt(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.greaterThan(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def gte(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.greaterThanOrEqual(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def divisible_by(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.divisibleBy(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def contains(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.contains(
        _wrap_string_expression(left_exp),
        _wrap_string_expression(right_exp)
    )

def starts_with(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.startsWith(
        _wrap_string_expression(left_exp),
        _wrap_string_expression(right_exp)
    )

def ends_with(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.endsWith(
        _wrap_string_expression(left_exp),
        _wrap_string_expression(right_exp)
    )

def matches(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.matches(
        _wrap_string_expression(left_exp),
        _wrap_string_expression(right_exp)
    )

def eq(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.BooleanExpressions.equals(
        _wrap_object_expression(left_exp),
        _wrap_object_expression(right_exp)
    )

def add(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.add(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def sub(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.subtract(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def div(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.divide(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def mul(left_exp, right_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.multiply(
        _wrap_double_expression(left_exp),
        _wrap_double_expression(right_exp)
    )

def abs(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.abs(
        _wrap_double_expression(exp)
    )

def exp(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.exp(
        _wrap_double_expression(exp)
    )

def log(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.log(
        _wrap_double_expression(exp)
    )

def log10(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.log10(
        _wrap_double_expression(exp)
    )

def sqrt(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.sqrt(
        _wrap_double_expression(exp)
    )

def sin(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.sin(
        _wrap_double_expression(exp)
    )

def cos(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.cos(
        _wrap_double_expression(exp)
    )

def tan(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.tan(
        _wrap_double_expression(exp)
    )

def asin(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.asin(
        _wrap_double_expression(exp)
    )

def acos(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.acos(
        _wrap_double_expression(exp)
    )

def atan(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.atan(
        _wrap_double_expression(exp)
    )

def sinh(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.sinh(
        _wrap_double_expression(exp)
    )

def cosh(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.cosh(
        _wrap_double_expression(exp)
    )

def tanh(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.tanh(
        _wrap_double_expression(exp)
    )

def min(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.min(
        _wrap_object_expression(exp)
    )

def max(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.max(
        _wrap_object_expression(exp)
    )

def count(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.count(
        _wrap_object_expression(exp)
    )

def sum(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.sum(
        _wrap_object_expression(exp)
    )

def avg(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.avg(
        _wrap_object_expression(exp)
    )

def stdev(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.standardDeviation(
        _wrap_object_expression(exp)
    )

def var(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.variance(
        _wrap_object_expression(exp)
    )

def concat(exp_list):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    from py4j.java_collections import ListConverter
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.concat(
        ListConverter().convert([_wrap_string_expression(exp) for exp in exp_list], tsc._gateway._gateway_client)
    )

def if_then_else(if_exp, then_exp, else_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.ifThenElse(
        if_exp,
        _wrap_object_expression(then_exp),
        _wrap_object_expression(else_exp)
    )

def if_then(if_exp, then_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.ifThen(
        if_exp,
        _wrap_object_expression(then_exp)
    )

def match_case(if_then_exp_list, otherwise_exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    from py4j.java_collections import ListConverter
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.matchCase(
        ListConverter().convert(if_then_exp_list, tsc._gateway._gateway_client),
        _wrap_object_expression(otherwise_exp)
    )

def with_attr(attr_name, exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.RecordExpressions.withAttribute(
        attr_name,
        _wrap_record_expression(exp)
    )

def _wrap_object_expression(exp):
    import numbers
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    if isinstance(exp, tuple) and exp[0] is None:
        if exp[1] is None:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.id()
        elif isinstance(exp[1], int):
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.idIndex(exp[1])
        else:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.idAttr(exp[1])
    elif isinstance(exp, numbers.Number):
        return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.constant(exp)
    elif isinstance(exp, str):
        return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.constant(exp)
    else:
        return exp

def _wrap_record_expression(exp):
    import numbers
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    if isinstance(exp, tuple) and exp[0] is None:
        if exp[1] is None:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.RecordExpressions.id()
        else:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.idAttr(exp[1])
    elif isinstance(exp, numbers.Number):
        return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.constant(exp)
    elif isinstance(exp, str):
        return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.constant(exp)
    else:
        return exp

def _wrap_double_expression(exp):
    import numbers
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    if isinstance(exp, tuple) and exp[0] is None:
        if exp[1] is None:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.id()
        elif isinstance(exp[1], int):
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.idIndex(exp[1])
        else:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.idAttr(exp[1])
    elif isinstance(exp, numbers.Number):
        return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.NumberExpressions.constant(exp)
    else:
        return exp

def _wrap_string_expression(exp):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    if isinstance(exp, tuple) and exp[0] is None:
        if exp[1] is None:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.id()
        elif isinstance(exp[1], int):
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.idIndex(exp[1])
        else:
            return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.idAttr(exp[1])
    elif isinstance(exp, str):
        return tsc._jvm.com.ibm.research.time_series.transforms.utils.python.StringExpressions.constant(exp)
    else:
        return exp
