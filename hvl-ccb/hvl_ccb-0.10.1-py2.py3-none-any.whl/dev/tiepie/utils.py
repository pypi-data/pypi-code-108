#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""

"""
import logging

from aenum import Enum

logger = logging.getLogger(__name__)


class PublicPropertiesReprMixin:
    """General purpose utility mixin that overwrites object representation to a one
    analogous to `dataclass` instances, but using public properties and their values
    instead of `fields`.
    """

    def _public_properties_gen(self):
        """
        Generator that returns instance's properties names and their values,
        for properties that do not start with `"_"`

        :return: attribute name and value tuples
        """
        for name in dir(self):
            if (
                not (name.startswith("_") or name.startswith("clean"))
                and isinstance(getattr(self, name), (int, float, str, Enum))
            ):
                yield name, getattr(self, name)

    def __repr__(self):
        attrs = ", ".join(
            [f"{name}={value!r}" for name, value in self._public_properties_gen()]
        )
        return f"{self.__class__.__qualname__}({attrs})"
