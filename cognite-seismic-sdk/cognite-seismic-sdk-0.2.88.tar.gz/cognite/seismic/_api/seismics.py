import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import (
    LineRange,
    MaybeString,
    Metadata,
    get_coverage_spec,
    get_identifier,
    get_search_spec,
)
from cognite.seismic.data_classes.api_types import BinaryHeader, Geometry, Seismic, TextHeader, VolumeDef
from google.protobuf.struct_pb2 import Struct
from google.protobuf.wrappers_pb2 import Int32Value as i32
from google.protobuf.wrappers_pb2 import StringValue

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import CRS as CRSProto
    from cognite.seismic.protos.types_pb2 import GeoJson, Wkt
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import CoverageSpec, Identifier, OptionalMap
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import VolumeDef as VolumeDefPB
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        CreateSeismicRequest,
        DeleteSeismicRequest,
        DeleteSeismicResponse,
        EditSeismicRequest,
        SearchSeismicsRequest,
        VolumeRequest,
    )
else:
    from cognite.seismic._api.shims import Identifier


class SeismicAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    def create(
        self,
        *,
        external_id: str,
        partition_identifier: Union[int, str],
        seismic_store_id: int,
        name: MaybeString = None,
        volumedef: Optional[str] = None,
        geometry: Optional[Geometry] = None,
        empty: bool = False,
        metadata: Optional[Metadata] = None,
        copy_metadata: bool = False,
        text_header: Optional[TextHeader] = None,
        binary_header: Optional[BinaryHeader] = None,
    ) -> Seismic:
        """Create a new Seismic.

        If neither volumedef nor geometry are specified, the new Seismic will be able to access the entire seismic store it is derived from.

        Args:
            external_id (str): The external id of the new Seismic
            name (str | None): (Optional) If specified, the name of the new Seismic
            partition_identifier (int | str): Either the partition id or external_id that the Seismic is part of
            seismic_store_id (int): The seismic store that the new Seismic is derived from
            volumedef (str | None): (Optional) If specified, uses a VolumeDef as the shape of the Seismic
            geometry (Geometry | None): (Optional) If specified, uses a Geometry (either a WKT or GeoJson) as the shape of the Seismic
            empty (bool): If True, creates an empty seismic with no trace data included.
            metadata (Dict[str, str] | None): If specified, sets the metadata to the provided value.
            copy_metadata (bool): If True, ignores the `metadata` arg and copies the metadata from the seismic store.
            text_header (TextHeader | None): (Optional) If specified, sets the provided text header on the new seismic
            binary_header (BinaryHeader | None): (Optional) If specified, sets the provided binary header on the new seismic

        Returns:
            Seismic: The newly created Seismic with minimal data. Use search() or get() to retrieve all data.
        """
        if type(partition_identifier) == int:
            identifier = Identifier(id=partition_identifier)
        elif type(partition_identifier) == str:
            identifier = Identifier(external_id=partition_identifier)
        else:
            raise Exception("partition_identifier should be an int or a str.")

        request = CreateSeismicRequest(external_id=external_id, partition=identifier, seismic_store_id=seismic_store_id)
        if volumedef is not None:
            request.volume_def.MergeFrom(VolumeDefPB(json=volumedef))
        elif geometry is not None:
            request.geometry.MergeFrom(geometry.to_proto())
        elif empty:
            request.empty = True

        if name is not None:
            request.name = name

        if metadata is not None:
            request.metadata.MergeFrom(OptionalMap(data=metadata))

        if copy_metadata:
            request.copy_metadata = True

        if text_header is not None:
            request.text_header.MergeFrom(text_header.into_proto())

        if binary_header is not None:
            request.binary_header.MergeFrom(binary_header.into_proto())

        return Seismic.from_proto(self.query.CreateSeismic(request))

    def search(
        self,
        mode: str = "seismic",
        *,
        id: Optional[int] = None,
        external_id: MaybeString = None,
        external_id_substring: MaybeString = None,
        name: MaybeString = None,
        name_substring: MaybeString = None,
        include_text_header: bool = False,
        include_binary_header: bool = False,
        include_line_range: bool = False,
        include_volume_definition: bool = False,
        include_seismic_store: bool = False,
        include_partition: bool = False,
        include_coverage=False,
        coverage_crs: Optional[str] = None,
        coverage_format: Optional[str] = None,
        get_all: bool = False,
    ) -> Iterable[Seismic]:
        """Search for seismics.

        Can search all seismics included in surveys, partitions, or directly search seismics,
        specified by id, external_id, name, or substrings of external_id or name.
        Only one search method should be specified. The behaviour when multiple are specified is undefined.

        Args:
            mode (str): One of "survey", "seismic" or "partition".
            id (int|None): id to search by
            external_id (str|None): external id to search by
            external_id_substring (str|None): Substring of external id to search by
            name (str|None): Name to search by
            name_substring (str|None): Substring of name to search by

            include_text_header (bool): If true, includes the text header in the responses
            include_binary_header (bool): If true, includes the binary header in the responses
            include_line_range (bool): If true, includes the line range in the responses
            include_volume_definition (bool): If true, includes the volume def in the responses
            include_seismic_store (bool): If true, include the seismic store info in the responses
            include_partition (bool): If true, include the partition info in the responses
            coverage_crs (str|None): If specified, includes the coverage in the given CRS. Either coverage_crs or coverage_format must be specified to retrieve coverage.
            coverage_format (str|None): One of "wkt", "geojson". If specified, includes the coverage as the given format.
            get_all (bool): Whether to instead retrieve all visible Seismic. Equivalent to list().

        Returns:
            Iterable[Seismic]: The list of matching Seismics
        """

        if include_coverage:
            raise DeprecationWarning(
                """include_coverage is deprecated. Use coverage_crs and coverage_format instead.
For example, search(coverage_format="wkt") is identical to using include_coverage=True. Refer to the SDK documentation for more info.
"""
            )

        if coverage_crs is not None or coverage_format is not None:
            coverage = get_coverage_spec(coverage_crs, coverage_format)
        else:
            coverage = None

        if get_all:
            req = SearchSeismicsRequest(coverage=coverage)
        else:
            spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)
            if mode == "seismic":
                req = SearchSeismicsRequest(seismic=spec, coverage=coverage)
            elif mode == "survey":
                req = SearchSeismicsRequest(survey=spec, coverage=coverage)
            elif mode == "partition":
                req = SearchSeismicsRequest(partition=spec, coverage=coverage)
            else:
                raise Exception("mode should be one of: survey, seismic, partition")

        req.include_text_header = include_text_header
        req.include_binary_header = include_binary_header
        req.include_line_range = include_line_range
        req.include_volume_definition = include_volume_definition
        req.include_seismic_store = include_seismic_store
        req.include_partition = include_partition

        results = self.query.SearchSeismics(req)
        for s in results:
            yield Seismic.from_proto(s)

    def list(
        self,
        *,
        include_text_header: bool = False,
        include_binary_header: bool = False,
        include_line_range: bool = False,
        include_volume_definition: bool = False,
        include_seismic_store: bool = False,
        include_partition: bool = False,
        coverage_crs: MaybeString = None,
        coverage_format: MaybeString = None,
    ) -> Iterable[Seismic]:
        return self.search(
            get_all=True,
            include_text_header=include_text_header,
            include_binary_header=include_binary_header,
            include_line_range=include_line_range,
            include_volume_definition=include_volume_definition,
            include_seismic_store=include_seismic_store,
            include_partition=include_partition,
            coverage_crs=coverage_crs,
            coverage_format=coverage_format,
        )

    def get(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        coverage_crs: MaybeString = None,
        coverage_format: MaybeString = None,
    ) -> Seismic:
        """Get a seismic by id or external id.

        Equivalent to search("seismic", id=) or search("seismic", external_id=), returning all info.

        Args:
            id (int | None): id of seismic to get
            external_id (str | None): external id of seismic to get
            coverage_crs (str | None): The CRS of the received coverage. Defaults to the file's CRS.
            coverage_format (str | None): The desired file format for the coverage. Defaults to WKT.

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.Seismic`: The matching seismic
        """
        if id is None and external_id is None:
            raise Exception("Need to provide either the seismic id or external id")

        result = [
            x
            for x in self.search(
                "seismic",
                id=id,
                external_id=external_id,
                include_text_header=True,
                include_binary_header=True,
                include_line_range=True,
                include_volume_definition=True,
                include_seismic_store=True,
                include_partition=True,
                coverage_crs=coverage_crs,
                coverage_format=coverage_format,
            )
        ]

        if len(result) > 1:
            raise Exception("Multiple seismics found. Please contact support")
        elif len(result) == 0:
            if id is not None:
                msg = f"Seismic with id '{id}'' not found"
            else:
                msg = f"Seismic with external id '{external_id}' not found"
            raise Exception(msg)
        return result[0]

    def edit(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        name: MaybeString = None,
        metadata: Union[Metadata, None] = None,
    ) -> Seismic:
        """Edit an existing seismic.

        Either the id or the external_id should be provided in order to identify the seismic.
        The editable fields are name and metadata. Providing a name or metadata field will replace the existing data with the new data. Providing an empty string as the name will delete the seismic name.

        Args:
            id (int | None): The id of the seismic
            external_id (str | None): The external id of the seismic
            name (str | None): (Optional) The new name of the seismic
            metadata (Dict[str, str] | None): (Optional) The new metadata for the seismic

        Returns:
            Seismic: The edited Seismic with minimal data. Use search() to retrieve all data.
        """
        identifier = get_identifier(id, external_id)
        request = EditSeismicRequest(seismic=identifier)
        if name is not None:
            request.name.CopyFrom(StringValue(value=name))
        if metadata is not None:
            request.metadata.MergeFrom(OptionalMap(data=metadata))

        return Seismic.from_proto(self.query.EditSeismic(request))

    def delete(self, *, id: Union[int, None] = None, external_id: MaybeString = None) -> bool:
        """Delete a seismic

        Either the id or the external id should be provided in order to identify the seismic.

        Args:
            id (int | None): The id of the seismic
            external_id (str | None): The external id of the seismic

        Returns:
            bool: True if successful
        """
        identifier = get_identifier(id, external_id)
        request = DeleteSeismicRequest(seismic=identifier)

        return self.query.DeleteSeismic(request).succeeded
