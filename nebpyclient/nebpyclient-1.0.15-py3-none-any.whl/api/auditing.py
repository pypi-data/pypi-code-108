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
from .common import PageInput, NebEnum, read_value
from datetime import datetime

__all__ = [
    "AuditingMixin",
    "AuditLogFilter",
    "AuditLogList",
    "AuditLogEntry",
    "AuditStatus"
]


class AuditStatus(NebEnum):
    """Defines the status of a record in the audit log"""

    InProgress = "InProgress"
    """Operation is still ongoing"""

    Completed = "Completed"
    """Operation completed successfully"""

    Failed = "Failed"
    """Operation failed"""


class AuditLogFilter:
    """A filter object to filter audit log entries

    Allows filtering for specific audit log entries in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            start_after: datetime = None,
            start_before: datetime = None,
            operation: str = None,
            component: str = None,
            npod_uuid: str = None,
            spu_serial: str = None,
            status: AuditStatus = None
    ):
        """Constructs a new filter object

        :param start_after: Filter audit records to include only records that
            were created after the specified date and time
        :type start_after: datetime, optional
        :param start_before: Filter audit records to include only records that
            were created before the specified date and time
        :type start_before: datetime, optional
        :param operation: Filter audit records to include only records that
            match the specified operation name TODO: Add options
        :type operation: str, optional
        :param component: Filter audit records to include only records that
            match the specified component TODO: Add options
        :param npod_uuid: Filter audit records to include only records that
            are associated with the specified nPod unique identifier
        :type npod_uuid: str, optional
        :param spu_serial: Filter audit records to include only records that
            are associated with the specified services processing unit serial
            number
        :type spu_serial: str, optional
        :param status: Filter audit records to include only records that match
            the specified operation status
        :type status: AuditStatus, optional
        """

        self.__start_after = start_after
        self.__start_before = start_before
        self.__operation = operation
        self.__component = component
        self.__npod_uuid = npod_uuid
        self.__spu_serial = spu_serial
        self.__status = status

    @property
    def start_after(self) -> datetime:
        """Filter for records created after the specified date and time"""
        return self.__start_after

    @property
    def start_before(self) -> datetime:
        """Filter for records created before the specified date and time"""
        return self.__start_before

    @property
    def operation(self) -> str:
        """Filter for records that match the specified operation name"""
        return self.__operation

    @property
    def component(self) -> str:
        """Filter for records that match the specified component type"""
        return self.__component

    @property
    def npod_uuid(self) -> str:
        """Filter for records that match the specified nPod UUID"""
        return self.__npod_uuid

    @property
    def spu_serial(self) -> str:
        """Filter for records that match the specified SPU serial number"""
        return self.__spu_serial

    @property
    def status(self) -> AuditStatus:
        """Filter for records that match the specified operation status"""
        return self.__status

    @property
    def as_dict(self) -> dict:
        result = dict()
        result["startAfter"] = self.start_after
        result["startBefore"] = self.start_before
        result["operation"] = self.operation
        result["component"] = self.component
        result["nPodUUID"] = self.npod_uuid
        result["spuSerial"] = self.spu_serial
        result["status"] = self.status
        return result


class AuditLogEntry:
    """Instance of an audit record entry in nebulon ON

    An audit record entry represents an action that a user performed in
    nebulon ON. Actions include exclusively commands that alter the
    configuration of resources in nebulon ON or in your infrastructure. Queries
    that read configuration information are not included in the audit record
    list.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new audit record instance object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__operation = read_value(
            "operation", response, str, True)
        self.__parameters = read_value(
            "parameters", response, str, True)
        self.__start = read_value(
            "start", response, datetime, True)
        self.__finish = read_value(
            "finish", response, datetime, False)
        self.__status = read_value(
            "status", response, AuditStatus, True)
        self.__error = read_value(
            "error", response, str, True)
        self.__component = read_value(
            "component", response, str, True)
        self.__component_id = read_value(
            "componentID", response, str, True)
        self.__user_uuid = read_value(
            "user.uuid", response, str, False)
        self.__user_name = read_value(
            "user.name", response, str, False)
        self.__npod_uuid = read_value(
            "nPod.uuid", response, str, False)
        self.__spu_serial = read_value(
            "spu.serial", response, str, False)
        self.__client_ip = read_value(
            "clientIP", response, str, True)
        self.__client_app = read_value(
            "clientApp", response, str, True)
        self.__client_platform = read_value(
            "clientPlatform", response, str, True)

    @property
    def operation(self) -> str:
        """The operation a user executed"""
        return self.__operation

    @property
    def parameters(self) -> str:
        """Parameters that were supplied with the operation"""
        return self.__parameters

    @property
    def start(self) -> datetime:
        """Start time for the operation"""
        return self.__start

    @property
    def finish(self) -> datetime:
        """Completion time for the operation"""
        return self.__finish

    @property
    def status(self) -> AuditStatus:
        """Status of the operation"""
        return self.__status

    @property
    def error(self) -> str:
        """Error message associated with the operation"""
        return self.__error

    @property
    def component(self) -> str:
        """Affected component by the operation"""
        return self.__component

    @property
    def component_id(self) -> str:
        """Identifier of the affected component"""
        return self.__component_id

    @property
    def user_uuid(self) -> str:
        """Unique identifier of the user that executed the operation"""
        return self.__user_uuid

    @property
    def user_name(self) -> str:
        """Name of the user that executed the operation"""
        return self.__user_name

    @property
    def npod_uuid(self) -> str:
        """Unique identifier of the nPod involved in the operation"""
        return self.__npod_uuid

    @property
    def spu_serial(self) -> str:
        """Serial number of the SPU involved in the operation"""
        return self.__spu_serial

    @property
    def client_ip(self) -> str:
        """IP address of the client that invoked the operation"""
        return self.__client_ip

    @property
    def client_app(self) -> str:
        """Client application identifier from which the operation was called"""
        return self.__client_app

    @property
    def client_platform(self) -> str:
        """Client platform information from which the operation was called"""
        return self.__client_platform

    @staticmethod
    def fields():
        return [
            "operation",
            "parameters",
            "start",
            "finish",
            "status",
            "error",
            "component",
            "componentID",
            "user{uuid,name}",
            "nPod{uuid}",
            "spu{serial}",
            "clientIP",
            "clientApp",
            "clientPlatform",
        ]


class AuditLogList:
    """Paginated audit record list object

    Contains a list of audit records and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response
    ):
        """Constructs a new audit record list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: If illegal data is returned from the server
        """
        self.__more = read_value(
            "more", response, bool, True)
        self.__items = read_value(
            "items", response, AuditLogEntry, True)

    @property
    def items(self) -> [AuditLogEntry]:
        """List of audit log entries in the pagination list"""
        return self.__items

    @property
    def more(self) -> bool:
        """Indicates if there are more items on the server"""
        return self.__more

    @staticmethod
    def fields():
        return [
            "more",
            "items{%s}" % (",".join(AuditLogEntry.fields())),
        ]


class AuditingMixin(NebMixin):
    """Mixin to add audit log related methods to the GraphQL client"""

    def get_audit_records(
            self,
            page: PageInput = None,
            audit_filter: AuditLogFilter = None
    ) -> AuditLogList:
        """Retrieves a list of audit records

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param audit_filter: A filter object to filter the audit records on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type audit_filter: AuditLogFilter, optional

        :returns AuditLogList: A paginated list of audit records

        :raises GraphQLError: An error with the GraphQL endpoint
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            audit_filter, "AuditLogFilter", False)

        # make the request
        response = self._query(
            name="getAuditLog",
            params=parameters,
            fields=AuditLogList.fields()
        )

        # convert to object
        return AuditLogList(response)
