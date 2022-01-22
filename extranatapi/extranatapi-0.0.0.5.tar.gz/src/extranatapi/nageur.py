# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-public-methods
"""Nageur."""
import datetime
import re
import sys


from .base import ExtranatObject, ExtranatObjectCollection
from .tools import Tools


class Nage(ExtranatObject):
    """CLASS : Nage."""

    def __init__(self, name='', classement='', temps='', points=None, bassin=None):
        """Constructor."""
        self.__name__ = name
        self.__temps__ = temps
        self.__classement__ = classement
        self.__points__ = points
        self.__bassin__ = bassin

    @property
    def name(self):
        """Get name."""
        return self.convertstr(self.__name__)

    @property
    def temps(self):
        """Get temps."""
        return self.convertstr(self.__temps__)

    @property
    def classement(self):
        """Get classement."""
        return self.convertstr(self.__classement__)

    @property
    def bassin(self):
        """Get bassin."""
        return self.convertstr(self.__bassin__)

    @property
    def points(self):
        """Get points."""
        return self.convertstr(self.__points__)

    @property
    def points_i(self):
        """Get point, format integer."""
        return self.__points__

    @property
    def keyname(self):
        """Get keyname."""
        return 'nage'

    def __str__(self):
        """To string."""
        name = self.name + ' :'
        return f'{name:35} {self.temps} ({self.classement}) {self.points}'

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.bassin,
            self.name,
            self.temps,
            self.classement,
            self.points]

        return startarray + data

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            "bassin",
            "nage",
            "temps",
            "classement",
            "points"]

        return startarray + data

    def to_json_data(self):
        """To json data."""
        return {'name': self.name, 'temps': self.temps, 'classement': self.classement}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        name = self.name
        temps = self.temps
        classement = self.classement
        points = self.points
        bassin = self.bassin

        output.write(f'{bassin:8}{name:10}{classement:6}{temps:10}{points}')

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        name = 'nage'
        temps = 'temps'
        classement = 'pos.'
        points = 'points'
        bassin = 'bassin'

        output.write(f'{bassin:8}{name:10}{classement:6}{temps:10}{points}')

    def cotation(self, nageur, cotation, coeff_enable=True):
        """Cotation."""
        tps = self.temps

        # 00:40.91
        index1 = tps.find(':')
        index2 = tps.find('.')
        if index1 > 0:
            if index2 > 0:
                tps2 = tps[index1 + 1:].replace('.', '')
                tps = tps[:index1] + '.' + tps2
            else:
                return

        self.__points__ = cotation.get_cotation_nageur(nageur=nageur, nage=self.name, temps=tps, coeff_enable=coeff_enable)

        return


class Nageur(ExtranatObject):
    """CLASS : nageur."""

    def __init__(self, iuf=None, name='', sexe=None, yearofbirth=None, age=None, nationality=None):
        """Constructor."""
        self.__name__ = name
        self.__number__ = 0
        if yearofbirth is None:
            self.__yearofbirth__ = None
        else:
            self.__yearofbirth__ = int(yearofbirth)
        if age is None:
            self.__age__ = None
        else:
            self.__age__ = int(age)
        self.__iuf__ = iuf
        self.__nationality__ = nationality
        self.__sexe__ = sexe
        self.__category_age__ = None
        self.__nages__ = ExtranatObjectCollection(Nage())

    @property
    def keyname(self):
        """Get keyname."""
        return 'nageur'

    @property
    def name(self):
        """Get name."""
        return self.convertstr(self.__name__)

    @property
    def sexe(self):
        """Get sexe."""
        return self.convertstr(self.__sexe__)

    @property
    def yearofbirth(self):
        """Get year of birth."""
        return self.convertstr(self.__yearofbirth__)

    @property
    def age(self):
        """Get age."""
        if self.__age__ is None and self.__yearofbirth__ is not None:
            year = datetime.datetime.now().year
            self.__age__ = year - int(self.__yearofbirth__)

        return self.convertstr(self.__age__)

    @property
    def iuf(self):
        """Get iuf."""
        return self.convertstr(self.__iuf__)

    @property
    def nationality(self):
        """Get nationality."""
        return self.convertstr(self.__nationality__)

    @property
    def nages(self):
        """Get nages."""
        return self.__nages__

    @property
    def category_age(self):
        """Get category age."""
        if self.__category_age__ is None:
            self.__category_age__ = Tools.age_to_category(self.age)

        return self.convertstr(self.__category_age__)

    def setname(self, name, number=None):
        """Set name."""
        self.__name__ = name

        if number is not None:
            self.__number__ = number

    def setnamewithinfo(self, namewithinfo):
        """Set name with infos.

        ex: 1. NAME FirstName (Year/age ans)  FRA [xxxxx]
        """
        info = namewithinfo.split(".")

        if len(info) > 1:
            self.__number__ = info[0]
            result_re = re.search(r'(.*)\((\d+)/(\d+) ans\)\s*(.*)\s*\[(\d+)\]', info[1])
            if result_re:
                self.__name__ = result_re.group(1).strip()
                self.__yearofbirth__ = result_re.group(2)
                self.__age__ = result_re.group(3)
                self.__nationality__ = result_re.group(4).strip()
                self.__iuf__ = result_re.group(5)
            else:
                self.__name__ = info[1]
        elif len(info) == 1:
            result_re = re.search(r'(.*)\((\d+)\)\s*(.*)\s*\[(\d+)\]', info[0])
            if result_re:
                self.__name__ = result_re.group(1).strip()
                self.__yearofbirth__ = result_re.group(2)
                self.__nationality__ = result_re.group(3).strip()
                self.__iuf__ = result_re.group(4)
            else:
                self.__name__ = info[0]
        else:
            self.__name__ = info[0]

    def addnage(self, nage, classement='', temps='', points=None, bassin=None):
        """Add nage."""
        nage = Tools.convertnage(nage)
        self.__nages__.append(Nage(name=nage, classement=classement, temps=temps, points=points, bassin=bassin))

    def __str__(self):
        """To string."""
        result = f'{self.__number__} - {self.__name__}\n'

        for item in self.__nages__:
            result += "- " + item.__str__() + "\n"

        return result

    def has_nage(self, nage):
        """Has nage."""

        for item in self.__nages__:
            if nage == item.name:
                return True

        return False

    def get_nage(self, nage):
        """Has nage."""

        for item in self.__nages__:
            if nage == item.name:
                return item

        return None

    def get_list_nages_name(self):
        """Get list nages name."""
        result = []

        for item in self.__nages__:
            result += [item.name]

        return result

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.name,
            self.yearofbirth,
            self.age,
            self.nationality,
            self.iuf,
            self.sexe]

        return self.__nages__.to_array(startarray=startarray + data)

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            'nageur',
            'annee',
            'age',
            'nationalite',
            'iuf',
            'sexe']

        return self.__nages__.to_array_header(startarray=startarray + data)

    def to_json_data(self):
        """To json data."""
        return {'name': self.name, 'sexe': self.sexe, 'yearofbirth': self.yearofbirth, 'age': self.age, 'iuf': self.iuf, 'nationality': self.nationality, 'nages': self.__nages__.to_json_data()}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        name = self.name
        yearofbirth = self.yearofbirth
        age = self.age
        iuf = self.iuf
        nationality = self.nationality
        sexe = self.sexe

        output.write(f'{iuf:8}{sexe:5}{yearofbirth:10}{age:6}{nationality:5}{name}')

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        name = 'nom'
        yearofbirth = 'naissance'
        age = 'age'
        iuf = 'iuf'
        nationality = 'Nat.'
        sexe = 'sexe'

        output.write(f'{iuf:8}{sexe:5}{yearofbirth:10}{age:6}{nationality:5}{name}')

    def cotation(self, cotation, coeff_enable=True):
        """Cotation."""

        for item in self.__nages__:
            item.cotation(nageur=self, cotation=cotation, coeff_enable=coeff_enable)
