from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

from . import gco, mcc

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_CellGeometryCode(Codelist):
    pass


@dataclass
class MD_TopologyLevelCode(Codelist):
    pass


@dataclass
class MD_DimensionNameTypeCode(Codelist):
    pass


@dataclass
class MD_GeometricObjectTypeCode(Codelist):
    pass


@dataclass
class MD_Dimension:
    dimensionName: Codelist[MD_DimensionNameTypeCode]
    dimensionSize: gco.Integer
    resolution: Optional[gco.Measure] = None
    dimensionTitle: Optional[gco.CharacterString] = None
    dimensionDescription: Optional[gco.CharacterString] = None


@dataclass
class MD_GeometricObjects:
    geometricObjectType: Codelist[MD_GeometricObjectTypeCode]
    geometricObjectCount: Optional[gco.Integer] = None


@dataclass
class MD_GridSpatialRepresentation(mcc.Abstract_SpatialRepresentation):
    numberOfDimensions: gco.Integer = gco.Integer(0)
    axisDimensionProperties: Optional[list[msr.MD_Dimension]] = field(
        default_factory=list
    )
    cellGeometry: Codelist[msr.MD_CellGeometryCode] = None
    transformationParameterAvailability: gco.Boolean = gco.Boolean(False)


@dataclass
class MD_VectorSpatialRepresentation(mcc.Abstract_SpatialRepresentation):
    topologyLevel: Optional[Codelist[MD_TopologyLevelCode]] = None
    geometricObjects: Optional[list[MD_GeometricObjects]] = field(
        default_factory=list
    )
