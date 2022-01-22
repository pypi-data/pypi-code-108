# -*- coding: utf-8 -*-
"""Base."""

import collections.abc
import json
import sys


class ExtranatObject():
    """CLASS : Extranat Object."""

    def to_json_data(self):  # pylint: disable=no-self-use
        """To json data."""
        return {}

    def to_json(self):
        """To json string."""
        val = self.to_json_data()
        if isinstance(val, list):
            val = {'data': val}

        return json.dumps(val)

    def to_stdcolumn(self, output=sys.stdout):  # pylint: disable=no-self-use
        """To stdout by column."""

    def to_array(self, startarray):  # pylint: disable=no-self-use
        """To array data."""
        return startarray

    def to_array_header(self, startarray):  # pylint: disable=no-self-use
        """To array header."""
        return startarray

    @staticmethod
    def convertstr(value):
        """Convert to str."""
        if value is None:
            return "na"
        return str(value)


class ExtranatObjectCollection(ExtranatObject, collections.abc.Iterable):
    """CLASS : Collection of Extranat Object."""

    def __init__(self, otype):
        self.__items__ = []
        self.__type__ = otype

    def __getitem__(self, key):
        return self.__items__[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.__items__[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self.__items__[self._keytransform(key)]

    def __iter__(self):
        return iter(self.__items__)

    def __len__(self):
        return len(self.__items__)

    @staticmethod
    def _keytransform(key):
        return key

    def append(self, item):
        """Append item."""
        self.__items__.append(item)

    def to_json_data(self):
        """To json."""
        results = []

        for item in self.__items__:
            results.append(item.to_json_data())

        return results

    def to_json(self):
        """To json string."""
        val = self.to_json_data()
        if isinstance(val, list):
            val = {self.__type__.keyname + 's': val}

        return json.dumps(val)

    def to_stdcolumn(self, output=sys.stdout):
        """To stdout by column."""
        self.__type__.to_stdcolumn_header(output=output)
        output.write('\n')

        for item in self.__items__:
            item.to_stdcolumn(output=output)
            output.write('\n')
            output.flush()

    def to_array(self, startarray):
        """To array data."""
        results = []

        for item in self.__items__:
            res = item.to_array(startarray=startarray)
            if len(res) > 0:
                if isinstance(res[0], list):
                    results += res
                else:
                    results.append(res)

        return results

    def to_array_header(self, startarray):
        """To array header."""
        return self.__type__.to_array_header(startarray=startarray)

    def __str__(self):
        """To string."""

        result = ''

        for item in self.__items__:
            result += item.__str__() + '\n'

        return result

    def __repr__(self):
        """To string."""
        results = []

        for item in self.__items__:
            results.append(item.__repr__())

        return ','.join(results)
