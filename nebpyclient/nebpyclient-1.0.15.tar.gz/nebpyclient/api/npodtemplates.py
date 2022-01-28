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
from .filters import StringFilter, UuidFilter
from .sorting import SortDirection

__all__ = [
    "NPodTemplateFilter",
    "NPodTemplateSort",
    "CreateNPodTemplateInput",
    "UpdateNPodTemplateInput",
    "NPodTemplate",
    "NPodTemplateList",
    "NPodTemplateMixin"
]


class NPodTemplateFilter:
    """A filter object to filter nPod templates

    Allows filtering for specific nPod templates in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            os: StringFilter = None,
            app: StringFilter = None,
            nebulon_template: bool = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        :param uuid: Allows filtering based on nPod template unique identifier
        :type uuid: str, optional
        :param name: Allows for filtering for nPod template name
        :type name: StringFilter, optional
        :param os: Allows for filtering for operating system name
        :type os: StringFilter, optional
        :param app: Allows filtering for application name
        :type app: StringFilter, optional
        :param nebulon_template: If set to ``True`` will filter for nebulon
            provided templates. If set to ``False`` only custom templates
            will be returned.
        :type nebulon_template: bool, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: NPodTemplateFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: NPodTemplateFilter, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__os = os
        self.__app = app
        self.__nebulon_template = nebulon_template
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on nPod template unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on nPod template name"""
        return self.__name

    @property
    def os(self) -> StringFilter:
        """Filter based on nPod template operating system name"""
        return self.__os

    @property
    def app(self) -> StringFilter:
        """Filter based on nPod template application name"""
        return self.__app

    @property
    def nebulon_template(self) -> bool:
        """Filter nPod templates for nebulon templates or custom templates"""
        return self.__nebulon_template

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
        result["os"] = self.os
        result["app"] = self.app
        result["nebulonTemplate"] = self.nebulon_template
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class NPodTemplateSort:
    """A sort object for nPod templates

    Allows sorting nPod templates on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None,
            os: SortDirection = None,
            app: SortDirection = None
    ):
        """Constructs a new sort object for nPod templates

        :param name: Sort direction for the ``name`` property
        :type name: SortDirection, optional
        :param os: Sort direction for the ``os`` property
        :type os: SortDirection, optional
        :param app: Sort direction for the ``app`` property
        :type app: SortDirection, optional
        """

        # check the basics
        param_count = 0
        if name is not None:
            param_count += 1
        if os is not None:
            param_count += 1
        if app is not None:
            param_count += 1

        if param_count != 1:
            raise ValueError("Exactly one parameter must be specified")

        self.__name = name
        self.__os = os
        self.__app = app

    @property
    def name(self) -> SortDirection:
        """Sort direction for the ``name`` property"""
        return self.__name

    @property
    def os(self) -> SortDirection:
        """Sort direction for the ``os`` property"""
        return self.__os

    @property
    def app(self) -> SortDirection:
        """Sort direction for the ``app`` property"""
        return self.__app

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["os"] = self.os
        result["app"] = self.app
        return result


class CreateNPodTemplateInput:
    """An input object to create a new nPod template

    nPod templates are used during nPod creation and are application specific.
    The template defines the anticipated data storage savings and the expected
    storage artifacts. Architects would compile nPod templates and users would
    consume templates during self-service infrastructure provisioning.
    """

    def __init__(
            self,
            name: str,
            saving_factor: float,
            mirrored_volume: bool,
            boot_volume: bool,
            os: str,
            volume_size_bytes: int = None,
            shared_volume: bool = None,
            boot_volume_size_bytes: int = None,
            boot_image_url: str = None,
            app: str = None,
            note: str = None,
            snapshot_schedule_template_uuids: [str] = None,
            volume_count: int = None
    ):
        """Constructs a new input object for creating a nPod template

        :param name: The name of the nPod template to update. The name cannot
            be changed. If users want to change the name of a nPod template they
            should clone the template with a new name and delete the old record
        :type name: str
        :param saving_factor: The anticipated saving factor for the specified
            application after data compression and data deduplication. Allowed
            values are between `1.0` and `10.0`. nebulon ON will use this
            assumption for provisioning storage volumes.
        :type saving_factor: float
        :param mirrored_volume: Specifies if volumes shall be mirrored for
            high availability. If set to ``True`` two copies of the same volume
            will be created in an nPod on different SPUs for high availability.
        :type mirrored_volume: bool
        :param boot_volume: If set to ``True`` nebulon ON will provision a
            boot volume for the server's operating system. If set, the parameter
            ``boot_volume_size_bytes`` must also be specified.
        :type boot_volume: bool
        :param os: The name of the operating system that will be installed on
            servers in the nPod.
        :type os: str
        :param volume_size_bytes: The size of volumes to create in bytes. Either
            volume size or volume count must be present.
        :type volume_size_bytes: int
        :param shared_volume: Allows configuring volume export options. If set
            to ``True`` all volumes except boot volumes will be made available
            to each host / server in the nPod for read and write access. If set
            to ``False`` volumes will only be made available to the local host
            of every SPU. By default volumes are created as shared volumes.
        :type shared_volume: bool, optional
        :param boot_volume_size_bytes: The size of the boot volume to create
            in bytes. This value is only considered when the parameter
            ``boot_volume`` is set to ``True``.
        :type boot_volume_size_bytes: int, optional
        :param boot_image_url: Allows specifying an HTTP(s) URL for a boot
            image that is applied to the boot volume when an nPod is created.
        :type boot_image_url: str, optional
        :param app: The name of the application that will be running on the
            nPod.
        :type app: str, optional
        :param note: An optional note for the nPod template
        :type note: str, optional
        :param snapshot_schedule_template_uuids: Allows specifying snapshot
            schedule templates that will be automatically created for any
            derived nPods after nPod creation.
        :type snapshot_schedule_template_uuids: [str], optional
        :param volume_count: Allows specifying a volume count. This option is
            only allowed when ``shared_volume`` is set to ``False`` and allows
            creating a specific number of volumes per host / server. This is
            useful when the size of the volume does not matter but the number
            of volumes is important
        :type volume_count: int, optional
        """

        self.__name = name
        self.__volume_size_bytes = volume_size_bytes
        self.__saving_factor = saving_factor
        self.__mirrored_volume = mirrored_volume
        self.__shared_volume = shared_volume
        self.__boot_volume = boot_volume
        self.__boot_volume_size_bytes = boot_volume_size_bytes
        self.__boot_image_url = boot_image_url
        self.__os = os
        self.__app = app
        self.__note = note
        self.__snapshot_schedule_template_uuids = \
            snapshot_schedule_template_uuids
        self.__volume_count = volume_count

    @property
    def name(self) -> str:
        """The unique name of the nPod template"""
        return self.__name

    @property
    def volume_size_bytes(self) -> int:
        """Volume size in bytes"""
        return self.__volume_size_bytes

    @property
    def saving_factor(self) -> float:
        """Anticipated data saving factor after compression and deduplication"""
        return self.__saving_factor

    @property
    def mirrored_volume(self) -> bool:
        """Indicates if volumes will be mirrored across SPUs in an nPod"""
        return self.__mirrored_volume

    @property
    def shared_volume(self) -> bool:
        """Indicates if volumes are shared between all hosts in an nPod"""
        return self.__shared_volume

    @property
    def boot_volume(self) -> bool:
        """Indicates if a boot volume for the O/S will be provisioned"""
        return self.__boot_volume

    @property
    def boot_volume_size_bytes(self) -> int:
        """Indicates the boot volume size in bytes"""
        return self.__boot_volume_size_bytes

    @property
    def boot_image_url(self) -> str:
        """Allows specifying a URL to an O/S image for the boot volume"""
        return self.__boot_image_url

    @property
    def os(self) -> str:
        """Name of the operating system running on the hosts in the nPod"""
        return self.__os

    @property
    def app(self) -> str:
        """Name of the application running on the hosts in the nPod"""
        return self.__app

    @property
    def note(self) -> str:
        """An optional note for the nPod template"""
        return self.__note

    @property
    def snapshot_schedule_template_uuids(self) -> list:
        """List of associated snapshot schedule templates"""
        return self.__snapshot_schedule_template_uuids

    @property
    def volume_count(self) -> int:
        """Indicates how many volumes shall be provisioned by the template"""
        return self.__volume_count

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["volumeSizeBytes"] = self.volume_size_bytes
        result["savingFactor"] = self.saving_factor
        result["mirroredVolume"] = self.mirrored_volume
        result["sharedLUN"] = self.shared_volume
        result["bootVolume"] = self.boot_volume
        result["bootVolumeSizeBytes"] = self.boot_volume_size_bytes
        result["bootImageURL"] = self.boot_image_url
        result["os"] = self.os
        result["app"] = self.app
        result["note"] = self.note
        result["snapshotScheduleTemplatesUUIDs"] = \
            self.snapshot_schedule_template_uuids
        result["volumeCount"] = self.volume_count
        return result


class UpdateNPodTemplateInput:
    """An input object to update nPod template properties

    Every change to a nPod template will create a new version of the template
    and generate a new unique identifier (uuid). The parent / original nPod
    template is accessible via the nPod template ``parent_uuid`` property.
    """

    def __init__(
            self,
            name: str,
            volume_size_bytes: int = None,
            saving_factor: float = None,
            mirrored_volume: bool = None,
            shared_volume: bool = None,
            boot_volume: bool = None,
            boot_volume_size_bytes: int = None,
            boot_image_url: str = None,
            os: str = None,
            app: str = None,
            note: str = None,
            snapshot_schedule_template_uuids: [str] = None,
            volume_count: int = None
    ):
        """Constructs a new input object for updating nPod template properties

        :param name: The name of the nPod template to update. The name cannot
            be changed. If users want to change the name of a nPod template they
            should clone the template with a new name and delete the old record
        :type name: str
        :param saving_factor: The anticipated saving factor for the specified
            application after data compression and data deduplication. Allowed
            values are between `1.0` and `10.0`. nebulon ON will use this
            assumption for provisioning storage volumes.
        :type saving_factor: float, optional
        :param mirrored_volume: Specifies if volumes shall be mirrored for
            high availability. If set to ``True`` two copies of the same volume
            will be created in an nPod on different SPUs for high availability.
        :type mirrored_volume: bool, optional
        :param boot_volume: If set to ``True`` nebulon ON will provision a
            boot volume for the server's operating system. If set, the parameter
            ``boot_volume_size_bytes`` must also be specified.
        :type boot_volume: bool, optional
        :param os: The name of the operating system that will be installed on
            servers in the nPod.
        :type os: str, optional
        :param volume_size_bytes: The size of volumes to create in bytes. Either
            volume size or volume count must be present.
        :type volume_size_bytes: int, optional
        :param shared_volume: Allows configuring volume export options. If set
            to ``True`` all volumes except boot volumes will be made available
            to each host / server in the nPod for read and write access. If set
            to ``False`` volumes will only be made available to the local host
            of every SPU. By default volumes are created as shared volumes.
        :type shared_volume: bool, optional
        :param boot_volume_size_bytes: The size of the boot volume to create
            in bytes. This value is only considered when the parameter
            ``boot_volume`` is set to ``True``.
        :type boot_volume_size_bytes: int, optional
        :param boot_image_url: Allows specifying an HTTP(s) URL for a boot
            image that is applied to the boot volume when an nPod is created.
        :type boot_image_url: str, optional
        :param app: The name of the application that will be running on the
            nPod.
        :type app: str, optional
        :param note: An optional note for the nPod template
        :type note: str, optional
        :param snapshot_schedule_template_uuids: Allows specifying snapshot
            schedule templates that will be automatically created for any
            derived nPods after nPod creation.
        :type snapshot_schedule_template_uuids: [str], optional
        :param volume_count: Allows specifying a volume count. This option is
            only allowed when ``shared_volume`` is set to ``False`` and allows
            creating a specific number of volumes per host / server. This is
            useful when the size of the volume does not matter but the number
            of volumes is important
        :type volume_count: int, optional
        """

        self.__name = name
        self.__volume_size_bytes = volume_size_bytes
        self.__saving_factor = saving_factor
        self.__mirrored_volume = mirrored_volume
        self.__shared_volume = shared_volume
        self.__boot_volume = boot_volume
        self.__boot_volume_size_bytes = boot_volume_size_bytes
        self.__boot_image_url = boot_image_url
        self.__os = os
        self.__app = app
        self.__note = note
        self.__snapshot_schedule_template_uuids = \
            snapshot_schedule_template_uuids
        self.__volume_count = volume_count

    @property
    def name(self) -> str:
        """The unique name of the nPod template"""
        return self.__name

    @property
    def volume_size_bytes(self) -> int:
        """Volume size in bytes"""
        return self.__volume_size_bytes

    @property
    def saving_factor(self) -> float:
        """Anticipated data saving factor after compression and deduplication"""
        return self.__saving_factor

    @property
    def mirrored_volume(self) -> bool:
        """Indicates if volumes will be mirrored across SPUs in an nPod"""
        return self.__mirrored_volume

    @property
    def shared_volume(self) -> bool:
        """Indicates if volumes are shared between all hosts in an nPod"""
        return self.__shared_volume

    @property
    def boot_volume(self) -> bool:
        """Indicates if a boot volume for the O/S will be provisioned"""
        return self.__boot_volume

    @property
    def boot_volume_size_bytes(self) -> int:
        """Indicates the boot volume size in bytes"""
        return self.__boot_volume_size_bytes

    @property
    def boot_image_url(self) -> str:
        """Allows specifying a URL to an O/S image for the boot volume"""
        return self.__boot_image_url

    @property
    def os(self) -> str:
        """Name of the operating system running on the hosts in the nPod"""
        return self.__os

    @property
    def app(self) -> str:
        """Name of the application running on the hosts in the nPod"""
        return self.__app

    @property
    def note(self) -> str:
        """An optional note for the nPod template"""
        return self.__note

    @property
    def snapshot_schedule_template_uuids(self) -> list:
        """List of associated snapshot schedule templates"""
        return self.__snapshot_schedule_template_uuids

    @property
    def volume_count(self) -> int:
        """Indicates how many volumes shall be provisioned by the template"""
        return self.__volume_count

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["volumeSizeBytes"] = self.volume_size_bytes
        result["savingFactor"] = self.saving_factor
        result["mirroredVolume"] = self.mirrored_volume
        result["sharedVolume"] = self.shared_volume
        result["bootVolume"] = self.boot_volume
        result["bootVolumeSizeBytes"] = self.boot_volume_size_bytes
        result["bootImageURL"] = self.boot_image_url
        result["os"] = self.os
        result["app"] = self.app
        result["note"] = self.note
        result["updatedSchedSnapTemplateUUIDs"] = \
            self.snapshot_schedule_template_uuids
        result["volumeCount"] = self.volume_count
        return result


class NPodTemplate:
    """Defines a nebulon Pod (nPod) template

    nPod templates are used during nPod creation and are application specific.
    The template defines the anticipated data storage savings and the expected
    storage artifacts. Architects would compile nPod templates and users would
    consume templates during self-service infrastructure provisioning.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new nPod template object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__parent_uuid = read_value(
            "parentUUID", response, str, True)
        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__volume_size_bytes = read_value(
            "volumeSizeBytes", response, int, True)
        self.__saving_factor = read_value(
            "savingFactor", response, float, True)
        self.__mirrored_volume = read_value(
            "mirroredVolume", response, bool, True)
        self.__shared_lun = read_value(
            "sharedLun", response, bool, True)
        self.__boot_volume = read_value(
            "bootVolume", response, bool, True)
        self.__boot_volume_size_bytes = read_value(
            "bootVolumeSizeBytes", response, int, True)
        self.__boot_image_url = read_value(
            "bootImageURL", response, str, True)
        self.__os = read_value(
            "os", response, str, True)
        self.__app = read_value(
            "app", response, str, True)
        self.__version = read_value(
            "version", response, int, True)
        self.__note = read_value(
            "note", response, str, True)
        self.__nebulon_template = read_value(
            "nebulonTemplate", response, bool, True)
        self.__snapshot_schedule_template_uuids = read_value(
            "snapshotScheduleTemplates.uuid", response, str, True)
        self.__volume_count = read_value(
            "volumeCount", response, int, True)

    @property
    def parent_uuid(self) -> str:
        """The unique identifier of the original template if versioned"""
        return self.__parent_uuid

    @property
    def uuid(self) -> str:
        """The unique identifier of the template if versioned"""
        return self.__uuid

    @property
    def name(self) -> str:
        """The unique name of the nPod template"""
        return self.__name

    @property
    def volume_size_bytes(self) -> int:
        """Volume size in bytes"""
        return self.__volume_size_bytes

    @property
    def saving_factor(self) -> float:
        """Anticipated data saving factor after compression and deduplication"""
        return self.__saving_factor

    @property
    def mirrored_volume(self) -> bool:
        """Indicates if volumes will be mirrored across SPUs in an nPod"""
        return self.__mirrored_volume

    @property
    def shared_lun(self) -> bool:
        """Indicates if volumes are shared between all hosts in an nPod"""
        return self.__shared_lun

    @property
    def boot_volume(self) -> bool:
        """Indicates if a boot volume for the O/S will be provisioned"""
        return self.__boot_volume

    @property
    def boot_volume_size_bytes(self) -> int:
        """Indicates the boot volume size in bytes"""
        return self.__boot_volume_size_bytes

    @property
    def boot_image_url(self) -> str:
        """Allows specifying a URL to an O/S image for the boot volume"""
        return self.__boot_image_url

    @property
    def os(self) -> str:
        """Name of the operating system running on the hosts in the nPod"""
        return self.__os

    @property
    def app(self) -> str:
        """Name of the application running on the hosts in the nPod"""
        return self.__app

    @property
    def version(self) -> int:
        """The version of the template. Every update creates a new version"""
        return self.__version

    @property
    def note(self) -> str:
        """An optional note for the nPod template"""
        return self.__note

    @property
    def nebulon_template(self) -> bool:
        """Indicates if nebulon created the nPod template"""
        return self.__nebulon_template

    @property
    def snapshot_schedule_template_uuids(self) -> list:
        """List of associated snapshot schedule templates"""
        return self.__snapshot_schedule_template_uuids

    @property
    def volume_count(self) -> int:
        """Indicates how many volumes shall be provisioned by the template"""
        return self.__volume_count

    @staticmethod
    def fields():
        return [
            "parentUUID",
            "uuid",
            "name",
            "volumeSizeBytes",
            "savingFactor",
            "mirroredVolume",
            "sharedLun",
            "bootVolume",
            "bootVolumeSizeBytes",
            "bootImageURL",
            "os",
            "app",
            "version",
            "note",
            "nebulonTemplate",
            "snapshotScheduleTemplates{uuid}",
            "volumeCount",
        ]


class NPodTemplateList:
    """Paginated nPod template list object

    Contains a list of nPod template objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new nPod template list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__items = read_value(
            "items", response, NPodTemplate, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> [NPodTemplate]:
        """List of nPod templates in the pagination list"""
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
            "items{%s}" % ",".join(NPodTemplate.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class NPodTemplateMixin(NebMixin):
    """Mixin to add nPod template related methods to the GraphQL client"""

    def get_npod_templates(
            self,
            page: PageInput = None,
            template_filter: NPodTemplateFilter = None,
            sort: NPodTemplateSort = None
    ) -> NPodTemplateList:
        """Retrieve a list of provisioned nPod templates

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param template_filter: A filter object to filter the nPod templates
            on the server. If omitted, the server will return all objects as a
            paginated response.
        :type template_filter: NPodTemplateFilter, optional
        :param sort: A sort definition object to sort the nPod template objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: NPodTemplateSort, optional

        :returns NPodTemplateList: A paginated list of nPod templates.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            template_filter, "NPodTemplateFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "NPodTemplateSort", False)

        # make the request
        response = self._query(
            name="getNPodTemplates",
            params=parameters,
            fields=NPodTemplateList.fields()
        )

        # convert to object
        return NPodTemplateList(response)

    def create_npod_template(
            self,
            name: str,
            saving_factor: float,
            mirrored_volume: bool,
            boot_volume: bool,
            os: str,
            volume_size_bytes: int = None,
            shared_volume: bool = None,
            boot_volume_size_bytes: int = None,
            boot_image_url: str = None,
            app: str = None,
            note: str = None,
            snapshot_schedule_template_uuids: [str] = None,
            volume_count: int = None
    ) -> NPodTemplate:
        """Create a new nPod template

        :param name: The name of the nPod template to update. The name cannot
            be changed. If users want to change the name of a nPod template they
            should clone the template with a new name and delete the old record
        :type name: str
        :param saving_factor: The anticipated saving factor for the specified
            application after data compression and data deduplication. Allowed
            values are between `1.0` and `10.0`. nebulon ON will use this
            assumption for provisioning storage volumes.
        :type saving_factor: float
        :param mirrored_volume: Specifies if volumes shall be mirrored for
            high availability. If set to ``True`` two copies of the same volume
            will be created in an nPod on different SPUs for high availability.
        :type mirrored_volume: bool
        :param boot_volume: If set to ``True`` nebulon ON will provision a
            boot volume for the server's operating system. If set, the parameter
            ``boot_volume_size_bytes`` must also be specified.
        :type boot_volume: bool
        :param os: The name of the operating system that will be installed on
            servers in the nPod.
        :type os: str
        :param volume_size_bytes: The size of volumes to create in bytes. Either
            volume size or volume count must be present.
        :type volume_size_bytes: int
        :param shared_volume: Allows configuring volume export options. If set
            to ``True`` all volumes except boot volumes will be made available
            to each host / server in the nPod for read and write access. If set
            to ``False`` volumes will only be made available to the local host
            of every SPU. By default volumes are created as shared volumes.
        :type shared_volume: bool, optional
        :param boot_volume_size_bytes: The size of the boot volume to create
            in bytes. This value is only considered when the parameter
            ``boot_volume`` is set to ``True``.
        :type boot_volume_size_bytes: int, optional
        :param boot_image_url: Allows specifying an HTTP(s) URL for a boot
            image that is applied to the boot volume when an nPod is created.
        :type boot_image_url: str, optional
        :param app: The name of the application that will be running on the
            nPod.
        :type app: str, optional
        :param note: An optional note for the nPod template
        :type note: str, optional
        :param snapshot_schedule_template_uuids: Allows specifying snapshot
            schedule templates that will be automatically created for any
            derived nPods after nPod creation.
        :type snapshot_schedule_template_uuids: [str], optional
        :param volume_count: Allows specifying a volume count. This option is
            only allowed when ``shared_volume`` is set to ``False`` and allows
            creating a specific number of volumes per host / server. This is
            useful when the size of the volume does not matter but the number
            of volumes is important
        :type volume_count: int, optional

        :returns NPodTemplate: The created nPod template

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateNPodTemplateInput(
                name=name,
                saving_factor=saving_factor,
                mirrored_volume=mirrored_volume,
                boot_volume=boot_volume,
                os=os,
                volume_size_bytes=volume_size_bytes,
                shared_volume=shared_volume,
                boot_volume_size_bytes=boot_volume_size_bytes,
                boot_image_url=boot_image_url,
                app=app,
                note=note,
                snapshot_schedule_template_uuids=
                snapshot_schedule_template_uuids,
                volume_count=volume_count
            ),
            "CreateNPodTemplateInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createNPodTemplate",
            params=parameters,
            fields=NPodTemplate.fields()
        )

        # convert to object
        return NPodTemplate(response)

    def update_npod_template(
            self,
            name: str,
            volume_size_bytes: int = None,
            saving_factor: float = None,
            mirrored_volume: bool = None,
            shared_volume: bool = None,
            boot_volume: bool = None,
            boot_volume_size_bytes: int = None,
            boot_image_url: str = None,
            os: str = None,
            app: str = None,
            note: str = None,
            snapshot_schedule_template_uuids: [str] = None,
            volume_count: int = None
    ) -> NPodTemplate:
        """Update nPod template properties

        Every change to a nPod template will create a new version of the
        template and generate a new unique identifier (uuid). The parent /
        original nPod template is accessible via the nPod template
        ``parent_uuid`` property.

        :param name: The name of the nPod template to update. The name cannot
            be changed. If users want to change the name of a nPod template they
            should clone the template with a new name and delete the old record
        :type name: str
        :param saving_factor: The anticipated saving factor for the specified
            application after data compression and data deduplication. Allowed
            values are between `1.0` and `10.0`. nebulon ON will use this
            assumption for provisioning storage volumes.
        :type saving_factor: float, optional
        :param mirrored_volume: Specifies if volumes shall be mirrored for
            high availability. If set to ``True`` two copies of the same volume
            will be created in an nPod on different SPUs for high availability.
        :type mirrored_volume: bool, optional
        :param boot_volume: If set to ``True`` nebulon ON will provision a
            boot volume for the server's operating system. If set, the parameter
            ``boot_volume_size_bytes`` must also be specified.
        :type boot_volume: bool, optional
        :param os: The name of the operating system that will be installed on
            servers in the nPod.
        :type os: str, optional
        :param volume_size_bytes: The size of volumes to create in bytes. Either
            volume size or volume count must be present.
        :type volume_size_bytes: int, optional
        :param shared_volume: Allows configuring volume export options. If set
            to ``True`` all volumes except boot volumes will be made available
            to each host / server in the nPod for read and write access. If set
            to ``False`` volumes will only be made available to the local host
            of every SPU. By default volumes are created as shared volumes.
        :type shared_volume: bool, optional
        :param boot_volume_size_bytes: The size of the boot volume to create
            in bytes. This value is only considered when the parameter
            ``boot_volume`` is set to ``True``.
        :type boot_volume_size_bytes: int, optional
        :param boot_image_url: Allows specifying an HTTP(s) URL for a boot
            image that is applied to the boot volume when an nPod is created.
        :type boot_image_url: str, optional
        :param app: The name of the application that will be running on the
            nPod.
        :type app: str, optional
        :param note: An optional note for the nPod template
        :type note: str, optional
        :param snapshot_schedule_template_uuids: Allows specifying snapshot
            schedule templates that will be automatically created for any
            derived nPods after nPod creation.
        :type snapshot_schedule_template_uuids: [str], optional
        :param volume_count: Allows specifying a volume count. This option is
            only allowed when ``shared_volume`` is set to ``False`` and allows
            creating a specific number of volumes per host / server. This is
            useful when the size of the volume does not matter but the number
            of volumes is important
        :type volume_count: int, optional

        :returns NPodTemplate: The updated nPod template

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            UpdateNPodTemplateInput(
                name=name,
                saving_factor=saving_factor,
                mirrored_volume=mirrored_volume,
                boot_volume=boot_volume,
                os=os,
                volume_size_bytes=volume_size_bytes,
                shared_volume=shared_volume,
                boot_volume_size_bytes=boot_volume_size_bytes,
                boot_image_url=boot_image_url,
                app=app,
                note=note,
                snapshot_schedule_template_uuids=
                snapshot_schedule_template_uuids,
                volume_count=volume_count
            ),
            "UpdateNPodTemplateInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateNPodTemplate",
            params=parameters,
            fields=NPodTemplate.fields()
        )

        # convert to object
        return NPodTemplate(response)

    def delete_npod_template(
            self,
            parent_uuid: str
    ) -> bool:
        """Delete an existing nPod template tree

        This deletes an nPod template and all associated versions will become
        unavailable for nPod provisioning.

        :param parent_uuid: The unique identifier of the nPod template tree.
            The ``parent_uuid`` property of the nPod template should be used for
            deletion.
        :type parent_uuid: str

        :returns bool: If the deletion was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises ValueError: When illegal parameters are supplied.
        """

        # check the basics
        if parent_uuid is None or len(parent_uuid) == 0:
            raise ValueError("parent_uuid must be a valid UUID string")

        # setup query parameters
        parameters = dict()
        parameters["parentUUID"] = GraphQLParam(
            parent_uuid,
            "UUID",
            True
        )

        # make the request
        response = self._mutation(
            name="deleteNPodTemplate",
            params=parameters,
            fields=None
        )

        # response is a bool
        return response
