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
import sys
from . import context
from .. platform import types
from .. types import factory
from .. platform.port import PortType, instantiate


def port_structures_to_dict(inputs, outputs):
    port_structure = {}
    group = False

    all_names = {}
    for field, field_data in zip(['inputs', 'outputs'], [inputs, outputs]):
        names = {}
        all_names[field] = names

        if field_data is not None:
            field_data = [port.to_dict() for port in field_data]
            # Temporary restoration of indices.
            for i, port in enumerate(field_data):
                port['index'] = i
                name = port.get('name')

                type_ = port.get('type', None)
                if (isinstance(type_, tuple) and
                        "'sygroup'" in str(type_)):
                    group = True

                if name is not None and name in names:
                    raise ValueError(
                        "{} port names may not be reused".format(field[:-1]))

                if name is not None:
                    names.setdefault(name, 0)
                    names[name] += 1

                    if name.startswith('__sy'):
                        raise ValueError(
                            "Port names starting with __sy are "
                            "reserved for internal use.")

                if 'n' in port:
                    if not name:
                        raise ValueError(
                            "When 'n' is used port name needs to be defined")

            port_structure[field] = field_data
        else:
            # Temporarily creating empty definition.
            port_structure[field] = []

        if group:
            if set(all_names.get('inputs', {})).intersection(
                    all_names.get('outputs', {})):
                raise ValueError("When template group is used, port names "
                                 "need to be unique")

    return port_structure


class Ports(object):
    def __init__(self, ports):
        self.ports = ports
        self._lookup = {port['name']: port
                        for port in self.ports if 'name' in port}

    def __getitem__(self, key):
        try:
            return self.ports[key]
        except TypeError:
            return self._lookup[key]

    def __iter__(self):
        for item in self.ports:
            yield item

    def __str__(self):
        return '\n'.join(str(item) for item in self)


def make_list_port(port, changes=None):
    port_dict = port.to_dict()
    if changes:
        port_dict.update(changes)
    if 'name' not in port_dict:
        port_dict['name'] = None
    res = PortType.from_dict(port_dict)
    res.type = '[{}]'.format(port.type)
    return res


def CustomPort(port_type, description, name=None):
    return PortType(description, port_type, 'hdf5', name=name,
                    requiresdata=None, preview=False)


class Port(object):
    """Provides staticmethods to create Ports for built in types."""

    @staticmethod
    def Table(description, name=None, **kwargs):
        return CustomPort('table', description, name)

    @staticmethod
    def Tables(description, name=None, **kwargs):
        return CustomPort('[table]', description, name)

    @staticmethod
    def TableDict(description, name=None, **kwargs):
        return CustomPort('{table}', description, name)

    @staticmethod
    def ADAF(description, name=None, **kwargs):
        return CustomPort('adaf', description, name)

    @staticmethod
    def ADAFs(description, name=None, **kwargs):
        return CustomPort('[adaf]', description, name)

    # Keep old names for backwards compatibility
    Adaf = ADAF
    Adafs = ADAFs

    @staticmethod
    def Figure(description, scheme=None, name=None, **kwargs):
        return PortType(description, 'figure', 'text', name=name, **kwargs)

    @staticmethod
    def Figures(description, scheme=None, name=None, **kwargs):
        return PortType(description, '[figure]', 'text', name=name, **kwargs)

    @staticmethod
    def Datasource(description, scheme=None, name=None, **kwargs):
        return PortType(description, 'datasource', 'text', name=name,
                        **kwargs)

    @staticmethod
    def Datasources(description, scheme=None, name=None, **kwargs):
        return PortType(description, '[datasource]', 'text', name=name,
                        **kwargs)

    @staticmethod
    def Text(description, name=None, **kwargs):
        return CustomPort('text', description, name)

    @staticmethod
    def Texts(description, name=None, **kwargs):
        return CustomPort('[text]', description, name)

    @staticmethod
    def Json(description, name=None, **kwargs):
        return CustomPort('json', description, name)

    @staticmethod
    def Jsons(description, name=None, **kwargs):
        return CustomPort('[json]', description, name)

    @staticmethod
    def Custom(port_type, description, name=None, scheme='hdf5', n=None,
               preview=False):
        return PortType(
            description, port_type, scheme, name=name, n=n, preview=preview)


class RunPorts(object):
    """
    Provides ways to access Ports.

    In addition to accessing by string key it is also possible to access using
    numeric indices.

    Ports with names can be accessed using getattr.
    """
    def __init__(self, ports, infos):
        self.__ports = ports
        self.__infos = infos
        self.__lookup = {info['name']: port
                         for port, info in zip(ports, infos) if 'name' in info}

    def __getitem__(self, key):
        try:
            result = self.nth(key)
        except (IndexError, TypeError):
            result = self.__lookup[key]
        except KeyError:
            raise KeyError('No port named: "{}"'.format(key))
        return result

    def __iter__(self):
        return iter(self.__ports)

    def __contains__(self, key):
        return str(key) in self.__lookup

    def __len__(self):
        return len(self.__ports)

    def __str__(self):
        return '\n'.join(str(PortType.from_dict(info))
                         for info in self.__infos)

    def group(self, name):
        return [port for port, info in
                zip(self.__ports, self.__infos) if info.get('name') == name]

    @property
    def first(self):
        return self.nth(0)

    @property
    def second(self):
        return self.nth(1)

    @property
    def third(self):
        return self.nth(2)

    @property
    def fourth(self):
        return self.nth(3)

    @property
    def fifth(self):
        return self.nth(4)

    def nth(self, n):
        return self.__ports[n]


_use_linking = True


def disable_linking():
    """
    Internal function for disabling linking.
    Do not use this in function in client code.

    It globally disables linking, currently used to avoid a known bug in h5py
    related to h5py.ExternalLink:s and open files.
    """
    global _use_linking
    _use_linking = False


def _dummy_port_maker(cls, *args, **kwargs):
    """
    Wraps and returns the result of port_maker.
    For arguments to use consult port_maker.

    In case of an exception a PortDummy will be returned,
    capturing the error.
    Otherwise the result will be the same as for port_maker.
    """
    try:
        return port_maker(*args, **kwargs)
    except Exception:
        return cls(sys.exc_info())


def dummy_port_maker(*args, **kwargs):
    return _dummy_port_maker(context.PortDummy, *args, **kwargs)


def dummy_input_port_maker(*args, **kwargs):
    return _dummy_port_maker(context.InputPortDummy, *args, **kwargs)


def dummy_output_port_maker(*args, **kwargs):
    return _dummy_port_maker(context.OutputPortDummy, *args, **kwargs)


def port_maker(port_information, mode, external=True, expanded=False,
               managed=False, no_datasource=False):
    """
    Typaliases should be simplified with intra-dependencies expanded.
    """
    if no_datasource:
        return port_mem_maker(port_information)
    else:
        return port_file_maker(
            port_information,
            mode,
            external,
            expanded,
            managed)


def port_mem_maker(port_information):
    alias = port_information['type']
    return factory.typefactory.from_type(types.from_string(alias))


def port_file_maker(port_information, mode, external=True, expanded=False,
                    managed=False):
    """Return maker for port."""
    link =  _use_linking and not external
    alias = port_information['type']
    dstype = port_information.get('dstype')
    if dstype != None:
        dstype = str(dstype)
    type_expanded = str(types.from_string_expand(alias))
    type_expanded = type_expanded.replace('sytable', 'table')
    type_expanded = type_expanded.replace('sytext', 'text')

    data = {
        'scheme': port_information['scheme'],
        'type': str(alias),
        'dstype': dstype,
        'type_expanded': type_expanded,
        'mode': mode,
        'external': external,
        'can_link': link,
        'path': [],
        'resource': port_information['file'],
    }

    return factory.typefactory.from_dict(data, managed=managed)


def typealiases_parser(typealiases):
    """Parse and return dictionary of typaliases."""
    return {alias:
            types.from_string_alias(
                'sytypealias {0} = {1}'.format(alias, value['type']))
            for alias, value in typealiases.items()}


def typealiases_expander(typealiases_parsed):
    """
    Return dictionary of typealiases.
    The intra-dependencies are expanded.
    """
    return dict(
        types.simplify_aliases(typealiases_parsed.values()))
