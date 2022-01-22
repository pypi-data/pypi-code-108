# -*- coding: utf-8 -*-
# https://ffn.extranat.fr/webffn/structures.php?idact=&iddep=&idreg=
"""Location."""

import sys

from .base import ExtranatObject


class Region(ExtranatObject):
    """CLASS : Region."""

    def __init__(self, idreg=None, idstruct=None, name=None):
        """Constructor."""
        self.__idreg__ = idreg
        self.__idstruct__ = idstruct
        self.__name__ = name

    @property
    def idreg(self):
        """Get id region."""
        return self.convertstr(self.__idreg__)

    @property
    def idstruct(self):
        """Get id structure."""
        return self.convertstr(self.__idstruct__)

    @property
    def name(self):
        """Get name."""
        return self.convertstr(self.__name__)

    @property
    def keyname(self):
        """Get keyname."""
        return 'region'

    def to_json_data(self):
        """To json data."""
        return {'idreg': self.idreg, 'idstruct': self.idstruct, 'name': self.name}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        idreg = self.idreg
        idstruct = self.idstruct
        name = self.name

        output.write(f'{idreg:8}{idstruct:10}{name}')

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        idreg = 'id'
        idstruct = 'idstruct'
        name = 'région'

        output.write(f'{idreg:8}{idstruct:10}{name}')

    def __repr__(self):
        """To string."""
        return self.__name__

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.idreg,
            self.idstruct,
            self.name]

        return startarray + data

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            "idreg",
            "idstruct",
            "region"]

        return startarray + data


class Departement(ExtranatObject):
    """CLASS : Departement."""

    def __init__(self, iddep=None, idstruct=None, name=None, region=None):
        """Constructor."""
        self.__iddep__ = iddep
        self.__idstruct__ = idstruct
        self.__name__ = name
        self.__region__ = region

    @property
    def iddep(self):
        """Get id departement."""
        return self.convertstr(self.__iddep__)

    @property
    def idstruct(self):
        """Get id structure."""
        return self.convertstr(self.__idstruct__)

    @property
    def name(self):
        """Get name."""
        return self.convertstr(self.__name__)

    @property
    def region(self):
        """Get region."""
        return self.__region__

    @property
    def keyname(self):
        """Get keyname."""
        return 'departement'

    def to_json_data(self):
        """To json data."""
        return {'iddep': self.iddep, 'idstruct': self.idstruct, 'name': self.name, 'region': self.region.to_json_data()}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        iddep = self.iddep
        idstruct = self.idstruct
        name = self.name
        region_name = self.region.name

        output.write(f'{iddep:8}{idstruct:10}{region_name:30}{name}')

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        iddep = 'id'
        idstruct = 'idstruct'
        name = 'département'
        region_name = 'région'

        output.write(f'{iddep:8}{idstruct:10}{region_name:30}{name}')

    def __repr__(self):
        """To string."""
        return self.__name__

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.iddep,
            self.idstruct,
            self.region.name,
            self.name]

        return startarray + data

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            'iddep',
            'idstruct',
            'region',
            'departement']

        return startarray + data


class Club(ExtranatObject):
    """CLASS : Club."""

    def __init__(self, idclub=None, name=None, departement=None):
        """Constructor."""
        self.__idclub__ = idclub
        self.__name__ = name
        self.__departement__ = departement

    @property
    def idclub(self):
        """Get id club."""
        return self.convertstr(self.__idclub__)

    @property
    def name(self):
        """Get name."""
        return self.convertstr(self.__name__)

    @property
    def departement(self):
        """Get departement."""
        return self.__departement__

    @property
    def keyname(self):
        """Get keyname."""
        return 'club'

    def to_json_data(self):
        """To json data."""
        return {'idclub': self.idclub, 'name': self.name, 'departement': self.departement.to_json_data()}

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        idclub = self.idclub
        name = self.name
        departement_name = self.departement.name

        output.write(f'{idclub:8}{departement_name:30}{name}')

    @staticmethod
    def to_stdcolumn_header(output=sys.stdout):
        """To stdout by column - Header."""
        idclub = 'id'
        name = 'club'
        # region_name = 'région'
        departement_name = 'département'

        output.write(f'{idclub:8}{departement_name:30}{name}')

    def __repr__(self):
        """To string."""
        return self.__name__

    def to_array(self, startarray):
        """To array data."""
        data = [
            self.idclub,
            self.departement.name,
            self.departement.region.name,
            self.name]

        return startarray + data

    def to_array_header(self, startarray):
        """To array header."""
        data = [
            'idclub',
            'region',
            'departement',
            'club']

        return startarray + data
