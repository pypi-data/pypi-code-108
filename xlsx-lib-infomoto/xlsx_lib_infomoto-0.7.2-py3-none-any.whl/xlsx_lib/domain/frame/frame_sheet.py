from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell import Cell
from typing import List

from xlsx_lib.domain.frame.element_part import ElementPart
from xlsx_lib.domain.frame.frame_cell_value_types import FrameCellValueTypes
from xlsx_lib.domain.frame.frame_element import FrameElement
from xlsx_lib.domain.xlsx_elements.sheet import Sheet

from xlsx_lib.domain.frame.complex_frame_element_error import ComplexFrameElementError
from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException


def get_frame_cell_value_type(cell: Cell) -> FrameCellValueTypes:
    if cell.font.b and cell.alignment.horizontal in ["left", "general", None]:
        return FrameCellValueTypes.FRAME_ELEMENT
    elif cell.alignment.horizontal == "right":
        return FrameCellValueTypes.ELEMENT_PART


class FrameSheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.frame_elements: List[FrameElement] = list()

        super().__init__(
            worksheet=worksheet,
            end_of_sheet_rows_limit=20,
            start_col=1,
            start_row=2,
        )

        self.process_frame_elements()

    def process_frame_elements(self) -> None:
        col_index: int = self.start_col
        row_index: int = self.start_row

        while True:
            cell: Cell = self.sheet_reader.read_cell(col_index, row_index)

            try:
                self.process_cell(cell, col_index, row_index)
            except ContinueException:
                row_index += 1
                continue
            except ComplexFrameElementError as error:
                row_index += error.jumped_rows
                continue
            except SheetEndException:
                break

            row_index += 1

    def process_cell(self, cell: Cell, col_index: int, row_index: int):
        if cell.value is None:
            if self.sheet_reader.read_cell_value(col_index, row_index + 1) is None \
                    and self.frame_elements[-1].value is None \
                    and self.frame_elements[-1].element_parts is not None\
                    and len(self.frame_elements[-1].element_parts) == 0 \
                    and self.frame_elements[-1].observations is None:
                self.process_complex_frame_element_observations(
                    row=row_index,
                )

            self.check_next_values(row=row_index)

            raise ContinueException

        cell_value_type = get_frame_cell_value_type(cell)

        if cell_value_type is FrameCellValueTypes.FRAME_ELEMENT:
            self.process_frame_element(col_index, row_index)
        elif cell_value_type is FrameCellValueTypes.ELEMENT_PART:
            self.process_element_part(col_index, row_index)

    def process_frame_element(
            self,
            col: int,
            row: int,
    ) -> None:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        self.frame_elements.append(
            FrameElement(
                name=values[0],
                value=values[1],
                observations=values[2],
            )
        )

    def process_element_part(
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

        if self.frame_elements[-1].element_parts is None:
            self.frame_elements[-1].element_parts = list()

        self.frame_elements[-1].element_parts.append(
            ElementPart(
                name=values[0],
                value=values[1],
                observations=values[2]
            )
        )

    def process_complex_frame_element_observations(
            self,
            row: int,
    ) -> None:
        self.frame_elements[-1].observations = [value for value in self.sheet_reader.read_cells_values(
            start_col=self.start_col + 2,
            end_col=self.start_col + 2,
            start_row=row,
            end_row=row + 6
        ) if value is not None]

        raise ComplexFrameElementError(5)

    def check_next_values(
            self,
            row: int,
    ) -> None:
        element_parts_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + self.end_of_sheet_rows_limit,
            start_col=self.start_col,
        )

        element_parts_matches: int = len([cell for cell in element_parts_cells
                                          if cell.value is not None
                                          and get_frame_cell_value_type(cell)
                                          is FrameCellValueTypes.ELEMENT_PART])

        frame_elements_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + self.end_of_sheet_rows_limit,
            start_col=self.start_col,
        )

        frame_elements_matches: int = len([cell for cell in frame_elements_cells
                                           if cell.value is not None
                                           and get_frame_cell_value_type(cell)
                                           is FrameCellValueTypes.FRAME_ELEMENT])

        if frame_elements_matches == 0 and element_parts_matches == 0:
            raise SheetEndException
