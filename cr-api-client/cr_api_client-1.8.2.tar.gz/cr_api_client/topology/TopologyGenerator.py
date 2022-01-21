#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
import random
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

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
from cr_api_client.topology.TopologyLinksGenerator import LinksGenerator
from cr_api_client.topology.TopologyNodesGenerator import NodesGenerator
from cr_api_client.topology.validator.topology import Topology as TopologyValidator
from cr_api_client.yaml_helper import object_to_yaml_str
from cr_api_client.yaml_helper import yaml_string_to_object


class Topologies(Enum):
    r"""The Topologies Enum class lists the types of topologies which can be generate:
    - FLAT,
    - ROUTING,
    - VLAN,
    - SILO,
    - MANUAL,
    - POC_ZONES"""

    FLAT = 0
    ROUTING = 1
    VLAN = 2
    SILO = 3
    MANUAL = 4
    POC_ZONES = 5

    def __str__(self):
        return str(self.name)


MAX_ZONE_COUNT = 1

MIN_NODE_COUNT = 3  # 1 switch, 1 router and 1 machine (client or server)
MAX_NODE_COUNT = 10  # limited by the host capabilities

DEFAULT_TOPOLOGY_COMPLEXITY = 0

DEFAULT_OS_AVAILABLE = {
    RoleEnum.CLIENT: {"win7": 75},
    RoleEnum.ADMIN: {"win7_admin": 76},
    RoleEnum.AD: {"win_server_2012": 68},
    RoleEnum.FILE_SERVER: {"win_server_2012": 69}
    # RoleEnum.XXXX = {"XXXX": NN, "YYYY", MM, ...}
}


class YamlString:
    def __init__(self):
        self._buffer = bytes()

    def reset(self):
        self._buffer = bytes()

    def write(self, buf):
        self._buffer += buf

    @property
    def string(self):
        return self._buffer.decode("utf-8")


class Generation(Enum):
    r"""The Generation Enum class lists what the generator will produce:
    - YAML_ONLY: yaml file only,
    - LINKS: links objects and yaml file,
    - FULL: by default, nodes and links objects, plus yaml file"""

    YAML_ONLY = 1  # yaml file only
    LINKS = 2  # links objects and yaml file
    FULL = 3  # default : nodes and links objects, plus yaml file


class TopologyGenerator(object):
    r"""The TopologyGenerator class is the API class used to generate a topology.

    The TopologyGenerator constructor expects one parameter:

    :param topology_type: This parameter defines the type of topology to produce.
    Default value is Topologies.FLAT.
    :type topology_type: :class:`Topologies`, optional

    >>> topo_gen = TopologyGenerator()
    >>> yaml_content = topo_gen.generate()
    >>> len(yaml_content) > 10
    True
    """

    def __init__(self, topology_type=Topologies.FLAT):
        if not isinstance(topology_type, Topologies):
            # Node is the parent class of all nodes (machine, router, ...)
            raise TypeError("'node' has to be a node object!")

        self._current_file = None

        self._topology = CommentedMap()
        self._topology["name"] = ""
        self._topology["nodes"] = []
        self._topology["links"] = []

        self._os_available = DEFAULT_OS_AVAILABLE

        # number of zones
        # self._zones_count = random.randrange(1, MAX_ZONE_COUNT+1)
        self._zones_count = 1  # FLAT mode
        # number of nodes
        self._nodes_count = random.randrange(MIN_NODE_COUNT, MAX_NODE_COUNT + 1)
        # type of network isolation for zones (flat, routing, VLAN, silo, ...)
        self._type_zone_network_isolation = topology_type
        # topology complexity
        self._topology_complexity = DEFAULT_TOPOLOGY_COMPLEXITY

    @property
    def name(self):
        r"""The name of the topology to generate.
        It will be used to set the filename of the YAML output file.
        If not set, the filename will be generated from the type of topology
        and its number of nodes."""

        return self._topology["name"]

    @name.setter
    def name(self, n):
        self._topology["name"] = n

    def reset(self):
        r"""Clear the Generator context, before a next new generation."""

        self._topology.clear()
        self._topology["name"] = ""
        self._topology["nodes"] = []
        self._topology["links"] = []
        self._os_available = DEFAULT_OS_AVAILABLE
        # number of zones
        # self._zones_count = random.randrange(1, MAX_ZONE_COUNT+1)
        self._zones_count = 1  # FLAT mode
        # number of nodes
        self._nodes_count = random.randrange(MIN_NODE_COUNT, MAX_NODE_COUNT + 1)
        # type of network isolation for zones (flat, routing, VLAN, silo, ...)
        self._type_zone_network_isolation = Topologies.FLAT
        # topology complexity
        self._topology_complexity = DEFAULT_TOPOLOGY_COMPLEXITY

    def add_node(self, node: Node) -> None:
        r"""Add the given node in the current topopology.

        :param node: The node to add.
        :type node: :class:`~cr_api_client.TopologyElements.Node`
        :raises: :class:`TypeError` if node parameter is not a
                :class:`~cr_api_client.TopologyElements.Node`"""

        if not isinstance(node, Node):
            # Node is the parent class of all nodes (machine, router, ...)
            raise TypeError("'node' has to be a node object!")
        for n in self._topology["nodes"]:
            if n._name == node._name:
                raise ValueError(
                    f'The name "{n._name}" is already in use in the topology.'
                )
        self._topology["nodes"].append(node)

    def add_link(self, link: Link) -> None:
        r"""Add the given link in the current topopology.

        :param link: The link to add.
        :type link: :class:`~cr_api_client.TopologyElements.Link`
        :raises: :class:`TypeError` if node parameter is not a
                :class:`~cr_api_client.TopologyElements.Link`"""

        if not isinstance(link, Link):
            # Link is the parent class of all links
            raise TypeError("'link' has to be a link object!")
        # Check if the link already exists
        for l in self._topology["links"]:
            if l.switch == link.switch and l.node == link.node:
                return
        self._topology["links"].append(link)

    def add_network(self, network: Network) -> None:
        r"""Add the given network in the current topopology.

        :param network: The network to add.
        :type network: :class:`~cr_api_client.TopologyElements.Network`
        :raises: :class:`TypeError` if network parameter is not a
                :class:`~cr_api_client.TopologyElements.Network`"""

        if not isinstance(network, Network):
            raise TypeError("'network' has to be a Network object!")

        internet_switches: Dict[str, List[str]] = {}

        def _find_switch(node_name: str):
            for switch, links in internet_switches.items():
                if node_name in links:
                    return switch
            return None

        for net in network:
            for subnet in net.subnets:
                switch = _find_switch(net.router.name) or _find_switch(
                    subnet.router.name
                )
                if not switch:
                    switch = Switch()
                    self.add_node(switch)
                    internet_switches[switch] = [subnet.router.name, net.router.name]

                self.add_link(
                    Link(
                        switch=switch,
                        node=subnet.router,
                        params=NetworkConfig(),
                    )
                )
                self.add_link(
                    Link(
                        switch=switch,
                        node=net.router,
                        params=NetworkConfig(),
                    )
                )

            links_gen = LinksGenerator()

            network_nodes = [net.switch, net.router] + net.nodes
            if network_nodes:
                self._topology["nodes"].extend(network_nodes)

            links = links_gen.generate(network_nodes, subnet=net.subnet_address)
            self._topology["links"].extend(links)

    def generate(self, gen_level=Generation.FULL) -> str:
        r"""Generate a topopology and returns it in a YAML format string.

        :param gen_level: The level of automatic generation.
            Default value is `Generation.FULL`: generates nodes and links objects, plus yaml content
            if `Generation.LINKS`: generates links objects and yaml content
            if `Generation.YAML_ONLY`: generates only yaml content
        :type gen_level: :class:`Generation`
        :raises: :class:`TypeError` if gen_level parameter is not a
                :class:`Generation`
        :raises: :class:`TypeError` if the type of  :class:`Topologies`
        :returns: topology in a yaml :class:`str`"""

        if not isinstance(gen_level, Generation):
            raise TypeError("'gen_level' has to be a Generation Enum value!")

        # self._type_zone_network_isolation = choice(list(TopologyEnum._member_map_.values()))
        nodes_gen = None
        links_gen = None
        yaml_content = None

        if self._type_zone_network_isolation == Topologies.FLAT:
            # only one switch and no VLAN
            if gen_level.value >= Generation.FULL.value:
                nodes_gen = NodesGenerator(os_container=self._os_available)
                self._topology["nodes"] = nodes_gen.generate(self._nodes_count)
            if gen_level.value >= Generation.LINKS.value:
                links_gen = LinksGenerator()
                self._topology["links"] = links_gen.generate(self._topology["nodes"])

            if self._topology["name"] == "":
                name = "{}-{}-nodes".format(
                    self._type_zone_network_isolation.name, len(self._topology["nodes"])
                )
                self._topology["name"] = name

            yaml_content = self._generate_yaml()

        elif self._type_zone_network_isolation == Topologies.MANUAL:
            if gen_level.value >= Generation.FULL.value:
                nodes_gen = NodesGenerator(os_container=self._os_available)
                # self._topology['nodes'] = nodes_gen.generate(self._nodes_count)

            if self._topology["name"] == "":
                name = "{}-{}-nodes".format(
                    self._type_zone_network_isolation.name, len(self._topology["nodes"])
                )
                self._topology["name"] = name

            yaml_content = self._generate_yaml()

        elif self._type_zone_network_isolation == Topologies.POC_ZONES:
            if self._topology["name"] == "":
                name = "{}-{}-nodes".format(
                    self._type_zone_network_isolation.name, len(self._topology["nodes"])
                )
                self._topology["name"] = name
            yaml_content = self._generate_yaml()

        # elif other topology type...
        # TODO
        else:
            raise TypeError("Type of topology not implemented yet!")

        if yaml_content == "":
            if gen_level == Generation.YAML_ONLY:
                yaml_content = self._generate_yaml()

        return yaml_content

    def _generate_yaml(self) -> str:
        if self._topology["name"] == "":
            name = "{}-{}-nodes".format(
                self._type_zone_network_isolation.name, len(self._topology["nodes"])
            )
            self._topology["name"] = name

        yaml_content = object_to_yaml_str(self._topology)

        # yaml = self._yaml_builder()

        # yaml_str = YamlString()
        # yaml.dump(self._topology, yaml_str)
        # #yaml_content = yaml_str.string.replace("!Base", "!")  # a small cleaning
        # yaml_content = yaml_str.string.replace("_name:", "name:")

        yaml_content = yaml_content.replace("_name:", "name:")

        return yaml_content

    @staticmethod
    def validate_yaml(value: str):
        obj = yaml_string_to_object(value)
        print(obj)
        print(type(obj))
        return TopologyValidator(obj)

    @property
    def nodes_count(self) -> int:
        return self._nodes_count

    @nodes_count.setter  # type: ignore
    def nodes_count(self, nodes_count):
        self._nodes_count = nodes_count

    @property
    def zones_count(self) -> int:
        return self._zones_count

    @zones_count.setter  # type: ignore
    def zones_count(self, zones_count):
        # self._zones_count = zones_count
        raise NotImplementedError

    @property
    def type_zone_network_isolation(self):
        return self._type_zone_network_isolation

    @type_zone_network_isolation.setter  # type: ignore
    def type_zone_network_isolation(self, type_zone_network_isolation):
        # self._type_zone_network_isolation = type_zone_network_isolation
        raise NotImplementedError

    @property
    def topology_complexity(self):
        return self._topology_complexity

    @topology_complexity.setter  # type: ignore
    def topology_complexity(self, topology_complexity):
        # self._topology_complexity = topology_complexity
        raise NotImplementedError

    @property
    def os_dict(self):
        return self._os_available

    @os_dict.setter  # type: ignore
    def os_dict(self, new_os_dict):
        self._os_available = new_os_dict


if __name__ == "__main__":
    topology = TopologyGenerator()

    topology.add_node(Switch())
    topology.add_node(Router())

    node = VirtualMachine(roles=[RoleEnum.AD])
    node.basebox_id = "AMOSSYS/windows/windows_7_edge_chrome_firefox"
    topology.add_node(node)

    node = VirtualMachine(roles=[RoleEnum.FILE_SERVER])
    node.basebox_id = "AMOSSYS/windows/windows_7_edge_chrome_firefox"
    topology.add_node(node)

    node = VirtualMachine(roles=[RoleEnum.CLIENT], name="Client")
    node.basebox_id = "AMOSSYS/windows/windows_7_edge_chrome_firefox"
    topology.add_node(node)

    yaml_content = topology.generate(gen_level=Generation.LINKS)

    full_filename = (
        "/tmp/topology-" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".yaml"
    )

    with open(full_filename, "w") as file:
        file.write(yaml_content)

    print(full_filename)
