"""
This module is used for formatting the result of ONTAP REST API calls into a table
of result rows
"""

from collections import OrderedDict

try:
    RECLINE_INSTALLED = False
    from recline.formatters.table_formatter import TableFormat  # type: ignore
    RECLINE_INSTALLED = True
except ImportError:
    # can't stop the rest of the module parsing, but we will if/else it out
    pass

from netapp_ontap.resource import Resource


__pdoc__ = {
    "ResourceTable": False,
}


if RECLINE_INSTALLED:
    class ResourceTable(TableFormat):  # pylint: disable=too-few-public-methods
        """This subclass of TableFormat takes into account how the results from the
        REST API are returned and turns them into a consistent table.
        """

        def format_output(self, results):
            rows = []
            for result in results:
                if isinstance(result, Resource):
                    rows.append(result.to_dict())
                else:
                    rows.append(result)
            if not rows:
                return super().format_output(rows)
            rows = _normalize_fields(rows)
            complex_fields = []
            for result in rows:
                result.pop("_links", None)
                for field in result:
                    if isinstance(result[field], (dict, list)):
                        complex_fields.append(field)
            for result in rows:
                for field in complex_fields:
                    result.pop(field, None)
            return super().format_output(rows)


def _normalize_fields(rows):
    """Make sure all rows have all the same fields in the same order"""

    for row in rows:
        for header in row.keys():
            for item in rows:
                if header not in item:
                    item[header] = "-"

    sorted_entries = []
    headers = sorted(rows[0].keys())
    for row in rows:
        ordered_entry = OrderedDict()
        for header in headers:
            ordered_entry[header] = row[header]
        sorted_entries.append(ordered_entry)

    return sorted_entries
