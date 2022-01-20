import datetime
import operator
import json

from agilicus import context
from agilicus.output.json import convert_to_json

from dataclasses import dataclass
from typing import Callable

from prettytable import PrettyTable


def format_date(date_input):
    return date_input.strftime("%Y-%m-%d %H:%M:%S %z (%Z)")


def date_else_identity(input_obj):
    if isinstance(input_obj, datetime.datetime):
        return format_date(input_obj)
    return input_obj


@dataclass
class OutputColumn:
    in_name: str
    out_name: str
    format_fn: Callable = date_else_identity
    getter: Callable = None
    optional: bool = False


def column(name, newname=None, optional=False, getter=None):
    out_name = newname
    if not out_name:
        out_name = name
    return OutputColumn(
        in_name=name, out_name=out_name, optional=optional, getter=getter
    )


def mapped_column(in_name, out_name):
    return OutputColumn(in_name=in_name, out_name=out_name)


def subtable(
    ctx,
    in_name,
    columns,
    out_name=None,
    subobject_name=None,
    table_getter=operator.attrgetter,
    optional=False,
):
    if not out_name:
        out_name = in_name

    def format_fn(records):
        return format_table(ctx, records, columns, getter=table_getter)

    def getter(record, base_getter):
        subobject = base_getter(subobject_name)(record)
        return base_getter(in_name)(subobject)

    col_getter = None
    if subobject_name:
        col_getter = getter

    return OutputColumn(
        in_name=in_name,
        out_name=out_name,
        format_fn=format_fn,
        getter=col_getter,
        optional=optional,
    )


def subobject_column(
    in_name,
    out_name,
    subobject_name,
    optional=False,
    max_size=None,
    json_dump=None,
    **kwargs,
):
    if not out_name:
        out_name = in_name

    def output_val(val):
        if json_dump:
            return json.dumps(val, indent=4)
        return val

    def getter(record, base_getter):
        try:
            subobject = base_getter(subobject_name)(record)
            val = base_getter(in_name)(subobject)
            if max_size is not None and val:
                return output_val(val[:max_size])
            return output_val(val)
        except Exception as exc:
            if not optional:
                raise exc
            return None

    return OutputColumn(
        in_name=in_name, out_name=out_name, getter=getter, optional=optional
    )


def metadata_column(in_name, out_name=None, **kwargs):
    return subobject_column(in_name, out_name, "metadata", **kwargs)


def spec_column(in_name, out_name=None, **kwargs):
    return subobject_column(in_name, out_name, "spec", **kwargs)


def status_column(in_name, out_name=None, **kwargs):
    return subobject_column(in_name, out_name, "status", **kwargs)


# An implementation of attrgetter that handles a None in the middle
def short_circuit_attrgetter(item):
    def func(obj):
        for name in item.split("."):
            if obj is None:
                return None
            obj = getattr(obj, name)
        return obj

    return func


def format_table(
    ctx, records, columns, getter=short_circuit_attrgetter, row_filter=None
):
    if context.output_json(ctx):
        records_as_dicts = [
            record.to_dict() if not isinstance(record, dict) else record
            for record in records
        ]
        return convert_to_json(ctx, records_as_dicts)
    table = PrettyTable([column.out_name for column in columns])
    if not records:
        return table

    if not isinstance(records, list):
        records = [records]

    for record in records:
        row = []

        if row_filter is not None:
            if not row_filter(record):
                continue
        for column in columns:
            in_value = None
            if column.getter:
                try:
                    in_value = column.getter(record, getter)
                except Exception as exc:
                    if not column.optional:
                        raise exc
            else:
                try:
                    in_value = getter(column.in_name)(record)
                except Exception as exc:
                    if not column.optional:
                        raise exc

            out_value = "---"
            if in_value is not None:
                out_value = column.format_fn(in_value)
            row.append(out_value)

        table.add_row(row)
    table.align = "l"
    return table
