# Copyright 2020 Cognite AS

import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import MaybeString, get_identifier, get_search_spec
from cognite.seismic.data_classes.api_types import File
from cognite.seismic.data_classes.errors import NotFoundError
from google.protobuf.struct_pb2 import Struct
from grpc import StatusCode

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import CRS, GeoJson, Geometry, LineBasedRectangle, PositionQuery, Wkt
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        SearchFilesRequest,
        SegYSeismicRequest,
        SegYSeismicResponse,
    )
else:
    from cognite.seismic._api.shims import SegYSeismicResponse


class FileSeismicAPI(API):
    def __init__(self, query, ingestion, client):
        super().__init__(query=query, ingestion=ingestion)
        self.client = client

    def get_segy(
        self, *, id: Union[int, None] = None, external_id: MaybeString = None, seismic_store_id: Union[int, None] = None
    ) -> Iterable[SegYSeismicResponse]:
        """
        Get SEGY file

        Provide one of: the seismic id, the seismic external id, the seismic store id.

        Args:
            id (int | None): The id of the seismic to retrieve traces from.
            external_id (str | None): The external id of the seismic to retrieve traces from.
            seismic_store_id (int | None): The id of the seismic store to retrieve traces from. Only permitted for data managers.
            
        The returned stream of SegYSeismicResponse objects have a content attribute each containing a fragment of the SEG-Y file.
        Write these to disk in the order received, or stream to a receiver expecting a SEGY bytestream.

        Returns: An iterable of SegYSeismicResponse: SEGY file
        """
        request = SegYSeismicRequest()
        if seismic_store_id:
            request.seismic_store_id = seismic_store_id
        else:
            request.seismic.MergeFrom(get_identifier(id, external_id))

        return (i for i in self.query.GetSegYFile(request))

    def get_segy_by_lines(
        self,
        *,
        id: Optional[int] = None,
        external_id: MaybeString = None,
        seismic_store_id: Optional[int] = None,
        top_left_inline: Optional[int] = None,
        top_left_xline: Optional[int] = None,
        bottom_right_inline: Optional[int] = None,
        bottom_right_xline: Optional[int] = None,
    ) -> Iterable[SegYSeismicResponse]:
        """
        Get a part of a SEGY file with data inside a given range of inlines and xlines

        Provide one of: the seismic id, the seismic external id, the seismic store id.

        Args:
            id (int | None): The id of the seismic to retrieve traces from.
            external_id (str | None): The external id of the seismic to retrieve traces from.
            seismic_store_id (int | None): The id of the seismic store to retrieve traces from. Only permitted for data managers.
            top_left_inline (int | None): Top left inline.
            top_left_xline (int | None): Top left xline.
            bottom_right_inline (int | None): Bottom right inline.
            bottom_right_xline (int | None): Bottom right xline.

        The returned stream of SegYSeismicResponse objects have a content attribute each containing a fragment of the SEG-Y file.
        Write these to disk in the order received, or stream to a receiver expecting a SEGY bytestream.

        Returns: An iterable of SegYSeismicResponse: SEGY file
        """
        top_left = PositionQuery(iline=top_left_inline, xline=top_left_xline)
        bottom_right = PositionQuery(iline=bottom_right_inline, xline=bottom_right_xline)
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)
        request = SegYSeismicRequest(lines=rectangle)
        if seismic_store_id:
            request.seismic_store_id = seismic_store_id
        else:
            request.seismic.MergeFrom(get_identifier(id, external_id))

        return (i for i in self.query.GetSegYFile(request))

    def get_segy_by_geometry(
        self,
        *,
        id: Optional[int] = None,
        external_id: MaybeString = None,
        seismic_store_id: Optional[int] = None,
        crs: str = None,
        wkt: str = None,
        geo_json=None,
    ) -> Iterable[SegYSeismicResponse]:
        """
        Get a part of a SEGY file with data inside an arbitrary 2D polygon.

        Provide one of: the seismic id, the seismic external id, the seismic store id.
        Provide one of: wkt, geo_json.

        Args:
            id (int | None): The id of the seismic to retrieve traces from.
            external_id (str | None): The external id of the seismic to retrieve traces from.
            seismic_store_id (int | None): The id of the seismic store to retrieve traces from. Only permitted for data managers.
            crs (str): CRS
            wkt (str): polygon in WKT format
            geo_json (dict): polygon in geoJson format

        The returned stream of SegYSeismicResponse objects have a 'content' attribute each containing a fragment of the SEG-Y file.
        Write these to disk in the order received, or stream to a receiver expecting a SEGY bytestream.

        Returns: An iterable of SegYSeismicResponse: SEGY file
        """
        self._verify_input(crs, wkt, geo_json)
        if geo_json:
            geo_json_struct = Struct()
            geo_json_struct.update(geo_json)
            geo = Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json_struct))
        else:
            geo = Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))
        request = SegYSeismicRequest(polygon=geo)
        if seismic_store_id:
            request.seismic_store_id = seismic_store_id
        else:
            request.seismic.MergeFrom(get_identifier(id, external_id))

        return (i for i in self.query.GetSegYFile(request))

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def list(self) -> List[File]:
        """List all files.

        Returns:
            List[:py:class:`~cognite.seismic.data_classes.api_types.File`]: A list of Files.
        """
        request = SearchFilesRequest()
        return [File.from_proto(f) for f in self.query.SearchFiles(request)]

    def search(
        self,
        *,
        id: MaybeString = None,
        external_id: MaybeString = None,
        external_id_substring: MaybeString = None,
        name: MaybeString = None,
        name_substring: MaybeString = None,
    ) -> Iterable[File]:
        """Search for files.

        Args:
            id (str | None): A string id to search for
            name (str | None): A name to search for
            name_substring (str | None): Substring of a name to search for

        Returns:
            Iterable[:py:class:`~cognite.seismic.data_classes.api_types.File`]: A list of found Files.
        """
        spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)

        req = SearchFilesRequest(spec=spec)

        return (File.from_proto(f) for f in self.query.SearchFiles(req))

    def get(self, *, id: Optional[str], external_id: Optional[str] = None) -> File:
        """Fetch a file by id.

        Args:
            file_id (str): The id of the file to fetch

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.File`: The retrieved file
        """

        result = self.search(id=id)
        try:
            [file] = result
        except ValueError:
            raise NotFoundError(status=StatusCode.NOT_FOUND, message=f"File with id {id} not found")
        return file

    ### The following operations are wrappers for various ingestion APIs.
    def register(self, *args, **kwargs):
        """See :py:func:`~cognite.seismic._api.file.FileAPI.register`"""
        self.client.file.register(*args, **kwargs)
