from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell import Cell
from typing import List

from xlsx_lib.domain.electronic.component_attribute import ComponentAttribute
from xlsx_lib.domain.electronic.electronic_value_types import ElectronicValueTypes
from xlsx_lib.domain.electronic.element_component import ElementComponent
from xlsx_lib.domain.xlsx_elements.sheet import Sheet

from xlsx_lib.domain.electronic.electronic_element import ElectronicElement


# TODO: Sort conditions by usage
from xlsx_lib.modules.format_cell_value import format_cell_value


def get_electronic_cell_value_type(cell: Cell) -> ElectronicValueTypes:
    if cell.font.b and cell.alignment.horizontal == "center":
        return ElectronicValueTypes.ELECTRONIC_ELEMENT
    elif cell.font.b and cell.alignment.horizontal in ["left", "general", None]:
        return ElectronicValueTypes.ELEMENT_COMPONENT
    elif cell.alignment.horizontal == "right":
        return ElectronicValueTypes.COMPONENT_ATTRIBUTE


class ElectronicSheet(Sheet):
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet=worksheet)

    def get_electronic_elements(
            self,
            start_col: int = 2,
            start_row: int = 2,
    ) -> List[ElectronicElement]:
        col_index = start_col
        row_index = start_row

        elements: List[ElectronicElement] = list()

        while True:
            cell: Cell = self.sheet_reader.read_cell(col_index, row_index)

            # TODO: Update and test all sheets
            if format_cell_value(cell.value) is None:
                components_cells: List[Cell] = self.sheet_reader.read_cells(
                    start_col=1,
                    end_col=1,
                    start_row=row_index + 1,
                    end_row=row_index + 4,
                )

                components_matches: int = len([cell for cell in components_cells
                                               if cell.value is not None
                                               and get_electronic_cell_value_type(cell)
                                               is ElectronicValueTypes.ELEMENT_COMPONENT])

                elements_cells: List[Cell] = self.sheet_reader.read_cells(
                    start_col=2,
                    end_col=2,
                    start_row=row_index + 1,
                    end_row=row_index + 4,
                )

                elements_matches: int = len([cell for cell in elements_cells
                                             if cell.value is not None
                                             and get_electronic_cell_value_type(cell)
                                             is ElectronicValueTypes.ELECTRONIC_ELEMENT])

                if elements_matches == 0 and components_matches == 0:
                    break
                elif (elements_matches != 0 and components_matches == 0) or \
                        (elements_matches != 0 and components_matches != 0
                         and self.sheet_reader.read_cell_value(col_index, row_index + 1) is None):
                    col_index = start_col

                row_index += 1
                continue

            if format_cell_value(cell.value) == "ESQUEMA ELECTRICO":
                break

            cell_value_type = get_electronic_cell_value_type(cell)

            if cell_value_type is ElectronicValueTypes.ELECTRONIC_ELEMENT:
                elements.append(self.get_electronic_element(col_index, row_index))
                col_index = start_col - 1

            elif cell_value_type is ElectronicValueTypes.ELEMENT_COMPONENT:
                if elements[-1].components is None:
                    elements[-1].components = list()

                elements[-1].components.append(
                    self.get_element_component(col_index, row_index)
                )

            elif cell_value_type is ElectronicValueTypes.COMPONENT_ATTRIBUTE:
                if elements[-1].components[-1].attributes is None:
                    elements[-1].components[-1].attributes = list()

                elements[-1].components[-1].attributes.append(
                    self.get_component_attribute(col_index, row_index)
                )

            row_index += 1

        return elements

    def get_electronic_element(
            self,
            col: int,
            row: int
    ) -> ElectronicElement:
        return ElectronicElement(
            name=self.sheet_reader.read_cell_value(col, row)
        )

    def get_element_component(
            self,
            col: int,
            row: int
    ) -> ElementComponent:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        return ElementComponent(
            name=values[0],
            value=values[1],
            observations=values[2]
        )

    def get_component_attribute(
            self,
            col: int,
            row: int
    ) -> ComponentAttribute:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        return ComponentAttribute(
            name=values[0],
            value=values[1],
            observations=values[2]
        )
