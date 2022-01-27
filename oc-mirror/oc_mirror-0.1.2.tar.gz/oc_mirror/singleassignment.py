#!/usr/bin/env python

"""Wrapper class to warn on double assignments."""

import logging

LOGGER = logging.getLogger(__name__)


class SingleAssignment:
    """Object that warns if a value is assigned twice."""

    def __init__(self, name):
        setattr(self, "__name", name)
        setattr(self, "__assigned", False)
        setattr(self, "__initialized", True)

    def __setattr__(self, name, value):
        if getattr(self, "__initialized", False):
            __name = getattr(self, "__name")
            if name == __name:
                if getattr(self, "__assigned", False):
                    LOGGER.warning("Overriding previously value of %s!", __name)
                else:
                    setattr(self, "__assigned", True)
        self.__dict__[name] = value

    def get(self):
        """
        Wrapper to allow retrieval without providing the attribute name.

        Returns:
            The value of the wrapped attribute.
        """
        name = getattr(self, "__name")
        return getattr(self, name, None)

    def set(self, value):
        """
        Wrapper to allow assignment without providing the attribute name.

        Args:
            value: The value to be assigned to the wrapped attribute.
        """
        name = getattr(self, "__name")
        setattr(self, name, value)
