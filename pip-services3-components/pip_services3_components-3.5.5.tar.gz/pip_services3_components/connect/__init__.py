# -*- coding: utf-8 -*-
"""
    pip_services3_components.connect.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains implementation of connection parameters, using various connection strings,
    which are stripped of all credentials. If we need to configure a service, the port,
    ip address, protocol, and other parameters – we use the ConnectionParams object, and
    relevant helper classes (like :class:`ConnectionResolver <pip_services3_components.connect.ConnectionResolver.ConnectionResolver>`), for acquiring these parameters,
    and for discovery of objects, components (which store and retrieve connection parameters).

    ### Discovery ###

    Service that store a registry of various end-points (what services are where, and how to
    connect to them). It knows the end-points, but doesn't have the credentials to connect to them.
    Separated for security reasons. IDiscovery – interface for creating registries.
    MemoryDiscovery – registry that is stored in memory.

    There exist 2 types of discovery:
        - Static discovery: all services have static IP addresses (like DNS, which also works using static
        discovery) that are configured from the start and don't change along the way. As of lately, used
        more often than dynamic, because it is simpler to use and more reliable.
        - Proxy (or reverse proxy) is created with a dns name, and all the dynamics of
        starting/restarting/switching from one host to another – everything is nice and clear for the clients.
        Infrastructure does all the hard work out of the box.
        - Configure sets the static registry.
        - Dynamic discovery: every time a service starts, it registers its address in the discovery service
        ("Service name" at the following address "IP"). Clients then ask to resolve the address
        by which the requested service can be reached. The service has a general name, by which other
        services can resolve it.
        - If a service stops working, you need to refresh its address, clean stale addresses,
        heartbeats must be used – lots of problems and challenges. One service can have more than one address.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['CompositeConnectionResolver', 'ConnectionParams',
           'IDiscovery', 'ConnectionResolver',
           'ConnectionUtils', 'MemoryDiscovery', 'DefaultDiscoveryFactory']

from .CompositeConnectionResolver import CompositeConnectionResolver
from .ConnectionParams import ConnectionParams
from .ConnectionResolver import ConnectionResolver
from .ConnectionUtils import ConnectionUtils
from .DefaultDiscoveryFactory import DefaultDiscoveryFactory
from .IDiscovery import IDiscovery
from .MemoryDiscovery import MemoryDiscovery
