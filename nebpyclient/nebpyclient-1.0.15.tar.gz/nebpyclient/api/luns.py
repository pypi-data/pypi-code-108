#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from .graphqlclient import GraphQLParam, NebMixin
from .common import PageInput, read_value
from .filters import UuidFilter, IntFilter
from .sorting import SortDirection
from .tokens import TokenResponse


class LunSort:
    """A sort object for LUNs

    Allows sorting LUNs on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            lun_id: SortDirection = None
    ):
        """Constructs a new sort object for LUNs

        :param lun_id: Sort direction for the ``lun_id`` property of a LUN
        :type lun_id: SortDirection, optional
        """

        self.__lun_id = lun_id

    @property
    def lun_id(self) -> SortDirection:
        """Sort direction for the ``lun_id`` property of a LUN"""
        return self.__lun_id

    @property
    def as_dict(self):
        result = dict()
        result["lunID"] = self.lun_id
        return result


class LunFilter:
    """A filter object to filter LUNs.

    Allows filtering for specific LUNs. The filter allows only one property to
    be specified. If filtering on multiple properties is needed, use the
    ``and_filter`` and ``or_filter`` options to concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            lun_id: IntFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on datacenter unique identifiers
        :type uuid: UuidFilter, optional
        :param lun_id: Filter based on ``lun_id`` property of a LUN
        :type lun_id: IntFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__lun_id = lun_id
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on LUN unique identifier"""
        return self.__uuid

    @property
    def lun_id(self) -> IntFilter:
        """Filter based on LUN ID"""
        return self.__lun_id

    @property
    def and_filter(self):
        """Allows concatenation of multiple filters via logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation of multiple filters via logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["uuid"] = self.uuid
        result["lunID"] = self.lun_id
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateLunInput:
    """An input object to create a LUN for a volume

    Allows the creation of a LUN for a volume. A LUN is an instance of a
    volume export that makes a volume accessible to a host.
    """

    def __init__(
            self,
            volume_uuid: str,
            lun_id: int = None,
            host_uuids: [str] = None,
            spu_serials: [str] = None,
            local: bool = None
    ):
        """Constructs a new input object to create a LUN for a volume

        Allows the creation of a LUN for a volume. A LUN is an instance of a
        volume export that makes a volume accessible to a host.

        At least one host must be specified via ``host_uuids`` or ``spu_serials`` -
        either one option must be specified but not both. If the ``local`` option
        is provided and set to ``True`` then the volume will be exported with
        ALUA, otherwise with ALUA turned off.

        :param volume_uuid: The unique identifier of the volume that shall be
            made available to a host
        :type volume_uuid: str
        :param lun_id: An optional LUN ID to export volumes with a specific ID
        :type lun_id: int
        :param host_uuids: List of host UUIDs that identify the hosts the
            volume shall be exported to. This must be provided if
            ``spu_serials`` is not provided.
        :type host_uuids: [str], optional
        :param spu_serials: List of SPU serials that identify the serials the
            volume shall be exported to. This must be provided if ``host_uuids``
            is not provided.
        :type spu_serials: [str], optional
        :param local: If provided and set to ``True`` then the volume will be
            exported with ALUA, otherwise with ALUA turned off.
        :type local: bool, optional
        """

        self.__volume_uuid = volume_uuid
        self.__host_uuids = host_uuids
        self.__spu_serials = spu_serials
        self.__lun_id = lun_id
        self.__local = local

    @property
    def volume_uuid(self) -> str:
        """The identifier of the volume that shall be exported to a host"""
        return self.__volume_uuid

    @property
    def host_uuids(self) -> [str]:
        """The hosts to which a volume shall be exported to"""
        return self.__host_uuids

    @property
    def spu_serials(self) -> [str]:
        """The SPUs from which a volume shall be exported from"""
        return self.__spu_serials

    @property
    def lun_id(self) -> int:
        """An optional LUN ID to assign to the volume export"""
        return self.__lun_id

    @property
    def local(self) -> bool:
        """If ``True``, volumes will be exported with ALUA turned on"""
        return self.__local

    @property
    def as_dict(self):
        result = dict()
        result["volumeUUID"] = self.volume_uuid
        result["hostUUIDs"] = self.host_uuids
        result["spuSerials"] = self.spu_serials
        result["lunID"] = self.lun_id
        result["local"] = self.local
        return result


class BatchDeleteLunInput:
    """An input object to delete multiple LUNs at once"""

    def __init__(
            self,
            volume_uuid: str,
            lun_uuids: [str] = None,
            host_uuids: [str] = None
    ):
        """Constructs a new input object to delete multiple LUNs

        Either ``lun_uuids`` or ``host_uuids`` must be specified, but not both.

        :param volume_uuid: The unique identifier of the volume from which the
            LUNs shall be deleted
        :type volume_uuid: str
        :param lun_uuids: The list of LUN identifiers that shall be deleted. If
            ``host_uuids`` is not specified this parameter is mandatory
        :type lun_uuids: [str], optional
        :param host_uuids: The list of host identifiers from which the LUNs
            shall be deleted. IF ``lun_uuids`` is not specified this parameter is
            mandatory
        :type host_uuids: [str], optional
        """

        self.__volume_uuid = volume_uuid
        self.__host_uuids = host_uuids
        self.__lun_uuids = lun_uuids

    @property
    def volume_uuid(self) -> str:
        """Identifier of the volume from which LUNs shall be deleted"""
        return self.__volume_uuid

    @property
    def host_uuids(self) -> [str]:
        """List of host identifiers from which LUNs shall be deleted"""
        return self.host_uuids

    @property
    def lun_uuids(self) -> [str]:
        """List of LUN identifiers that shall be deleted"""
        return self.__lun_uuids

    @property
    def as_dict(self):
        result = dict()
        result["lunUUIDs"] = self.lun_uuids
        result["volumeUUID"] = self.volume_uuid
        result["hostUUIDs"] = self.host_uuids
        return result


class Lun:
    """A LUN / an export of a volume to a host

    A LUN is an instance of a volume export that makes a volume accessible to
    a host.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new LUN object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__spu_serial = read_value(
            "spu.serial", response, str, True)
        self.__lun_id = read_value(
            "lunID", response, int, True)
        self.__volume_uuid = read_value(
            "volume.uuid", response, str, True)

    @property
    def uuid(self) -> str:
        """The unique identifier of the LUN"""
        return self.__uuid

    @property
    def spu_serial(self) -> str:
        """The SPU serial where the LUN is exported from"""
        return self.__spu_serial

    @property
    def lun_id(self) -> int:
        """The LUN ID of the volume export"""
        return self.__lun_id

    @property
    def volume_uuid(self) -> str:
        """The unique identifier of the volume that is exported"""
        return self.__volume_uuid

    @staticmethod
    def fields():
        return [
            "uuid",
            "spu{serial}",
            "lunID",
            "volume{uuid}",
        ]


class LunList:
    """Paginated LUN list object

    Contains a list of LUN objects and information for pagination. By default a
    single page includes a maximum of `100` items unless specified otherwise
    in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new LUN list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)
        self.__items = read_value(
            "items", response, Lun, True)

    @property
    def items(self) -> [Lun]:
        """List of LUN objects in the pagination list"""
        return self.__items

    @property
    def more(self) -> bool:
        """Indicates if there are more items on the server"""
        return self.__more

    @property
    def total_count(self) -> int:
        """The total number of items on the server"""
        return self.__total_count

    @property
    def filtered_count(self) -> int:
        """The number of items on the server matching the provided filter"""
        return self.__filtered_count

    @staticmethod
    def fields():
        return [
            "items{%s}" % (",".join(Lun.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class LunsMixin(NebMixin):
    """Mixin to add LUN related methods to the GraphQL client"""

    def get_luns(
            self,
            page: PageInput = None,
            lun_filter: LunFilter = None,
            sort: LunSort = None
    ) -> LunList:
        """Retrieves a list of LUN objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param lun_filter: A filter object to filter the LUNs on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type lun_filter: LunFilter, optional
        :param sort: A sort definition object to sort the LUN objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: LunSort, optional

        :returns LunList: A paginated list of LUNs.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            lun_filter, "LUNFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "LUNSort", False)

        # make the request
        response = self._query(
            name="getLUNs",
            params=parameters,
            fields=LunList.fields()
        )

        # convert to object
        return LunList(response)

    def create_lun(
            self,
            volume_uuid: str,
            lun_id: int = None,
            host_uuids: [str] = None,
            spu_serials: [str] = None,
            local: bool = None
    ):
        """Allows creation of a new LUN

        Allows the creation of a LUN for a volume. A LUN is an instance of a
        volume export that makes a volume accessible to a host.

        At least one host must be specified via ``host_uuids`` or ``spu_serials`` -
        either one option must be specified but not both. If the ``local`` option
        is provided and set to ``True`` then the volume will be exported with
        ALUA, otherwise with ALUA turned off.

        :param volume_uuid: The unique identifier of the volume that shall be
            made available to a host
        :type volume_uuid: str
        :param lun_id: An optional LUN ID to export volumes with a specific ID
        :type lun_id: int
        :param host_uuids: List of host UUIDs that identify the hosts the
            volume shall be exported to. This must be provided if
            ``spu_serials`` is not provided.
        :type host_uuids: [str], optional
        :param spu_serials: List of SPU serials that identify the serials the
            volume shall be exported to. This must be provided if ``host_uuids``
            is not provided.
        :type spu_serials: [str], optional
        :param local: If provided and set to ``True`` then the volume will be
            exported with ALUA, otherwise with ALUA turned off.
        :type local: bool, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateLunInput(
                volume_uuid=volume_uuid,
                host_uuids=host_uuids,
                spu_serials=spu_serials,
                lun_id=lun_id,
                local=local
            ),
            "CreateLUNInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createLUN",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def delete_lun(
            self,
            lun_uuid: str
    ):
        """Allows deletion of a LUN

        :param lun_uuid: The unique identifier of the LUN to delete
        :type lun_uuid: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(lun_uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteLUN",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def delete_luns(
            self,
            volume_uuid: str,
            lun_uuids: [str] = None,
            host_uuids: [str] = None
    ):
        """Allows deletion of multiple LUNs

        :param volume_uuid: The unique identifier of the volume from which the
            LUNs shall be deleted
        :type volume_uuid: str
        :param lun_uuids: The list of LUN identifiers that shall be deleted. If
            ``host_uuids`` is not specified this parameter is mandatory
        :type lun_uuids: [str], optional
        :param host_uuids: The list of host identifiers from which the LUNs
            shall be deleted. IF ``lun_uuids`` is not specified this parameter is
            mandatory
        :type host_uuids: [str], optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            BatchDeleteLunInput(
                volume_uuid=volume_uuid,
                lun_uuids=lun_uuids,
                host_uuids=host_uuids
            ),
            "BatchDeleteLUNInput",
            True
        )

        # make the request
        response = self._mutation(
            name="batchDeleteLUN",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        token_response = TokenResponse(response)
        token_response.deliver_token()
