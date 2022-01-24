from pathlib import Path
from string import Formatter
from typing import Union

from sphinxcontrib.constdata.flatfiles import FlatfileReader
from sphinxcontrib.constdata.l10n import gettext
from sphinxcontrib.constdata.settings import Settings
from sphinxcontrib.constdata.utils import ConstdataError


def resolve_template(
    settings: Settings,
    template_string: str,
    row_id: str,
    rel_path: Union[Path, str],
) -> str:
    """
    Takes template string, CSV file path, and returns final string with placeholders replaced with values from CSV files.

    E.g., for

    ::

        :menuselection:`{label}`

    returns

    ::

        :menuselection:`Settings --> Permissions`

    or, for

    ::

        ``{_('Configuration parameter')}``

    returns

    ::

        ConsumptionsSeparated

    :param settings: :py:class:`settings.Settings`: object
    :param template_string:
    :param rel_path: path to the file, relative to constdata_root
    """

    formatter = Formatter()

    # parse() loop over the template string and return an iterable of tuples (literal_text, field_name, format_spec, conversion).
    # E.g., for template string
    #       '``{_(\'Conf parameter\')}``'
    # returns
    #       ["_('Conf parameter')", None]
    # we need field_name (the second in the tuple) without None values
    column_names = [t[1] for t in formatter.parse(template_string) if t[1] is not None]

    # Transform column names to values in the current row
    mapping = {}
    flatfile = FlatfileReader(settings, rel_path)

    _ = gettext(settings)

    # lookup row
    row = flatfile.get_row_by_id(row_id)
    if not row:
        raise ConstdataError(
            f"File '{rel_path}' doesn't contain a row with ID '{row_id}'."
        )

    for column_name in column_names:
        try:
            column_value = row[column_name]
            column_value_translated = _(column_value)
        except KeyError:
            columns_in_file = list(row.keys())
            raise ConstdataError(
                f"File '{rel_path}' doesn't contain column '{column_name}' referred in template '{template_string}' but only {columns_in_file} columns."
            )

        mapping[column_name] = column_value_translated

    # render and return the result
    resolved = formatter.format(template_string, **mapping)
    return resolved
