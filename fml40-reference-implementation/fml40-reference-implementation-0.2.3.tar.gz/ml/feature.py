"""This module implements the Feature class according to the Forest
Modeling Language 4.0."""

import inspect
import os
import sys
from abc import ABC

from ml.identifier import ID
from ml.thing import Thing


class Feature(ABC):
    """The Feature class represents the base class for all functionalities
    and values."""

    def __init__(self, namespace, name="", identifier="", parent=None):
        """Constructs a new Feature class object with the given name and
        identifier.

        :param name: Name of the feature
        :param identifier: Identifier of the feature
        """
        self.parent = parent
        self.namespace = namespace
        self.__name = name
        self.__class_name = f"{self.namespace}::{self.__class__.__name__}"

        self.__identifier = identifier
        self.__subFeatures = dict()
        self.__json_out = dict()

    @property
    def class_name(self):
        """Adds the prefix ml40:: to the class name and returns it.

        :returns: Name of this object's class
        :rtype: str

        """

        return self.__class_name

    @class_name.setter
    def class_name(self, value):
        """Sets __class_name to value.

        :param value: New class name
        :type value: str

        """
        # !!! What about the namespace?
        # ??? Do we really need to have this function?
        # Can't this be done implicitly?
        self.__class_name = value

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
        :type value: str

        """

        self.__name = value

    @property
    def identifier(self):
        """Returns the feature's local identifier.

        :returns: Identifier
        :rtype: str

        """

        return self.__identifier

    @identifier.setter
    def identifier(self, value):
        """Builds an ID object from value and assigns the resulting identifier
        to __identifier.

        :param value: Proposal of the identifier
        :type value: str
        """

        self.__identifier = value

    @property
    def subFeatures(self):
        """Returns a dict containing all subordinate features.

        :returns: All subordinate features.
        :rtype: dict[<str>, <Feature>]

        """

        return self.__subFeatures

    @subFeatures.setter
    def subFeatures(self, value):
        """Replaces __subFeatures with value.

        :param value: New collection of subordinate features

        """

        # !!! Do we really want this? Better add and remove functions.
        self.__subFeatures = value

    @property
    def json_out(self):
        return self.__json_out

    def to_json(self):
        """Returns a JSON representation of this feature. Note that this
        function works recursively.

        :returns: Json representation
        :rtype: str

        """

        self.__json_out["class"] = self.__class_name

        if self.identifier:
            self.__json_out["identifier"] = self.identifier
        if self.name:
            self.__json_out["name"] = self.name
        if self.subFeatures:
            self.__json_out["subFeatures"] = []
        for key in self.subFeatures.keys():
            res = self.subFeatures[key].to_json()
            self.__json_out["subFeatures"].append(res)
        return self.__json_out

    def get_my_thing(self):
        tmp = self.parent
        print("Searching for thing....")
        print(type(tmp))
        while not isinstance(tmp, Thing):
            if tmp is None:
                return None
            tmp = tmp.parent
        return tmp
