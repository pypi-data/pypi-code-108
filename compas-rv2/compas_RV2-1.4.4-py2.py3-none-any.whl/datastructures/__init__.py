"""
********************************************************************************
compas_rv2.datastructures
********************************************************************************

.. currentmodule:: compas_rv2.datastructures

Patterns
========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Skeleton
    Pattern


Diagrams
========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    FormDiagram
    ForceDiagram
    ThrustDiagram

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .meshmixin import MeshMixin
from .subdmesh import SubdMesh
from .skeleton import Skeleton
from .pattern import Pattern
from .formdiagram import FormDiagram
from .forcediagram import ForceDiagram
from .thrustdiagram import ThrustDiagram

__all__ = [
    'MeshMixin',
    "SubdMesh",
    'Skeleton',
    'Pattern',
    'FormDiagram',
    'ForceDiagram',
    'ThrustDiagram'
]
