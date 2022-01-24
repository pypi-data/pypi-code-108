from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TypeVar


@dataclass
class WithParent:
    parentName: Optional[str] = None
    parentId: Optional[int] = None

    T = TypeVar("T", bound="WithParent")

    def with_parent_id(self: T, parent_id: int) -> T:
        """

        :param parent_id:
        :return: iself
        """
        self.parentName = None
        self.parentId = parent_id
        return self

    def with_parent_name(self: T, parent_name: str) -> T:
        """

        :param parent_name:
        :return: iself
        """
        self.parentName = parent_name
        self.parentId = None
        return self
