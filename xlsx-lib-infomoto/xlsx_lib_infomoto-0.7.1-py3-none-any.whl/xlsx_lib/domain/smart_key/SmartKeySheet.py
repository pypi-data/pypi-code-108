import uuid
from typing import List, Optional

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl_image_loader import SheetImageLoader

from xlsx_lib.domain.shared.NewImageData import NewImageData
from xlsx_lib.domain.shared.NewImageFile import NewImageFile
from xlsx_lib.domain.shared.TextLine import TextLine
from xlsx_lib.domain.smart_key.Fault import Fault
from xlsx_lib.domain.smart_key.SmartKeyCellValueKind import SmartKeyCellValueKind
from xlsx_lib.domain.smart_key.SmartKeyData import SmartKeyData
from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException
from xlsx_lib.domain.xlsx_elements.sheet import Sheet


def get_smart_key_cell_value_kind(cell: Cell) -> SmartKeyCellValueKind:
    if cell.alignment.horizontal == "center" and cell.value == 'TIPO DE FALLO':
        return SmartKeyCellValueKind.FAULT_KIND_TITLE
    else:
        return SmartKeyCellValueKind.FAULT_CONTENT


class SmartKeySheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.smart_key_data: SmartKeyData = SmartKeyData()

        self.smart_key_images: List[NewImageFile] = []

        self.stored_flash_pattern_images_data: List[NewImageData] = []
        self.stored_flashs_number_by_time: List[str] = []
        self.stored_parts_to_review: List[str] = []

        super().__init__(
            worksheet=worksheet,
            end_of_sheet_rows_limit=20,
            start_col=0,
            start_row=0,
        )

        image_loader = SheetImageLoader(worksheet)

        for image in worksheet._images:
            filename: str = f"{uuid.uuid4()}.{image.format}"

            self.smart_key_images.append(
                NewImageFile(
                    filename=filename,
                    file=image.ref,
                )
            )

            self.stored_flash_pattern_images_data.append(
                NewImageData(
                    filename=filename,
                    width=image.width,
                    height=image.height
                )
            )

        self.process_data()

        for i in range(len(self.smart_key_data.faults_list)):
            self.smart_key_data.faults_list[i].flash_pattern_image = self.stored_flash_pattern_images_data[i]

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
        if cell.value is None and self.sheet_reader.read_cell_value(row=row_index, col=col_index+3) is None:
            self.check_next_values(row=row_index)
            raise ContinueException

        cell_value_type = get_smart_key_cell_value_kind(cell)

        if cell_value_type is SmartKeyCellValueKind.FAULT_CONTENT:
            self.process_fault(col_index, row_index)

    def process_fault(
            self,
            col: int,
            row: int,
    ) -> None:
        values: List[str] = self.sheet_reader.read_cells_values(
            col,
            col + 3,
            row,
            row
        )

        if values[0] is not None:
            if self.sheet_reader.read_cell_value(row=row-1, col=col) is not None:

                if self.smart_key_data.faults_list[-1].fault_kind[-1].text[-1] == " ":
                    self.smart_key_data.faults_list[-1].fault_kind[-1].text += " "

                self.smart_key_data.faults_list[-1].fault_kind[-1].text += f" {values[0]}"

            elif self.sheet_reader.read_cell_value(row=row-2, col=col) is not None:
                self.smart_key_data.faults_list[-1].fault_kind.append(TextLine(text=values[0]))

            else:
                self.smart_key_data.faults_list.append(
                    Fault(
                        fault_kind=[TextLine(text=values[0])],
                        flashs_number_by_time=self.stored_flashs_number_by_time.pop() if len(self.stored_flashs_number_by_time) != 0 else None,
                        parts_to_review=[TextLine(text=self.stored_parts_to_review.pop())] if len(self.stored_parts_to_review) != 0 else None,
                    )
                )

        if values[2] is not None:
            if self.sheet_reader.read_cell_value(row=row-1, col=col+2) is not None \
                    or self.sheet_reader.read_cell_value(row=row-2, col=col+2) is not None:

                if self.smart_key_data.faults_list[-1].flashs_number_by_time[-1] == " ":
                    self.smart_key_data.faults_list[-1].flashs_number_by_time += " "

                self.smart_key_data.faults_list[-1].flashs_number_by_time += f" {values[2]}"

            else:
                if self.smart_key_data.faults_list[-1].flashs_number_by_time is None:
                    self.smart_key_data.faults_list[-1].flashs_number_by_time = values[2]
                else:
                    self.stored_flashs_number_by_time.append(values[2])

        if values[3] is not None:
            previous_row_value = self.sheet_reader.read_cell_value(row=row-1, col=col+3)

            if previous_row_value is None:
                if self.smart_key_data.faults_list[-1].parts_to_review is None:
                    self.smart_key_data.faults_list[-1].parts_to_review = [TextLine(text=values[3])]
                elif self.sheet_reader.read_cell_value(row=row - 2, col=col + 3) is None:
                    self.stored_parts_to_review.append(values[3])
                else:
                    self.smart_key_data.faults_list[-1].parts_to_review.append(TextLine(text=values[3]))

            else:
                if previous_row_value.startswith("REVISAR") and values[3].startswith("REVISAR"):
                    self.smart_key_data.faults_list[-1].parts_to_review.append(TextLine(text=values[3]))
                elif self.smart_key_data.faults_list[-1].parts_to_review is not None:
                    if self.smart_key_data.faults_list[-1].parts_to_review[-1].text[-1] == " ":
                        self.smart_key_data.faults_list[-1].parts_to_review[-1].text += " "
                    self.smart_key_data.faults_list[-1].parts_to_review[-1].text += f" {values[3]}"

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
            end_col=self.start_col+2,
        )

        fault_cells_matches: int = len([cell for cell in fault_cells
                                        if cell.value is not None
                                        and get_smart_key_cell_value_kind(cell)
                                        is SmartKeyCellValueKind.FAULT_CONTENT])

        if fault_cells_matches == 0:
            if continue_mode:
                raise ContinueException

            raise SheetEndException

