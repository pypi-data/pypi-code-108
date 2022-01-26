# -*- coding: utf-8 -*-
"""
    pip_services3_container.refer.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the inversion of control design pattern but does not contain the fully
    functional container (we can just only create a class that will set various references).

    Once the objects of a container are configured, if they implement the IReferencable interface,
    they are passed a set of references for recreating links between objects in the container.
    If objects implement the IOpenable interface, the :func:`open()` method is called and they start to work.
    Connections to various services are made, after which the objects start,
    the container starts running, and the objects carry out their tasks. When the container starts to close,
    the objects that implement the ICloseable interface are closed via their
    :func:`close()` method (which should make them stop working and disconnect from other services),
    after which objects that implement the IUnreferenceable interface delete various links between objects,
    and, finally, the contains destroys all objects and turns off.

    :class:`BuildReferencesDecorator`, :class:`LinkReferencesDecorator`, and
    :class:`RunReferencesDecorator` - ReferenceDecorators are used during the corresponding building, linking,
    and running stages and are united in :class:`ManagedReferences`, which are extended by :class:`ContainerReferences`.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['ReferencesDecorator', 'RunReferencesDecorator', 'LinkReferencesDecorator',
           'BuildReferencesDecorator', 'ManagedReferences', 'ContainerReferences']

from .BuildReferencesDecorator import BuildReferencesDecorator
from .ContainerReferences import ContainerReferences
from .LinkReferencesDecorator import LinkReferencesDecorator
from .ManagedReferences import ManagedReferences
from .ReferencesDecorator import ReferencesDecorator
from .RunReferencesDecorator import RunReferencesDecorator
