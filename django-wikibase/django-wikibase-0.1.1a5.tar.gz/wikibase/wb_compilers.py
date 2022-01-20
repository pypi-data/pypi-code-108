from json.encoder import JSONEncoder
from typing import Any, Tuple

from django.core.exceptions import EmptyResultSet, FieldError
from django.db import DatabaseError, NotSupportedError
from django.db.models.sql import compiler
from django.db.models.sql.where import WhereNode
from django.db.models.lookups import Exact
from django.db.models.expressions import Col, OrderBy
from django.db.models.sql.datastructures import BaseTable, Join
from django.db.transaction import TransactionManagementError

from json import dumps

# The izip_longest was renamed to zip_longest in py3
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from .ir.cmd import Cmd
from .ir.django_model import DjangoModel
from .ir.django_property import DjangoProperty
from .loggable import Loggable


_BUILT_IN_TYPES = {int, float, str, bool}


class SQLCompiler(compiler.SQLCompiler, Loggable):

    _select_data = {
        'models': None,
        'sparql': None
    }

    def resolve_columns(self, row, fields=()):
        # We need to convert values from database to correct django field representation.
        # For instance, if we defined a BooleanField field, django-wikibase do create a
        # smallint field into DB. When retrieving this field value, it's converted to
        # BooleanField again.
        index_start = len(self.query.extra_select)
        values = []
        for value, field in zip_longest(row[index_start:], fields):
            v = self.query.convert_values(
                value, field, connection=self.connection)
            values.append(v)
        return row[:index_start] + tuple(values)

    def compile(self, expression_node) -> Tuple:
        type_of_expression_node = type(expression_node)
        wb_database_connection = self.connection.connection
        if type_of_expression_node is Col:
            django_table_name = expression_node.field.model._meta.db_table
            if not(django_table_name in self.query.alias_refmap):
                self.query.alias_refmap[django_table_name] = []
            if not(expression_node.field.column in self.query.alias_refmap[django_table_name]):
                self.query.alias_refmap[django_table_name].append(
                    expression_node.field.column)
            # DjangoProperty(expression_node.field, DjangoModel), []
            return f'?{expression_node.field.column}', []
        if type_of_expression_node is BaseTable:
            expressions = [wb_database_connection.expression_instance_of(
                expression_node.table_name)]
            for property_name in self.query.alias_refmap[expression_node.table_name]:
                expressions.append(wb_database_connection.expression_has_property(
                    expression_node.table_name, property_name))
            self.query.alias_refmap[expression_node.table_name].clear()
            return expressions, []
        if type_of_expression_node is WhereNode:
            sql, params = expression_node.as_sql(self, self.connection)
            return sql.replace(' AND ', ' && ').replace(' OR ', ' || '), params
        if type_of_expression_node is Exact:
            lhs_sql, params = self.compile(expression_node.lhs)
            rhs_sql, rhs_params = self.compile(expression_node.rhs)
            if rhs_params:
                params.extend(rhs_params)
            return f'{lhs_sql} = {rhs_sql}', params
        if type_of_expression_node in _BUILT_IN_TYPES:
            return wb_database_connection.sparql_parameter_value(expression_node), None
        if type_of_expression_node is Join:
            expressions = [
                wb_database_connection.expression_instance_of(
                    expression_node.parent_alias),
                wb_database_connection.expression_instance_of(
                    expression_node.table_alias)
            ]
            # Add a join condition for each pair of joining columns.
            for lhs_col, rhs_col in expression_node.join_cols:
                expressions.append(wb_database_connection.expression_has_property(
                    expression_node.parent_alias, lhs_col))
                expressions.append(wb_database_connection.expression_has_property(
                    expression_node.table_alias, rhs_col))
                expressions.append(
                    f'FILTER(str(?{lhs_col}) = str(?{rhs_col}))')
            return expressions, []
        if type_of_expression_node is OrderBy:
            order_by: OrderBy = expression_node
            sql, params = order_by.as_sql()
            return sql, params
        raise NotImplementedError(
            f'Sorry, I can\'t perform compile for the node expression {expression_node}')

    def as_sql(self, with_limits=True, with_col_aliases=False):
        refcounts_before = self.query.alias_refcount.copy()
        self.query.alias_refmap = {f: [] for f in refcounts_before}
        models = {self.query.model}
        try:
            if self.query.model:
                self.query.base_table = self.query.model._meta.db_table
            extra_select, order_by, group_by = self.pre_sql_setup()
            for_update_part = None
            # Is a LIMIT/OFFSET clause needed?
            with_limit_offset = with_limits and (
                self.query.high_mark is not None or self.query.low_mark)
            combinator = self.query.combinator
            features = self.connection.features

            result = self.connection.connection.prefixes()

            if combinator:
                if not getattr(features, 'supports_select_{}'.format(combinator)):
                    raise NotSupportedError(
                        '{} is not supported on this database backend.'.format(combinator))
                result, params = self.get_combinator_sql(
                    combinator, self.query.combinator_all)
            else:
                distinct_fields, distinct_params = self.get_distinct()
                # This must come after 'select', 'ordering', and 'distinct'
                # (see docstring of get_from_clause() for details).
                from_, f_params = self.get_from_clause()
                try:
                    sparql_filter, w_params = self.compile(
                        self.where) if self.where is not None else ('', [])
                except EmptyResultSet:
                    if self.elide_empty:
                        raise
                    # Use a predicate that's always False.
                    sparql_filter, w_params = '0 = 1', []
                having, h_params = self.compile(
                    self.having) if self.having is not None else ("", [])
                result.append('SELECT')
                params = []

                if self.query.distinct:
                    distinct_result, distinct_params = self.connection.ops.distinct_sql(
                        distinct_fields,
                        distinct_params,
                    )
                    result += distinct_result
                    params += distinct_params

                out_cols = []
                col_idx = 1
                for col, (s_sql, s_params), alias in self.select + extra_select:
                    # if alias:
                    #     s_sql = '%s AS %s' % (
                    #         s_sql, self.connection.ops.quote_name(alias))
                    # elif with_col_aliases:
                    #     s_sql = '%s AS %s' % (
                    #         s_sql,
                    #         self.connection.ops.quote_name('col%d' % col_idx),
                    #     )
                    #     col_idx += 1
                    params.extend(s_params)
                    # out_cols.append(s_sql)

                    # update models
                    models.add(col.field.model)
                    out_cols.append(s_sql)

                # result += [', '.join(out_cols), 'FROM', *from_]
                deduplicated_from_clause = list(dict.fromkeys(*from_))
                result += [' '.join(out_cols), 'WHERE {', '\n . '.join(deduplicated_from_clause)]
                params.extend(f_params)

                if self.query.select_for_update and self.connection.features.has_select_for_update:
                    if self.connection.get_autocommit():
                        raise TransactionManagementError(
                            'select_for_update cannot be used outside of a transaction.')

                    if with_limit_offset and not self.connection.features.supports_select_for_update_with_limit:
                        raise NotSupportedError(
                            'LIMIT/OFFSET is not supported with '
                            'select_for_update on this database backend.'
                        )
                    nowait = self.query.select_for_update_nowait
                    skip_locked = self.query.select_for_update_skip_locked
                    of = self.query.select_for_update_of
                    no_key = self.query.select_for_no_key_update
                    # If it's a NOWAIT/SKIP LOCKED/OF/NO KEY query but the
                    # backend doesn't support it, raise NotSupportedError to
                    # prevent a possible deadlock.
                    if nowait and not self.connection.features.has_select_for_update_nowait:
                        raise NotSupportedError(
                            'NOWAIT is not supported on this database backend.')
                    elif skip_locked and not self.connection.features.has_select_for_update_skip_locked:
                        raise NotSupportedError(
                            'SKIP LOCKED is not supported on this database backend.')
                    elif of and not self.connection.features.has_select_for_update_of:
                        raise NotSupportedError(
                            'FOR UPDATE OF is not supported on this database backend.')
                    elif no_key and not self.connection.features.has_select_for_no_key_update:
                        raise NotSupportedError(
                            'FOR NO KEY UPDATE is not supported on this '
                            'database backend.'
                        )
                    for_update_part = self.connection.ops.for_update_sql(
                        nowait=nowait,
                        skip_locked=skip_locked,
                        of=self.get_select_for_update_of_arguments(),
                        no_key=no_key,
                    )

                if for_update_part and self.connection.features.for_update_after_from:
                    result.append(for_update_part)

                if sparql_filter:
                    result.append(' . FILTER (%s)' % sparql_filter)
                    params.extend(w_params)

                result.append('}')

                grouping = []
                for g_sql, g_params in group_by:
                    grouping.append(g_sql)
                    params.extend(g_params)
                if grouping:
                    if distinct_fields:
                        raise NotImplementedError(
                            'annotate() + distinct(fields) is not implemented.')
                    order_by = order_by or self.connection.ops.force_no_ordering()
                    result.append('GROUP BY %s' % ', '.join(grouping))
                    if self._meta_ordering:
                        order_by = None
                if having:
                    result.append('HAVING %s' % having)
                    params.extend(h_params)

            if self.query.explain_info:
                result.insert(0, self.connection.ops.explain_query_prefix(
                    self.query.explain_info.format,
                    **self.query.explain_info.options
                ))

            if order_by:
                ordering = []
                for _, (o_sql, o_params, _) in order_by:
                    ordering.append(o_sql)
                    params.extend(o_params)
                result.append('ORDER BY %s' % ', '.join(ordering))

            if with_limit_offset:
                result.append(self.connection.ops.limit_offset_sql(
                    self.query.low_mark, self.query.high_mark))

            if for_update_part and not self.connection.features.for_update_after_from:
                result.append(for_update_part)

            if self.query.subquery and extra_select:
                # If the query is used as a subquery, the extra selects would
                # result in more columns than the left-hand side expression is
                # expecting. This can happen when a subquery uses a combination
                # of order_by() and distinct(), forcing the ordering expressions
                # to be selected as well. Wrap the query in another subquery
                # to exclude extraneous selects.
                sub_selects = []
                sub_params = []
                for index, (select, _, alias) in enumerate(self.select, start=1):
                    if not alias and with_col_aliases:
                        alias = 'col%d' % index
                    if alias:
                        sub_selects.append("%s.%s" % (
                            self.connection.ops.quote_name('subquery'),
                            self.connection.ops.quote_name(alias),
                        ))
                    else:
                        select_clone = select.relabeled_clone(
                            {select.alias: 'subquery'})
                        subselect, subparams = select_clone.as_sql(
                            self, self.connection)
                        sub_selects.append(subselect)
                        sub_params.extend(subparams)
                return 'SELECT %s FROM (%s) subquery' % (
                    ', '.join(sub_selects),
                    ' '.join(result),
                ), tuple(sub_params + params)

        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)

        cmd_data = {**self._select_data, **{
            'models': [DjangoModel(model) for model in models],
            'sparql': '\n'.join(result)
        }}
        return Cmd('select', cmd_data), params


class SQLInsertCompiler(compiler.SQLInsertCompiler, Loggable):

    _add_items_data = {
        'model': None,
        'fields': None,
    }

    def as_sql(self, with_limits=True, with_col_aliases=False):
        # sql, params = super(compiler.SQLInsertCompiler, self).as_sql(
        #     with_limits=with_limits, with_col_aliases=with_col_aliases)
        self.debug('SQL insert compiler, as_sql, with limits %s, with col aliases %s',
                   with_limits, with_col_aliases)
        cmd_data = {**self._add_items_data, **{
            'model': DjangoModel(self.query.fields[0].model),
            'fields': [DjangoProperty(f, DjangoModel) for f in self.query.fields]
        }}

        return [(Cmd('add_items', cmd_data),
                 [{f['property_name']: getattr(o, f['attribute_name']) for f in cmd_data['fields']} for o in self.query.objs])]


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, Loggable):

    _remove_items_data = {
        'sparql': None
    }

    def as_sql(self, with_limits=True, with_col_aliases=False):
        sql, params = super(compiler.SQLDeleteCompiler, self).as_sql(
            with_limits=False, with_col_aliases=with_col_aliases)
        self.debug('SQL delete compiler, as_sql, with limits %s, with col aliases %s',
                   with_limits, with_col_aliases)
        cmd_data = {**self._remove_items_data, **{'sparql': sql}}
        return [(Cmd('remove_items', cmd_data), (params))]


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, Loggable):

    _set_items_data = {
        'model': None,
        'values': None,
        'where': None
    }

    def as_sql(self, with_limits=True, with_col_aliases=False):
        # sql, params = super(compiler.SQLUpdateCompiler, self).as_sql(
        #     with_limits=False, with_col_aliases=with_col_aliases)
        self.debug('SQL update compiler, as_sql, with limits %s, with col aliases %s',
                   with_limits, with_col_aliases)
        self.pre_sql_setup()
        cmd_data = {**self._set_items_data, **{
            'model': DjangoModel(self.query.model),
            'values': [DjangoProperty(f, DjangoModel) for f, _, _ in self.query.values],
            'where': self.query.where.as_sql(self, self.connection)
        }}

        return Cmd('set_items', cmd_data), [{f['property_name']: getattr(v, f['attribute_name']) for f in cmd_data['values']} for _, _, v in self.query.values]


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, Loggable):

    _agg_items_data = {
        'sparql': None
    }

    def as_sql(self, with_limits=True, with_col_aliases=False):
        sql, params = super(compiler.SQLAggregateCompiler, self).as_sql(
            with_limits=False, with_col_aliases=with_col_aliases)
        self.debug('SQL aggregate compiler, as_sql, with limits %s, with col aliases %s',
                   with_limits, with_col_aliases)
        cmd_data = {**self._agg_items_data, **{'sparql': sql}}
        return [(Cmd('agg_items', cmd_data), (params))]
