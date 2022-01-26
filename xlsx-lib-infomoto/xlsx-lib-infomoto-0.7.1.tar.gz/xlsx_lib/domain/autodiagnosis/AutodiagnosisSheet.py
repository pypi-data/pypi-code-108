from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell import Cell
from typing import List, Optional

from xlsx_lib.domain.autodiagnosis.AutodiagnosisData import AutodiagnosisData
from xlsx_lib.domain.autodiagnosis.Fault import Fault
from xlsx_lib.domain.autodiagnosis.AutodiagnosisCellValueKind import AutodiagnosisCellValueKind
from xlsx_lib.domain.xlsx_elements.sheet import Sheet

from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException


def get_autodiagnosis_cell_value_kind(cell: Cell) -> AutodiagnosisCellValueKind:
    # if cell.font.b and cell.alignment.horizontal in ["left", "general", None]:
    #     return FrameCellValueTypes.FRAME_ELEMENT
    # elif cell.alignment.horizontal == "right":
    #     return FrameCellValueTypes.ELEMENT_PART
    if cell.font.b and cell.alignment.horizontal == "center":
        try:
            return {
                "ELEMENTO": AutodiagnosisCellValueKind.ELEMENT_COLUMN_TITLE,
                "CODIGO": AutodiagnosisCellValueKind.CODE_COLUMN_TITLE,
                "DESCRIPCION AVERIA": AutodiagnosisCellValueKind.FAULT_DESCRIPTION_COLUMN_TITLE,
            }[cell.value]
        except KeyError:
            raise ContinueException
    else:
        return AutodiagnosisCellValueKind.FAULT_CONTENT


class AutodiagnosisSheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.autodiagnosis: AutodiagnosisData = AutodiagnosisData()
        self.faults_list_found: bool = False
        self.faults_list_with_code: bool = False

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
                row_index += 1
                continue
            except SheetEndException:
                break

            row_index += 1

    def process_cell(self, cell: Cell, col_index: int, row_index: int):
        if cell.value is None:
            self.check_next_values(row=row_index)
            raise ContinueException

        cell_value_type = get_autodiagnosis_cell_value_kind(cell)

        if self.faults_list_found and cell_value_type is AutodiagnosisCellValueKind.FAULT_CONTENT:
            self.process_fault(col_index, row_index)

        elif (cell_value_type is AutodiagnosisCellValueKind.ELEMENT_COLUMN_TITLE) \
                or (cell_value_type is AutodiagnosisCellValueKind.FAULT_DESCRIPTION_COLUMN_TITLE):
            self.faults_list_found = True

        elif cell_value_type is AutodiagnosisCellValueKind.CODE_COLUMN_TITLE:
            self.check_next_values(row=row_index, rows_checked=2, continue_mode=True)

            self.faults_list_found = True
            self.faults_list_with_code = True

    def process_fault(
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

        self.autodiagnosis.faults_list.append(
            Fault(
                code=values[0] if self.faults_list_with_code else None,
                description=values[1] if self.faults_list_with_code else values[0],
                observations=values[2] if self.faults_list_with_code else values[1],
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

        fault_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + rows_checked,
            start_col=self.start_col,
        )

        fault_cells_matches: int = len([cell for cell in fault_cells
                                        if cell.value is not None
                                        and get_autodiagnosis_cell_value_kind(cell)
                                        is AutodiagnosisCellValueKind.FAULT_CONTENT])

        if fault_cells_matches == 0:
            if continue_mode:
                raise ContinueException

            raise SheetEndException

