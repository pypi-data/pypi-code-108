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
from random import choice

from cr_api_client.topology.TopologyElements import PhysicalGateway
from cr_api_client.topology.TopologyElements import Router
from cr_api_client.topology.TopologyElements import Switch
from cr_api_client.topology.TopologyElements import VirtualMachine
from cr_api_client.topology.validator.node import RoleEnum
from cr_api_client.topology.validator.node import TypeEnum


MIN_NODE_COUNT = 3  # 1 switch, 1 router and 1 machine (client or server)
MAX_NODE_COUNT = 10  # limited by the host capabilities

DEFAULT_TOPOLOGY_COMPLEXITY = 0


class NodeGenerator(object):
    def generate(self, node_type, role, name=None, os_list=None):
        if role is None:
            if node_type == TypeEnum.SWITCH:
                return Switch(name)
            elif node_type == TypeEnum.ROUTER:
                return Router(name)
            elif node_type == TypeEnum.PHYSICAL_GATEWAY:
                return PhysicalGateway(name)

        elif role == RoleEnum.AD:
            if (
                node_type == TypeEnum.VIRTUAL_MACHINE
                and os_list
                and type(os_list) == list
            ):
                return self._generate_machine_ad(name, os_list)

        elif role == RoleEnum.ADMIN:
            if (
                node_type == TypeEnum.VIRTUAL_MACHINE
                and os_list
                and type(os_list) == list
            ):
                return self._generate_machine_admin(name, os_list)

        elif role == RoleEnum.FILE_SERVER:
            if (
                node_type == TypeEnum.VIRTUAL_MACHINE
                and os_list
                and type(os_list) == list
            ):
                return self._generate_machine_fileserver(name, os_list)

        elif role == RoleEnum.CLIENT:
            if (
                node_type == TypeEnum.VIRTUAL_MACHINE
                and os_list
                and type(os_list) == list
            ):
                return self._generate_machine_client(name, os_list)
        return None

    def _generate_machine_ad(self, name, os_list):
        node = VirtualMachine(name=name, roles=[RoleEnum.AD])
        node.basebox_id = choice(os_list)  # choice([68]) = 68
        node.memory_size = 2048
        node.nb_proc = 1
        return node

    def _generate_machine_admin(self, name, os_list):
        node = VirtualMachine(name=name, roles=[RoleEnum.ADMIN])
        node.basebox_id = choice(os_list)  # choice([75]) = 76
        node.memory_size = 2048
        node.nb_proc = 1
        return node

    def _generate_machine_fileserver(self, name, os_list):
        node = VirtualMachine(name=name, roles=[RoleEnum.FILE_SERVER])
        node.basebox_id = choice(os_list)  # choice([69]) = 69
        node.memory_size = 2048
        node.nb_proc = 1
        return node

    def _generate_machine_client(self, name, os_list):
        node = VirtualMachine(name=name, roles=[RoleEnum.CLIENT])
        node.basebox_id = choice(os_list)  # choice([75]) = 75
        node.memory_size = 2048
        node.nb_proc = 1
        return node
