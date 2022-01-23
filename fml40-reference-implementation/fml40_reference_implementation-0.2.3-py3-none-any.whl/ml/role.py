"""This module implements the role class according to Forest Modeling Language 4.0."""

import inspect
import sys
from abc import ABC

from ml.identifier import ID


class Role(ABC):
    """Each Role class manages a role which can be assigned to things."""

    def __init__(self, namespace, name="", identifier="", parent=None):
        """Constructs a new Role class object with the given name and
        identifier.

        :param name: Name of the feature
        :param identifier: Identifier of the feature
        """
        self.parent = parent
        self.__identifier = identifier
        self.__name = name
        if name == "":
            self.__name = self.__class__.__name__
        self.__class_name = f"{namespace}::{self.__class__.__name__}"
        self.__json_out = {}

    @property
    def class_name(self):
        """Adds the prefix ml40:: to the class name and returns it.

        :returns: class name of the object
        :rtype: str
        """
        return self.__class_name

    @property
    def name(self):
        """Returns the object's name.

        :returns: Name of the object
        :rtype: str

        """

        return self.__name

    @name.setter
    def name(self, value):
        """Sets __name to value.

        :param value: New name

        """

        self.__name = value

    @property
    def identifier(self):
        """Returns the role's local identifier.

        :returns: Identifier
        :rtype: str

        """

        return self.__identifier

    @identifier.setter
    def identifier(self, value):
        """Builds an ID object from value and assigns the resulting identifier
        to __identifier.

        :param value: Proposal of the identifier
        """

        self.__identifier = value

    def to_json(self):
        """Returns a JSON representation of this role."""

        self.__json_out = {"class": self.__class_name, "name": self.__name}
        if self.identifier:
            self.__json_out["identifier"] = self.identifier
        return self.__json_out

    def set_parent(self, value):
        self.parent = value
