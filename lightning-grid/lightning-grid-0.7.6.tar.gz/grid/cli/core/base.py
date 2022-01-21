import re

from grid.cli.client import Grid


class GridObject:
    """
    Base object. Inherited by all user-facing object; providing
    common methods and the Grid client instance.
    """
    def __init__(self):
        self._data = None
        self.client = Grid()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._update_meta()

    def _update_meta(self) -> None:
        """Updates object attributes with metadata from backend."""
        if not self._data:
            return

        for k, v in self._data.items():
            setattr(self, self._camel_case_to_snake_case(k), v)

    def refresh(self):  # pragma: no cover
        """
        Refreshes object metadata. This makes a query to Grid to fetch the
        object's latest data.
        """
        raise NotImplementedError

    @staticmethod
    def _camel_case_to_snake_case(data: str) -> str:
        """
        Original implementation from:

            * https://www.geeksforgeeks.org/python-program-to-convert-camel-case-string-to-snake-case/
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', data)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
