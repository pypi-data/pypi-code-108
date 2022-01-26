from ..threedi_model import models
from .base import BaseCheck
from sqlalchemy.orm import Query


class CrossSectionBaseCheck(BaseCheck):
    """Base class for all cross section definition checks."""

    def __init__(self, column, *args, **kwargs):
        self.shapes = kwargs.pop("shapes", None)
        super().__init__(column, *args, **kwargs)

    @property
    def shape_msg(self):
        return {x.value for x in self.shapes}

    def to_check(self, session):
        qs = super().to_check(session)
        if self.shapes is not None:
            qs = qs.filter(models.CrossSectionDefinition.shape.in_(self.shapes))
        return qs.filter(
            models.CrossSectionDefinition.id.in_(
                Query(models.CrossSectionLocation.definition_id).union_all(
                    Query(models.Pipe.cross_section_definition_id),
                    Query(models.Culvert.cross_section_definition_id),
                    Query(models.Weir.cross_section_definition_id),
                    Query(models.Orifice.cross_section_definition_id),
                )
            )
        )


class CrossSectionNullCheck(CrossSectionBaseCheck):
    """Check if width / height is not NULL or empty"""

    def get_invalid(self, session):
        return (
            self.to_check(session)
            .filter((self.column == None) | (self.column == ""))
            .all()
        )

    def description(self):
        return f"{self.column_name} cannot be null or empty"


class CrossSectionFloatCheck(CrossSectionBaseCheck):
    """Check that width / height is a valid non-negative float"""

    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (self.column != None) & (self.column != "")
        ):
            try:
                value = float(getattr(record, self.column.name))
            except ValueError:
                invalids.append(record)
            else:
                if value < 0:
                    invalids.append(record)

        return invalids

    def description(self):
        return f"{self.column_name} should be a positive number for shapes {self.shape_msg}"


class CrossSectionNonZeroCheck(CrossSectionBaseCheck):
    """Check that width / height is larger than >0"""

    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (self.column != None) & (self.column != "")
        ):
            try:
                value = float(getattr(record, self.column.name))
            except ValueError:
                continue

            if value == 0:
                invalids.append(record)
        return invalids

    def description(self):
        return f"{self.column_name} should be nonzero for shapes {self.shape_msg}"


class CrossSectionFloatListCheck(CrossSectionBaseCheck):
    """Tabulated definitions should use a space for separating the floats."""

    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (self.column != None) & (self.column != "")
        ):
            try:
                [float(x) for x in getattr(record, self.column.name).split(" ")]
            except ValueError:
                invalids.append(record)

        return invalids

    def description(self):
        return f"{self.column_name} should contain a space separated list of numbers for shapes {self.shape_msg}"


class CrossSectionEqualElementsCheck(CrossSectionBaseCheck):
    """Tabulated definitions should have equal numbers of width and height elements."""

    def __init__(self, *args, **kwargs):
        super().__init__(column=models.CrossSectionDefinition.width, *args, **kwargs)

    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (models.CrossSectionDefinition.width != None)
            & (models.CrossSectionDefinition.width != "")
            & (models.CrossSectionDefinition.height != None)
            & (models.CrossSectionDefinition.height != "")
        ):
            try:
                widths = [float(x) for x in record.width.split(" ")]
                heights = [float(x) for x in record.height.split(" ")]
            except ValueError:
                continue  # other check catches this

            if len(widths) != len(heights):
                invalids.append(record)

        return invalids

    def description(self):
        return f"{self.table.name} width and height should an equal number of elements for shapes {self.shape_msg}"


class CrossSectionIncreasingCheck(CrossSectionBaseCheck):
    """Tabulated definitions should have an increasing list of heights."""

    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (self.column != None) & (self.column != "")
        ):
            try:
                values = [
                    float(x) for x in getattr(record, self.column.name).split(" ")
                ]
            except ValueError:
                continue  # other check catches this

            if len(values) > 1 and any(
                x > y for (x, y) in zip(values[:-1], values[1:])
            ):
                invalids.append(record)

        return invalids

    def description(self):
        return f"{self.column_name} should be monotonically increasing for shapes {self.shape_msg}. Maybe the width and height have been interchanged?"


class CrossSectionFirstElementNonZeroCheck(CrossSectionBaseCheck):
    """Tabulated definitions should have an increasing list of heights."""

    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (self.column != None) & (self.column != "")
        ):
            try:
                values = [
                    float(x) for x in getattr(record, self.column.name).split(" ")
                ]
            except ValueError:
                continue  # other check catches this

            if abs(values[0]) <= 0:
                invalids.append(record)

        return invalids

    def description(self):
        return f"The first element of {self.column_name} should be larger than 0 for shapes {self.shape_msg}. Zero as first value may lead to numerical issues."
