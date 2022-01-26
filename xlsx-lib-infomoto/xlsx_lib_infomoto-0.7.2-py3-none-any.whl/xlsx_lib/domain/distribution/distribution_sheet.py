import uuid
from io import BytesIO
from typing import List

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl_image_loader import SheetImageLoader
from openpyxl.drawing.image import Image

from xlsx_lib.domain.shared.NewImageData import NewImageData
from xlsx_lib.domain.shared.NewImageFile import NewImageFile
from xlsx_lib.domain.shared.TextLine import TextLine
from xlsx_lib.domain.distribution.data_block import DataBlock
from xlsx_lib.domain.distribution.distribution_cell_value_types import DistributionCellValueType
from xlsx_lib.domain.distribution.distribution_data import DistributionData
from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException
from xlsx_lib.domain.xlsx_elements.sheet import Sheet


def get_distribution_value_type(cell: Cell) -> DistributionCellValueType:
    if cell.font.underline:
        return DistributionCellValueType.TITLE
    else:
        return DistributionCellValueType.TEXT


class DistributionSheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.distribution_images: List[NewImageFile] = []
        self.distribution_data: DistributionData = DistributionData()

        self.max_col: int = 3
        self.start_col: int = 0

        super().__init__(
            worksheet=worksheet,
            end_of_sheet_rows_limit=20,
            start_col=self.start_col,
            start_row=1,
        )

        image_loader = SheetImageLoader(worksheet)

        for image in worksheet._images:
            filename: str = f"{uuid.uuid4()}.{image.format}"

            self.distribution_images.append(
                NewImageFile(
                    filename=filename,
                    file=image.ref,
                )
            )

            self.distribution_data.blocks.append(
                DataBlock(
                    image=NewImageData(
                        filename=filename,
                        width=image.width,
                        height=image.height,
                    )
                )
            )

        self.process_sheet_data()

    def process_sheet_data(self) -> None:
        col_index: int = self.start_col
        row_index: int = self.start_row

        while True:
            cell: Cell = self.sheet_reader.read_cell(col_index, row_index)

            try:
                self.process_cell(cell, col_index, row_index)
            except ContinueException:
                col_index += 1

                if col_index > self.max_col:
                    col_index = self.start_col
                    row_index += 1

                continue
            except SheetEndException:
                break

            row_index += 1

    def process_cell(self, cell: Cell, col_index: int, row_index: int):
        if cell.value is None:
            self.check_next_values(row=row_index)
            raise ContinueException

        cell_value_type = get_distribution_value_type(cell)

        if cell_value_type is DistributionCellValueType.TEXT:
            self.distribution_data.blocks.append(
                DataBlock(
                    text_lines=[
                        TextLine(
                            text=self.sheet_reader.read_cell(
                                row=row_index,
                                col=col_index,
                            ).value
                        ),
                    ],
                )
            )
        elif cell_value_type is DistributionCellValueType.TITLE:
            self.distribution_data.subtitle = self.sheet_reader.read_cell(
                row=row_index,
                col=col_index,
            ).value

    def check_next_values(
            self,
            row: int,
    ) -> None:
        next_cells = self.sheet_reader.read_cells(
            start_row=row,
            end_row=row+20,
            start_col=self.start_col,
            end_col=self.start_col + 2,
        )

        if len([cell for cell in next_cells
                if cell.value is not None]) > 0:
            raise ContinueException

        raise SheetEndException

