from importlib.util import find_spec
from functools import wraps
from math import isclose
from pathlib import Path
from typing import Collection, Any, Type, List, TypeVar, Iterator

# Conditional imports
if find_spec('xlrd'):
    import xlrd
    from xlrd.sheet import Sheet
else:
    xlrd = None
    Sheet = TypeVar('Sheet')

if find_spec('xlwt'):
    import xlwt
    from xlwt import Workbook as WriteWorkbook, Worksheet as WriteWorksheet
else:
    xlwt = None
    WriteWorkbook = TypeVar('WriteWorkbook')
    WriteWorksheet = TypeVar('WriteWorksheet')

if find_spec('xlutils'):
    import xlutils
    from xlutils.copy import copy as xlutils_copy
else:
    xlutils = None

from ..core import requires
from ..spreadsheets import SpreadsheetSerializer
from ..typing import ParsedDataRow


__ALL__ = ['XLSSerializer', 'xls', ]


class XLSSerializer(SpreadsheetSerializer):
    MAX_LINES = 65536
    MAX_COLS = 256

    def __init__(self, int_precision: float | None = 1E-9, **kwargs):
        super().__init__(**kwargs)
        self.int_precision = int_precision

    #  xlwt specific implementation
    @staticmethod
    @requires('xlwt')
    def _add_sheet(workbook: WriteWorkbook, sheet_name: str) -> WriteWorksheet:
        return workbook.add_sheet(sheet_name)

    @staticmethod
    @requires('xlwt')
    def _write_headers(sheet: WriteWorksheet, headers: Collection[str]):
        for header_col, header_title in enumerate(headers):
            sheet.write(0, header_col, header_title)

    @staticmethod
    @requires('xlwt')
    def _write_row(sheet: WriteWorksheet, headers: Collection[str], row_num: int, row_data: ParsedDataRow,
                   default: Any = SpreadsheetSerializer.DEFAULT_EMPTY_ON_WRITE):
        for col_num, col_key in enumerate(headers):
            sheet.write(row_num, col_num, row_data.get(col_key, default))

    @staticmethod
    @requires('xlwt')
    def _freeze_headers(sheet: WriteWorksheet):
        sheet.set_panes_frozen(True)  # frozen headings instead of split panes
        sheet.set_horz_split_pos(1)  # in general, freeze after last heading row
        sheet.set_remove_splits(True)  # if user does unfreeze, don't leave a split there

    @staticmethod
    @requires('xlwt')
    def _get_new_workbook():
        return xlwt.Workbook()

    @staticmethod
    @requires('xlwt')
    def _save_workbook(workbook, fp: Path | str):
        workbook.save(fp)

    # xlrd specific implementation
    @staticmethod
    @requires('xlrd')
    def _get_sheet_name(sheet) -> str:
        return sheet.name

    @staticmethod
    @requires('xlrd')
    def _get_all_sheets(book) -> List[Any]:
        return book.sheets()

    @requires('xlrd')
    def _iter_through_sheet(self,
                            sheet: Sheet,
                            workbook,
                            constructor: Type = None,
                            default: Any = SpreadsheetSerializer.DEFAULT_EMPTY_ON_READ,
                            ) -> Iterator[ParsedDataRow]:

        has_formatting_info = getattr(workbook, 'has_formatting_info', False)
        int_precision = self.int_precision

        # Extract headers from first row
        headers = list()
        for col_num in range(sheet.ncols):
            headers.append(sheet.cell_value(0, col_num))

        # Extract data from remaining rows
        for row_num in range(1, sheet.nrows):

            row = dict()

            for col_num in range(sheet.ncols):
                value = sheet.cell_value(row_num, col_num)
                value = value if value != '' else default

                if has_formatting_info:
                    value = self._format_cell(value, sheet.cell_type(row_num, col_num), workbook.datemode, default)

                # Convert floats to ints if they are close to an integer
                if int_precision and isinstance(value, float) and isclose(value, int(value), abs_tol=int_precision):
                    value = int(value)

                row[headers[col_num]] = value

            yield constructor(**row) if constructor else row

    @requires('xlrd')
    def _format_cell(self, value, xl_index, date_mode,
                     default: Any = SpreadsheetSerializer.DEFAULT_EMPTY_ON_READ) -> Any:
        match xl_index:
            case xlrd.XL_CELL_EMPTY:
                return default
            case xlrd.XL_CELL_TEXT:
                return str(value)
            case xlrd.XL_CELL_NUMBER:
                return float(value)
            case xlrd.XL_CELL_DATE:
                return xlrd.xldate_as_tuple(value, date_mode)
            case xlrd.XL_CELL_BOOLEAN:
                return bool(value)
            case xlrd.XL_CELL_ERROR:
                return self.CellError.match_behaviour(self.cell_error, value, default)
            case xlrd.XL_CELL_BLANK:
                return default
            case _:
                return value

    @requires('xlrd')
    def _open_workbook(self, fp: Path | str, for_append=False, **kwargs) -> 'xlrd.Workbook':
        try:
            has_formatting_info = kwargs.setdefault('formatting_info', True)
            workbook = xlrd.open_workbook(Path(fp), **kwargs)
        except NotImplementedError:
            # Catches formatting_info not implemented for 2007 Excel files
            has_formatting_info = False
            kwargs['formatting_info'] = False
            workbook = xlrd.open_workbook(Path(fp), **kwargs)

        workbook.has_formatting_info = has_formatting_info

        return self._convert_for_append(workbook) if for_append else workbook

    @staticmethod
    @requires('xlutils')
    def _convert_for_append(workbook):
        return xlutils_copy(workbook)


# Default implementation
xls = XLSSerializer()
