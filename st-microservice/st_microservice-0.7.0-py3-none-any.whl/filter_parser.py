from datetime import date
import pyparsing as pp
from sqlalchemy import Column
from sqlalchemy.orm import Query


math_operators = '< <= > >= <> != ='


def math_query(q: Query, f: Column, operator: str, v: any):
    return {
        '=': q.where(f == v),
        '<': q.where(f < v),
        '<=': q.where(f <= v),
        '>': q.where(f > v),
        '>=': q.where(f >= v),
        '<>': q.where(f != v),
        '!=': q.where(f != v)
    }[operator]


def number_filter_parser(query: Query, field: Column, filter_string: str) -> Query:
    exp = pp.Opt(pp.one_of(math_operators), '=') + pp.common.number + pp.LineEnd()
    tokens = exp.parse_string(filter_string)

    return math_query(query, field, tokens[0], tokens[1])


def date_filter_parser(query: Query, field: Column, filter_string: str) -> Query:
    two_digits = pp.Word(pp.nums, exact=2)
    four_digits = pp.Word(pp.nums, exact=4)

    isodate_exp = pp.Combine(four_digits + '-' + two_digits + '-' + two_digits)

    short_year_exp = pp.Opt(pp.Suppress('/')) + four_digits | two_digits
    short_month_exp = pp.Opt(pp.Suppress('/')) + two_digits + pp.Opt(short_year_exp)
    short_date_exp = pp.Combine(two_digits + pp.Opt(short_month_exp))

    date_exp = pp.CaselessLiteral('t') | isodate_exp | short_date_exp

    exp = pp.Opt(pp.one_of(math_operators), '=') + date_exp + pp.lineEnd()

    tokens = exp.parse_string(filter_string)

    today = date.today()

    value = tokens[1]

    if value == 't':
        value = today
    elif len(value) == 2:
        value = date(today.year, today.month, int(value))
    elif len(value) == 4:
        value = date(today.year, int(value[2:4]), int(value[0:2]))
    elif len(value) == 6:
        value = date(2000 + int(value[4:6]), int(value[2:4]), int(value[0:2]))
    elif len(value) == 8:
        value = date(int(value[4:8]), int(value[2:4]), int(value[0:2]))
    # else means isodate
    return math_query(query, field, tokens[0], value)


def boolean_filter_parser(query: Query, field: Column, filter_string: str) -> Query:
    exp = pp.one_of(['y', 'yes', 'true', 'n', 'no', 'false'], True) + pp.LineEnd()
    token = exp.parse_string(filter_string)[0]

    if token in ['y', 'yes', 'true']:
        return query.where(field == True)
    else:
        return query.where(field == False)
