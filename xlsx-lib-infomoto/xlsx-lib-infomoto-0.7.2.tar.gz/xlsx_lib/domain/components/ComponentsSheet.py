import uuid

from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell import Cell
from typing import List, Optional

from openpyxl_image_loader import SheetImageLoader

from xlsx_lib.domain.shared.NewImageData import NewImageData
from xlsx_lib.domain.shared.NewImageFile import NewImageFile
from xlsx_lib.domain.components.ComponentsData import ComponentsData
from xlsx_lib.domain.components.Component import Component
from xlsx_lib.domain.xlsx_elements.sheet import Sheet

from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException


class ComponentsSheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.components_data: ComponentsData = ComponentsData()
        self.components_image: Optional[NewImageFile] = None

        super().__init__(
            worksheet=worksheet,
            end_of_sheet_rows_limit=20,
            start_col=1,
            start_row=1,
        )

        image_loader = SheetImageLoader(worksheet)

        if len(worksheet._images) > 0:
            image = worksheet._images[0]
            filename: str = f"{uuid.uuid4()}.{image.format}"

            self.components_data.components_image = \
                NewImageData(
                    filename=filename,
                    width=image.width,
                    height=image.height,
                )

            self.components_image = \
                NewImageFile(
                    filename=filename,
                    file=image.ref,
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

        self.process_component(col_index, row_index)

    def process_component(
            self,
            col: int,
            row: int,
    ) -> None:
        values: List[str] = self.sheet_reader.read_cells_values(
            col,
            col + 1,
            row,
            row
        )

        self.components_data.components.append(
            Component(
                number=values[0],
                name=values[1],
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

        components_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + rows_checked,
            start_col=self.start_col,
        )

        components_cells_matches: int = len([cell for cell in components_cells
                                             if cell.value is not None])

        if components_cells_matches == 0:
            if continue_mode:
                raise ContinueException

            raise SheetEndException
