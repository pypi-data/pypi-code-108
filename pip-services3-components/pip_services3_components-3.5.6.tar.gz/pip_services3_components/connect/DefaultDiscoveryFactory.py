# -*- coding: utf-8 -*-
"""
    pip_services3_components.connect.DefaultDiscoveryFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Default discovery factory implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer.Descriptor import Descriptor

from .MemoryDiscovery import MemoryDiscovery
from ..build.Factory import Factory


class DefaultDiscoveryFactory(Factory):
    """
    Creates :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` components by their descriptors.

    See :class:`Factory <pip_services3_components.build.Factory.Factory>`,
    :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`,
    :class:`MemoryDiscovery <pip_services3_components.connect.MemoryDiscovery.MemoryDiscovery>`,
    """

    MemoryDiscoveryDescriptor = Descriptor("pip-services", "discovery", "memory", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()
        self.register_as_type(DefaultDiscoveryFactory.MemoryDiscoveryDescriptor, MemoryDiscovery)
