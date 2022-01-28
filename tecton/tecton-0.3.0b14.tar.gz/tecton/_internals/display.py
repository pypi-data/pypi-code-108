from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Callable
from typing import List

from google.protobuf import timestamp_pb2
from jinja2 import BaseLoader
from jinja2 import Environment
from texttable import Texttable

from tecton_proto.data.summary_pb2 import FcoSummary
from tecton_proto.data.summary_pb2 import SummaryItem


_TABLE_HTML_TEMPLATE = """
<table>
<thead>
    <tr>
    {% for heading in headings %}
    <th style='text-align: left;'>{{heading}}</th>
    {% endfor %}
    </tr>
</thead>
<tbody>
    {% for item in items %}
    <tr>
        {% for value in item %}
        {% if value is string and '\n' in value %}
        <td style='text-align: left;'><pre style='padding: 5px; border:1px solid #efefef'>{{value}}</pre></td>
        {% else %}
        <td style='text-align: left;'>{{value}}</td>
        {% endif %}
        {% endfor %}
    </tr>
    {% endfor %}
</tbody>
</table>
"""


def _fco_metadata_formatter(key, value):
    if isinstance(value, timestamp_pb2.Timestamp):
        t = datetime.fromtimestamp(value.ToSeconds())
        return t.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    return value


class Displayable(object):
    _table_template = Environment(loader=BaseLoader(), autoescape=True).from_string(_TABLE_HTML_TEMPLATE)

    def __init__(self, text_table, html):
        self._text_table = text_table
        self._html = html

    def __repr__(self):
        return self._text_table.draw()

    def __str__(self):
        return self.__repr__()

    def _repr_html_(self):
        return self._html

    @classmethod
    def from_items(cls, headings, items, max_width=None, deco=Texttable.HEADER):
        """Returns a displayable table built from an iterable of tuples."""
        for row_index, item in enumerate(items):
            if len(item) != len(headings):
                raise ValueError(
                    f"malformed dimensions: headings has length {len(headings)}, but row {row_index} has lenght {len(item)}"
                )

        text_table = Texttable()
        if max_width is not None:
            text_table.set_max_width(max_width)
        text_table.add_rows(items, header=False)
        text_table.header(headings)
        text_table.set_deco(deco)

        # build HTML version
        html = cls._table_template.render(headings=headings, items=items)

        return cls(text_table, html)

    @classmethod
    def from_fco_summary(
        cls,
        fco_summary: FcoSummary,
        additional_items=[],
        value_formatter: Callable[[str, Any], str] = _fco_metadata_formatter,
    ):

        fco_metadata_fields = [
            "name",
            "workspace",
            "description",
            "created_at",
            "owner",
            "last_modified_by",
            "family",
            "source_filename",
            "tags",
        ]
        table_items = [
            (_transform_field_name(field), _fco_metadata_formatter(field, getattr(fco_summary.fco_metadata, field)))
            for field in fco_metadata_fields
        ]

        for item in fco_summary.summary_items:
            if not item.HasField("display_name"):
                continue
            if item.HasField("value"):
                value = item.value
            elif len(item.multi_values) > 0:
                value = ", ".join(item.multi_values)
            elif len(item.nested_summary_items) > 0:
                value = str(cls._get_nested_table(item.nested_summary_items))
            else:
                value = ""
            table_items.append((item.display_name, value_formatter(item.key, value)))

        for key, value in additional_items:
            table_items.append((key, value_formatter(key, value)))

        text_table = Texttable()
        text_table.add_rows(table_items, header=False)
        text_table.set_deco(Texttable.BORDER | Texttable.VLINES | Texttable.HLINES)
        text_table.set_cols_valign(["m", "m"])

        # build HTML version
        html = cls._table_template.render(headings=["", ""], items=table_items)

        return cls(text_table, html)

    @classmethod
    def _get_nested_table(cls, nested_summary_items: List[SummaryItem]):
        displayed_items = []
        for nested_item in nested_summary_items:
            if not nested_item.HasField("display_name"):
                continue
            if len(nested_item.nested_summary_items) > 0:
                displayed_items.append(
                    (nested_item.display_name, str(cls._get_nested_table(nested_item.nested_summary_items)))
                )
            else:
                displayed_items.append((nested_item.display_name, nested_item.value))

        text_table = Texttable()
        text_table.add_rows(displayed_items, header=False)
        text_table.set_deco(0)
        return text_table.draw()


def _transform_field_name(name):
    return name.replace("_", " ").title()
