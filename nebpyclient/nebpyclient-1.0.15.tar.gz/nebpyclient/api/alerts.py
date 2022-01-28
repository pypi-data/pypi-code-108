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
from .common import PageInput, NebEnum, ResourceType, read_value
from datetime import datetime

__all__ = [
    "Alert",
    "AlertFilter",
    "AlertsMixin",
    "AlertStatus",
    "AlertList",
    "AlertSeverity"
]


class AlertSeverity(NebEnum):
    """Defines the severity of an alert"""

    Unknown = "Unknown"
    """Alert severity is not known"""

    Urgent = "Urgent"
    """
    Alert severity indicates complete loss of functionality or data
    unavailability and requires immediate attention by service owners.
    """

    Critical = "Critical"
    """
    Alert severity indicates complete loss of functionality or data
    unavailability and requires immediate attention by service owners.
    """

    Major = "Major"
    """
    Alert severity indicates that there is partial loss of functionality or 
    partial data unavailability, no redundancy in a service (failure of one
    more resource will cause an outage) and requires immediate attention by
    service owners.
    """

    Minor = "Minor"
    """
    Alert severity indicates that there is no loss in functionality, performance
    and stability issues that require attention by service owners
    """

    Trivial = "Trivial"
    """
    Alert severity indicates that there is no loss in functionality, only minor
    impacts to performance, or cosmetic issues or bugs, not affecting the 
    customer's ability to use the product
    """


class AlertStatus(NebEnum):
    """Defines the status of an alert"""

    Unknown = "Unknown"
    """Status of the alert is not known"""

    Open = "Open"
    """The alert is not resolved"""

    Closed = "Closed"
    """The alert is resolved"""


class AlertFilter:
    """A filter object to filter alerts.

    Allows filtering for specific alerts in nebulon ON. The
    filter allows multiple properties to be specified. If multiple properties
    are provided they are concatenated with a logical AND.
    """

    def __init__(
            self,
            created_after: datetime = None,
            created_before: datetime = None,
            severity: AlertSeverity = None,
            resource_type: ResourceType = None,
            resource_id: str = None,
            status: AlertStatus = None
    ):
        """Constructs a new filter object

        Allows filtering for specific alerts in nebulon ON. The filter allows
        multiple properties to be specified. If multiple properties are
        provided they are concatenated with a logical AND.

        :param created_after: Filter alerts to include only alerts that were
            created after the specified date and time.
        :type created_after: datetime, optional
        :param created_before: Filter alerts to include only alerts that were
            created before the specified date and time.
        :type created_before: datetime, optional
        :param severity: Filter alerts to include only alerts with the
            specified severity.
        :type severity: ResourceType, optional
        :param resource_type: Filter alerts to include only alerts that are
            associated with the specified resource type
        :type resource_type: ResourceType, optional
        :param resource_id: Filter alerts to include only alerts that are
            associated with the specified resource identifier
        :type resource_id: AlertStatus, optional
        :param status: Filter alerts to include only alerts that match the
            specified status
        :type status: AlertStatus, optional
        """
        self.__created_after = created_after
        self.__created_before = created_before
        self.__severity = severity
        self.__resource_type = resource_type
        self.__resource_id = resource_id
        self.__status = status

    @property
    def created_after(self) -> datetime:
        """Filter for alerts created after the specified date and time"""
        return self.__created_after

    @property
    def created_before(self) -> datetime:
        """Filter for alerts created before the specified date and time"""
        return self.__created_before

    @property
    def severity(self) -> AlertSeverity:
        """Filter for alerts that match the specified alert severity"""
        return self.__severity

    @property
    def resource_type(self) -> ResourceType:
        """Filter for alerts that match the specified resource type"""
        return self.__resource_type

    @property
    def resource_id(self) -> str:
        """Filter for alerts that match the specified resource identifier"""
        return self.__resource_id

    @property
    def status(self) -> AlertStatus:
        """Filter for alerts that match the specified status"""
        return self.__status

    @property
    def as_dict(self) -> dict:
        result = dict()
        result["createdAfter"] = self.created_after
        result["createdBefore"] = self.created_before
        result["severity"] = self.severity
        result["resourceType"] = self.resource_type
        result["resourceID"] = self.resource_id
        result["status"] = self.status
        return result


class Alert:
    """Instance of an alert in nebulon ON

    An alert represents an issue in nebulon ON or your infrastructure. If the
    alert is reporting a status of ``Open`` it is an active alert in your
    environment that may require immediate attention. If it is reporting
    ``Closed`` the issue was resolved.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new alert instance object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__id = read_value(
            "id", response, str, True)
        self.__code = read_value(
            "code", response, str, True)
        self.__create_time = read_value(
            "createTime", response, datetime, True)
        self.__resource_id = read_value(
            "resourceID", response, str, True)
        self.__resource_name = read_value(
            "resourceName", response, str, True)
        self.__resource_type = read_value(
            "resourceType", response, ResourceType, True)
        self.__severity = read_value(
            "severity", response, AlertSeverity, True)
        self.__status = read_value(
            "status", response, AlertStatus, True)
        self.__spu_serial = read_value(
            "spuSerial", response, str, False)
        self.__pod_uuid = read_value(
            "nPodUUID", response, str, False)
        self.__summary = read_value(
            "summary", response, str, True)
        self.__details = read_value(
            "details", response, str, True)
        self.__corrective_actions = read_value(
            "correctiveActions", response, str, False)

    @property
    def id(self) -> str:
        """Identifier of the alert"""
        return self.__id

    @property
    def code(self) -> str:
        """Alert code allows the unique identification of an alert type"""
        return self.__code

    @property
    def create_time(self) -> datetime:
        """Timestamp for when the alert was detected"""
        return self.__create_time

    @property
    def resource_id(self) -> str:
        """Related resource identifier"""
        return self.__resource_id

    @property
    def resource_name(self) -> str:
        """Related resource name"""
        return self.__resource_name

    @property
    def resource_type(self) -> ResourceType:
        """Related resource type"""
        return self.__resource_type

    @property
    def severity(self) -> AlertSeverity:
        """Severity of the alert"""
        return self.__severity

    @property
    def status(self) -> AlertStatus:
        """Status of the alert"""
        return self.__status

    @property
    def spu_serial(self) -> str:
        """Related services processing unit serial number"""
        return self.__spu_serial

    @property
    def pod_uuid(self) -> str:
        """Related nPod uuid"""
        return self.__pod_uuid

    @property
    def summary(self) -> str:
        """Summary description for the alert"""
        return self.__summary

    @property
    def details(self) -> str:
        """Detailed description for the alert"""
        return self.__details

    @property
    def corrective_actions(self) -> [str]:
        """List of corrective actions to resolve the alert"""
        return self.__corrective_actions

    @staticmethod
    def fields():
        return [
            "id",
            "code",
            "createTime",
            "resourceID",
            "resourceName",
            "resourceType",
            "severity",
            "status",
            "spuSerial",
            "nPodUUID",
            "summary",
            "details",
            "correctiveActions",
        ]


class AlertList:
    """Paginated Alert list object

    Contains a list of alert objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new alert list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, Alert, False)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> [Alert]:
        """List of alerts in the pagination list"""
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
            "items{%s}" % ",".join(Alert.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class AlertsMixin(NebMixin):
    """Mixin to add alert related methods to the GraphQL client"""

    def get_open_alerts(
            self,
            page: PageInput = None,
            alert_filter: AlertFilter = None
    ) -> AlertList:
        """Retrieves a list of open alerts

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param alert_filter: A filter object to filter the open alerts on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type alert_filter: AlertFilter, optional

        :returns AlertList: A paginated list of open alerts.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            alert_filter, "AlertFilter", False)

        # make the request
        response = self._query(
            name="getOpenAlerts",
            params=parameters,
            fields=AlertList.fields()
        )

        # convert to object
        return AlertList(response)

    def get_historical_alerts(
            self,
            page: PageInput = None,
            alert_filter: AlertFilter = None
    ) -> AlertList:
        """Retrieves a list of resolved alerts

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param alert_filter: A filter object to filter the closed alerts on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type alert_filter: AlertFilter, optional

        :returns AlertList: A paginated list of closed alerts.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            alert_filter, "AlertFilter", False)

        # make the request
        response = self._query(
            name="getHistoricalAlerts",
            params=parameters,
            fields=AlertList.fields()
        )

        # convert to object
        return AlertList(response)
