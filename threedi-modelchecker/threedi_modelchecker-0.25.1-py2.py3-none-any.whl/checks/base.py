from abc import ABC
from abc import abstractmethod
from enum import IntEnum
from geoalchemy2 import functions as geo_func
from geoalchemy2.types import Geometry
from pathlib import Path
from sqlalchemy import and_
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import types
from sqlalchemy.orm.session import Session
from typing import List
from typing import NamedTuple


class CheckLevel(IntEnum):
    ERROR = 40
    WARNING = 30
    INFO = 20

    @classmethod
    def get(cls, value):
        """Get a CheckLevel from a CheckLevel, str or int."""
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls[value.upper()]
        else:
            return cls(value)


class BaseCheck(ABC):
    """Base class for all checks.

    A Check defines a constraint on a specific column and its table.
    One can validate if the constrain holds using the method `get_invalid()`.
    This method will return a list of rows (as named_tuples) which are invalid.
    """

    def __init__(
        self,
        column,
        filters=None,
        level=CheckLevel.ERROR,
        error_code=0,
    ):
        self.column = column
        self.table = column.table
        self.filters = filters
        self.error_code = int(error_code)
        self.level = CheckLevel.get(level)

    @abstractmethod
    def get_invalid(self, session: Session) -> List[NamedTuple]:
        """Return a list of rows (named_tuples) which are invalid.

        What is invalid is defined in the check. Returns an empty list if no
        invalid rows are present.

        :param session: sqlalchemy.orm.session.Session
        :return: list of named_tuples or empty list if there are no invalid
            rows
        """
        pass

    def get_valid(self, session: Session) -> List[NamedTuple]:
        """Return a list of rows (named_tuples) which are valid.

        :param session: sqlalchemy.orm.session.Session
        :return: list of named_tuples or empty list if there are no valid rows
        """
        all_rows = self.to_check(session)
        invalid_row_ids = set([row.id for row in self.get_invalid(session)])
        valid = []
        for row in all_rows:
            if row.id not in invalid_row_ids:
                valid.append(row)
        return valid

    def to_check(self, session):
        """Return a Query object filtering on the rows this check is applied.

        :param session: sqlalchemy.orm.session.Session
        :return: sqlalchemy.Query
        """
        query = session.query(self.table)
        if self.filters is not None:
            query = query.filter(self.filters)
        return query

    @property
    def column_name(self) -> str:
        return f"{self.table.name}.{self.column.name}"

    def description(self) -> str:
        """Return a string explaining why rows are invalid according to this
        check.

        :return: string
        """
        return "Invalid value in column '%s'" % self.column_name

    def __repr__(self) -> str:
        return "<%s: %s>" % (self.__class__.__name__, self.column_name)


class QueryCheck(BaseCheck):
    """Specify a sqlalchemy.orm.Query object to return invalid instances"""

    def __init__(
        self,
        column,
        invalid,
        message,
        filters=None,
        level=CheckLevel.ERROR,
        error_code=0,
    ):
        super().__init__(column, level=level, error_code=error_code)
        self.invalid = invalid
        self.message = message
        self.filters = filters

    def get_invalid(self, session):
        query = self.invalid.with_session(session)
        if self.filters is not None:
            query = query.filter(self.filters)
        return query.all()

    def description(self):
        return self.message


class ForeignKeyCheck(BaseCheck):
    """Check all values in `column` are in `reference_column`.

    Null values are ignored."""

    def __init__(self, reference_column, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_column = reference_column

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_foreign_keys_query = q_invalid.filter(
            self.column.notin_(session.query(self.reference_column)),
            self.column != None,
        )
        return invalid_foreign_keys_query.all()

    def description(self):
        return "%s refers to a non-existing %s" % (
            self.column_name,
            self.reference_column.table,
        )


class UniqueCheck(BaseCheck):
    """Check all values in `column` are unique

    Null values are ignored."""

    def get_invalid(self, session):
        duplicate_values = (
            session.query(self.column)
            .group_by(self.column)
            .having(func.count(self.column) > 1)
        )
        q_invalid = self.to_check(session)
        invalid_uniques_query = q_invalid.filter(self.column.in_(duplicate_values))
        return invalid_uniques_query.all()

    def description(self):
        return f"{self.column_name} should to be unique"


class NotNullCheck(BaseCheck):
    """ "Check all values in `column` that are not null"""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        not_null_query = q_invalid.filter(self.column == None)
        return not_null_query.all()

    def description(self):
        return f"{self.column_name} cannot be null"


class TypeCheck(BaseCheck):
    """Check all values in `column` that are of the column defined type.

    Null values are ignored."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_types = _sqlalchemy_to_sqlite_types(self.column.type)

    def get_invalid(self, session):
        if "sqlite" not in session.bind.dialect.dialect_description:
            return []
        q_invalid = self.to_check(session)
        invalid_type_query = q_invalid.filter(
            func.typeof(self.column).notin_(self.expected_types),
            func.typeof(self.column) != "null",
        )
        return invalid_type_query.all()

    def description(self):
        return f"{self.column_name} is not of type {self.expected_types}"


def _sqlalchemy_to_sqlite_types(column_type):
    """Convert the sqlalchemy column type to allowed sqlite data types

    Returns the value similar as the sqlite 'typeof' function.
    Raises TypeError if the column type is unknown.
    See https://www.sqlite.org/datatype3.html

    :param column_type: sqlalchemy.column
    :return: (str)
    """
    if isinstance(column_type, types.TypeDecorator):
        column_type = column_type.impl

    if isinstance(column_type, types.String):
        return ["text"]
    elif isinstance(column_type, (types.Float, types.Numeric)):
        return ["integer", "numeric", "real"]
    elif isinstance(column_type, types.Integer):
        return ["integer"]
    elif isinstance(column_type, types.Boolean):
        return ["integer"]
    elif isinstance(column_type, types.Date):
        return ["text"]
    elif isinstance(column_type, Geometry):
        return ["blob"]
    elif isinstance(column_type, types.TIMESTAMP):
        return ["text"]
    else:
        raise TypeError("Unknown column type: %s" % column_type)


class GeometryCheck(BaseCheck):
    """Check all values in `column` are a valid geometry.

    Null values are ignored."""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_geometries = q_invalid.filter(
            geo_func.ST_IsValid(self.column) != True, self.column != None
        )
        return invalid_geometries.all()

    def description(self):
        return f"{self.column_name} is an invalid geometry"


class GeometryTypeCheck(BaseCheck):
    """Check all values in `column` are of geometry type in defined in
    `column`.

    Null values are ignored"""

    def get_invalid(self, session):
        expected_geometry_type = _get_geometry_type(
            self.column, dialect=session.bind.dialect.name
        )
        q_invalid = self.to_check(session)
        if expected_geometry_type is None:
            # skip in case of generic GEOMETRY column
            return q_invalid.filter(false())
        invalid_geometry_types_q = q_invalid.filter(
            geo_func.ST_GeometryType(self.column) != expected_geometry_type,
            self.column != None,
        )
        return invalid_geometry_types_q.all()

    def description(self):
        return "%s has invalid geometry type, expected %s" % (
            self.column_name,
            self.column.type.geometry_type,
        )


def _get_geometry_type(column, dialect):
    if column.type.geometry_type == "GEOMETRY":
        return  # should skip the check
    if dialect == "sqlite":
        return column.type.geometry_type
    elif dialect == "postgresql":
        geom_type = column.type.geometry_type.capitalize()
        return "ST_%s" % geom_type
    else:
        raise TypeError("Unexpected dialect %s" % dialect)


class EnumCheck(BaseCheck):
    """Check all values in `column` are within the defined Enum values of
    `column`.

    Unexpected values are values not defined by its enum_class.

    Null values are ignored"""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_values_q = q_invalid.filter(
            self.column.notin_(list(self.column.type.enum_class))
        )
        return invalid_values_q.all()

    def description(self):
        allowed = {x.value for x in self.column.type.enum_class}
        return f"{self.column_name} is not one of {allowed}"


class RangeCheck(BaseCheck):
    """Check to if all values are within range [min_value, max_value]

    Use left_inclusive and right_inclusive to specify whether the min/max values
    themselves should be considered valid. By default they are both considered
    valid.
    """

    def __init__(
        self,
        min_value=None,
        max_value=None,
        left_inclusive=True,
        right_inclusive=True,
        message=None,
        *args,
        **kwargs,
    ):
        if min_value is None and max_value is None:
            raise ValueError("Please supply at least one of {min_value, max_value}.")
        self.min_value = min_value
        self.max_value = max_value
        self.left_inclusive = left_inclusive
        self.right_inclusive = right_inclusive
        self.message = message
        super().__init__(*args, **kwargs)

    def get_invalid(self, session):
        conditions = []
        if self.min_value is not None:
            if self.left_inclusive:
                conditions.append(self.column >= self.min_value)
            else:
                conditions.append(self.column > self.min_value)
        if self.max_value is not None:
            if self.right_inclusive:
                conditions.append(self.column <= self.max_value)
            else:
                conditions.append(self.column < self.max_value)
        return self.to_check(session).filter(~and_(*conditions)).all()

    def description(self):
        if self.message:
            return self.message
        if self.min_value is None:
            msg = f"is not less than{' or equal to' if self.right_inclusive else ''} {self.max_value}"
        elif self.max_value is None:
            msg = f"is not greater than{' or equal to' if self.left_inclusive else ''} {self.min_value}"
        else:
            # no room for 'left_inclusive' / 'right_inclusive' info
            msg = f"is not between {self.min_value} and {self.max_value}"
        return f"{self.column_name} {msg}"


class FileExistsCheck(BaseCheck):
    """Check whether a file referenced in given Column exists.

    In order to perform this check, the SQLAlchemy session requires a
    `model_checker_context` attribute, which is set automatically by the
    ThreediModelChecker and contains either `available_rasters` or `base_path`.

    If it contains `available_rasters`, non-empty file fields are checked
    against this list. If a field contains a filename and does not occur in
    the list, the field is invalid.

    Else, if it contains `base_path`, the file fields are checked in the local
    filesystem. Paths are interpreted relative to `base_path`. The `base_path`
    is set automatically by ThreediModelChecker if a spatialite is used.

    If the context does not exist, the checker is skipped.
    """

    def to_check(self, session):
        return (
            super()
            .to_check(session)
            .filter(
                self.column != None,
                self.column != "",
            )
        )

    def none(self, session):
        return self.to_check(session).filter(false()).all()  # empty query

    def get_invalid(self, session):
        context = getattr(session, "model_checker_context", None)
        available_rasters = getattr(context, "available_rasters", None)
        if available_rasters is not None and self.to_check(session).count() > 0:
            if self.column.name in available_rasters:
                # the raster is available (so says the context)
                return self.none(session)
            else:
                # the raster is not available (so says the context)
                return self.to_check(session).all()

        base_path = getattr(context, "base_path", None)
        if not base_path:
            # cannot check if there is no path: skip the check
            return self.none(session)

        invalid = []
        for record in self.to_check(session).all():
            path = getattr(record, self.column.name)
            if not Path(base_path / path).exists():
                invalid.append(path)

        return self.to_check(session).filter(self.column.in_(invalid)).all()

    def description(self):
        return f"The file in {self.column_name} is not present"
