import re
from typing import List, Optional

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from xlsx_lib.domain.abs.AbsCellValueKind import AbsCellValueKind
from xlsx_lib.domain.abs.AbsData import AbsData
from xlsx_lib.domain.abs.Problem import Problem
from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException
from xlsx_lib.domain.xlsx_elements.sheet import Sheet


def get_abs_cell_value_kind(cell: Cell) -> AbsCellValueKind:
    if cell.font.b and cell.alignment.horizontal == "center" and cell.value is not None:
        search_result = re.search("(CODIGO)", str(cell.value).upper())

        result_count = len(search_result.groups()) if search_result is not None else 0

        if result_count > 0:
            return AbsCellValueKind.CODE_COLUMN_TITLE
        else:
            raise ContinueException
    elif not cell.font.b and cell.alignment.horizontal == "center":
        return AbsCellValueKind.PROBLEM_CONTENT
    else:
        raise ContinueException


class AbsSheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.abs_data: AbsData = AbsData()
        self.problems_list_found: bool = False

        super().__init__(
            worksheet=worksheet,
            end_of_sheet_rows_limit=20,
            start_col=0,
            start_row=0,
        )

        self.process_data()

    def process_data(self) -> None:
        col_index: int = self.start_col
        row_index: int = self.start_row

        while True:
            cell: Cell = self.sheet_reader.read_cell(col_index, row_index)

            try:
                self.process_cell(cell, col_index, row_index)
            except ContinueException:
                pass
            except SheetEndException:
                break

            row_index += 1

    def process_cell(self, cell: Cell, col_index: int, row_index: int):
        if cell.value is None:
            self.check_next_values(row=row_index)
            raise ContinueException

        cell_value_type = get_abs_cell_value_kind(cell)

        if self.problems_list_found and cell_value_type is AbsCellValueKind.PROBLEM_CONTENT:
            self.process_problem(col_index, row_index)

        elif cell_value_type is AbsCellValueKind.CODE_COLUMN_TITLE:
            self.check_next_values(row=row_index, rows_checked=2, continue_mode=True)
            self.problems_list_found = True

    def process_problem(
            self,
            col: int,
            row: int,
    ) -> None:
        values: List[str] = self.sheet_reader.read_cells_values(
            col,
            col + 2,
            row,
            row
        )

        self.abs_data.problems_list.append(
            Problem(
                code=values[0],
                involved_element=values[1],
                description=values[2],
            )
        )

    def check_next_values(
            self,
            row: int,
            rows_checked: Optional[int] = None,
            continue_mode: bool = False,
    ) -> None:
        if rows_checked is None:
            rows_checked = self.end_of_sheet_rows_limit

        problem_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + rows_checked,
            start_col=self.start_col,
        )

        problem_cells_matches: int = len([cell for cell in problem_cells
                                          if cell.value is not None
                                          and get_abs_cell_value_kind(cell)
                                          is AbsCellValueKind.PROBLEM_CONTENT])

        if problem_cells_matches == 0:
            if continue_mode:
                raise ContinueException

            raise SheetEndException

