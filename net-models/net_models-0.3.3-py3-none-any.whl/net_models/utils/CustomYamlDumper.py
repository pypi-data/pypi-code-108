# Preparation for migration to ruamel.yaml
# from ruamel.yaml import YAML
# from ruamel.yaml.representer import Representer
# from ruamel.yaml.dumper import Dumper
# from ruamel.yaml.emitter import Emitter
# from ruamel.yaml.serializer import Serializer
# from ruamel.yaml.resolver import Resolver



import yaml
from yaml.representer import Representer
from yaml.dumper import Dumper
from yaml.emitter import Emitter
from yaml.serializer import Serializer
from yaml.resolver import Resolver
from collections import OrderedDict
import ipaddress

from pydantic.typing import Union, Type


from net_models.fields import DoubleQoutedString, Jinja2String
from net_models.fields.InterfaceNames import *

class CustomYamlRepresenter(Representer):

    def __init__(self, default_style=None, default_flow_style: bool =False, sort_keys: bool = True):
        super().__init__(default_style=default_style, default_flow_style=default_flow_style, sort_keys=sort_keys)


    def represent_none(self, data):
        return self.represent_scalar(u'tag:yaml.org,2002:null', u'')

    def represent_dict(self, data):
        data_keys = sorted(list(data.keys()))
        if "name" in data_keys:
            data_keys.insert(0, data_keys.pop(data_keys.index("name")))
        if "tags" in data_keys:
            data_keys.insert(1, data_keys.pop(data_keys.index("tags")))
        if "hosts" in data_keys:
            data_keys.append(data_keys.pop(data_keys.index("hosts")))
        values = [(self.represent_data(key), self.represent_data(data[key])) for key in data_keys]
        return yaml.nodes.MappingNode(tag=u'tag:yaml.org,2002:map', value=values)

    def represent_ordered_dict(self, data):
        values = []
        for item_key, item_value in data.items():
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            values.append((node_key, node_value))

        return yaml.nodes.MappingNode(tag=u'tag:yaml.org,2002:map', value=values)

    def represent_double_quoted_string(self, value):
        return self.represent_scalar(tag=u'tag:yaml.org,2002:str', value=value, style=u'"')

    def represent_ip_interface(self, value: Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]):
        return self.represent_scalar(tag=u'tag:yaml.org,2002:str', value=value.with_prefixlen, style=u'')

    def represent_ip_address(self, value: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]):
        return self.represent_scalar(tag=u'tag:yaml.org,2002:str', value=str(value), style=u'')

    def represent_ip_network(self, value: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]):
        return self.represent_scalar(tag=u'tag:yaml.org,2002:str', value=str(value), style=u'')

    def represent_interface_name(self, value: BaseInterfaceName):
        return self.represent_scalar(tag=u'tag:yaml.org,2002:str', value=str(value), style=u'')

CustomYamlRepresenter.add_representer(type(None), CustomYamlRepresenter.represent_none)
CustomYamlRepresenter.add_representer(dict, CustomYamlRepresenter.represent_dict)
CustomYamlRepresenter.add_representer(OrderedDict, CustomYamlRepresenter.represent_ordered_dict)
CustomYamlRepresenter.add_representer(DoubleQoutedString, CustomYamlRepresenter.represent_double_quoted_string)
CustomYamlRepresenter.add_representer(Jinja2String, CustomYamlRepresenter.represent_double_quoted_string)
CustomYamlRepresenter.add_representer(ipaddress.IPv4Interface, CustomYamlRepresenter.represent_ip_interface)
CustomYamlRepresenter.add_representer(ipaddress.IPv6Interface, CustomYamlRepresenter.represent_ip_interface)
CustomYamlRepresenter.add_representer(ipaddress.IPv4Address, CustomYamlRepresenter.represent_ip_address)
CustomYamlRepresenter.add_representer(ipaddress.IPv6Address, CustomYamlRepresenter.represent_ip_address)
CustomYamlRepresenter.add_representer(ipaddress.IPv4Network, CustomYamlRepresenter.represent_ip_network)
CustomYamlRepresenter.add_representer(ipaddress.IPv6Network, CustomYamlRepresenter.represent_ip_network)
CustomYamlRepresenter.add_representer(GenericInterfaceName, CustomYamlRepresenter.represent_interface_name)
CustomYamlRepresenter.add_representer(IosInterfaceName, CustomYamlRepresenter.represent_interface_name)
CustomYamlRepresenter.add_representer(JuniperInterfaceName, CustomYamlRepresenter.represent_interface_name)


class CustomYamlDumper(Emitter, Serializer, CustomYamlRepresenter, Resolver):
    def __init__(self, stream,
                 default_style=None, default_flow_style=None,
                 canonical=None, indent=None, width=None,
                 allow_unicode=None, line_break=None,
                 encoding=None, explicit_start=None, explicit_end=None, sort_keys=False,
                 version=None, tags=None):
        Emitter.__init__(self, stream, canonical=canonical,
                         indent=indent, width=width,
                         allow_unicode=allow_unicode, line_break=line_break)
        Serializer.__init__(self, encoding=encoding,
                            explicit_start=explicit_start, explicit_end=explicit_end,
                            version=version, tags=tags)
        CustomYamlRepresenter.__init__(self, default_style=default_style,
                                       default_flow_style=default_flow_style)
        Resolver.__init__(self)

    def increase_indent(self, flow=False, indentless=False):
        return super(CustomYamlDumper, self).increase_indent(flow=flow, indentless=False)
