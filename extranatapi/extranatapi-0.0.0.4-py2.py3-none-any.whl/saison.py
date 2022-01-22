# -*- coding: utf-8 -*-
"""Saison."""

import sys

from .base import ExtranatObject, ExtranatObjectCollection
from .competition import Competition


class Saison(ExtranatObject):
    """CLASS : Saison."""

    def __init__(self, idclub, saison):
        """Constructor."""
        self.__saison__ = saison
        self.__club__ = idclub
        self.__competitions__ = ExtranatObjectCollection(Competition())

    @property
    def keyname(self):
        """Get keyname."""
        return 'saison'

    @property
    def saison(self):
        """Get saison."""
        return self.convertstr(self.__saison__)

    @property
    def idclub(self):
        """Get id club."""
        return self.convertstr(self.__club__)

    def __str__(self):
        """To string."""
        result = f"Saison: {self.saison}\n"

        return result + self.__competitions__.__str__()

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.saison]

        return self.__competitions__.to_array(startarray=startarray + data)

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            "saison"]

        return self.__competitions__.to_array_header(startarray=startarray + data)

    def to_json_data(self):
        """To json data."""
        return {'saison': self.saison, 'competitions': self.__competitions__.to_json_data()}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        return self.__competitions__.to_stdcolumn(output=output)

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        return Competition.to_stdcolumn_header(output=output)
