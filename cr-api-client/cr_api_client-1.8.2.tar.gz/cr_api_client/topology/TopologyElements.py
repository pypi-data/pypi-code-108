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
from typing import Dict
from typing import List
from typing import Union

from cr_api_client.topology.validator.node import RoleEnum
from cr_api_client.topology.validator.node import TypeEnum


class NetworkConfig:
    def __init__(self, ip=None, mac=None):
        self.ip = ip
        # TODO: allow to define mac address at topology.yaml file
        # self.mac = mac
        self.domains = []


class Link:
    def __init__(self, switch=None, node=None, params=None):
        self.switch = switch
        self.node = node
        self.params = params


class Node:
    def __init__(self, node_type, name, roles=None):
        if not node_type:
            raise ValueError("'node_type' argument is mandatory!")
        if type(node_type) != TypeEnum:
            raise ValueError("'node_type' type has to be TypeEnum!")

        self.type = node_type.value
        self.active = True
        self._name = NameGen.process(node_type=self.type, name=name, roles=roles)

    @property
    def name(self):
        return self._name

    @name.setter  # type: ignore
    def name(self, name):
        # old = self._name
        self._name = NameGen.process(node_type=self.type, name=name, roles=None)


class Machine(Node):
    def __init__(self, node_type, roles, name=None):
        if not roles or len(roles) == 0:
            raise ValueError("'roles' argument is mandatory!")
        if type(roles) != list or type(roles[0]) != RoleEnum:
            raise ValueError("'roles' type has to be list(RoleEnum)!")
        super().__init__(node_type=node_type, roles=roles, name=name)
        self.memory_size = 2048
        self.nb_proc = 1
        self.roles = []
        for role in roles:
            self.roles.append(role.value)


class DockerEnvironment:
    def __init__(self, key: str, value: str):
        self.__dict__[key] = value


class DockerVolume:
    def __init__(self, host_path: str, bind: str, writable: bool = False):
        self.host_path = host_path
        self.bind = bind
        self.writable = writable


class Docker(Machine):
    def __init__(
        self,
        name: str,
        roles: List[RoleEnum],
        image: str,
        volumes: List[DockerVolume] = [],
        environment: List[DockerEnvironment] = [],
    ):
        super().__init__(node_type=TypeEnum.DOCKER, roles=roles, name=name)
        self.base_image = image
        self.volumes = volumes
        self.environment = environment


class VirtualMachine(Machine):
    def __init__(self, roles, name=None):
        super().__init__(node_type=TypeEnum.VIRTUAL_MACHINE, roles=roles, name=name)
        self.basebox_id = None


class PhysicalMachine(Node):
    def __init__(self, name=None):
        super().__init__(
            node_type=TypeEnum.PHYSICAL_MACHINE, roles=[RoleEnum.CLIENT], name=name
        )
        self.roles = [RoleEnum.CLIENT.value]


class Router(Node):
    def __init__(self, name=None):
        super().__init__(node_type=TypeEnum.ROUTER, name=name)
        self.routes = []


class Switch(Node):
    def __init__(self, name=None):
        super().__init__(node_type=TypeEnum.SWITCH, name=name)
        return


class PhysicalGateway(Node):
    def __init__(self, name=None):
        super().__init__(node_type=TypeEnum.PHYSICAL_GATEWAY, name=name)
        return


class HostMachine(Node):
    def __init__(self, name=None):
        super().__init__(node_type=TypeEnum.HOST_MACHINE, name=name)
        return


class NameGen:
    # Class properties used for naming generation and unicity control
    _node_group_counts: Dict[str, int] = {}

    @classmethod
    def reset(cls):
        cls._node_group_counts = {}

    @classmethod
    def process(cls, node_type, roles, name):
        new_name = None
        if name is not None:
            new_name = name
        else:
            if not node_type:
                node_type = "default"

            prefix = "Node"
            if not roles or len(roles) == 0:
                if node_type == TypeEnum.PHYSICAL_GATEWAY:
                    prefix = "Physical_gateway"
                elif node_type == TypeEnum.ROUTER:
                    prefix = "Router"
                elif node_type == TypeEnum.SWITCH:
                    prefix = "Switch"
            # The 1st role is used for naming
            elif roles[0] == RoleEnum.AD.value:
                prefix = "AD"
            elif roles[0] == RoleEnum.ADMIN.value:
                prefix = "ADMIN"
            elif roles[0] == RoleEnum.CLIENT.value:
                prefix = "CLIENT"
            elif roles[0] == RoleEnum.FILE_SERVER.value:
                prefix = "FILE"
            else:
                raise ValueError("'{}' role not managed yet!".format(roles[0]))

            if prefix in NameGen._node_group_counts:
                idx = NameGen._node_group_counts[prefix]
            else:
                NameGen._node_group_counts[prefix] = 1
                idx = 1
            new_name = prefix + str(idx)
            NameGen._node_group_counts[prefix] += 1
        return new_name


class Network:
    def __init__(self, subnet_address: str, *childrens: List[Union[Node, "Network"]]):
        self._subnet_address = subnet_address
        self._router = Router(name=f"router-{subnet_address}")
        self._switch = Switch(name=f"switch-{subnet_address}")
        self._nodes = self._sanitize_childrens(childrens)

    @staticmethod
    def _sanitize_childrens(childrens) -> List[Union[Node, "Network"]]:
        """Sanitize the list of childrens.
        Childrens should be of type `Node` or `Network`
        """

        def validate(child):
            return isinstance(child, Node) or isinstance(child, Network)

        return [child for child in list(childrens) if validate(child)]

    @property
    def router(self):
        return self._router

    @property
    def switch(self):
        return self._switch

    @property
    def nodes(self):
        return [node for node in self._nodes if isinstance(node, Node)]

    @property
    def childrens(self):
        return self._nodes

    @childrens.setter
    def childrens(self, childrens):
        self._nodes = self._sanitize_childrens(childrens)

    @childrens.deleter
    def childrens(self, childrens):
        self._nodes = []

    @property
    def subnets(self):
        return [node for node in self._nodes if isinstance(node, Network)]

    @property
    def subnet_address(self):
        return self._subnet_address

    def __iter__(self):
        yield self
        for child in self.childrens:
            if isinstance(child, Network):
                yield from child
