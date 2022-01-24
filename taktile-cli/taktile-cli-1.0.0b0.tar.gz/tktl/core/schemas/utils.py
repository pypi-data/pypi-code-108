from typing import List

from beautifultable import BeautifulTable  # type: ignore

from tktl.core.schemas.repository import Endpoint


def get_table_from_list_of_schemas(
    models: List[Endpoint],
    keys: List[str] = None,
    names: List[str] = None,
    maxwidth=140,
):
    if not names:
        names = []
    table = BeautifulTable(
        maxwidth=maxwidth, default_alignment=BeautifulTable.ALIGN_LEFT
    )
    rows = len(models)
    if rows < 1:
        raise ValueError("Nothing to print")

    first = models[0]
    as_dict = first.table_repr(subset=keys)
    if names:
        table.columns.header = list(as_dict.keys())

    if not names and keys:
        table.columns.header = keys
    elif not names and not keys:
        keys = list(first.table_repr().keys())
        table.columns.header = keys
    for i in range(rows):
        if keys:
            table.rows.append([models[i].table_repr()[attr] for attr in keys])
    table.set_style(BeautifulTable.STYLE_NONE)
    return table
