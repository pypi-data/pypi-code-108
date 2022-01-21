from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .. import types


@dataclass
class EX_Extent:
    description: Optional[str] = None
    geographicElement: list[AbstractEX_GeographicExtent] = field(
        default_factory=list
    )
    temporalElement: list[EX_TemporalExtent] = field(default_factory=list)
    verticalElement: list[EX_VerticalExtent] = field(default_factory=list)


@dataclass
class EX_VerticalExtent:
    minimumValue: str
    maximumValue: str
    verticalCRSId: Optional[types.mrs.MD_ReferenceSystem] = None
    verticalCRS: Optional[types.gml.AbstractCRS] = None


@dataclass
class EX_TemporalExtent:
    extent: types.gml.AbstractTimePrimitive


@dataclass
class AbstractEX_GeographicExtent:
    extentTypeCode: bool


@dataclass
class EX_GeographicDescription(AbstractEX_GeographicExtent):
    geographicIdentifier: types.mcc.MD_Identifier


@dataclass
class EX_BoundingPolygon(AbstractEX_GeographicExtent):
    polygon: list[types.gml.AbstractGeometry] = field(default_factory=list)


@dataclass
class EX_GeographicBoundingBox(AbstractEX_GeographicExtent):
    westBoundLongitude: str
    eastBoundLongitude: str
    southBoundLatitude: str
    northBoundLatitude: str
