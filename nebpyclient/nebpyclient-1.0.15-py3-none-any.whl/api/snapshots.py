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
from .filters import UuidFilter, StringFilter
from .sorting import SortDirection
from .tokens import TokenResponse

__all__ = [
    "SnapConsistencyLevel",
    "SnapshotConsistencyLevel",
    "CreateCloneInput",
    "ScheduleInput",
    "SnapshotScheduleTemplateSort",
    "SnapshotScheduleTemplateFilter",
    "CreateSnapshotScheduleTemplateInput",
    "UpdateSnapshotScheduleTemplateInput",
    "Schedule",
    "SnapshotScheduleTemplate",
    "SnapshotScheduleTemplateList",
    "NPodSnapshotSchedule",
    "SnapshotMixin"
]


class SnapConsistencyLevel(NebEnum):
    """Defines the snapshot consistency level for snapshots

    This enumeration is deprecated. Use ``SnapshotConsistencyLevel`` instead.
    """
    Volume = "VV"
    SPU = "SPU"
    NPod = "Pod"


class SnapshotConsistencyLevel(NebEnum):
    """Defines the snapshot consistency level for snapshots"""
    Volume = "Volume"
    SPU = "SPU"
    NPod = "NPod"


class CreateCloneInput:
    """An input object to create a volume clone

    Allows the creation of a volume clone from a base volume or snapshot.
    Clones are read and writeable copies of another volume. Clones can be used
    to quickly instantiate copies of data and data for recovery purposes when
    applications require read/write access for copy operations.
    """

    def __init__(
            self,
            name: str,
            volume_uuid: str
    ):
        """Constructs a new input object to create a volume clone

        Allows the creation of a volume clone from a base volume or snapshot.
        Clones are read and writeable copies of another volume. Clones can be
        used to quickly instantiate copies of data and data for recovery
        purposes when applications require read/write access for copy
        operations.

        :param name: The human readable name for the volume clone
        :type name: str
        :param volume_uuid: The unique identifier for the volume or snapshot
            from which to create the clone
        :type volume_uuid: str
        """

        self.__name = name
        self.__volume_uuid = volume_uuid

    @property
    def name(self) -> str:
        """Name for the volume clone"""
        return self.__name

    @property
    def volume_uuid(self) -> str:
        """Unique identifier of the volume or snapshot to clone"""
        return self.__volume_uuid

    @property
    def as_dict(self):
        result = dict()
        result["cloneVolumeName"] = self.name
        result["originVolumeUUID"] = self.volume_uuid
        return result


class ScheduleInput:
    """An input object to create a schedule

    Schedules are used to perform operations automatically. The schedule defines
    when and how often the operations are executed.
    """

    def __init__(
            self,
            minute: [int] = None,
            hour: [int] = None,
            day_of_week: [int] = None,
            day_of_month: [int] = None,
            month: [int] = None
    ):
        """Constructs a new input object to create a schedule

        Schedules are used to perform operations automatically. The schedule
        defines when and how often the operations are executed. Multiple values
        for ``minute``, ``hour``, ``day_of_week``, ``day_of_month``, and ``month`` can
        be specified when the operation should be executed multiple times in the
        respective time frame.

        :param minute: The minute of the time when an operation should be
            executed. The valid range is `00` to `60`.
        :type minute: [int], optional
        :param hour: The hour of the time when an operation should be
            executed. The valid range is `00` to `23`.
        :type hour: [int], optional
        :param day_of_week: The day of the week when an operation should be
            executed. The valid range is `1` to `7`, where `1` is Monday.
        :type day_of_week: [int], optional
        :param day_of_month: The day in the month when an operation should be
            executed. The valid range is `1` to `31`.
        :type day_of_month: [int], optional
        :param month: The month in the year when an operation should be
            executed. The valid range is `1` to `12`.
        :type month: [int], optional
        """

        self.__minute = minute
        self.__hour = hour
        self.__day_of_week = day_of_week
        self.__day_of_month = day_of_month
        self.__month = month

    @property
    def minute(self) -> [int]:
        """The minutes of the time when an operation should be executed"""
        return self.__minute

    @property
    def hour(self) -> [int]:
        """The hours of the time when an operation should be executed"""
        return self.__hour

    @property
    def day_of_week(self) -> [int]:
        """The days of the week when an operation should be executed"""
        return self.__day_of_week

    @property
    def day_of_month(self) -> [int]:
        """The days in the month when an operation should be executed"""
        return self.__day_of_month

    @property
    def month(self) -> [int]:
        """The months in the year when an operation should be executed"""
        return self.__month

    @property
    def as_dict(self):
        result = dict()
        result["minute"] = self.minute
        result["hour"] = self.hour
        result["dayOfWeek"] = self.day_of_week
        result["dayOfMonth"] = self.day_of_month
        result["month"] = self.month
        return result


class SnapshotScheduleTemplateSort:
    """A sort object for snapshot schedule templates

    Allows sorting snapshot schedule templates on common properties. The sort
    object allows only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for snapshot schedule templates

        :param name: Sort direction for the ``name`` property
        :type name: SortDirection, optional
        """

        self.__name = name

    @property
    def name(self) -> SortDirection:
        """Sort direction for the ``name`` property"""
        return self.__name

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        return result


class SnapshotScheduleTemplateFilter:
    """A filter object to filter snapshot schedule templates

    Allows filtering for specific snapshot schedule templates in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on snapshot schedule template unique
            identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on snapshot schedule template name
        :type name: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: SnapshotScheduleTemplateFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: SnapshotScheduleTemplateFilter, optional
        """
        self.__uuid = uuid
        self.__name = name
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on snapshot schedule template unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on snapshot schedule template name"""
        return self.__name

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
        result["name"] = self.name
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateSnapshotScheduleTemplateInput:
    """An input object to create a snapshot schedule template

    Allows the creation of snapshot schedule templates. Snapshot schedule
    templates are used to consistently provision snapshot schedules across
    nPods. They are referenced in nPod templates and are provisioned when a
    nPod is formed from such a template.
    """

    def __init__(
            self,
            name: str,
            name_pattern: str,
            schedule: ScheduleInput,
            expiration_seconds: int = None,
            retention_seconds: int = None,
            ignore_boot_volumes: bool = None
    ):
        """Constructs a input object to create a snapshot schedule template

        Allows the creation of snapshot schedule templates. Snapshot schedule
        templates are used to consistently provision snapshot schedules across
        nPods. They are referenced in nPod templates and are provisioned when a
        nPod is formed from such a template.

        :param name: Human readable name for the snapshot schedule template
        :type name: str
        :param name_pattern: A naming pattern for volume snapshot names when
            they are automatically created. Available variables for the format
            string are from the standard ``strftime`` function. Additionally `%v`
            is used for the base volume name.
        :type name_pattern: str
        :param schedule: The schedule by which volume snapshots will be created
        :type schedule: ScheduleInput
        :param expiration_seconds: A time in seconds when snapshots will be
            automatically deleted. If not specified, snapshots will not be
            deleted automatically (not recommended)
        :type expiration_seconds: int, optional
        :param retention_seconds: A time in seconds that prevents users from
            deleting snapshots. If not specified, snapshots can be immediately
            deleted.
        :type retention_seconds: int, optional
        :param ignore_boot_volumes: Allows specifying if boot volumes shall be
            included when doing snapshots (``True``) or if they shall be ignored
            (`False). By default, all volumes are included.
        :type ignore_boot_volumes: bool, optional
        """
        self.__name = name
        self.__name_pattern = name_pattern
        self.__schedule = schedule
        self.__expiration_seconds = expiration_seconds
        self.__retention_seconds = retention_seconds
        self.__consistency_level = SnapshotConsistencyLevel.Volume
        self.__ignore_boot_volumes = ignore_boot_volumes

    @property
    def name(self) -> str:
        """Name for the snapshot schedule template"""
        return self.__name

    @property
    def name_pattern(self) -> str:
        """A naming pattern for the snapshots created by the schedule"""
        return self.__name_pattern

    @property
    def schedule(self) -> ScheduleInput:
        """The schedule in which snapshots will be created"""
        return self.__schedule

    @property
    def expiration_seconds(self) -> int:
        """Time in seconds when snapshots will be automatically deleted"""
        return self.__expiration_seconds

    @property
    def retention_seconds(self) -> int:
        """Time in seconds that prevents users from deleting snapshots"""
        return self.__retention_seconds

    @property
    def consistency_level(self) -> SnapshotConsistencyLevel:
        """Snapshot consistency level. Always set to ``Volume``"""
        return self.__consistency_level

    @property
    def ignore_boot_volumes(self) -> bool:
        """Specifies if boot volumes are ignored by the schedule or included"""
        return self.__ignore_boot_volumes

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["namePattern"] = self.name_pattern
        result["schedule"] = self.schedule
        result["expirationSec"] = self.expiration_seconds
        result["retentionSec"] = self.retention_seconds
        result["consistencyLevel"] = self.consistency_level
        result["ignoreBootLUNs"] = self.ignore_boot_volumes
        return result


class UpdateSnapshotScheduleTemplateInput:
    """An input object to update snapshot schedule template properties

    Allows updating of snapshot schedule template properties. Snapshot schedule
    templates are used to consistently provision snapshot schedules across
    nPods. They are referenced in nPod templates and are provisioned when a
    nPod is formed from such a template.
    """

    def __init__(
            self,
            name: str = None,
            name_pattern: str = None,
            schedule: ScheduleInput = None,
            expiration_seconds: int = None,
            retention_seconds: int = None,
            ignore_boot_volumes: bool = None
    ):
        """Constructs a input object to update a snapshot schedule template

        Allows updating of snapshot schedule template properties. Snapshot
        schedule templates are used to consistently provision snapshot schedules
        across nPods. They are referenced in nPod templates and are provisioned
        when a nPod is formed from such a template.

        :param name: Human readable name for the snapshot schedule template
        :type name: str, optional
        :param name_pattern: A naming pattern for volume snapshot names when
            they are automatically created. Available variables for the format
            string are from the standard ``strftime`` function. Additionally `%v`
            is used for the base volume name.
        :type name_pattern: str, optional
        :param schedule: The schedule by which volume snapshots will be created
        :type schedule: ScheduleInput, optional
        :param expiration_seconds: A time in seconds when snapshots will be
            automatically deleted. If not specified, snapshots will not be
            deleted automatically (not recommended)
        :type expiration_seconds: int, optional
        :param retention_seconds: A time in seconds that prevents users from
            deleting snapshots. If not specified, snapshots can be immediately
            deleted.
        :type retention_seconds: int, optional
        :param ignore_boot_volumes: Allows specifying if boot volumes shall be
            included when doing snapshots (``True``) or if they shall be ignored
            (`False). By default, all volumes are included.
        :type ignore_boot_volumes: bool, optional
        """

        self.__name = name
        self.__name_pattern = name_pattern
        self.__read_only = None
        self.__schedule = schedule
        self.__expiration_seconds = expiration_seconds
        self.__retention_seconds = retention_seconds
        self.__consistency_level = None
        self.__ignore_boot_volumes = ignore_boot_volumes

    @property
    def name(self) -> str:
        """Name for the snapshot schedule template"""
        return self.__name

    @property
    def name_pattern(self) -> str:
        """A naming pattern for the snapshots created by the schedule"""
        return self.__name_pattern

    @property
    def schedule(self) -> ScheduleInput:
        """The schedule in which snapshots will be created"""
        return self.__schedule

    @property
    def expiration_seconds(self) -> int:
        """Time in seconds when snapshots will be automatically deleted"""
        return self.__expiration_seconds

    @property
    def retention_seconds(self) -> int:
        """Time in seconds that prevents users from deleting snapshots"""
        return self.__retention_seconds

    @property
    def consistency_level(self) -> SnapshotConsistencyLevel:
        """Snapshot consistency level (Can not be specified)"""
        return self.__consistency_level

    @property
    def ignore_boot_volumes(self) -> bool:
        """Specifies if boot volumes are ignored by the schedule or included"""
        return self.__ignore_boot_volumes

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["namePattern"] = self.name_pattern
        result["schedule"] = self.schedule
        result["expirationSec"] = self.expiration_seconds
        result["retentionSec"] = self.retention_seconds
        result["consistencyLevel"] = self.consistency_level
        result["ignoreBootLUNs"] = self.ignore_boot_volumes
        return result


class Schedule:
    """An schedule object

    Schedules are used to perform operations automatically. The schedule defines
    when and how often the operations are executed.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new schedule object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__minute = read_value(
            "minute", response, int, True)
        self.__hour = read_value(
            "hour", response, int, True)
        self.__day_of_week = read_value(
            "dayOfWeek", response, int, True)
        self.__day_of_month = read_value(
            "dayOfMonth", response, int, True)
        self.__month = read_value(
            "month", response, int, True)

    @property
    def minute(self) -> [int]:
        """The minutes of the hour when an operation should be executed"""
        return self.__minute

    @property
    def hour(self) -> [int]:
        """The hours of the day when an operation should be executed"""
        return self.__hour

    @property
    def day_of_week(self) -> [int]:
        """The days of the week when an operation should be executed"""
        return self.__day_of_week

    @property
    def day_of_month(self) -> [int]:
        """The days in the month when an operation should be executed"""
        return self.__day_of_month

    @property
    def month(self) -> [int]:
        """The months in the year when an operation should be executed"""
        return self.__month

    @staticmethod
    def fields():
        return [
            "minute",
            "hour",
            "dayOfWeek",
            "dayOfMonth",
            "month",
        ]


class SnapshotScheduleTemplate:
    """A snapshot schedule template object

    Snapshot schedule templates are used to consistently provision snapshot
    schedules across nPods. They are referenced in nPod templates and are
    provisioned when a nPod is formed from such a template.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new schedule object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__name_pattern = read_value(
            "namePattern", response, str, True)
        self.__schedule = read_value(
            "schedule", response, Schedule, True)
        self.__expiration_seconds = read_value(
            "expirationSec", response, int, True)
        self.__retention_seconds = read_value(
            "retentionSec", response, int, True)
        self.__consistency_level = read_value(
            "consistencyLevel", response, SnapshotConsistencyLevel, True)
        self.__ignore_boot_volumes = read_value(
            "ignoreBootLUNs", response, bool, True)
        self.__associated_npod_template_count = read_value(
            "associatedNPodTemplateCount", response, int, True)
        self.__associated_schedule_count = read_value(
            "associatedScheduleCount", response, int, True)

    @property
    def uuid(self) -> str:
        """The unique identifier of the snapshot schedule template"""
        return self.__uuid

    @property
    def name(self) -> str:
        """Name for the snapshot schedule template"""
        return self.__name

    @property
    def name_pattern(self) -> str:
        """A naming pattern for the snapshots created by the schedule"""
        return self.__name_pattern

    @property
    def schedule(self) -> ScheduleInput:
        """The schedule in which snapshots will be created"""
        return self.__schedule

    @property
    def expiration_seconds(self) -> int:
        """Time in seconds when snapshots will be automatically deleted"""
        return self.__expiration_seconds

    @property
    def retention_seconds(self) -> int:
        """Time in seconds that prevents users from deleting snapshots"""
        return self.__retention_seconds

    @property
    def consistency_level(self) -> SnapshotConsistencyLevel:
        """Snapshot consistency level. Always set to ``Volume``"""
        return self.__consistency_level

    @property
    def ignore_boot_volumes(self) -> bool:
        """Specifies if boot volumes are ignored by the schedule or included"""
        return self.__ignore_boot_volumes

    @property
    def associated_npod_template_count(self) -> int:
        """The number of nPod templates that make use of this template"""
        return self.__associated_npod_template_count

    @property
    def associated_schedule_count(self) -> int:
        """The number of provisioned snapshot schedules from this template"""
        return self.__associated_schedule_count

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "namePattern",
            "schedule{%s}" % ",".join(Schedule.fields()),
            "expirationSec",
            "retentionSec",
            "consistencyLevel",
            "ignoreBootLUNs",
            "associatedNPodTemplateCount",
            "associatedScheduleCount",
        ]


class SnapshotScheduleTemplateList:
    """Paginated snapshot schedule template list

    Contains a list of snapshot schedule template objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new snapshot schedule template list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, SnapshotScheduleTemplate, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> [SnapshotScheduleTemplate]:
        """List of snapshot schedule templates in the pagination list"""
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
            "items{%s}" % ",".join(SnapshotScheduleTemplate.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class NPodSnapshotSchedule:
    """A snapshot schedule that is defined for an entire nPod

    nPod snapshot schedules are defined for the entire nPod vs. for individual
    volumes. They are centrally configured through a template or on-demand and
    apply to every volume in an nPod.
    """

    def __init__(
            self,
            response
    ):
        """Constructs a new NPodSnapshotSchedule object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__uuid = read_value(
            "scheduleUID", response, str, True)
        self.__spu_serial = read_value(
            "spuSerial", response, str, True)
        self.__consistency_level = read_value(
            "consistencyLevel", response, SnapConsistencyLevel, True)
        self.__name_pattern = read_value(
            "namePattern", response, str, True)
        self.__expiration_seconds = read_value(
            "expirationSec", response, int, True)
        self.__retention_seconds = read_value(
            "retentionSec", response, int, True)
        self.__ignore_boot_volumes = read_value(
            "ignorebootLuns", response, bool, True)
        self.__minute = read_value(
            "minute", response, int, True)
        self.__hour = read_value(
            "hour", response, int, True)
        self.__day_of_week = read_value(
            "dayOfWeek", response, int, True)
        self.__day_of_month = read_value(
            "dayOfMonth", response, int, True)
        self.__month = read_value(
            "month", response, int, True)
        self.__snapshot_count = read_value(
            "snapshotCount", response, int, True)
        self.__snapshot_uuids = read_value(
            "snapshots", response, str, False)
        self.__snapshot_schedule_template_uuid = read_value(
            "snapScheduleTemplate.templateUUID", response, str, False)

    @property
    def uuid(self) -> str:
        """The unique identifier for the nPod snapshot schedule"""
        return self.__uuid

    @property
    def spu_serial(self) -> str:
        """The SPU serial number on which the schedule is defined"""
        return self.__spu_serial

    @property
    def consistency_level(self) -> SnapshotConsistencyLevel:
        """Defines the consistency level when snapshotting multiple volumes"""
        return self.__consistency_level

    @property
    def name_pattern(self) -> str:
        """A naming pattern for the snapshots created by the schedule"""
        return self.__name_pattern

    @property
    def expiration_seconds(self) -> int:
        """Time in seconds when snapshots will be automatically deleted"""
        return self.__expiration_seconds

    @property
    def retention_seconds(self) -> int:
        """Time in seconds that prevents users from deleting snapshots"""
        return self.__retention_seconds

    @property
    def ignore_boot_volumes(self) -> bool:
        """Specifies if boot volumes are ignored by the schedule or included"""
        return self.__ignore_boot_volumes

    @property
    def minute(self) -> [int]:
        """The minutes of the hour when a snapshot is created"""
        return self.__minute

    @property
    def hour(self) -> [int]:
        """The hours of the day when a snapshot is created"""
        return self.__hour

    @property
    def day_of_week(self) -> [int]:
        """The days of the week when a snapshot is created"""
        return self.__day_of_week

    @property
    def day_of_month(self) -> [int]:
        """The days in the month when a snapshot is created"""
        return self.__day_of_month

    @property
    def month(self) -> [int]:
        """The months in the year when a snapshot is created"""
        return self.__month

    @property
    def snapshot_count(self) -> int:
        """The number of snapshots created from this schedule"""
        return self.__snapshot_count

    @property
    def snapshot_uuids(self) -> [str]:
        """Unique identifiers of the snapshots created from this schedule"""
        return self.__snapshot_uuids

    @property
    def snapshot_schedule_template_uuid(self) -> str:
        """Unique identifiers of the templates that created this schedule"""
        return self.__snapshot_schedule_template_uuid

    @staticmethod
    def fields():
        return [
            "scheduleUID",
            "spuSerial",
            "consistencyLevel",
            "namePattern",
            "expirationSec",
            "retentionSec",
            "ignorebootLuns",
            "minute",
            "hour",
            "dayOfWeek",
            "dayOfMonth",
            "month",
            "snapshotCount",
            "snapshots{uid}",
            "snapScheduleTemplate{templateUUID}",
        ]


class SnapshotMixin(NebMixin):
    """Mixin to add snapshot related methods to the GraphQL client"""

    def get_snapshot_schedule_templates(
            self,
            page: PageInput = None,
            template_filter: SnapshotScheduleTemplateFilter = None,
            sort: SnapshotScheduleTemplateSort = None
    ) -> SnapshotScheduleTemplateList:
        """Retrieves a list of snapshot schedule template objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param template_filter: A filter object to filter the snapshot schedule
            template objects on the server. If omitted, the server will return
            all objects as a paginated response.
        :type template_filter: SnapshotScheduleTemplateFilter, optional
        :param sort: A sort definition object to sort the snapshot schedule
            template objects on supported properties. If omitted objects are
            returned in the order as they were created in.
        :type sort: SnapshotScheduleTemplateSort, optional

        :returns SnapshotScheduleTemplateList: A paginated list of snapshot
            schedule templates.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            template_filter, "SnapshotScheduleTemplateFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "SnapshotScheduleTemplateSort", False)

        # make the request
        response = self._query(
            name="getSnapshotScheduleTemplates",
            params=parameters,
            fields=SnapshotScheduleTemplateList.fields()
        )

        # convert to object
        return SnapshotScheduleTemplateList(response)

    def create_snapshot_schedule_template(
            self,
            name: str,
            name_pattern: str,
            schedule: ScheduleInput,
            expiration_seconds: int = None,
            retention_seconds: int = None,
            ignore_boot_volumes: bool = None
    ) -> SnapshotScheduleTemplate:
        """Allows creation of a new snapshot schedule template

        Allows the creation of snapshot schedule templates. Snapshot schedule
        templates are used to consistently provision snapshot schedules across
        nPods. They are referenced in nPod templates and are provisioned when a
        nPod is formed from such a template.

        :param name: Human readable name for the snapshot schedule template
        :type name: str
        :param name_pattern: A naming pattern for volume snapshot names when
            they are automatically created. Available variables for the format
            string are from the standard ``strftime`` function. Additionally `%v`
            is used for the base volume name.
        :type name_pattern: str
        :param schedule: The schedule by which volume snapshots will be created
        :type schedule: ScheduleInput
        :param expiration_seconds: A time in seconds when snapshots will be
            automatically deleted. If not specified, snapshots will not be
            deleted automatically (not recommended)
        :type expiration_seconds: int, optional
        :param retention_seconds: A time in seconds that prevents users from
            deleting snapshots. If not specified, snapshots can be immediately
            deleted.
        :type retention_seconds: int, optional
        :param ignore_boot_volumes: Allows specifying if boot volumes shall be
            included when doing snapshots (``True``) or if they shall be ignored
            (``False``). By default, all volumes are included.
        :type ignore_boot_volumes: bool, optional

        :returns SnapshotScheduleTemplate: The new snapshot schedule template

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateSnapshotScheduleTemplateInput(
                name=name,
                name_pattern=name_pattern,
                schedule=schedule,
                expiration_seconds=expiration_seconds,
                retention_seconds=retention_seconds,
                ignore_boot_volumes=ignore_boot_volumes
            ),
            "CreateSnapshotScheduleTemplateInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createSnapshotScheduleTemplate",
            params=parameters,
            fields=SnapshotScheduleTemplate.fields()
        )

        # convert to object
        return SnapshotScheduleTemplate(response)

    def update_snapshot_schedule_template(
            self,
            uuid: str,
            name: str = None,
            name_pattern: str = None,
            schedule: ScheduleInput = None,
            expiration_seconds: int = None,
            retention_seconds: int = None,
            ignore_boot_volumes: bool = None
    ) -> SnapshotScheduleTemplate:
        """Allows updating the properties of a snapshot schedule template

        Allows updating of snapshot schedule template properties. Snapshot
        schedule templates are used to consistently provision snapshot schedules
        across nPods. They are referenced in nPod templates and are provisioned
        when a nPod is formed from such a template.

        :param name: Human readable name for the snapshot schedule template
        :type name: str, optional
        :param name_pattern: A naming pattern for volume snapshot names when
            they are automatically created. Available variables for the format
            string are from the standard ``strftime`` function. Additionally `%v`
            is used for the base volume name.
        :type name_pattern: str, optional
        :param schedule: The schedule by which volume snapshots will be created
        :type schedule: ScheduleInput, optional
        :param expiration_seconds: A time in seconds when snapshots will be
            automatically deleted. If not specified, snapshots will not be
            deleted automatically (not recommended)
        :type expiration_seconds: int, optional
        :param retention_seconds: A time in seconds that prevents users from
            deleting snapshots. If not specified, snapshots can be immediately
            deleted.
        :type retention_seconds: int, optional
        :param ignore_boot_volumes: Allows specifying if boot volumes shall be
            included when doing snapshots (``True``) or if they shall be ignored
            (``False``). By default, all volumes are included.
        :type ignore_boot_volumes: bool, optional

        :returns SnapshotScheduleTemplate: The updated snapshot schedule
            template

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateSnapshotScheduleTemplateInput(
                name=name,
                name_pattern=name_pattern,
                schedule=schedule,
                expiration_seconds=expiration_seconds,
                retention_seconds=retention_seconds,
                ignore_boot_volumes=ignore_boot_volumes
            ),
            "UpdateSnapshotScheduleTemplateInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateSnapshotScheduleTemplate",
            params=parameters,
            fields=SnapshotScheduleTemplate.fields()
        )

        # convert to object
        return SnapshotScheduleTemplate(response)

    def delete_snapshot_schedule_template(
            self,
            uuid: str
    ) -> bool:
        """Allows deletion of an existing snapshot schedule template

        :param uuid: The unique identifier of the snapshot schedule template
            to delete
        :type uuid: str

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteSnapshotScheduleTemplate",
            params=parameters,
            fields=None
        )

        # response is a boolean
        return response

    def get_snapshot_schedules(
            self,
            npod_uuid: str
    ):
        """Retrieves a list of provisioned snapshot schedules on an nPod

        :param npod_uuid: The unique identifier of the nPod from which the
            snapshot schedules shall be retrieved.
        :type npod_uuid: str

        :returns [NPodSnapshotSchedule]: A list of snapshot schedules

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["pod"] = GraphQLParam(
            npod_uuid,
            "String",
            False
        )

        # make the request
        response = self._query(
            name="PodSnapshotSchedules",
            params=parameters,
            fields=NPodSnapshotSchedule.fields()
        )

        # convert to object
        return [NPodSnapshotSchedule(i) for i in response]

    def create_snapshot(
            self,
            parent_volume_uuids: [str],
            name_patterns: [str],
            expiration_seconds: int = None,
            retention_seconds: int = None
    ):
        """Allows creation of an on-demand snapshot of volumes

        If multiple volumes are provided, multiple name patterns are required,
        where the index of the list of items are related. For example, the
        name pattern at index `3` of the ``name_patterns`` parameter will be
        applied to the volume specified at index `3` of the
        ``parent_volume_uuids`` list.

        :param parent_volume_uuids: List of unique identifiers for all volumes
            for which to create a snapshot
        :type parent_volume_uuids: [str]
        :param name_patterns: List of naming patterns for volume snapshots.
            Options of the ``strftime`` function are available to format time and
            the variable `%v` that will be translated to the volume name.
        :type name_patterns: [str]
        :param expiration_seconds: The number of seconds after snapshot creation
            when the snapshots will be automatically deleted
        :type expiration_seconds: int
        :param retention_seconds: The number of seconds before a user can delete
            the snapshots.
        :type retention_seconds: int

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: If token delivery failed
        """

        # setup query parameters
        parameters = dict()
        parameters["parentVvUID"] = GraphQLParam(
            parent_volume_uuids, "[String!]", True)
        parameters["snapNamePattern"] = GraphQLParam(
            name_patterns, "[String!]", True)
        parameters["consistencyLevel"] = GraphQLParam(
            SnapConsistencyLevel.Volume, "SnapConsistencyLevel", True)
        parameters["roSnap"] = GraphQLParam(
            True, "Boolean", True)
        parameters["expirationSec"] = GraphQLParam(
            expiration_seconds, "Int", False)
        parameters["retentionSec"] = GraphQLParam(
            retention_seconds, "Int", False)
        # make the request
        response = self._mutation(
            name="createSnap",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def create_clone(
            self,
            name: str,
            volume_uuid: str
    ):
        """Allows creating a read/writeable clone of a volume or snapshot

        Allows the creation of a volume clone from a base volume or snapshot.
        Clones are read and writeable copies of another volume. Clones can be
        used to quickly instantiate copies of data and data for recovery
        purposes when applications require read/write access for copy
        operations.

        :param name: The human readable name for the volume clone
        :type name: str
        :param volume_uuid: The unique identifier for the volume or snapshot
            from which to create the clone
        :type volume_uuid: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: If token delivery failed
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateCloneInput(
                name=name,
                volume_uuid=volume_uuid,
            ),
            "CreateCloneInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createClone",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()
