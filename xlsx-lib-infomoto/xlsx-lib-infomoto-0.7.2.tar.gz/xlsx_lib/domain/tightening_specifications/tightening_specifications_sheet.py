from typing import Optional, List

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from xlsx_lib.domain.tightening_specifications.specification_element import SpecificationElement
from xlsx_lib.domain.tightening_specifications.element_part import ElementPart
from xlsx_lib.domain.tightening_specifications.part_screw import Screw
from xlsx_lib.domain.tightening_specifications.tightening_torque_step import TighteningSpecificationStep
from xlsx_lib.domain.xlsx_elements.sheet import Sheet


class TighteningSpecificationsSheet(Sheet):
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet=worksheet)

    def get_specification_elements(
            self,
            start_col: int = 0,
            start_row: int = 2,
    ) -> List[SpecificationElement]:
        row_index = start_row

        elements: List[SpecificationElement] = list()

        while True:
            cell: Cell = self.sheet_reader.read_cell(start_col, row_index)
            
            if str(cell.value).startswith("*"):
                row_index += 1
                continue

            if cell.value is None:
                values = self.sheet_reader.read_cells_values(
                    start_col=start_col,
                    end_col=start_col,
                    start_row=row_index + 1,
                    end_row=row_index + 4,
                )

                matches: List[str] = [value for value in values if value is not None]

                if len(matches) == 0:
                    break
                elif elements[-1].parts[-1].screws[-1].steps is not None \
                        and len(elements[-1].parts[-1].screws[-1].steps) > 0:
                    step = self.get_tightening_specification_step(start_col, row_index)

                    if step.name is not None or step.tightening_specification is not None:
                        if elements[-1].parts[-1].screws[-1].steps is None:
                            elements[-1].parts[-1].screws[-1].steps = list()
                        elements[-1].parts[-1].screws[-1].steps.append(step)

                    row_index += 1
                    continue
                else:
                    row_index += 1
                    continue

            if cell.font.b and cell.alignment.horizontal == "right":
                elements.append(
                    self.get_specification_element(start_col, row_index)
                )

            elif cell.font.b and cell.alignment.horizontal == "center":
                if elements[-1].parts is None:
                    elements[-1].parts = list()

                elements[-1].parts.append(
                    self.get_element_part(start_col, row_index)
                )

            elif cell.alignment.horizontal in ["left", "general", None]:
                if elements[-1].parts[-1].screws is None:
                    elements[-1].parts[-1].screws = list()

                elements[-1].parts[-1].screws.append(
                    self.get_screw(start_col, row_index)
                )

            elif cell.alignment.horizontal == "right":
                if elements[-1].parts[-1].screws[-1].steps is None:
                    elements[-1].parts[-1].screws[-1].steps = list()

                elements[-1].parts[-1].screws[-1].steps.append(
                    self.get_tightening_specification_step(start_col, row_index)
                )

            row_index += 1

        return elements

    def get_specification_element(
            self,
            col: int,
            row: int
    ) -> SpecificationElement:
        return SpecificationElement(
            name=self.sheet_reader.read_cell_value(col, row)
        )

    def get_element_part(
            self,
            col: int,
            row: int
    ) -> ElementPart:
        return ElementPart(
            name=self.sheet_reader.read_cell_value(col, row)
        )

    def get_screw(
            self,
            col: int,
            row: int
    ) -> Screw:
        values: List[str] = self.sheet_reader.read_cells_values(
            col,
            col + 1,
            row,
            row
        )

        tightening_torque: str = values[1]

        detail: Optional[str] = None
        if tightening_torque is not None and tightening_torque.endswith("*"):
            detail = self.sheet_reader.read_cell_value(col, row + 1)

        return Screw(
            name=values[0],
            tightening_specification=tightening_torque,
            detail=detail,
        )

    def get_tightening_specification_step(
            self,
            col: int,
            row: int
    ) -> TighteningSpecificationStep:
        values: List[str] = self.sheet_reader.read_cells_values(col, col + 1, row, row)

        return TighteningSpecificationStep(
            name=values[0],
            tightening_specification=values[1],
        )
