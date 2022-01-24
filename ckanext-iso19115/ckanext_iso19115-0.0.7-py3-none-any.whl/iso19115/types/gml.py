from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class GenericMetaData:
    pass


@dataclass
class AbstractSurface:
    pass


@dataclass
class AbstractCurve:
    pass


@dataclass
class AbstractCurveSegment:
    pass


@dataclass
class AbstractSolid:
    pass


@dataclass
class AbstractGeometricPrimitive:
    pass


@dataclass
class AbstractSurfacePatch:
    pass


@dataclass
class AbstractRing:
    pass


@dataclass
class AbstractGeometry:
    metaDataProperty: list[GenericMetaData] = field(default_factory=list)
    description: Optional[str] = None
    # descriptionReference
    # identifier
    name: Optional[str] = None


@dataclass
class ArcStringByBulge(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)
    bulge: list[str] = field(default_factory=list)


@dataclass
class LineStringSegment(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)


@dataclass
class GeodesicString(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    pointProperty: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)


@dataclass
class BSpline(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)
    degree: int = 0
    knot: Optional[Knot] = None


@dataclass
class OffsetCurve(AbstractCurveSegment):
    offsetBase: Optional[AbstractCurve] = None
    distance: Optional[str] = None


@dataclass
class ArcByCenterPoint(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)
    radius: Optional[str] = None
    startAngle: Optional[str] = None
    endAngle: Optional[str] = None


@dataclass
class ArcString(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)


@dataclass
class CubicSpline(AbstractCurveSegment):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)


@dataclass
class Clothoid(AbstractCurveSegment):
    refLocation: Optional[AffinePlacement] = None
    scaleFactor: Optional[str] = None
    startParameter: Optional[str] = None
    endParameter: Optional[str] = None


@dataclass
class AffinePlacement:
    location: list[str] = field(default_factory=list)
    inDimension: Optional[int] = None
    outDimension: Optional[int] = None


@dataclass
class LineString(AbstractGeometry, AbstractGeometricPrimitive, AbstractCurve):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)


@dataclass
class MultiSurface(AbstractGeometry):
    surfaceMember: list[AbstractSurface] = field(default_factory=list)
    surfaceMembers: list[AbstractSurface] = field(default_factory=list)


@dataclass
class MultiCurve(AbstractGeometry):
    curveMember: list[AbstractCurve] = field(default_factory=list)
    curveMembers: list[AbstractCurve] = field(default_factory=list)


@dataclass
class Curve(AbstractGeometry, AbstractGeometricPrimitive, AbstractCurve):
    segments: list[AbstractCurveSegment] = field(default_factory=list)


@dataclass
class Grid(AbstractGeometry):
    limirs: Optional[GridEnvelope] = None
    axisLabels: list[str] = field(default_factory=list)
    axisName: list[str] = field(default_factory=list)


@dataclass
class MultiPoint(AbstractGeometry):
    pointMember: list[Point] = field(default_factory=list)
    pointMembers: list[Point] = field(default_factory=list)


@dataclass
class CompositeSolid(
    AbstractGeometry, AbstractGeometricPrimitive, AbstractSolid
):
    solidMember: list[AbstractSolid] = field(default_factory=list)


@dataclass
class Ring(
    AbstractGeometry, AbstractRing, AbstractGeometricPrimitive, AbstractCurve
):
    curveMember: list[AbstractCurve] = field(default_factory=list)


@dataclass
class MultiSolid(AbstractGeometry):
    solidMember: list[AbstractSolid] = field(default_factory=list)
    solidMembers: list[AbstractSolid] = field(default_factory=list)


@dataclass
class Shell(AbstractGeometry, AbstractGeometricPrimitive, AbstractSurface):
    surfaceMember: list[AbstractSurface] = field(default_factory=list)


@dataclass
class MultiGeometry(AbstractGeometry):
    geometryMember: list[AbstractGeometry] = field(default_factory=list)
    geometryMembers: list[AbstractGeometry] = field(default_factory=list)


@dataclass
class CompositeSurface(
    AbstractGeometry, AbstractGeometricPrimitive, AbstractSurface
):
    surfaceMember: list[AbstractSurface] = field(default_factory=list)


@dataclass
class Point(AbstractGeometry, AbstractGeometricPrimitive):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None


@dataclass
class CompositeCurve(
    AbstractGeometry, AbstractGeometricPrimitive, AbstractCurve
):
    curveMember: list[AbstractCurve] = field(default_factory=list)


@dataclass
class OrientableCurve(
    AbstractGeometry, AbstractGeometricPrimitive, AbstractCurve
):
    baseCurve: list[AbstractCurve] = field(default_factory=list)


@dataclass
class Solid(AbstractGeometry, AbstractGeometricPrimitive, AbstractSolid):
    exterior: Optional[Shell] = None
    interior: list[Shell] = field(default_factory=list)


@dataclass
class LinearRing(
    AbstractGeometry, AbstractRing, AbstractGeometricPrimitive, AbstractCurve
):
    pos: list[str] = field(default_factory=list)
    coordinates: Optional[str] = None
    pointProperty: list[Point] = field(default_factory=list)
    pointRep: list[Point] = field(default_factory=list)
    posList: list[str] = field(default_factory=list)


@dataclass
class GeometricComplex(AbstractGeometry):
    element: list[AbstractGeometricPrimitive] = field(default_factory=list)


@dataclass
class OrientableSurface(
    AbstractGeometry, AbstractGeometricPrimitive, AbstractSurface
):
    baseSurface: Optional[AbstractSurface] = None


@dataclass
class Surface(AbstractGeometry, AbstractGeometricPrimitive, AbstractSurface):
    patches: list[AbstractSurfacePatch] = field(default_factory=list)


@dataclass
class Polygon(AbstractGeometry, AbstractGeometricPrimitive, AbstractSurface):
    exterior: Optional[AbstractRing] = None
    interior: list[AbstractRing] = field(default_factory=list)


@dataclass
class GridEnvelope:
    low: list[str] = field(default_factory=list)
    high: list[str] = field(default_factory=list)


@dataclass
class Rectangle(AbstractSurfacePatch):
    exterior: Optional[AbstractRing] = None


@dataclass
class Cone(AbstractSurfacePatch):
    rows: list[Row] = field(default_factory=list)


@dataclass
class Triangle(AbstractSurfacePatch):
    exterior: Optional[AbstractRing] = None


@dataclass
class PolygonPatch(AbstractSurfacePatch):
    exterior: Optional[AbstractRing] = None
    interior: list[AbstractRing] = field(default_factory=list)


@dataclass
class Sphere(AbstractSurfacePatch):
    rows: list[Row] = field(default_factory=list)


@dataclass
class Cylinder(AbstractSurfacePatch):
    rows: list[Row] = field(default_factory=list)


@dataclass
class Row:
    pointProperty: Point
    posList: list[str] = field(default_factory=list)
    pos: list[str] = field(default_factory=list)


@dataclass
class Knot:
    value: str
    weight: str
    multiplicity: Optional[int] = None


@dataclass
class AbstractTimePrimitive:
    metaDataProperty: list[GenericMetaData] = field(default_factory=list)
    description: Optional[str] = None
    # descriptionReference
    # identifier
    name: Optional[str] = None
    relatedTime: list[AbstractTimePrimitive] = field(default_factory=list)


@dataclass
class TimePeriod(AbstractTimePrimitive):
    beginPosition: Optional[str] = None
    endPosition: Optional[str] = None
    begin: Optional[TimeInstant] = None
    end: Optional[TimeInstant] = None
    duration: Optional[str] = None
    timeInterval: Optional[str] = None


@dataclass
class TimeEdge(AbstractTimePrimitive):
    start: Optional[TimeNode] = None
    end: Optional[TimeInstant] = None
    extent: Optional[TimePeriod] = None


@dataclass
class TimeInstant(AbstractTimePrimitive):
    timePosition: Optional[str] = None


@dataclass
class TimeNode(AbstractTimePrimitive):
    previousEdge: list[TimeEdge] = field(default_factory=list)
    nextEdge: list[TimeEdge] = field(default_factory=list)
    position: Optional[TimeInstant] = None


@dataclass
class AbstractCRS:
    metaDataProperty: list[GenericMetaData] = field(default_factory=list)
    description: Optional[str] = None
    # descriptionReference
    # identifier
    name: Optional[str] = None
    remarks: Optional[str] = None
    scope: list[str] = field(default_factory=list)


@dataclass
class UnitDefinition:
    metaDataProperty: Optional[list[GenericMetaData]] = field(
        default_factory=list
    )
    description: Optional[str] = None
    descriptionReference: Optional[Any] = None
    identifier: Any = None
    name: Optional[list[str]] = field(default_factory=list)
    remarks: Optional[str] = None
    quantityType: Optional[str] = None
    quantityTypeReference: Optional[str] = None
    catalogSymbol: Optional[str] = None
