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

import cr_api_client.topology.TopologyElements as TopologyElements

# from ruamel.yaml import YAML


DEFAULT_SUBNET = "192.168.1"


class LinksGenerator(object):
    def __init__(self):
        self._subnet = None
        self._links = []
        return

    def reset(self):
        self._subnet = None
        self._links.clear()

    def generate(self, nodes, subnet=None):
        # subnet : 192.168.x
        if subnet:
            self._subnet = subnet
        else:
            self._subnet = self._generate_subnet()

        # 1st, define the router links and its IP address
        switch = None
        for node in nodes:
            if node.type == TopologyElements.TypeEnum.ROUTER:

                net_config = TopologyElements.NetworkConfig()
                net_config.ip = self._generate_ip()

                link = TopologyElements.Link()
                link.switch = switch
                link.node = node
                link.params = net_config

                self._links.append(link)

            elif node.type == TopologyElements.TypeEnum.SWITCH:
                switch = node

        for node in nodes:
            if node == switch:
                # no link for a switch
                continue

            if node.type == TopologyElements.TypeEnum.ROUTER:
                # router links already set
                continue

            net_config = TopologyElements.NetworkConfig()
            net_config.ip = self._generate_ip()

            link = TopologyElements.Link()
            link.switch = switch
            link.node = node
            link.params = net_config

            self._links.append(link)
        return self._links

    def _generate_subnet(self):
        # DEFAULT_SUBNET = "192.168.1"
        return (
            DEFAULT_SUBNET[0 : DEFAULT_SUBNET.rfind(".")]
            + "."
            + str(random.randrange(1, 255))
        )

    def _generate_ip(self):
        ips = []
        # retrieve existing IPs
        for link in self._links:
            ips.append(link.params.ip)

        while 1:
            # loop until the IP address does not already exist
            sub_ip = random.randrange(1, 254)  # integer from 2 to 253 inclusive
            new_ip = self._subnet + "." + str(sub_ip)

            new_ip = new_ip + "/24"

            if new_ip not in ips:
                return new_ip
