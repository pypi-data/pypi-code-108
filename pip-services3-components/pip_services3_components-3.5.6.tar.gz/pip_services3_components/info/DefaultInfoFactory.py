# -*- coding: utf-8 -*-
"""
    pip_services3_components.info.DefaultInfoFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Default info factory implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer.Descriptor import Descriptor

from .ContextInfo import ContextInfo
from ..build.Factory import Factory


class DefaultInfoFactory(Factory):
    """
    Creates information components by their descriptors.

    See :class:`IFactory <pip_services3_components.build.IFactory.IFactory>`,
    :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>`
    """

    ContextInfoDescriptor = Descriptor("pip-services", "context-info", "default", "*", "1.0")
    ContainerInfoDescriptor = Descriptor("pip-services", "container-info", "default", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()
        self.register_as_type(DefaultInfoFactory.ContextInfoDescriptor, ContextInfo)
        self.register_as_type(DefaultInfoFactory.ContainerInfoDescriptor, ContextInfo)
