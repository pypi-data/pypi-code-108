from fnmatch import fnmatch
from typing import Any, List

from sqlalchemy.schema import SchemaItem


class IgnoreTables:
    """
    Ignore tables from migration.

        AlembicEnvPy(
            include_object=IgnoreTables(["ignore_*", "*_ignored"]),
        )

    """

    def __init__(self, ignore_tables: List[str]) -> None:
        self._ignore_tables = ignore_tables or []

    def _include_object(
        self,
        object: SchemaItem,
        name: str,
        type_: str,
        reflected: bool,
        compare_to: Any,
    ):
        """
        Should you include this table or not?
        https://stackoverflow.com/questions/65184035/alembic-ignore-specific-tables
        """
        if object.info.get("skip_autogenerate", False):
            return False
        if type_ == "table":
            if any(fnmatch(name, p) for p in self._ignore_tables):
                return False
        return True

    __call__ = _include_object
