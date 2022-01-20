from typing import List

from msgraphy.data import graphdataclass
from msgraphy.data.file import DriveItem


@graphdataclass
class Table:
    id: str = None
    name: str = None
    style: str = None
    show_filter_button: bool = None
    highlight_last_column: bool = None
    highlight_first_column: bool = None
    show_banded_columns: bool = None
    show_banded_rows: bool = None
    show_headers: bool = None
    show_totals: bool = None
    legacy_id: str = None


@graphdataclass
class WorkbookSessionInfo:
    id: str
    persist_changes: bool

    # This is not returned from the API - but it makes sense to keep the context
    workbook_reference: DriveItem = None

    def headers(self):
        return {"workbook-session-id": self.id}


@graphdataclass
class WorkbookTableRow:
    index: int
    values: List


@graphdataclass
class WorkbookTableColumn:
    id: str
    index: int
    name: str
    values: List


@graphdataclass
class WorkbookRange:
    address: str = None
    address_local: str = None
    cell_count: int = None
    column_count: int = None
    column_hidden: bool = None
    column_index: int = None
    formulas: dict = None
    formulas_local: dict = None
    formulasR1C1: dict = None
    hidden: bool = None
    number_format: dict = None
    row_count: int = None
    row_hidden: bool = None
    row_index: int = None
    text: dict = None
    value_types: str = None
    values: dict = None
