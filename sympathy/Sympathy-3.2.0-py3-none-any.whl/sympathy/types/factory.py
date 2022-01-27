# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""Factory module for sympathy level types."""
from hashlib import sha1

from .. platform.types import (
    TypeRecord, TypeList, TypeDict, TypeTable, TypeText, TypeAlias,
    TypeFunction, TypeTuple, TypeGeneric, parse_base_line)
from .. platform.types import manager as type_manager, get_storage_type
from .. utils import log
from . import sybase
from . sydict import sydict
from . import sylist
from . syrecord import syrecord
from . sytable import sytable
from . sytext import sytext
from . sygeneric import sygeneric
from . sylambda import sylambda
from . sytuple import sytuple
from .. datasources.factory import factory as datasource_factory


SyList = sylist.sylist
core_logger = log.get_logger('core')


class SyFactory(object):
    """Factory for sybase types."""

    def __init__(self, sygroup):
        self.sygroup = sygroup

    def from_dict(self, data, container_type, managed=False):
        """Create and return sygroup matching parameters."""
        # Create a relevant data source.

        storage_type = get_storage_type(container_type)
        data = dict(data)
        data_type = data['type']
        datasource = datasource_factory.from_type_dict(type(storage_type), data)

        try:
            sydata = self.sygroup(container_type, datasource, managed)
        except TypeError:
            sydata = self.sygroup(container_type, datasource)

        if managed and isinstance(container_type, TypeList):
            if sydata.can_write():
                sylist.set_write_through(sydata)
            else:
                sylist.set_read_through(sydata)

        return sydata

    def from_datasource(self, datasource, container_type):
        """Create and return sygroup matching parameters."""
        container_type = type_manager.normalize_instance(container_type)
        return self.sygroup(container_type, datasource)

    def from_type(self, container_type):
        """Create and return sygroup matching parameters."""
        container_type = type_manager.normalize_instance(container_type)
        return self.sygroup(container_type)


SYTYPE_FACTORIES = {
    TypeDict: sydict,
    TypeList: SyList,
    TypeRecord: syrecord,
    TypeTuple: sytuple,
    TypeText: sytext,
    TypeTable: sytable,
    TypeFunction: sylambda,
    TypeGeneric: sygeneric,
}


def typealias(container_type, datasource=sybase.NULL_SOURCE, managed=False):
    aliases = []

    while isinstance(container_type, TypeAlias):
        aliases.append(container_type)
        container_type = get_storage_type(container_type)

    syresult = SYTYPE_FACTORIES[
        type(container_type)](container_type, datasource)

    result = syresult
    raliases = reversed(aliases)

    for alias in raliases:
        util = type_manager.get_typealias_util(alias.name())
        result = util(fileobj=result, managed=managed)

    return result


FACTORIES = {
    TypeDict: SyFactory(sydict),
    TypeList: SyFactory(SyList),
    TypeRecord: SyFactory(syrecord),
    TypeTuple: SyFactory(sytuple),
    TypeText: SyFactory(sytext),
    TypeTable: SyFactory(sytable),
    TypeFunction: SyFactory(sylambda),
    TypeAlias: SyFactory(typealias),
    TypeGeneric: SyFactory(sygeneric),
}


class UnsupportedType(Exception):
    pass


def _factory(factory_mapping, container_type):
    try:
        return factory_mapping[type(container_type)]
    except KeyError:
        raise UnsupportedType(
            '{}: "{}"'.format(type(container_type), container_type))


def _sy_factory(container_type):
    return _factory(FACTORIES, container_type)


class TypeFactory(object):
    """ Factory for types """

    def __init__(self):
        """Init"""
        self.types = {}

    def from_dict(self, data, managed=False):
        """Create and return sympathy level type matching url."""
        typestring = str(data['type'])
        container_type = None

        if type_manager.has_typealias_definition(typestring):
            container_type = type_manager.get_typealias_definition(
                typestring)
        else:
            hash_name = sha1(typestring.encode('ascii')).hexdigest()
            legal_name = 'k' + hash_name
            try:
                container_type = self.types[legal_name]
            except KeyError:
                container_type = parse_base_line(typestring)

        try:
            type_manager.normalize()
        except KeyError:
            core_logger.warning('Fixme! Bad typealias in type manager.')

        return _sy_factory(container_type).from_dict(
            data, container_type, managed)

    def from_datasource(self, datasource, container_type):
        """
        Create and return sympathy level type matching datasource and
        container type.
        """
        container_type = type_manager.normalize_instance(container_type)
        return _sy_factory(container_type).from_datasource(
            datasource, container_type)

    def from_type(self, container_type):
        """Create and return sympathy level type matching container type."""
        container_type = type_manager.normalize_instance(container_type)
        return _sy_factory(container_type).from_type(container_type)


typefactory = TypeFactory()
