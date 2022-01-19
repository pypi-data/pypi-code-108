# orm/evaluator.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

import operator

from .. import inspect
from .. import util
from ..sql import and_
from ..sql import operators


class UnevaluatableError(Exception):
    pass


class _NoObject(operators.ColumnOperators):
    def operate(self, *arg, **kw):
        return None

    def reverse_operate(self, *arg, **kw):
        return None


_NO_OBJECT = _NoObject()

_straight_ops = set(
    getattr(operators, op)
    for op in (
        "add",
        "mul",
        "sub",
        "div",
        "mod",
        "truediv",
        "lt",
        "le",
        "ne",
        "gt",
        "ge",
        "eq",
    )
)

_extended_ops = {
    operators.in_op: (lambda a, b: a in b if a is not _NO_OBJECT else None),
    operators.not_in_op: (
        lambda a, b: a not in b if a is not _NO_OBJECT else None
    ),
}

_notimplemented_ops = set(
    getattr(operators, op)
    for op in (
        "like_op",
        "not_like_op",
        "ilike_op",
        "not_ilike_op",
        "startswith_op",
        "between_op",
        "endswith_op",
        "concat_op",
    )
)


class EvaluatorCompiler(object):
    def __init__(self, target_cls=None):
        self.target_cls = target_cls

    def process(self, *clauses):
        if len(clauses) > 1:
            clause = and_(*clauses)
        elif clauses:
            clause = clauses[0]

        meth = getattr(self, "visit_%s" % clause.__visit_name__, None)
        if not meth:
            raise UnevaluatableError(
                "Cannot evaluate %s" % type(clause).__name__
            )
        return meth(clause)

    def visit_grouping(self, clause):
        return self.process(clause.element)

    def visit_null(self, clause):
        return lambda obj: None

    def visit_false(self, clause):
        return lambda obj: False

    def visit_true(self, clause):
        return lambda obj: True

    def visit_column(self, clause):
        if "parentmapper" in clause._annotations:
            parentmapper = clause._annotations["parentmapper"]
            if self.target_cls and not issubclass(
                self.target_cls, parentmapper.class_
            ):
                raise UnevaluatableError(
                    "Can't evaluate criteria against alternate class %s"
                    % parentmapper.class_
                )
            key = parentmapper._columntoproperty[clause].key
        else:
            key = clause.key
            if (
                self.target_cls
                and key in inspect(self.target_cls).column_attrs
            ):
                util.warn(
                    "Evaluating non-mapped column expression '%s' onto "
                    "ORM instances; this is a deprecated use case.  Please "
                    "make use of the actual mapped columns in ORM-evaluated "
                    "UPDATE / DELETE expressions." % clause
                )
            else:
                raise UnevaluatableError("Cannot evaluate column: %s" % clause)

        get_corresponding_attr = operator.attrgetter(key)
        return (
            lambda obj: get_corresponding_attr(obj)
            if obj is not None
            else _NO_OBJECT
        )

    def visit_tuple(self, clause):
        return self.visit_clauselist(clause)

    def visit_clauselist(self, clause):
        evaluators = list(map(self.process, clause.clauses))
        if clause.operator is operators.or_:

            def evaluate(obj):
                has_null = False
                for sub_evaluate in evaluators:
                    value = sub_evaluate(obj)
                    if value:
                        return True
                    has_null = has_null or value is None
                if has_null:
                    return None
                return False

        elif clause.operator is operators.and_:

            def evaluate(obj):
                for sub_evaluate in evaluators:
                    value = sub_evaluate(obj)
                    if not value:
                        if value is None or value is _NO_OBJECT:
                            return None
                        return False
                return True

        elif clause.operator is operators.comma_op:

            def evaluate(obj):
                values = []
                for sub_evaluate in evaluators:
                    value = sub_evaluate(obj)
                    if value is None or value is _NO_OBJECT:
                        return None
                    values.append(value)
                return tuple(values)

        else:
            raise UnevaluatableError(
                "Cannot evaluate clauselist with operator %s" % clause.operator
            )

        return evaluate

    def visit_binary(self, clause):
        eval_left, eval_right = list(
            map(self.process, [clause.left, clause.right])
        )
        operator = clause.operator
        if operator is operators.is_:

            def evaluate(obj):
                return eval_left(obj) == eval_right(obj)

        elif operator is operators.is_not:

            def evaluate(obj):
                return eval_left(obj) != eval_right(obj)

        elif operator in _extended_ops:

            def evaluate(obj):
                left_val = eval_left(obj)
                right_val = eval_right(obj)
                if left_val is None or right_val is None:
                    return None

                return _extended_ops[operator](left_val, right_val)

        elif operator in _straight_ops:

            def evaluate(obj):
                left_val = eval_left(obj)
                right_val = eval_right(obj)
                if left_val is None or right_val is None:
                    return None
                return operator(eval_left(obj), eval_right(obj))

        else:
            raise UnevaluatableError(
                "Cannot evaluate %s with operator %s"
                % (type(clause).__name__, clause.operator)
            )
        return evaluate

    def visit_unary(self, clause):
        eval_inner = self.process(clause.element)
        if clause.operator is operators.inv:

            def evaluate(obj):
                value = eval_inner(obj)
                if value is None:
                    return None
                return not value

            return evaluate
        raise UnevaluatableError(
            "Cannot evaluate %s with operator %s"
            % (type(clause).__name__, clause.operator)
        )

    def visit_bindparam(self, clause):
        if clause.callable:
            val = clause.callable()
        else:
            val = clause.value
        return lambda obj: val
