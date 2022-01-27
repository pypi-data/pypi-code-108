from openpyxl.worksheet.worksheet import Worksheet

from xlsx_lib.domain.xlsx_elements.sheet_reader import SheetReader


class Sheet:
    def __init__(
            self,
            worksheet: Worksheet,
            end_of_sheet_rows_limit: int = 20,
            start_col: int = 1,
            start_row: int = 1,
    ):
        self.sheet_reader: SheetReader = SheetReader(worksheet=worksheet)
        self.start_col: int = start_col
        self.start_row: int = start_row
        self.end_of_sheet_rows_limit: int = end_of_sheet_rows_limit
