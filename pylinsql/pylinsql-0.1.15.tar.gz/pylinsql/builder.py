"""
Constructs a PostgreSQL DML/DQL statement from an abstract syntax tree expression.

This module is used internally.
"""

from __future__ import annotations

import builtins
import dataclasses
import enum
import functools
from dataclasses import MISSING, dataclass
from datetime import date, time
from typing import Any, Dict, List, Optional, Set, Tuple

from .ast import *
from .base import DataClass, is_dataclass_instance
from .core import *

_aggregate_functions = Dispatcher([avg, count, max, min, sum])
_conditional_aggregate_functions = Dispatcher(
    [avg_if, count_if, max_if, min_if, sum_if]
)
_datetime_functions = Dispatcher([year, month, day, hour, minute, second])
_matching_functions = Dispatcher([like, ilike, matches, imatches])
_join_functions = Dispatcher([full_join, inner_join, left_join, right_join])
_order_functions = Dispatcher([asc, desc])


@enum.unique
class _JoinType(enum.Enum):
    InnerJoin = inner_join.__name__
    LeftJoin = left_join.__name__
    RightJoin = right_join.__name__
    FullJoin = full_join.__name__


@dataclass
class _EntityJoin:
    join_type: _JoinType
    left_entity: str
    left_attr: str
    right_entity: str
    right_attr: str

    def swap(self) -> _EntityJoin:
        if self.join_type is _JoinType.LeftJoin:
            swap_type = _JoinType.RightJoin
        elif self.join_type is _JoinType.RightJoin:
            swap_type = _JoinType.LeftJoin
        else:
            swap_type = self.join_type
        return _EntityJoin(
            swap_type,
            self.right_entity,
            self.right_attr,
            self.left_entity,
            self.left_attr,
        )

    def as_join(self, entity_aliases):
        if self.join_type is _JoinType.InnerJoin:
            join_type = "INNER"
        elif self.join_type is _JoinType.LeftJoin:
            join_type = "LEFT"
        elif self.join_type is _JoinType.RightJoin:
            join_type = "RIGHT"
        elif self.join_type is _JoinType.FullJoin:
            join_type = "FULL"
        return f"{join_type} JOIN {entity_aliases[self.right_entity]} ON {self.left_entity}.{self.left_attr} = {self.right_entity}.{self.right_attr}"


class _EntityJoinCollection:
    entity_joins: Dict[Tuple[str, str], _EntityJoin]

    def __init__(self):
        self.entity_joins = {}

    def __str__(self) -> str:
        return "\n".join(str(e) for e in self.entity_joins.values())

    def __bool__(self) -> bool:
        return len(self.entity_joins) > 0

    def add(
        self,
        join_type: _JoinType,
        left_entity: str,
        left_attr: str,
        right_entity: str,
        right_attr: str,
    ):
        min_entity = builtins.min(left_entity, right_entity)
        max_entity = builtins.max(left_entity, right_entity)
        self.entity_joins[(min_entity, max_entity)] = _EntityJoin(
            join_type, left_entity, left_attr, right_entity, right_attr
        )

    def pop(self, left_entity: str, right_entity: str) -> Optional[_EntityJoin]:
        min_entity = builtins.min(left_entity, right_entity)
        max_entity = builtins.max(left_entity, right_entity)
        entity_join = self.entity_joins.pop((min_entity, max_entity), None)
        if entity_join:
            if left_entity != entity_join.left_entity:
                return entity_join.swap()
            else:
                return entity_join
        else:
            return None


@enum.unique
class _OrderType(enum.Enum):
    Ascending = asc.__name__
    Descending = desc.__name__


def _list_to_conj_expr(parts: List[Expression]) -> Union[Conjunction, Expression, None]:
    if len(parts) > 1:
        return Conjunction(parts)
    elif len(parts) == 1:
        return parts[0]
    else:
        return None


class _JoinExtractor:
    """
    Extracts the join part from a Python generator expression to be used in a SQL FROM clause.
    """

    entity_joins: _EntityJoinCollection

    def __init__(self):
        self.entity_joins = _EntityJoinCollection()

    @functools.singledispatchmethod
    def visit(self, arg: Expression) -> Expression:
        return arg

    @visit.register
    def _(self, conj: Conjunction) -> Union[Conjunction, Expression, None]:
        parts = []
        for expr in conj.exprs:
            part = self.visit(expr)
            if part:
                parts.append(part)

        return _list_to_conj_expr(parts)

    @visit.register
    def _(self, call: FunctionCall) -> Optional[FunctionCall]:
        sig = _join_functions.get(call)
        if sig:
            return self._join_expr(_JoinType(sig.name), sig["left"], sig["right"])

        return call

    def _join_expr(
        self, join_type: _JoinType, left: Expression, right: Expression
    ) -> None:
        if not (
            isinstance(left, AttributeAccess)
            and isinstance(right, AttributeAccess)
            and isinstance(left.base, LocalRef)
            and isinstance(right.base, LocalRef)
        ):
            raise QueryTypeError(
                "join expressions must adhere to the format: join(entity1.attr1, entity2.attr2)"
            )

        self.entity_joins.add(
            join_type,
            left.base.name,
            left.attr_name,
            right.base.name,
            right.attr_name,
        )


@enum.unique
class _ConditionContext(enum.Enum):
    UNDECIDED = ""
    WHERE = "WHERE"
    HAVING = "HAVING"


class _ConditionContextClassifier:
    _local_vars: List[str]
    _context: _ConditionContext = _ConditionContext.UNDECIDED
    _inside_aggregation: bool = False

    def __init__(self, local_vars: List[str]):
        self._local_vars = local_vars

    def visit(self, arg: Expression) -> _ConditionContext:
        self._context = _ConditionContext.UNDECIDED
        self._inside_aggregation = False
        self._visit(arg)
        return self._context

    @functools.singledispatchmethod
    def _visit(self, _: Expression) -> None:
        pass

    @_visit.register
    def _(self, bool_expr: BooleanExpression) -> None:
        for expr in bool_expr.exprs:
            self._visit(expr)

    @_visit.register
    def _(self, unary_expr: UnaryExpression) -> None:
        self._visit(unary_expr.expr)

    @_visit.register
    def _(self, binary_expr: BinaryExpression) -> None:
        self._visit(binary_expr.left)
        self._visit(binary_expr.right)

    @_visit.register
    def _(self, comp: Comparison) -> None:
        self._visit(comp.left)
        self._visit(comp.right)

    @_visit.register
    def _(self, call: FunctionCall) -> None:
        sig = _aggregate_functions.get(call)
        if sig:
            return self._visit_aggregation_func(sig, call)

        sig = _conditional_aggregate_functions.get(call)
        if sig:
            return self._visit_aggregation_func(sig, call)

        sig = _join_functions.get(call)
        if sig:
            raise QueryTypeError(
                f"join function {sig.name} can only be used at the top-level in the conditional part (following 'if') of the Python generator expression"
            )

        sig = _order_functions.get(call)
        if sig:
            raise QueryTypeError(
                f"order function {sig.name} can only be used as a top-level wrapper in the target expression part (preceding 'for') of the Python generator expression"
            )

        # process regular functions
        self._visit(call.base)
        for arg in call.pargs:
            self._visit(arg)
        for _, arg in call.kwargs.items():
            self._visit(arg)

    def _visit_aggregation_func(self, sig: BoundSignature, call: FunctionCall) -> None:
        if self._context is _ConditionContext.UNDECIDED:
            self._context = _ConditionContext.HAVING

        if self._context is _ConditionContext.HAVING:
            if self._inside_aggregation:
                raise QueryTypeError(
                    f"cannot nest aggregation function {sig.name} inside another"
                )

            self._visit(call.base)
            self._inside_aggregation = True
            for arg in call.pargs:
                self._visit(arg)
            for _, arg in call.kwargs.items():
                self._visit(arg)
            self._inside_aggregation = False

        elif self._context is _ConditionContext.WHERE:
            raise QueryTypeError(
                f"cannot use aggregation function {sig.name} in a non-aggregation context"
            )

    @_visit.register
    def _(self, attr: AttributeAccess) -> None:
        self._visit(attr.base)

    @_visit.register
    def _(self, arg: LocalRef) -> None:
        if arg.name not in self._local_vars:
            return

        if self._context is _ConditionContext.UNDECIDED:
            self._context = _ConditionContext.WHERE

        if self._context is _ConditionContext.HAVING and not self._inside_aggregation:
            raise QueryTypeError(
                f"cannot reference local variable {arg.name} outside of an aggregation function when in an aggregation context"
            )

    @_visit.register
    def _(self, arg: Constant) -> Constant:
        return arg


class _ConditionExtractor:
    _classifier: _ConditionContextClassifier
    _where: List[Expression]
    _having: List[Expression]

    """
    Extracts the conditional part from a Python generator expression to be used in a SQL WHERE or HAVING clause.

    This class takes the abstract syntax tree of a Python generator expression such as
    ```
    ( p for p in entity(Person) if p.given_name == "John" and min(p.birth_date) >= datetime.date(1989, 10, 23) )
    ```
    and extracts `p.given_name == ...`, which goes into the WHERE clause, and `min(p.birth_date) >= ...`, which goes
    into the HAVING clause.

    :param vars: Variables in the abstract syntax tree that correspond to entities.
    """

    def __init__(self, local_vars: List[str]):
        self._classifier = _ConditionContextClassifier(local_vars)
        self._where = []
        self._having = []

    def where(self) -> Union[Conjunction, Expression, None]:
        return _list_to_conj_expr(self._where)

    def having(self) -> Union[Conjunction, Expression, None]:
        return _list_to_conj_expr(self._having)

    @functools.singledispatchmethod
    def visit(self, arg: Expression) -> None:
        self._visit(arg)

    @visit.register
    def _(self, conj: Conjunction) -> None:
        for expr in conj.exprs:
            self._visit(expr)

    def _visit(self, expr: Expression) -> None:
        context = self._classifier.visit(expr)
        if context is _ConditionContext.HAVING:
            self._having.append(expr)
        else:
            self._where.append(expr)


_query_parameters = [p_1, p_2, p_3, p_4, p_5, p_6, p_7, p_8, p_9]


class _QueryVisitor:
    parameters: Set[_QueryParameter]
    stack: List[Expression]

    def __init__(self, closure_vars: Dict[str, Any]):
        self.closure_vars = closure_vars
        self.parameters = set()
        self.stack = [TopLevelExpression()]

    def visit(self, arg: Expression) -> str:
        self.stack.append(arg)
        expr = self._visit(arg)
        self.stack.pop()

        if arg.precedence < self.stack[-1].precedence:
            return f"({expr})"
        else:
            return expr

    @functools.singledispatchmethod
    def _visit(self, arg):
        raise NotImplementedError(
            f"unrecognized expression: {arg} (of type {type(arg)})"
        )

    def _sql_where_expr(self, adjoiner: str, exprs: List[Expression]) -> str:
        return f" {adjoiner} ".join(self.visit(expr) for expr in exprs)

    def _sql_unary_expr(self, op: str, unary_expr: UnaryExpression) -> str:
        expr = self.visit(unary_expr.expr)
        return f"{op}{expr}"

    def _sql_binary_expr(self, op: str, binary_expr: BinaryExpression) -> str:
        left = self.visit(binary_expr.left)
        right = self.visit(binary_expr.right)
        return f"{left} {op} {right}"

    @_visit.register
    def _(self, conj: Conjunction) -> str:
        return self._sql_where_expr("AND", conj.exprs)

    @_visit.register
    def _(self, disj: Disjunction) -> str:
        return self._sql_where_expr("OR", disj.exprs)

    @_visit.register
    def _(self, branch: IfThenElse) -> str:
        condition = self.visit(branch.condition)
        on_true = self.visit(branch.on_true)
        on_false = self.visit(branch.on_false)
        return f"CASE WHEN {condition} THEN {on_true} ELSE {on_false} END"

    @_visit.register
    def _(self, neg: Negation) -> str:
        return self._sql_unary_expr("NOT ", neg)

    @_visit.register
    def _(self, expr: UnaryPlus) -> str:
        return self._sql_unary_expr("+", expr)

    @_visit.register
    def _(self, expr: UnaryMinus) -> str:
        return self._sql_unary_expr("-", expr)

    @_visit.register
    def _(self, expr: Exponentiation) -> str:
        return self._sql_binary_expr("^", expr)

    @_visit.register
    def _(self, expr: Multiplication) -> str:
        return self._sql_binary_expr("*", expr)

    @_visit.register
    def _(self, expr: Division) -> str:
        return self._sql_binary_expr("/", expr)

    @_visit.register
    def _(self, expr: Addition) -> str:
        return self._sql_binary_expr("+", expr)

    @_visit.register
    def _(self, expr: Subtraction) -> str:
        return self._sql_binary_expr("-", expr)

    @_visit.register
    def _(self, expr: BitwiseNot) -> str:
        return self._sql_unary_expr("~", expr)

    @_visit.register
    def _(self, expr: BitwiseAnd) -> str:
        return self._sql_binary_expr("&", expr)

    @_visit.register
    def _(self, expr: BitwiseXor) -> str:
        return self._sql_binary_expr("#", expr)

    @_visit.register
    def _(self, expr: BitwiseOr) -> str:
        return self._sql_binary_expr("|", expr)

    @_visit.register
    def _(self, comp: Comparison) -> str:
        if isinstance(comp.right, Constant) and comp.right.value is None:
            left = self.visit(comp.left)
            if comp.op == "is":
                return f"{left} IS NULL"
            elif comp.op == "is not":
                return f"{left} IS NOT NULL"
        elif comp.op in ["in", "not in"]:
            left = self.visit(comp.left)
            right = self.visit(comp.right)
            if comp.op == "in":
                return f"{left} IN {right}"
            elif comp.op == "not in":
                return f"{left} NOT IN {right}"
        else:
            left = self.visit(comp.left)
            right = self.visit(comp.right)
            binary_ops = {
                "==": "=",
                "!=": "<>",
                "<": "<",
                "<=": "<=",
                ">=": ">=",
                ">": ">",
            }
            if comp.op in binary_ops:
                op = binary_ops[comp.op]
                return f"{left} {op} {right}"

        raise TypeError(f"illegal comparison: {comp}")

    def _sql_func_args(self, sig: BoundSignature) -> Dict[str, Any]:
        "SQL arguments for a function call."

        sql_args: Dict[str, Any] = {}

        # iterate over function parameters in definition order
        for parameter in sig.args.signature.parameters.values():
            if parameter.kind in [
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.VAR_KEYWORD,
            ]:
                raise TypeError(
                    "keyword-only and variable arguments are not supported in SQL"
                )

            sql_arg = self.visit(sig.args.arguments[parameter.name])
            sql_args[parameter.name] = sql_arg

        return sql_args

    def _sql_func_call(self, sig: BoundSignature, name: str = None) -> str:
        "SQL expression for a function call."

        if name is None:
            name = sig.name
        sql_arglist = ", ".join(self._sql_func_args(sig).values())
        return f"{name}({sql_arglist})"

    @_visit.register
    def _(self, call: FunctionCall) -> str:
        sig = _aggregate_functions.get(call)
        if sig:
            return self._sql_func_call(sig, name=sig.name.upper())

        sig = _conditional_aggregate_functions.get(call)
        if sig:
            self.stack.append(TopLevelExpression())
            sql_args = self._sql_func_args(sig)
            self.stack.pop()
            func = sig.name.replace("_if", "").upper()
            expr = sql_args["expression"]
            cond = sql_args["condition"]
            return f"{func}({expr}) FILTER (WHERE {cond})"

        sig = _datetime_functions.get(call)
        if sig:
            sql_args = self._sql_func_args(sig)
            func = sig.name.upper()
            dt = sql_args["dt"]
            return f"EXTRACT({func} FROM {dt})"

        if call.is_dispatchable(now):
            return "CURRENT_TIMESTAMP"

        sig = _matching_functions.get(call)
        if sig:
            sql_args = self._sql_func_args(sig)

            if sig.name == like.__name__:
                op = "LIKE"
            elif sig.name == ilike.__name__:
                op = "ILIKE"
            elif sig.name == matches.__name__:
                op = "~"
            elif sig.name == imatches.__name__:
                op = "~*"

            text = sql_args["text"]
            pattern = sql_args["pattern"]
            return f"{text} {op} {pattern}"

        # special treatment for built-in functions
        fn_name = call.get_function_name()
        if fn_name == date.__name__:
            args = ", ".join([self.visit(arg) for arg in call.pargs])
            return f"MAKE_DATE({args})"

        if fn_name == time.__name__:
            args = ", ".join([self.visit(arg) for arg in call.pargs])
            return f"MAKE_TIME({args})"

        raise TypeError(f"unrecognized function call: {call}")

    @_visit.register
    def _(self, arg: AttributeAccess) -> str:
        base = self.visit(arg.base)
        return f"{base}.{arg.attr_name}"

    @_visit.register
    def _(self, arg: ClosureRef) -> str:
        value = self.closure_vars[arg.name]
        if isinstance(value, Query):
            return f"({value.sql})"
        raise TypeError(f"unexpected reference to closure variable: {arg.name}")

    @_visit.register
    def _(self, arg: GlobalRef) -> str:
        for param in _query_parameters:
            if arg.name == param.name:
                self.parameters.add(param)
                return param
        return arg.name

    @_visit.register
    def _(self, arg: LocalRef) -> str:
        return arg.name

    @_visit.register
    def _(self, arg: TupleExpression) -> str:
        self.stack.append(TopLevelExpression())
        value = ", ".join(self.visit(expr) for expr in arg.exprs)
        self.stack.pop()
        return value

    @_visit.register
    def _(self, arg: Constant) -> str:
        if isinstance(arg.value, str):
            return _to_sql_string(arg.value)
        else:
            return str(arg.value)


def _to_sql_string(s: str) -> str:
    "Converts a Python string object into a string that can be directly embedded in a SQL string."

    escaped_string = s.replace("'", "''")
    return f"'{escaped_string}'"


@dataclass
class Context:
    local_vars: List[str]
    closure_vars: Dict[str, Any]
    global_vars: Dict[str, Any]


class _SelectExtractor:
    _query_visitor: _QueryVisitor

    return_type: Type = None
    local_vars: List[str]
    select: List[str]
    group_by: List[str]
    order_by: List[str]
    has_aggregate: bool = False

    def __init__(
        self,
        query_visitor: _QueryVisitor,
        local_vars: List[str],
        global_vars: Dict[str, Any],
    ):
        self._query_visitor = query_visitor
        self.local_vars = local_vars
        self.global_vars = global_vars
        self.select = []
        self.group_by = []
        self.order_by = []

    def visit(self, expr: Expression) -> None:
        self._visit(expr)

    def _visit_expr(self, expr: Expression) -> str:
        item = self._query_visitor.visit(expr)
        if self._is_aggregate(expr):
            self.has_aggregate = True
        else:
            self.group_by.append(item)
        self.select.append(item)
        return item

    @functools.singledispatchmethod
    def _visit(self, expr: Expression) -> None:
        self._visit_expr(expr)

    @_visit.register
    def _(self, call: FunctionCall) -> None:
        sig = _order_functions.get(call)
        if sig:
            item = self._visit_expr(call.pargs[0])
            order = _OrderType(sig.name).value.upper()
            self.order_by.append(f"{item} {order}")
            return

        # outermost wrapper to construct return type
        fn_name = call.get_function_name()
        typ = self.global_vars.get(fn_name, None)
        if is_dataclass_type(typ):
            self.return_type = typ

            # put positional arguments in SELECT in the same order they appear in generator expression
            for expr in call.pargs:
                self._visit(expr)

            # reorder keyword arguments to match the order defined in the data class
            for f in dataclasses.fields(typ)[len(call.pargs) :]:
                expr = call.kwargs.get(f.name, MISSING)
                if expr is MISSING:
                    self.select.append("NULL")
                else:
                    self._visit(expr)

            return

        self._visit_expr(call)

    @_visit.register
    def _(self, ref: LocalRef) -> None:
        self.select.append("*")

    @_visit.register
    def _(self, tup: TupleExpression) -> None:
        self.return_type = tuple
        for expr in tup.exprs:
            self._visit(expr)

    def _is_aggregate(self, expr: Expression) -> bool:
        "True if an expression in a SELECT clause is an aggregation expression."

        context = _ConditionContextClassifier(self.local_vars).visit(expr)
        return context is _ConditionContext.HAVING


@dataclass
class QueryBuilderArgs:
    source: EntityProxy
    context: Context
    cond_expr: Expression
    yield_expr: Expression


class QueryBuilder:
    def select(self, qba: QueryBuilderArgs) -> str:
        query_visitor = _QueryVisitor(qba.context.closure_vars)

        # extract JOIN clause from "if" part of generator expression
        join_simplifier = _JoinExtractor()
        cond_expr = join_simplifier.visit(qba.cond_expr)
        entity_joins = join_simplifier.entity_joins

        # construct JOIN expression "a JOIN b ON a.foreign_key = b.primary_key JOIN ..."
        entity_aliases = {
            var: f'"{typ.__name__}" AS {var}'
            for typ, var in zip(qba.source.types, qba.context.local_vars)
        }
        remaining_entities = qba.context.local_vars.copy()
        sql_join = []
        while remaining_entities:
            first = remaining_entities.pop(0)
            joined_entities = set([first])
            sql_join_group = [entity_aliases[first]]

            while True:
                entity_join = self._match_entities(
                    entity_joins, joined_entities, remaining_entities
                )
                if not entity_join:
                    break

                joined_entities.add(entity_join.right_entity)
                remaining_entities.remove(entity_join.right_entity)

                sql_join_group.append(entity_join.as_join(entity_aliases))

            sql_join.append(" ".join(sql_join_group))

        # split compound conditional expression into parts
        condition_visitor = _ConditionExtractor(qba.context.local_vars)
        condition_visitor.visit(cond_expr)

        # construct WHERE expression
        where_expr = condition_visitor.where()
        sql_where = query_visitor.visit(where_expr) if where_expr else None

        # construct HAVING expression
        having_expr = condition_visitor.having()
        sql_having = query_visitor.visit(having_expr) if having_expr else None

        # construct SELECT expression
        select_visitor = _SelectExtractor(
            query_visitor, qba.context.local_vars, qba.context.global_vars
        )
        select_visitor.visit(qba.yield_expr)
        sql_group = select_visitor.group_by if select_visitor.has_aggregate else None
        sql_select = select_visitor.select
        sql_order = select_visitor.order_by

        sql_parts = ["SELECT"]
        sql_parts.append(", ".join(sql_select))
        if sql_join:
            sql_parts.extend(["FROM", ", ".join(sql_join)])
        if sql_where:
            sql_parts.extend(["WHERE", sql_where])
        if sql_group:
            sql_parts.extend(["GROUP BY", ", ".join(sql_group)])
        if sql_having:
            sql_parts.extend(["HAVING", sql_having])
        if sql_order:
            sql_parts.extend(["ORDER BY", ", ".join(sql_order)])

        sql = " ".join(sql_parts)
        typ = select_visitor.return_type
        return Query(typ, sql)

    def insert_or_select(
        self, qba: QueryBuilderArgs, insert_obj: DataClass[T]
    ) -> Query:
        if not is_dataclass_instance(insert_obj):
            raise TypeError(f"{insert_obj} must be a dataclass instance")

        query_visitor = _QueryVisitor(qba.context.closure_vars)

        # check JOIN clause in "if" part of generator expression
        join_simplifier = _JoinExtractor()
        cond_expr = join_simplifier.visit(qba.cond_expr)
        if join_simplifier.entity_joins:
            raise QueryTypeError(
                "no join conditions are allowed in an insert or select query"
            )

        # construct FROM expression
        if len(qba.source.types) != 1:
            raise QueryTypeError(
                "a single target entity is required for an insert or select query"
            )
        entity_type = qba.source.types[0]
        entity_var = qba.context.local_vars[0]
        if not isinstance(insert_obj, entity_type):
            raise QueryTypeError(
                f"object to insert has wrong type: {type(insert_obj)}, expected: {entity_type}"
            )
        sql_from = f'"{entity_type.__name__}" AS {entity_var}'

        # split compound conditional expression into parts
        condition_visitor = _ConditionExtractor(qba.context.local_vars)
        condition_visitor.visit(cond_expr)

        # construct WHERE expression
        where_expr = condition_visitor.where()
        sql_where = query_visitor.visit(where_expr) if where_expr else None

        # check HAVING expression
        if condition_visitor.having() is not None:
            raise QueryTypeError(
                "no aggregation functions are allowed in an insert or select query"
            )

        # construct SELECT expression
        select_visitor = _SelectExtractor(
            query_visitor, qba.context.local_vars, qba.context.global_vars
        )
        select_visitor.visit(qba.yield_expr)
        if select_visitor.has_aggregate:
            raise QueryTypeError(
                "no aggregation functions are allowed in an insert or select query"
            )

        sql_select = select_visitor.select
        sql_order = select_visitor.order_by

        sql_select_column_names = ", ".join(sql_select)
        select_parts = ["SELECT", sql_select_column_names, "FROM", sql_from]
        if sql_where:
            select_parts.extend(["WHERE", sql_where])
        if sql_order:
            select_parts.extend(["ORDER BY", ", ".join(sql_order)])
        select_query = " ".join(select_parts)

        if query_visitor.parameters:
            offset = builtins.max(param.index for param in query_visitor.parameters) + 1
        else:
            offset = 1

        fields = dataclasses.fields(insert_obj)
        insert_names = [
            field.name
            for field in fields
            if getattr(insert_obj, field.name) is not DEFAULT
        ]
        sql_insert_names = ", ".join(insert_names)
        sql_insert_placeholders = ", ".join(
            f"${index + offset}" for index in range(len(insert_names))
        )
        insert_query = f"INSERT INTO {sql_from} ({sql_insert_names}) SELECT {sql_insert_placeholders} WHERE NOT EXISTS (SELECT * FROM select_query) RETURNING {sql_select_column_names}"

        sql = f"WITH select_query AS ({select_query}), insert_query AS ({insert_query}) SELECT * FROM select_query UNION ALL SELECT * FROM insert_query"
        typ = select_visitor.return_type
        return Query(typ, sql)

    def _match_entities(
        self, entity_joins, joined_entities: List[str], remaining_entities: List[str]
    ) -> Optional[_EntityJoin]:
        """
        Pairs up entities with one another along a join expression.

        :joined_entities: Entities already joined by previous INNER, LEFT and RIGHT joins.
        :remaining_entities: Entities to be paired up with previously joined entities.
        :returns: A new pair not already in the joined entities set (or None).
        """

        for left in joined_entities:
            for right in remaining_entities:
                entity_join = entity_joins.pop(left, right)
                if entity_join:
                    return entity_join
        return None
