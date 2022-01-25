import functools
import re
from typing import List, Optional


class Column:
    def __init__(self, index: int, name: Optional[str], values: List):
        """
        :param index: index of the column in the original table
        :param name: name of the column, None mean the column doesn't have any name (different from having empty name)
        :param values: values in each row
        """
        self.index = index
        self.name = name
        self.values = values

    @functools.cached_property
    def clean_name(self) -> Optional[str]:
        """Clean the name that may contain many unncessary spaces"""
        if self.name is None:
            return None
        return re.sub(r"\s+", " ", self.name).strip()

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, key, value):
        self.values[key] = value
