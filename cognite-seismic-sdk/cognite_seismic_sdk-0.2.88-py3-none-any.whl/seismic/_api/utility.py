import os
from enum import Enum
from typing import *

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import CRS, GeoJson, Geometry, Wkt
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import CoverageSpec, Identifier, Partition, SearchSpec
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        CreatePartitionRequest,
        EditPartitionRequest,
        SearchPartitionsRequest,
    )
    from google.protobuf.struct_pb2 import Struct
else:
    from cognite.seismic._api.shims import CoverageSpec, Identifier


MaybeString = Optional[str]
Metadata = Dict[str, str]
LineRange = Union[Tuple[int, int], Tuple[int, int, int]]


class Direction(Enum):
    """Enum of the major direction of VolumeDefs"""

    INLINE = 0
    XLINE = 1


def get_identifier(id: Optional[int] = None, external_id: MaybeString = None) -> Identifier:
    """Turn an id or external id into a v1.Identifier.

    Returns:
        Identifier: The created Identifier
    """
    if (id is not None) and (external_id is not None):
        raise Exception("You should only specify one of: id, external_id")
    if id is not None:
        return Identifier(id=id)
    elif external_id is not None:
        return Identifier(external_id=external_id)
    raise Exception("You must specify at least one of: id, external_id")


def get_search_spec(
    id: Optional[int] = None,
    external_id: MaybeString = None,
    external_id_substring: MaybeString = None,
    name: MaybeString = None,
    name_substring: MaybeString = None,
):
    """Turns kwargs into a SearchSpec.

    Returns:
        SearchSpec: The created SearchSpec.
    """
    spec = SearchSpec()
    if id is not None:
        if isinstance(id, int):
            spec.id = id
        else:
            spec.id_string = id
    if external_id is not None:
        spec.external_id = external_id
    if external_id_substring is not None:
        spec.external_id_substring = external_id_substring
    if name is not None:
        spec.name = name
    if name_substring is not None:
        spec.name_substring = name_substring
    return spec


def get_coverage_spec(crs: Optional[str] = None, format: Optional[str] = None) -> CoverageSpec:
    """Turns an optional crs and an optional string into a CoverageSpec."""
    if format is None:
        format = "wkt"

    if format == "wkt":
        return CoverageSpec(crs=crs, format=0)
    elif format == "geojson":
        return CoverageSpec(crs=crs, format=1)
    else:
        raise ValueError(f"Unknown format {format}")


def make_geometry(crs: Optional[str] = None, wkt: Optional[str] = None, geo_json: Optional[dict] = None):
    """Make a Geometry proto from python sdk arguments"""

    if wkt is not None and geo_json is not None:
        raise ValueError("Provide either wkt or gejson, not both")

    wrapped_crs = None if crs is None else CRS(crs=crs)

    if wkt is not None:
        return Geometry(crs=wrapped_crs, wkt=Wkt(geometry=wkt))
    elif geo_json is not None:
        geo_json_struct = Struct()
        geo_json_struct.update(geo_json)
        return Geometry(crs=wrapped_crs, geo=GeoJson(json=geo_json_struct))
    else:
        return None


def get_exact_match_filter(metadata: Mapping[str, str]):
    """Create an exact key-value match for SearchSpec"""

    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Filter, KeyValueExactMatch, MetadataFilter

    metadata_filter = MetadataFilter()
    for key, val in metadata.items():
        filter = Filter(key_value_exact_match=KeyValueExactMatch(key=key, value=val))
        metadata_filter.filters.append(filter)
    return metadata_filter


def _egcd(a: int, b: int) -> (int, int, int):
    """The extended euclidean algorithm"""
    # We want a >= b. If not, swap the arguments and the result.
    if a < b:
        g, t, s = _egcd(b, a)
        return g, s, t
    r_prev = a
    r = b
    s_prev = 1
    s = 0
    t_prev = 0
    t = 1
    while r != 0:
        q = r_prev // r
        r, r_prev = r_prev - q * r, r
        s, s_prev = s_prev - q * s, s
        t, t_prev = t_prev - q * t, t

    return r_prev, s_prev, t_prev
