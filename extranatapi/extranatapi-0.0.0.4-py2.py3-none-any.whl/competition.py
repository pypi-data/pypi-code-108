# -*- coding: utf-8 -*-
"""Competition."""

import sys

from .base import ExtranatObject, ExtranatObjectCollection
from .nageur import Nageur


class Competition(ExtranatObject):
    """CLASS : Competition."""

    def __init__(self, club=None, competition_id=None, name=None):
        """Constructor."""
        self.__id__ = competition_id
        self.__name__ = name
        self.__club__ = club
        self.__date__ = None
        self.nageurs = ExtranatObjectCollection(Nageur())

    @property
    def idcpt(self):
        """Get id competition."""
        return self.convertstr(self.__id__)

    @property
    def name(self):
        """Get name."""
        return self.convertstr(self.__name__)

    @property
    def idclub(self):
        """Get id club."""
        return self.convertstr(self.__club__)

    @property
    def date(self):
        """Get date."""
        return self.convertstr(self.__date__)

    @property
    def keyname(self):
        """Get keyname."""
        return 'competition'

    @property
    def shortdate(self):
        """Get date in short format."""
        result = self.date

        end1 = self.date.rfind('/')
        if end1 >= 0:
            tmp = self.date[:end1]
            end2 = tmp.rfind('/')
            if end2 >= 0:
                result = self.date[end2 + 1:]

        return result

    def __str__(self):
        """To string."""
        result = f'{self.__date__} - {self.__name__}\n'

        for item in self.nageurs:
            result += str(item) + "\n"

        return result

    def to_json_data(self):
        """To json data."""
        return {'idcpt': self.__id__, 'name': self.__name__, 'date': self.__date__, 'nageurs': self.nageurs.to_json_data()}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        name = self.name
        idcpt = self.idcpt
        shortdate = self.shortdate
        date = self.date

        output.write(f'{idcpt:8}{shortdate:10}{name} / {date}')

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        name = 'competition'
        idcpt = 'id'
        date = 'date'

        output.write(f'{idcpt:8}{date:10}{name}')

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.date,
            self.name]

        if len(self.nageurs) > 0:
            return self.nageurs.to_array(startarray=startarray + data)

        return startarray + data

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            "competitiondate",
            "competitionname"]

        return self.nageurs.to_array_header(startarray=startarray + data)
