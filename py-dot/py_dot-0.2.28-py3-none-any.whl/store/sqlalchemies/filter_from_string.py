from datetime import datetime

from sqlalchemy import or_, Column, and_
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.sqltypes import String, TypeDecorator

from py_dot.core.date import Period
from py_dot.core.route import from_query_string


def _get_period_logic(column: Column, period: Period):
    begin = period.begin
    end = period.end

    if begin and end:
        # return f'{column.name}.between({begin}, {end})'
        print(begin, end)
        return column.between(begin, end)

    if begin:
        # return f'{column.name} >= {begin}'
        return column >= begin

    if end:
        # return f'{column.name} <= {end}'
        return column <= end

    raise ValueError('Period has not Begin and End Time')


def _get_normal_logic(column: Column, value):
    column_type = column.type

    if isinstance(column_type, sqltypes.DateTime):
        if not isinstance(value, (Period, datetime)):
            raise ValueError(f'`{column.name}` Keyword should be cast-able to Timestamp')

        if isinstance(value, Period):
            return _get_period_logic(column, value)

    if isinstance(value, (bool, datetime)):
        return column == value

    if _is_string_type(column):
        value = str(value)

        if _is_quote(value):
            return column.like(value[1:-1])

        value = value.replace('%', '\\%')
        # return f'{column.name}.like(%{value}%)'
        return column.like(f'%{value}%')

    # return f'{column.name} == {value[1:-1]}'
    return column == value


def _is_quote(value: str):
    if value.startswith('"') and value.endswith('"'):
        return True

    if value.startswith("'") and value.endswith("'"):
        return True

    return False


def _is_string_type(column: Column):
    if not hasattr(column, 'dot_is_string_type_'):
        setattr(column, 'dot_is_string_type_', _is_string_type_test(column))

    return column.dot_is_string_type_


def _is_string_type_test(column: Column):
    """
    todo: Make to Global Function
    """
    column_type = column.type

    if isinstance(column_type, String) or String in column_type.__class__.__mro__:
        return True

    if isinstance(column_type, TypeDecorator):
        impl = getattr(column_type.__class__, 'impl')
        if isinstance(impl, String) or String in impl.__class__.__mro__:
            return True

    return False


def filter_from_string(
    model: object,
    query_string: str,
    use_snake_case=False,
    use_default_timezone=False
):
    """ Make Sqlalchemy Query Filter by Query String

    :param model: ORM Class
    :param query_string: Query the Search String
    :param use_snake_case: Using snake_case to key
    :param use_default_timezone:
    :raise ValueError: when target condition is not a Column of Model
    """

    if not hasattr(model, '__table__'):
        raise ValueError('Not a Model Class')

    columns = model.__table__.columns

    conditions = from_query_string(
        query_string,
        use_snake_case=use_snake_case,
        use_default_timezone=use_default_timezone
    )

    filters = []

    for column_name in conditions:
        if not hasattr(columns, column_name):
            raise ValueError(f'{column_name} is not a Attribute')

        column: Column = getattr(columns, column_name)

        if not isinstance(column, Column):
            raise ValueError(f'{column_name} is not a Column')

        condition = conditions[column_name]

        if isinstance(condition, list):
            equal_values = []
            like_logics = []
            for or_condition in condition:
                if isinstance(or_condition, (bool, int, float)):
                    equal_values.append(or_condition)
                    continue

                if isinstance(or_condition, str) and _is_quote(or_condition):
                    equal_values.append(or_condition[1:-1])
                    continue

                like_logics.append(
                    _get_normal_logic(column, or_condition)
                )

            if equal_values and like_logics:
                # filters.append(
                #     '(' +
                #     ' OR '.join(
                #         [
                #             f'{column_name}.in({",".join(map(str, equal_values))})',
                #             *like_values
                #         ]
                #     )
                #     + ')'
                # )
                filters.append(
                    or_(
                        column.in_(*equal_values),
                        *like_logics
                    )
                )
                continue

            if equal_values:
                # filters.append(
                #     f'{column_name}.in({",".join(map(str, equal_values))})'
                # )
                filters.append(
                    column.in_(*equal_values)
                )
                continue

            # filters.append(f'({" OR ".join(like_values)})')
            filters.append(*like_logics)
            continue

        filters.append(
            _get_normal_logic(column, condition)
        )

    # return ' AND \n'.join(filters)
    return and_(*filters)

# query_string_parts = [
#     'single_int:1',
#     'single_str:foo',
#     'single_eq_str:"foo"',
#     'single_begin:20211130~',
#     'single_end:~20211130',
#     'single_period:20211129~20211130',
#
#     'multi_int:1,2',
#     'multi_str:foo,bar',
#     'multi_mix:1,foo',
#     'multi_eq_mix:1,"foo"',
#     'multi_eq_mix_with_numeric_str:"1","foo"'
# ]
# filters = filter_from_query_string({}, ';'.join(query_string_parts))
# print(filters)
