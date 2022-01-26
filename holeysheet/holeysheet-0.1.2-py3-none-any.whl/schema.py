from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, constr

Cell = constr(regex=r"[A-Z]+\d+")


class Literal(BaseModel):
    name: str
    value: Optional[Any]
    cell: Optional[Cell]


class Range(BaseModel):
    start: Cell
    end: Cell
    type: Optional[str]

    def __str__(self):
        return f"{self.start}:{self.end}"


class NamedRange(Range):
    name: str


class Header(BaseModel):
    column: Optional[str]
    row: Optional[int]


class Region(BaseModel):
    literals: Optional[List[Literal]]
    range: Optional[Range]
    header: Optional[Header]
    sheet: Optional[str]
    regions: Optional[List[Region]]

    def flatten(self) -> List[Region]:
        """
        Flatten the current region to a list of regions.
        :return:
        """
        return self._flatten(region=self)

    def _flatten(self, region, total_region: Optional[Region] = None) -> List[Region]:
        total_region = self._amend_total_region(
            total_region=total_region, region=region
        )
        if not region.regions or len(region.regions) == 0:
            if total_region:
                return [total_region]
        all_regions = []
        for sub_region in region.regions:
            all_regions.extend(
                self._flatten(region=sub_region, total_region=total_region)
            )
        return all_regions

    @staticmethod
    def _amend_total_region(total_region: Optional[Region], region: Region) -> Region:
        if total_region is None:
            return Region(
                literals=region.literals,
                header=region.header,
                sheet=region.sheet,
                range=region.range,
            )
        literals = total_region.literals + region.literals
        header = total_region.header or Header()
        range = total_region.range or region.range
        if region.header and region.header.column:
            header.column = region.header.column
        if region.header and region.header.row:
            header.row = region.header.row
        sheet = total_region.sheet or region.sheet
        return Region(literals=literals, header=header, sheet=sheet, range=range)


class Config(BaseModel):
    regions: List[Region]

    def flatten_regions(self):
        regions = []
        for region in self.regions:
            regions.extend(region.flatten())
        return regions


Region.update_forward_refs()
