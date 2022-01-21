# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from io import StringIO
from pathlib import Path

import ruamel.yaml

from cr_api_client.topology.TopologyElements import Docker
from cr_api_client.topology.TopologyElements import DockerEnvironment
from cr_api_client.topology.TopologyElements import DockerVolume
from cr_api_client.topology.TopologyElements import Link
from cr_api_client.topology.TopologyElements import Network
from cr_api_client.topology.TopologyElements import NetworkConfig
from cr_api_client.topology.TopologyElements import Node
from cr_api_client.topology.TopologyElements import PhysicalGateway
from cr_api_client.topology.TopologyElements import PhysicalMachine
from cr_api_client.topology.TopologyElements import RoleEnum
from cr_api_client.topology.TopologyElements import Router
from cr_api_client.topology.TopologyElements import Switch
from cr_api_client.topology.TopologyElements import VirtualMachine


#
# helper code inspired from Jeff Hykin (https://stackoverflow.com/a/63179923)
#


# setup loader
yaml = ruamel.yaml.YAML()
yaml.version = (1, 2)
yaml.indent(mapping=3, sequence=2, offset=0)
yaml.allow_duplicate_keys = True
yaml.explicit_start = False
yaml.preserve_quotes = True

yaml.register_class(Link)
yaml.register_class(VirtualMachine)
yaml.register_class(Docker)
yaml.register_class(DockerVolume)
yaml.register_class(DockerEnvironment)
yaml.register_class(Node)
yaml.register_class(PhysicalMachine)
yaml.register_class(NetworkConfig)
yaml.register_class(PhysicalGateway)
yaml.register_class(Router)
yaml.register_class(Switch)


# show null
def my_represent_none(self, data):
    return self.represent_scalar(u"tag:yaml.org,2002:null", u"null")


yaml.representer.add_representer(type(None), my_represent_none)


# object -> YAML string
def object_to_yaml_str(obj, options=None) -> str:
    if options == None:
        options = {}
    string_stream = StringIO()
    yaml.dump(obj, string_stream, **options)
    output_str = string_stream.getvalue()
    string_stream.close()
    return output_str


# YAML string -> object
def yaml_string_to_object(string, options=None):
    if options == None:
        options = {}
    return yaml.load(string, **options)


# YAML file -> object
def yaml_file_to_object(file_path, options=None):
    if options == None:
        options = {}
    as_path_object = Path(file_path)
    return yaml.load(as_path_object, **options)


# object -> YAML file
def object_to_yaml_file(obj, file_path, options=None):
    if options == None:
        options = {}
    as_path_object = Path(Path(file_path))
    with as_path_object.open("w") as output_file:
        return yaml.dump(obj, output_file, **options)


# --- string examples
#
# yaml_string = object_to_yaml_str({(1, 2): "hi"})
# print("yaml string:", yaml_string)
# obj = yaml_string_to_object(yaml_string)
# print("obj from string:", obj)

#
# --- file examples
#
# obj = yaml_file_to_object("./thingy.yaml")
# print("obj from file:", obj)
# object_to_yaml_file(obj, file_path="./thingy2.yaml")
# print("saved that to a file")
