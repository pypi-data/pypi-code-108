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

from cr_api_client.topology.TopologyNodeGenerator import NodeGenerator
from cr_api_client.topology.validator.node import RoleEnum
from cr_api_client.topology.validator.node import TypeEnum


class NodesGenerator(object):
    def __init__(self, os_container):
        self._os_container = os_container
        self._nodes_count = 0
        self._nodes = []
        self.reset()

    def reset(self):
        self._nodes_count = 0
        self._nodes.clear()

    def generate(self, nodes_count):
        self._nodes = []
        self._nodes_count = nodes_count
        if not self._check_node_creation(1.0):
            return self._nodes

        gen_node = NodeGenerator()

        # create the switch
        # the switch is the central node of the LAN
        node = gen_node.generate(node_type=TypeEnum.SWITCH, role=None)
        self._nodes.append(node)

        if self._check_node_creation(0.8):
            # create an AD (optional)
            node = gen_node.generate(
                node_type=TypeEnum.VIRTUAL_MACHINE,
                role=RoleEnum.AD,
                os_list=list(self._os_container[RoleEnum.AD].values()),
            )
            self._nodes.append(node)

        if self._check_node_creation(0.8):
            # create a router (optional)
            node = gen_node.generate(node_type=TypeEnum.ROUTER, role=None)
            self._nodes.append(node)

        if self._check_node_creation(0.8):
            # create an admin machine (optional)
            node = gen_node.generate(
                node_type=TypeEnum.VIRTUAL_MACHINE,
                role=RoleEnum.ADMIN,
                os_list=list(self._os_container[RoleEnum.ADMIN].values()),
            )
            self._nodes.append(node)

        if self._check_node_creation(0.5):
            # create a file server (optional)
            node = gen_node.generate(
                node_type=TypeEnum.VIRTUAL_MACHINE,
                role=RoleEnum.FILE_SERVER,
                os_list=list(self._os_container[RoleEnum.FILE_SERVER].values()),
            )
            self._nodes.append(node)

        nb_clients = self._nodes_count - len(self._nodes)
        if nb_clients <= 0:
            return self._nodes

        for _ in range(nb_clients):
            node = gen_node.generate(
                node_type=TypeEnum.VIRTUAL_MACHINE,
                role=RoleEnum.CLIENT,
                os_list=list(self._os_container[RoleEnum.CLIENT].values()),
            )
            self._nodes.append(node)

        return self._nodes

    def _check_node_creation(self, stat=0.5):
        # 1st, check if a node can be added
        available_node_count = self._nodes_count - len(self._nodes)
        if available_node_count <= 0:
            # no more node available
            return False
        # prepare a choice weighted by the 'stat' parameter
        if stat >= 1.0:
            # 100% probabilities
            return True
        if stat < 0.1:
            stat = 0.1
        stat_count = 10
        stat_proba_ok = int(stat * stat_count)
        stat_range = []
        for _ in range(stat_proba_ok):
            stat_range.append(True)
        for _i in range(stat_proba_ok, stat_count):
            stat_range.append(False)
        # return a random 'True' or 'False' choice based on the 'stat' weight
        return choice(stat_range)

    @property
    def node_count(self):
        return self._nodes_count

    @node_count.setter  # type: ignore
    def nodes_count(self, nodes_count):
        self._nodes_count = nodes_count
