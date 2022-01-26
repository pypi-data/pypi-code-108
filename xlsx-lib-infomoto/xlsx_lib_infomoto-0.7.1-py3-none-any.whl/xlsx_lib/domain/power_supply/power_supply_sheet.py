from typing import List

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from xlsx_lib.domain.power_supply.power_supply_component import PowerSupplyComponent
from xlsx_lib.domain.power_supply.component_attribute import ComponentAttribute
from xlsx_lib.domain.power_supply.power_supply_cell_value_types import PowerSupplyCellValueType
from xlsx_lib.domain.xlsx_elements.exceptions.continue_exception import ContinueException
from xlsx_lib.domain.xlsx_elements.exceptions.sheet_end_exception import SheetEndException
from xlsx_lib.domain.xlsx_elements.sheet import Sheet


def get_power_supply_cell_value_type(cell: Cell) -> PowerSupplyCellValueType:
    if cell.font.b and cell.alignment.horizontal in ["left", "general", None]:
        return PowerSupplyCellValueType.COMPONENT
    elif cell.alignment.horizontal == "right":
        return PowerSupplyCellValueType.COMPONENT_ATTRIBUTE


class PowerSupplySheet(Sheet):
    def __init__(
            self,
            worksheet: Worksheet,
    ):
        self.components: List[PowerSupplyComponent] = []

        super().__init__(
            worksheet=worksheet,
            end_of_sheet_rows_limit=20,
            start_col=1,
            start_row=2,
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
                row_index += 1
                continue
            except SheetEndException:
                break

            row_index += 1

    def process_cell(self, cell: Cell, col_index: int, row_index: int):
        if cell.value is None:
            self.check_next_values(row=row_index)
            raise ContinueException

        cell_value_type = get_power_supply_cell_value_type(cell)

        if cell_value_type is PowerSupplyCellValueType.COMPONENT:
            self.process_component(
                row=row_index,
                col=col_index,
            )
        elif cell_value_type is PowerSupplyCellValueType.COMPONENT_ATTRIBUTE:
            self.process_component_attribute(
                row=row_index,
                col=col_index,
            )

    def process_component(
            self,
            col: int,
            row: int,
    ) -> None:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        self.components.append(
            PowerSupplyComponent(
                name=values[0],
                value=values[1],
                observations=values[2],
            )
        )

    def process_component_attribute(
            self,
            row: int,
            col: int,
    ) -> None:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        if self.components[-1].component_attributes is None:
            self.components[-1].component_attributes = list()

        self.components[-1].component_attributes.append(
            ComponentAttribute(
                name=values[0],
                value=values[1],
                observations=values[2]
            )
        )

    def check_next_values(
            self,
            row: int,
    ) -> None:
        unnamed_attribute_cell: Cell = self.sheet_reader.read_cell(
            row=row,
            col=self.start_col + 1,
        )

        if unnamed_attribute_cell.value is not None:
            self.process_component_attribute(
                row=row,
                col=self.start_col
            )
            return

        component_attributes_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + self.end_of_sheet_rows_limit,
            start_col=self.start_col,
        )

        component_attributes_matches: int = len([cell for cell in component_attributes_cells
                                                 if cell.value is not None
                                                 and get_power_supply_cell_value_type(cell)
                                                 is PowerSupplyCellValueType.COMPONENT_ATTRIBUTE])

        components_cells: List[Cell] = self.sheet_reader.read_cells(
            start_row=row + 1,
            end_row=row + self.end_of_sheet_rows_limit,
            start_col=self.start_col,
        )

        components_matches: int = len([cell for cell in components_cells
                                       if cell.value is not None
                                       and get_power_supply_cell_value_type(cell)
                                       is PowerSupplyCellValueType.COMPONENT])

        if components_matches == 0 and component_attributes_matches == 0:
            raise SheetEndException
        else:
            raise ContinueException
