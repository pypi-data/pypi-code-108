from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell import Cell
from typing import List

from xlsx_lib.domain.xlsx_elements.sheet import Sheet


from xlsx_lib.domain.engine.engine_section import EngineSection
from xlsx_lib.domain.engine.section_element import SectionElement
from xlsx_lib.domain.engine.element_attribute import ElementAttribute

from xlsx_lib.domain.engine.engine_cell_value_types import EngineCellValueTypes
from xlsx_lib.modules.format_cell_value import format_cell_value


def get_engine_cell_value_type(cell: Cell) -> EngineCellValueTypes:
    if cell.font.b and cell.alignment.horizontal in ["left", "general", None]:
        if cell.font.sz == 20:
            return EngineCellValueTypes.ENGINE_SECTION
        elif cell.font.sz == 11:
            return EngineCellValueTypes.SECTION_ELEMENT
    elif cell.alignment.horizontal == "right":
        return EngineCellValueTypes.ELEMENT_ATTRIBUTE


class EngineSheet(Sheet):
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet=worksheet)
        self.engine_sections: List[EngineSection] = self.get_engine_sections()

    def get_engine_sections(
            self,
            start_col: int = 1,
            start_row: int = 1,
    ) -> List[EngineSection]:
        col_index = start_col
        row_index = start_row

        elements: List[EngineSection] = list()

        while True:
            cell: Cell = self.sheet_reader.read_cell(col_index, row_index)

            if cell.value is None:
                components_values = self.sheet_reader.read_cells_values(
                    start_col=1,
                    end_col=1,
                    start_row=row_index + 1,
                    end_row=row_index + 4,
                )

                components_matches: List[str] = [value for value in components_values
                                                 if value is not None]

                elements_cells = self.sheet_reader.read_cells(
                    start_col=2,
                    end_col=2,
                    start_row=row_index + 1,
                    end_row=row_index + 4,
                )

                elements_matches: List[Cell] = [cell for cell in elements_cells
                                                if cell.value is not None and
                                                get_engine_cell_value_type(cell)
                                                is EngineCellValueTypes.ENGINE_SECTION]

                if len(elements_matches) == 0 and len(components_matches) == 0:
                    break
                elif len(elements_matches) != 0:
                    col_index = start_col

                row_index += 1
                continue

            # TODO: Create distribution section and put it in self.distribution
            if format_cell_value(cell.value) == "DISTRIBUCION":
                break

            cell_value_type = get_engine_cell_value_type(cell)

            if cell_value_type is EngineCellValueTypes.ENGINE_SECTION:
                elements.append(
                    self.get_engine_section(col_index, row_index)
                )

            elif cell_value_type is EngineCellValueTypes.SECTION_ELEMENT:
                if elements[-1].section_elements is None:
                    elements[-1].section_elements = list()

                elements[-1].section_elements.append(
                    self.get_section_element(col_index, row_index)
                )

            elif cell_value_type is EngineCellValueTypes.ELEMENT_ATTRIBUTE:
                if elements[-1].section_elements[-1].element_attributes is None:
                    elements[-1].section_elements[-1].element_attributes = list()

                elements[-1].section_elements[-1].element_attributes.append(
                    self.get_element_attribute(col_index, row_index)
                )

            row_index += 1

        return elements

    def get_engine_section(
            self,
            col: int,
            row: int
    ) -> EngineSection:
        return EngineSection(
            name=self.sheet_reader.read_cell_value(col, row)
        )

    def get_section_element(
            self,
            col: int,
            row: int
    ) -> SectionElement:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        return SectionElement(
            name=values[0],
            value=values[1],
            observations=values[2]
        )

    def get_element_attribute(
            self,
            col: int,
            row: int
    ) -> ElementAttribute:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 2, row, row)

        return ElementAttribute(
            name=values[0],
            value=values[1],
            observations=values[2]
        )
