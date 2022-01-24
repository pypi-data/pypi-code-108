from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type, Union

from antlr4.ParserRuleContext import ParserRuleContext
from triad.utils.assertion import assert_or_throw

from _qpd_antlr import QPDParser as qp
from _qpd_antlr import QPDVisitor
from qpd.dataframe import Column, DataFrame, DataFrames
from qpd._parser.utils import (
    ColumnMention,
    ColumnMentions,
    Join,
    VisitorContext,
    is_agg,
    normalize_join_type,
)
from qpd.specs import (
    AggFunctionSpec,
    ArgumentSpec,
    OrderBySpec,
    OrderItemSpec,
    WindowFrameSpec,
    WindowFunctionSpec,
    WindowSpec,
    make_windowframe_spec,
    IsValueSpec,
)
from qpd.workflow import WorkflowDataFrame


class VisitorBase(QPDVisitor, VisitorContext):
    def __init__(self, context: VisitorContext, *args: Any, **kwargs: Any):
        VisitorContext.__init__(self, context, *args, **kwargs)

    def copy(self, tp: Type, *args: Any, **kwargs: Any) -> "VisitorBase":
        return tp(self, *args, **kwargs)

    def not_support(
        self, msg: Union[str, ParserRuleContext]
    ) -> None:  # pragma: no cover
        if isinstance(msg, ParserRuleContext):
            raise NotImplementedError(self.to_str(msg))
        raise NotImplementedError(msg)

    def assert_none(self, *nodes: Any) -> None:  # pragma: no cover
        for node in nodes:
            if isinstance(node, list):
                if len(node) > 0:
                    self.not_support(f"{node} is not empty")
            elif node is not None:
                expr = self.to_str(node)
                self.not_support(f"{expr}")

    def assert_support(
        self, cond, msg: Union[str, ParserRuleContext]
    ) -> None:  # pragma: no cover
        if not cond:
            self.not_support(msg)

    def visitCtes(self, ctx: qp.CtesContext) -> None:
        return

    def visitFunctionName(self, ctx: qp.FunctionNameContext) -> str:
        self.assert_support(ctx.qualifiedName() is not None, ctx)
        return self.to_str(ctx.qualifiedName()).lower()


class PreScan(VisitorBase):
    def __init__(self, context: VisitorContext, *args: Any, **kwargs: Any):
        VisitorContext.__init__(self, context, *args, **kwargs)
        self._in_agg = False
        self._in_window = False
        self._non_agg_mentions = ColumnMentions()
        self._agg_funcs: List[ParserRuleContext] = []
        self._group_by_expressions: List[ParserRuleContext] = []
        self._window_funcs: List[ParserRuleContext] = []
        self._having_expressions: List[ParserRuleContext] = []
        self._not_in_agg_star: Any = None
        self._func_args: List[Tuple[ParserRuleContext, bool, bool]] = []

    def visitStar(self, ctx: qp.StarContext) -> None:
        if self.to_str(ctx) == "*":
            self.set("select_all", True)
        else:
            self.add_column_mentions(ctx)
        if not self._in_agg:
            self._not_in_agg_star = ctx

    def visitColumnReference(self, ctx: qp.ColumnReferenceContext) -> None:
        m = self.add_column_mentions(ctx)
        if not self._in_agg:
            self._non_agg_mentions.add(m)

    def visitDereference(self, ctx: qp.DereferenceContext) -> None:
        m = self.add_column_mentions(ctx)
        if not self._in_agg:
            self._non_agg_mentions.add(m)

    def visitAliasedQuery(self, ctx: qp.QueryContext) -> None:
        return

    def visitFirst(self, ctx: qp.FirstContext) -> None:
        self._handle_func_call("first", ctx)

    def visitLast(self, ctx: qp.LastContext) -> None:
        self._handle_func_call("last", ctx)

    def visitFunctionCall(self, ctx: qp.FunctionCallContext) -> None:
        func = self.visit(ctx.functionName())
        if ctx.windowSpec() is None:
            self._handle_func_call(func, ctx)
        else:
            self.set("has_window_func", True)
            self.assert_support(not self._in_agg and not self._in_window, ctx)
            self._window_funcs.append(ctx)
            self._in_window = True
            self.visitChildren(ctx)
            self._in_window = False
        for a in ctx.argument:
            is_col, is_single = PreFunctionArgument(self).visit_argument(a)
            self._func_args.append((a, is_col, is_single))

    def visitPredicate(self, ctx: qp.PredicateContext):
        self.visitChildren(ctx)
        if ctx.expression() is not None:
            for a in ctx.expression():
                is_col, is_single = PreFunctionArgument(self).visit_argument(a)
                self._func_args.append((a, is_col, is_single))

    def visitWindowRef(self, ctx: qp.WindowRefContext) -> None:  # pragma: no cover
        self.not_support(ctx)

    def visitWindowDef(self, ctx: qp.WindowDefContext) -> None:
        self.set("has_window", True)
        super().visitWindowDef(ctx)

    def visitAggregationClause(self, ctx: qp.AggregationClauseContext):
        for e in ctx.expression():
            self._in_agg = True
            self._group_by_expressions.append(e)
            self.visit(e)
            self._in_agg = False

    def visitRegularQuerySpecification(
        self, ctx: qp.RegularQuerySpecificationContext
    ) -> None:
        self.assert_none(
            ctx.lateralView(),
            ctx.windowClause(),
        )
        if ctx.fromClause() is not None:
            self.copy(PreFrom).visit(ctx.fromClause())
        self.visit(ctx.selectClause())
        if ctx.whereClause() is not None:
            self.visit(ctx.whereClause())
        if ctx.aggregationClause() is not None:
            self.visit(ctx.aggregationClause())
        if ctx.havingClause() is not None:
            self.visit(ctx.havingClause())

        # assert not the case: SELECT *, SUM(x) FROM a
        self.assert_support(
            not self.get("has_agg_func", False) or self._not_in_agg_star is None,
            self._not_in_agg_star,
        )

        # assert not the case: SELECT SUM(x), ROW_NUMBER() OVER() FROM a
        self.assert_support(
            not (
                (self.get("has_agg_func", False) or ctx.aggregationClause() is not None)
                and self.get("has_window_func", False)
            ),
            "can't have both aggregation and window",
        )

        if len(self.joins) > 0:
            # get join details
            joined: Set[str] = set([self.joins[0].df_name])
            for i in range(1, len(self.joins)):
                j = self.joins[i]
                right = j.df_name
                v = self.copy(JoinCriteria)
                v._joined, v._right_name = joined, right
                if j.criteria_context is not None:
                    j.set_conditions(v.visit(j.criteria_context))
                else:
                    j.set_conditions([])
                joined.add(right)

        # handle agg
        self.set("non_agg_mentions", self._non_agg_mentions)
        self.set("agg_funcs", self._agg_funcs)
        self.set("group_by_expressions", self._group_by_expressions)
        self.set("window_funcs", self._window_funcs)
        self.set("func_arg_types", {id(x[0]): (x[1], x[2]) for x in self._func_args})

    def _handle_func_call(self, func: str, ctx: Any) -> None:
        if is_agg(func):
            self.set("has_agg_func", True)
            self.assert_support(not self._in_agg and not self._in_window, ctx)
            self._agg_funcs.append(ctx)
            self._in_agg = True
        self.visitChildren(ctx)
        self._in_agg = False


class RelationVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitTableAlias(self, ctx: qp.TableAliasContext) -> str:
        self.assert_none(ctx.identifierList())
        return self.to_str(ctx.strictIdentifier(), "")

    def visitTableName(self, ctx: qp.TableNameContext) -> Tuple[DataFrame, str]:
        self.assert_none(ctx.sample())
        df_name = self.to_str(ctx.multipartIdentifier(), "")
        assert_or_throw(
            df_name in self.dfs,
            KeyError(f"{df_name} is not found in {list(self.dfs.keys())}"),
        )
        alias = self.visitTableAlias(ctx.tableAlias())
        if alias == "":
            alias = df_name
        return self.dfs[df_name], alias

    def visitAliasedQuery(
        self, ctx: qp.AliasedQueryContext
    ) -> Tuple[DataFrame, str]:  # pragma: no cover
        if ctx.tableAlias().strictIdentifier() is not None:
            name = self.to_str(ctx.tableAlias().strictIdentifier(), "")
        else:
            name = self._obj_to_col_name(self.to_str(ctx.query()))
        v = StatementVisitor(
            VisitorContext(
                sql=self.sql, workflow=self.workflow, dfs=DataFrames(self.dfs)
            )
        )
        df = v.visitQuery(ctx.query())
        return df, name

    def visitAliasedRelation(
        self, ctx: qp.AliasedRelationContext
    ) -> Tuple[DataFrame, str]:
        self.assert_none(ctx.sample())
        df, a = self.copy(RelationVisitor).visit(ctx.relation())
        alias = self.visitTableAlias(ctx.tableAlias())
        return df, alias if alias != "" else a

    def visitRelation(self, ctx: qp.RelationContext) -> Tuple[DataFrame, str]:
        self.assert_none(ctx.joinRelation())
        res = self.visit(ctx.relationPrimary())
        if res is None:  # pragma: no cover
            self.not_support(f"{self.to_str(ctx.relationPrimary())} is not supported")
        return res


class PreFrom(RelationVisitor):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitFromClause(self, ctx: qp.FromClauseContext) -> None:
        rel = ctx.relation()
        self.assert_support(len(rel) == 1, ctx)
        self.assert_none(ctx.lateralView(), ctx.pivotClause())
        self.visit(rel[0])
        self.set("dfs", DataFrames({x.df_name: x.df for x in self.joins}))

    def visitRelation(self, ctx: qp.RelationContext) -> None:  # type: ignore
        joins = ctx.joinRelation()
        df, name = self.copy(RelationVisitor).visit(ctx.relationPrimary())
        self.add_join_relation(Join(name, df))
        for j in joins:
            self.visit(j)

    def visitJoinRelation(self, ctx: qp.JoinRelationContext) -> None:
        join_type = normalize_join_type(self.to_str(ctx.joinType()))
        natural = ctx.NATURAL() is not None
        df, name = self.copy(RelationVisitor).visit(ctx.right)
        self.add_join_relation(
            Join(
                name,
                df,
                join_type=join_type,
                natural=natural,
                criteria_context=ctx.joinCriteria(),
            )
        )


class ColumnMentionVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)
        self._mentions = ColumnMentions()

    def get_mentions(self, ctx: Any) -> ColumnMentions:
        self._mentions = ColumnMentions()
        if ctx is not None:
            self.visit(ctx)
        return self._mentions

    def visitStar(self, ctx: qp.StarContext) -> None:  # pragma: no cover
        self.not_support(ctx)
        # self._mentions.add(self.add_column_mentions(ctx))

    def visitColumnReference(self, ctx: qp.ColumnReferenceContext) -> None:
        self._mentions.add(self.add_column_mentions(ctx))

    def visitDereference(self, ctx: qp.DereferenceContext) -> None:
        self._mentions.add(self.add_column_mentions(ctx))


class JoinCriteria(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitJoinCriteria(
        self, ctx: qp.JoinCriteriaContext
    ) -> List[List[qp.ValueExpressionContext]]:
        self.assert_none(ctx.identifierList())
        res = self.visit(ctx.booleanExpression())
        self.assert_support(res is not None, ctx)
        return list(res)

    def visitPredicated(
        self, ctx: qp.PredicatedContext
    ) -> Iterable[List[qp.ValueExpressionContext]]:
        self.assert_none(ctx.predicate())
        res = self.visit(ctx.valueExpression())
        self.assert_support(res is not None, ctx)
        return res

    def visitLogicalBinary(
        self, ctx: qp.LogicalBinaryContext
    ) -> Iterable[List[qp.ValueExpressionContext]]:
        self.assert_support(ctx.AND() is not None, ctx)
        for x in self.visit(ctx.left):
            yield x
        for y in self.visit(ctx.right):
            yield y

    def visitComparison(
        self, ctx: qp.ComparisonContext
    ) -> Iterable[List[qp.ValueExpressionContext]]:
        self.assert_support(ctx.comparisonOperator().EQ() is not None, ctx)
        v = self.copy(ColumnMentionVisitor)
        left = v.get_mentions(ctx.left)
        left_ctx = ctx.left
        v = self.copy(ColumnMentionVisitor)
        right = v.get_mentions(ctx.right)
        right_ctx = ctx.right
        yield self._fit(left, left_ctx, right, right_ctx)  # type: ignore

    def _fit(
        self,
        left_mentions: ColumnMentions,
        left_ctx: qp.ValueExpressionContext,
        right_mentions: ColumnMentions,
        right_ctx: qp.ValueExpressionContext,
    ) -> List[qp.ValueExpressionContext]:
        left_set = set(x.df_name for x in left_mentions)
        right_set = set(x.df_name for x in right_mentions)
        joined_set = self._joined
        current_set = set([self._right_name])
        if left_set == current_set and right_set.issubset(joined_set):
            return [right_ctx, left_ctx]
        if right_set == current_set and left_set.issubset(joined_set):
            return [left_ctx, right_ctx]
        raise NotImplementedError(self.to_str(left_ctx), self.to_str(right_ctx))


class PreFunctionArgument(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)
        self._has_star = False
        self._has_func = False
        self._cols = 0
        self._constants = 0

    def visitStar(self, ctx: qp.StarContext) -> None:
        self._cols += 1
        self._has_star = True

    def visitColumnReference(self, ctx: qp.ColumnReferenceContext) -> None:
        self._cols += 1

    def visitDereference(self, ctx: qp.DereferenceContext) -> None:
        self._cols += 1

    def visitConstantDefault(self, ctx: qp.ConstantDefaultContext) -> None:
        self._constants += 1

    def visitFunctionCall(self, ctx: qp.FunctionCallContext) -> None:
        self._has_func = True
        super().visitFunctionCall(ctx)

    def visitLogicalNot(self, ctx: qp.LogicalNotContext) -> None:
        self._has_func = True
        super().visitLogicalNot(ctx)

    def visit_argument(self, ctx: Any) -> Tuple[bool, bool]:
        self._has_star = False
        self._has_func = False
        self._cols = 0
        self._constants = 0
        self.visit(ctx)
        is_col = self._cols > 0
        self.assert_support(is_col or self._constants > 0, ctx)  # neither
        if is_col:
            is_single = (
                self._cols == 1
                and not self._has_star
                and not self._has_func
                and self._constants == 0
            )
        else:
            is_single = self._constants == 1 and not self._has_func
        return is_col, is_single


# ----------------------------------------- Visitors for execution --------------------


class StatementVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitRegularQuerySpecification(
        self, ctx: qp.RegularQuerySpecificationContext
    ) -> DataFrame:
        self.copy(PreScan).visit(ctx)
        self.copy(FromVisitor).visit(ctx)
        if ctx.whereClause() is not None:
            self.copy(WhereVisitor).visit(ctx.whereClause())
        if ctx.aggregationClause() is not None or self.get("has_agg_func", False):
            self.copy(AggregationVisitor).visit(ctx)
        elif self.get("has_window_func", False):
            self.copy(WindowVisitor).visit(ctx)
        if ctx.havingClause() is not None:
            self.copy(WhereVisitor).visit(ctx.havingClause())
        self.copy(SelectVisitor).visit(ctx.selectClause())
        return self.current

    def visitSetOperation(self, ctx: qp.SetOperationContext) -> DataFrame:
        op = self.to_str(ctx.operator).lower()
        self.assert_support(op in ["union", "intersect", "except"], op)
        if op == "except":
            op = "except_df"
        unique = (
            ctx.setQuantifier() is None or ctx.setQuantifier().DISTINCT() is not None
        )
        v = StatementVisitor(
            VisitorContext(
                sql=self.sql, workflow=self.workflow, dfs=DataFrames(self.dfs)
            )
        )
        left = v.visit(ctx.left)
        v = StatementVisitor(
            VisitorContext(
                sql=self.sql, workflow=self.workflow, dfs=DataFrames(self.dfs)
            )
        )
        right = v.visit(ctx.right)
        return self.workflow.op_to_df(list(left.keys()), op, left, right, unique=unique)

    def visitQuery(self, ctx: qp.QueryContext) -> DataFrame:
        if ctx.ctes() is not None:
            self.visit(ctx.ctes())
        df = self.visit(ctx.queryTerm())
        return OrganizationVisitor(self).organize(df, ctx.queryOrganization())

    def visitSingleStatement(self, ctx: qp.SingleStatementContext):
        return self.visit(ctx.statement())

    def visitCtes(self, ctx: qp.CtesContext) -> None:
        for c in ctx.namedQuery():
            name, df = self.visitNamedQuery(c)
            self.set("dfs", DataFrames(self.dfs, {name: df}))

    def visitNamedQuery(self, ctx: qp.NamedQueryContext) -> Tuple[str, DataFrame]:
        self.assert_none(ctx.identifierList())
        name = self.to_str(ctx.name, "")
        v = StatementVisitor(
            VisitorContext(
                sql=self.sql, workflow=self.workflow, dfs=DataFrames(self.dfs)
            )
        )
        df = v.visit(ctx.query())
        return name, df


class OrganizationVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitSortItem(self, ctx: qp.SortItemContext) -> OrderItemSpec:
        name = self.to_str(ctx.expression())
        asc = ctx.DESC() is None
        if ctx.FIRST() is None and ctx.LAST() is None:
            na_position = "auto"
        else:
            na_position = "first" if ctx.FIRST() is not None else "last"
        return OrderItemSpec(name, asc, na_position)

    def visitQueryOrganization(
        self, ctx: qp.QueryOrganizationContext
    ) -> Tuple[OrderBySpec, int]:
        self.assert_none(ctx.clusterBy, ctx.distributeBy, ctx.sort, ctx.windowClause())
        if ctx.order is not None:
            items = [self.visitSortItem(x) for x in ctx.order]
            order_by = OrderBySpec(*items)
        else:
            order_by = OrderBySpec()
        if ctx.limit is not None:
            is_col, _ = PreFunctionArgument(self).visit_argument(ctx.limit)
            self.assert_support(not is_col, ctx)
            limit = int(eval(self.to_str(ctx.limit)))
            self.assert_support(limit >= 0, ctx)
        else:
            limit = -1
        return order_by, limit

    def organize(
        self, df: DataFrame, ctx: Optional[qp.QueryOrganizationContext]
    ) -> DataFrame:
        if ctx is None:
            return df
        order_by, limit = self.visitQueryOrganization(ctx)
        if len(order_by) == 0 and limit < 0:
            return df
        return self.workflow.op_to_df(
            list(df.keys()), "order_by_limit", df, order_by, limit
        )


class ExpressionVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitStar(self, ctx: qp.StarContext) -> List[Column]:
        return self._get_columns(ctx)

    def visitColumnReference(self, ctx: qp.ColumnReferenceContext) -> List[Column]:
        return self._get_columns(ctx)

    def visitDereference(self, ctx: qp.DereferenceContext) -> List[Column]:
        return self._get_columns(ctx)

    def visitConstantDefault(self, ctx: qp.ConstantDefaultContext) -> List[Column]:
        raw = self.to_str(ctx, "")
        if raw.lower() == "true":
            value = True
        elif raw.lower() == "false":
            value = False
        else:
            value = eval(raw)
        return [self.workflow.const_to_col(value)]

    def visitParenthesizedExpression(
        self, ctx: qp.ParenthesizedExpressionContext
    ) -> List[Column]:
        return self.visit(ctx.expression())

    def visitArithmeticUnary(  # type: ignore
        self, ctx: qp.ArithmeticUnaryContext
    ) -> List[Column]:
        op = self.to_str(ctx.operator)
        v = self._get_single_column(ctx.valueExpression())
        return [self.workflow.op_to_col("basic_unary_arithmetic_op", v, op)]

    def visitArithmeticBinary(  # type: ignore
        self, ctx: qp.ArithmeticBinaryContext
    ) -> List[Column]:
        op = self.to_str(ctx.operator)
        left, right = self._get_single_left_right(ctx)
        return [self.workflow.op_to_col("binary_arithmetic_op", left, right, op)]

    def visitLogicalNot(self, ctx: qp.LogicalNotContext) -> List[Column]:
        col = self._get_single_column(ctx.booleanExpression())
        return [self.workflow.op_to_col("logical_not", col)]

    def visitPredicated(self, ctx: qp.PredicatedContext) -> List[Column]:
        if ctx.predicate() is None:
            return self.visit(ctx.valueExpression())
        col = self._get_single_column(ctx.valueExpression())
        kind = self.to_str(ctx.predicate().kind).lower()
        positive = ctx.predicate().NOT() is None
        if kind in ["null", "true", "false"]:
            vs = IsValueSpec(kind, positive)
            return [self.workflow.op_to_col("is_value", col, vs)]
        if kind == "in":
            self.assert_support(len(ctx.predicate().expression()) > 0, ctx)
            in_cols: List[Column] = []
            in_values: List[Any] = []
            for e in ctx.predicate().expression():
                is_col, _ = self.get("func_arg_types")[id(e)]
                if not is_col:
                    in_values.append(eval(self.to_str(e)))
                else:
                    in_cols.append(self._get_single_column(e))
            return [
                self.workflow.op_to_col(
                    "is_in", col, *in_cols, *in_values, positive=positive
                )
            ]
        if kind == "between":
            lower = self._get_single_column((ctx.predicate().lower))
            upper = self._get_single_column((ctx.predicate().upper))
            return [
                self.workflow.op_to_col(
                    "is_between", col, lower, upper, positive=positive
                )
            ]
        return self.not_support(ctx)  # type: ignore  # pragma: no cover

    def visitComparison(self, ctx: qp.ComparisonContext) -> List[Column]:
        def to_op(o: qp.ComparisonOperatorContext):
            if o.EQ():
                return "=="
            if o.NEQ() or o.NEQJ():
                return "!="
            if o.LT():
                return "<"
            if o.LTE():
                return "<="
            if o.GT():
                return ">"
            if o.GTE():
                return ">="
            self.not_support("comparator " + self.to_str(o))  # pragma: no cover

        op = to_op(ctx.comparisonOperator())
        left, right = self._get_single_left_right(ctx)
        return [self.workflow.op_to_col("comparison_op", left, right, op)]

    def visitLogicalBinary(self, ctx: qp.LogicalBinaryContext) -> List[Column]:
        op = self.to_str(ctx.operator).lower()
        left, right = self._get_single_left_right(ctx)
        return [self.workflow.op_to_col("binary_logical_op", left, right, op)]

    def visitFirst(self, ctx: qp.FirstContext) -> List[Column]:
        return [self.current[self.get("agg_func_to_col")[id(ctx)]]]

    def visitLast(self, ctx: qp.LastContext) -> List[Column]:
        return [self.current[self.get("agg_func_to_col")[id(ctx)]]]

    def visitFunctionCall(  # type: ignore
        self, ctx: qp.FunctionCallContext
    ) -> List[Column]:
        # this part should be simplified: expresion_to_col
        if ctx.windowSpec() is not None:
            return [self.current[self.get("window_func_to_col")[id(ctx)]]]
        func = self.visit(ctx.functionName())
        if is_agg(func):
            return [self.current[self.get("agg_func_to_col")[id(ctx)]]]
        self.not_support(ctx)  # pragma: no cover

    def visitSearchedCase(self, ctx: qp.SearchedCaseContext) -> List[Column]:
        cols: List[Column] = []
        for when in ctx.whenClause():
            cols += self.visitWhenClause(when)
        cols.append(self._get_single_column(ctx.elseExpression))
        return [self.workflow.op_to_col("case_when", *cols)]

    def visitWhenClause(self, ctx: qp.WhenClauseContext) -> Tuple[Column, Column]:
        return (
            self._get_single_column(ctx.condition),
            self._get_single_column(ctx.result),
        )

    def _get_single_left_right(self, ctx: Any) -> List[Column]:
        left = self._get_single_column(ctx.left)
        right = self._get_single_column(ctx.right)
        return [left, right]

    def _get_single_column(self, ctx: Any) -> Column:
        c = list(self.visit(ctx))
        self.assert_support(len(c) == 1, ctx)
        return c[0]

    def _get_columns(self, ctx: Any) -> List[Column]:
        cols = self.get_column_mentions(ctx)
        return [self.current[c.encoded] for c in cols]


class FromVisitor(ExpressionVisitor):
    def __init__(self, context: VisitorContext):
        super().__init__(context)
        self._encoded_map: Dict[str, str] = {}

    def visitRegularQuerySpecification(
        self, ctx: qp.RegularQuerySpecificationContext
    ) -> None:
        if len(self.joins) == 0:
            self.update_current(None)  # type: ignore
            self.set("encoded_map", self._encoded_map)
            return
        joined = self._extract_df(self.joins[0].df_name)
        for join in self.joins[1:]:
            name = join.df_name
            df = self._extract_df(name)
            left, right = joined, df
            left_cols: List[Column] = []
            right_cols: List[Column] = []
            joined_cols = list(joined.keys())
            if "semi" not in join.join_type and "anti" not in join.join_type:
                joined_cols += list(df.keys())
            on: List[str] = []
            if len(join.conditions) > 0:
                for i in range(len(join.conditions)):
                    join_col_name = f"_{i}_"
                    left_cols.append(
                        self._join_col(join.conditions[i][0], joined).rename(
                            join_col_name
                        )
                    )
                    right_cols.append(
                        self._join_col(join.conditions[i][1], df).rename(join_col_name)
                    )
                    on.append(f"_{i}_")
                left = WorkflowDataFrame(joined, *left_cols)
                right = WorkflowDataFrame(df, *right_cols)
            joined = self.workflow.op_to_df(
                joined_cols, "join", left, right, on=on, join_type=join.join_type
            )
        self.update_current(joined)
        self.set("encoded_map", self._encoded_map)

    def _join_col(self, ctx: Any, df: WorkflowDataFrame) -> Column:
        self.update_current(df)
        return self._get_single_column(ctx)

    def _extract_df(self, name: str) -> WorkflowDataFrame:
        cols: List[Column] = []
        if self.get("select_all", False):
            df = self.dfs[name]
            for k in df.keys():
                cm = ColumnMention(name, k)
                cols.append(df[k].rename(cm.encoded))
                self._encoded_map[cm.encoded] = k
        else:
            for m in self.all_column_mentions:
                if m.df_name == name:
                    cols.append(self.dfs[name][m.col_name].rename(m.encoded))
                    self._encoded_map[m.encoded] = m.col_name
        return WorkflowDataFrame(*cols)


class WhereVisitor(ExpressionVisitor):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitWhereClause(self, ctx: qp.WhereClauseContext) -> None:
        self._filter(ctx)

    def visitHavingClause(self, ctx: qp.HavingClauseContext):
        self._filter(ctx)

    def _filter(self, ctx: Any):
        cond = self._get_single_column(ctx.booleanExpression())
        current = self.workflow.op_to_df(
            list(self.current.keys()), "filter_df", self.current, cond
        )
        self.update_current(current)


class AggregationVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)
        self._internal_exprs: Dict[str, Column] = {}
        self._gp_map: Dict[str, Tuple[str, AggFunctionSpec]] = {}
        self._gp_keys: List[str] = []
        self._f_to_name: Dict[int, str] = {}

    def visitFirst(  # type: ignore
        self, ctx: qp.FirstContext
    ) -> Tuple[AggFunctionSpec, List[Any]]:
        args = [ctx.expression()]
        dropna = ctx.IGNORE() is not None
        func = AggFunctionSpec("first", unique=False, dropna=dropna)
        return func, args

    def visitLast(  # type: ignore
        self, ctx: qp.LastContext
    ) -> Tuple[AggFunctionSpec, List[Any]]:
        args = [ctx.expression()]
        dropna = ctx.IGNORE() is not None
        func = AggFunctionSpec("last", unique=False, dropna=dropna)
        return func, args

    def visitFunctionCall(  # type: ignore
        self, ctx: qp.FunctionCallContext
    ) -> Tuple[AggFunctionSpec, List[Any]]:
        func_name = self.visitFunctionName(ctx.functionName())
        args = ctx.argument
        unique = (
            ctx.setQuantifier() is not None
            and ctx.setQuantifier().DISTINCT() is not None
        )
        func = AggFunctionSpec(
            func_name,
            unique=unique,
            dropna=func_name not in ["first", "last", "first_value", "last_value"],
        )
        return func, args

    def visitRegularQuerySpecification(
        self, ctx: qp.RegularQuerySpecificationContext
    ) -> None:
        self._handle_mentions()
        self._handle_agg_funcs()
        self._handle_group_by()
        if len(self._internal_exprs) > 0:
            self.update_current(
                WorkflowDataFrame(self.current, *list(self._internal_exprs.values()))
            )
        self.update_current(
            self.workflow.op_to_df(
                list(self._gp_map.keys()),
                "group_agg",
                self.current,
                self._gp_keys,
                self._gp_map,
            )
        )
        self.set("agg_func_to_col", self._f_to_name)

    def _handle_mentions(self) -> None:
        for m in self.get("non_agg_mentions"):
            func = AggFunctionSpec("first", unique=False, dropna=False)
            self._gp_map[m.encoded] = (m.encoded, func)

    def _handle_agg_funcs(self) -> None:
        for f_ctx in self.get("agg_funcs", None):
            func, args = self.visit(f_ctx)
            name = self._obj_to_col_name(self.expr(f_ctx))
            if func.name != "count":
                self.assert_support(len(args) == 1, f_ctx)
                internal_expr = self._get_func_args(args)
            else:
                if len(args) == 0:
                    expr = "*"
                else:
                    expr = self.expr(args[0])
                if expr == "*":
                    self.assert_support(len(args) <= 1, f_ctx)
                    internal_expr = ["*"]
                    func = AggFunctionSpec(func.name, func.unique, dropna=False)
                else:
                    internal_expr = self._get_func_args(args)
                    func = AggFunctionSpec(func.name, func.unique, dropna=True)
            self._gp_map[name] = (",".join(internal_expr), func)
            self._f_to_name[id(f_ctx)] = name

    def _handle_group_by(self) -> None:
        for i_ctx in self.get("group_by_expressions"):
            internal_expr, _ = self._get_internal_col(i_ctx)
            self._gp_keys.append(internal_expr)

    def _get_func_args(self, args: Any) -> List[str]:
        e: List[str] = []
        for i in range(len(args)):
            x, _ = self._get_internal_col(args[i])
            e.append(x)
        return e

    def _get_internal_col(self, ctx: Any) -> Tuple[str, Column]:
        internal_expr = self._obj_to_col_name(self.expr(ctx))
        if internal_expr not in self._internal_exprs:
            col = ExpressionVisitor(self)._get_single_column(ctx)
            self._internal_exprs[internal_expr] = col.rename(internal_expr)
        return internal_expr, self._internal_exprs[internal_expr]


class WindowVisitor(VisitorBase):
    def __init__(self, context: VisitorContext):
        super().__init__(context)
        self._internal_exprs: Dict[str, Column] = {}
        self._windows: Dict[str, Tuple[List[str], WindowFrameSpec]] = {}
        self._f_to_name: Dict[int, str] = {}

    def visitSortItem(self, ctx: qp.SortItemContext) -> OrderItemSpec:
        name, _ = self._get_internal_col(ctx.expression())
        asc = ctx.DESC() is None
        if ctx.FIRST() is None and ctx.LAST() is None:
            na_position = "auto"
        else:
            na_position = "first" if ctx.FIRST() is not None else "last"
        return OrderItemSpec(name, asc, na_position)

    def visitFrameBound(self, ctx: qp.FrameBoundContext) -> Tuple[bool, int]:
        unbounded = ctx.UNBOUNDED() is not None
        preceding = ctx.PRECEDING() is not None
        current = ctx.CURRENT() is not None
        if current:
            return False, 0
        if unbounded:
            return True, 0
        n = int(eval(self.to_str(ctx.expression(), "")))
        return False, -n if preceding else n

    def visitWindowFrame(self, ctx: qp.WindowFrameContext) -> WindowFrameSpec:
        if ctx is None:
            return make_windowframe_spec("")
        self.assert_support(ctx.ROWS() is not None and ctx.BETWEEN() is not None, ctx)
        s_unbounded, s_n = self.visitFrameBound(ctx.start)  # type: ignore
        e_unbounded, e_n = self.visitFrameBound(ctx.end)  # type: ignore
        return make_windowframe_spec(
            "rows", None if s_unbounded else s_n, None if e_unbounded else e_n
        )

    def visitWindowDef(self, ctx: qp.WindowDefContext) -> WindowSpec:
        wf = self.visitWindowFrame(ctx.windowFrame())
        partition_keys = [self._get_internal_col(p)[0] for p in ctx.partition]
        sort = OrderBySpec(*[self.visitSortItem(s) for s in ctx.sortItem()])
        return WindowSpec(
            "", partition_keys=partition_keys, order_by=sort, windowframe=wf
        )

    def visitFunctionCall(  # type: ignore
        self, ctx: qp.FunctionCallContext
    ) -> Tuple[WindowFunctionSpec, List[Any]]:
        func_name = self.visitFunctionName(ctx.functionName())
        args = ctx.argument
        unique = (
            ctx.setQuantifier() is not None
            and ctx.setQuantifier().DISTINCT() is not None
        )
        ws = self.visit(ctx.windowSpec())  # it won't be None
        func = WindowFunctionSpec(func_name, unique=unique, dropna=False, window=ws)
        return func, args

    def visitRegularQuerySpecification(
        self, ctx: qp.RegularQuerySpecificationContext
    ) -> None:
        self._handle_window_funcs()
        if len(self._internal_exprs) > 0:
            self.update_current(
                WorkflowDataFrame(self.current, *list(self._internal_exprs.values()))
            )
        for k, v in self._windows.items():
            self.update_current(
                self.workflow.op_to_df(
                    list(self.current.keys()) + [k],
                    "window",
                    self.current,
                    v[1],
                    v[0],
                    k,
                )
            )
        self.set("window_func_to_col", self._f_to_name)

    def _handle_window_funcs(self) -> None:
        for f_ctx in self.get("window_funcs", None):
            func, args = self.visit(f_ctx)
            name = self._obj_to_col_name(self.expr(f_ctx))
            args = self._get_func_args(args)
            self._windows[name] = (args, func)
            self._f_to_name[id(f_ctx)] = name

    def _get_func_args(self, args: Any) -> List[ArgumentSpec]:
        e: List[ArgumentSpec] = []
        for i in range(len(args)):
            is_col, is_single = self.get("func_arg_types")[id(args[i])]
            if is_col:
                x, _ = self._get_internal_col(args[i])
                e.append(ArgumentSpec(True, x))
            else:
                e.append(ArgumentSpec(False, eval(self.to_str(args[i]))))
        return e

    def _get_internal_col(self, ctx: Any) -> Tuple[str, Column]:
        internal_expr = self._obj_to_col_name(self.expr(ctx))
        if internal_expr not in self._internal_exprs:
            col = ExpressionVisitor(self)._get_single_column(ctx)
            self._internal_exprs[internal_expr] = col.rename(internal_expr)
        return internal_expr, self._internal_exprs[internal_expr]


class SelectVisitor(ExpressionVisitor):
    def __init__(self, context: VisitorContext):
        super().__init__(context)

    def visitNamedExpression(self, ctx: qp.NamedExpressionContext) -> Iterable[Column]:
        self.assert_none(ctx.identifierList())
        alias = ""
        if ctx.errorCapturingIdentifier() is not None:
            alias = self.to_str(ctx.errorCapturingIdentifier(), "")
        for col in self.visit(ctx.expression()):
            yield col if alias == "" else col.rename(alias)

    def visitNamedExpressionSeq(
        self, ctx: qp.NamedExpressionSeqContext
    ) -> Iterable[Column]:
        for ne in ctx.namedExpression():
            for r in self.visit(ne):
                yield r

    def visitSelectClause(self, ctx: qp.SelectClauseContext) -> None:
        self.update_current(
            WorkflowDataFrame(*list(self.visit(ctx.namedExpressionSeq())))
        )
        if (
            ctx.setQuantifier() is not None
            and ctx.setQuantifier().DISTINCT() is not None
        ):
            self.update_current(
                self.workflow.op_to_df(
                    list(self.current.keys()), "drop_duplicates", self.current
                )
            )

    def _get_columns(self, ctx: Any) -> List[Column]:
        if self.to_str(ctx) == "*":
            cols: List[Column] = []
            for c in self.current.values():
                cn = self.get("encoded_map", None).get(c.name, "")
                if cn != "":
                    cols.append(c.rename(cn))
            return cols
        return [
            self.current[x.encoded].rename(x.col_name)
            for x in self.get_column_mentions(ctx)
        ]
