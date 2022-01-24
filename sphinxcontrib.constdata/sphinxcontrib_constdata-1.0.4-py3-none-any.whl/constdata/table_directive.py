from typing import Any, Dict, List, Sequence, cast

from docutils import nodes

# mypy falsy reports
#       Module "docutils.parsers.rst" has no attribute "directives"; maybe "Directive"?
# but there is such module!
from docutils.parsers.rst import directives  # type: ignore[attr-defined]
from docutils.parsers.rst.directives.tables import CSVTable
from docutils.statemachine import StringList
from sphinx.util.docutils import SphinxDirective

from sphinxcontrib.constdata.flatfiles import FlatfileReader
from sphinxcontrib.constdata.l10n import gettext
from sphinxcontrib.constdata.settings import Settings
from sphinxcontrib.constdata.url import Url
from sphinxcontrib.constdata.utils import ConstdataError


class TableDirective(SphinxDirective):
    """
    A directive that inserts table filled from specified flatfile. Directive requires flatfile path as the argument and no content.

    Example::

        .. constdata:table:: menuselection.csv

    If no option "query", returns everything as-is.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0

    # Const table options
    option_spec = {
        # Limit returned rows
        "query": directives.unchanged,
        # Table title
        "title": directives.unchanged_required,
    }
    # include some CSVTable options
    csv_table_option_spec = {
        "header-rows": CSVTable.option_spec["header-rows"],
        "stub-columns": CSVTable.option_spec["stub-columns"],
        "width": CSVTable.option_spec["width"],
        "widths": CSVTable.option_spec["widths"],
        "align": CSVTable.option_spec["align"],
    }
    option_spec.update(csv_table_option_spec)

    def run(self):
        try:
            return self._run()
        except ConstdataError as ex:
            raise self.error(ex)

    def _run(self):
        """Actual run"""
        settings = Settings(self.env)

        # Argument - the only argument is the URL to a CSV
        # (e.g., ":constdata:table:: path/to/menuselection.csv")
        url = Url(self.arguments[0])
        rel_path = url.get_rel_path()

        # Options
        query_option = self.options.get("query", None)
        title_option = self.options.get("title", None)
        # pick all CSVTable options
        csv_table_options = {
            o: self.options[o] for o in self.csv_table_option_spec if o in self.options
        }  # if actually used
        # some sane defaults for CSVTable options, if unset
        if "header-rows" not in self.options:
            csv_table_options["header-rows"] = 1

        # Perform a query
        flatfile_reader = FlatfileReader(settings, rel_path)
        rows = flatfile_reader.iterate_rows(query_option)
        if not rows:
            raise ConstdataError("Query returns no rows")

        # translate
        rows = translate_table(gettext(settings), rows)

        # List of generated RST lines as would be typed by human in .rst file
        id_col_name = settings.get_id_col_name(rel_path)
        rst_lines = make_csv_table_content(rel_path, id_col_name, rows)
        # Target IDs used in the generated table
        row_ids = [r[id_col_name] for r in rows]

        self._save_to_domain(row_ids, rel_path)

        # Instantiate Docutils CSV table, run, return
        csv_table = CSVTable(
            name=self.name,
            arguments=[title_option] if title_option else [],
            options=csv_table_options,
            content=StringList(rst_lines),
            lineno=self.lineno,
            content_offset=self.content_offset,
            block_text="",
            state=self.state,
            state_machine=self.state_machine,
        )
        csv_table_nodes = csv_table.run()
        return csv_table_nodes

    def _save_to_domain(self, row_ids: Sequence[str], rel_path):
        """Save target ID - docname pairs to the domain."""
        # Save refs data to domain
        from sphinxcontrib.constdata import (  # local import to prevent circular reference
            ConstdataDomain,
        )

        for row_id in row_ids:
            target_id = make_url_safe_target_id(rel_path, row_id)
            domain = cast(ConstdataDomain, self.env.get_domain(ConstdataDomain.name))
            domain.add_target_record(target_id, self.env.docname)


def make_url_safe_target_id(rel_path, row_id) -> str:
    """
    Creates URL fragment safe string for table row target IDs.

    :param csv_file_path: path to CSV file relative to const_root
    :param row_id: row id value
    """
    # e.g. "constdata-agent/status.json-MaxCalls"
    ugly_id = f"constdata-{rel_path}-{row_id}"
    # e.g. "constdata-agent-status-json-maxcalls"
    nice_id = nodes.make_id(ugly_id)

    return nice_id


def translate_table(
    gettext_func, table: Sequence[Dict[str, Any]]
) -> Sequence[Dict[str, Any]]:
    """
    Find and translate cells using passed gettext_func. Return a new table.
    """
    new_table = []
    for i, row in enumerate(table):
        new_row = {}
        for original_col_name, col_val in row.items():
            # translate column name
            new_col_name = gettext_func(original_col_name)
            # and its value
            new_row[new_col_name] = gettext_func(col_val)
        new_table.append(new_row)

    return new_table


def make_csv_table_content(
    rel_path, id_col_name: str, table: Sequence[Dict[str, Any]]
) -> List[str]:
    """
    Construct CSV table directive content and return as a list of lines.

    Directive content are same intended lines bellow ``.. csv-table:`` and options. E.g. the following example has three content lines beginning "Albatross", "Crunchy Frog" and "Ganner Ripple"::

        .. csv-table:: Frozen Delights!
           :widths: 15, 10, 30

           "Treat", "Quantity", "Description"
           "Albatross", 2.99, "On a stick!"
           "Crunchy Frog", 1.49, "If we took the bones out, it wouldn't be crunchy, now would it?"
           "Gannet Ripple", 1.99, "On a stick!"
    )

    :param rel_path: path relative to root, used only to generate reStructuredText target unique across the whole project, not to actual reading a file
    :param id_col_name: name of ID column in table
    :param table: list of dicts, where dict is a row
    """
    # Wrap string to double quotes and escape double quote chars.
    def escape_field(unsafe_str: str) -> str:
        """Escape double quotes (``"``) with double double quotes (``""``)"""
        safe_trans_table = str.maketrans({r'"': r'""'})
        if not isinstance(unsafe_str, str):
            unsafe_str = str(unsafe_str)
        return "".join(['"', unsafe_str.translate(safe_trans_table), '"'])

    lines = []

    for i, row in enumerate(table):
        # prevent modifying rows passed in table param
        new_row = row.copy()

        # Header row with col names
        if i == 0:
            col_names = new_row.keys()
            escaped_col_names = [escape_field(col) for col in col_names]
            line = ",".join(escaped_col_names)
            lines.append(line)

        # All rows, except the header, needs a target
        try:
            id_col_value = new_row[id_col_name]
        except KeyError:
            raise ConstdataError(
                f"Can't list a table because '{rel_path}' has no ID column with name '{id_col_name}'."
            )

        # create target ID
        target_id = make_url_safe_target_id(rel_path, id_col_value)
        # generate RST label
        label_rst = f".. _{target_id}:"
        # prepend it to first column value
        new_row[id_col_name] = f"{label_rst}\n\n{new_row[id_col_name]}"

        escaped_col_values = [escape_field(val) for val in new_row.values()]
        line = ",".join(escaped_col_values)
        lines.append(line)

    return lines
