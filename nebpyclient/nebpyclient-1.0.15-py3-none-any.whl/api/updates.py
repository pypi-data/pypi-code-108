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
from datetime import datetime
from .common import NebEnum, read_value
from .issues import Issues
from .tokens import TokenResponse

__all__ = [
    "NebPackagePriority",
    "NebPackageType",
    "PackageInfo",
    "RecommendedPackages",
    "UpdatePackages",
    "UpdateStateSpu",
    "UpdateHistory",
    "UpdatesMixin"
]


class NebPackagePriority(NebEnum):
    """Indicates the importance for installing a nebulon package"""

    Normal = "Normal"
    """Indicates a routing installation package"""

    Critical = "Critical"
    """Indicates a critical update"""


class NebPackageType(NebEnum):
    """Indicates the type of software package"""

    Base = "Base"
    """Baseline package that includes major changes to nebOS"""

    Patch = "Patch"
    """A patch package that resolves a specific issue with nebOS"""

    Recovery = "Recovery"
    """A package that is used for recovery purposes"""


class PackageInfo:
    """A nebulon update package

    Allows updating nebulon services processing units to a specific nebOS
    version. The package information object describes each released nebOS
    package.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new package information object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__package_name = read_value(
            "packageName", response, str, True)
        self.__package_size_bytes = read_value(
            "packageSize", response, int, True)
        self.__release_notes_url = read_value(
            "releaseNotesURL", response, str, True)
        self.__prerequisites = read_value(
            "prerequisites", response, str, True)
        self.__package_description = read_value(
            "packageDescription", response, str, True)
        self.__package_type = read_value(
            "packageType", response, NebPackageType, True)
        self.__package_priority = read_value(
            "packagePriority", response, NebPackagePriority, True)
        self.__package_deprecated = read_value(
            "packageDeprecated", response, bool, True)
        self.__release_unix = read_value(
            "releaseUnix", response, int, True)
        self.__eligible_npod_uuids = read_value(
            "eligiblePods.uid", response, str, False)
        self.__version_number = read_value(
            "versionNumber", response, str, True)
        self.__patch_number = read_value(
            "patchNumber", response, str, False)

    @property
    def package_name(self) -> str:
        """The name of the nebulon update package"""
        return self.__package_name

    @property
    def package_size_bytes(self) -> int:
        """The size of the update package in bytes"""
        return self.__package_size_bytes

    @property
    def release_notes_url(self) -> str:
        """A URL to the release notes of the package"""
        return self.__release_notes_url

    @property
    def prerequisites(self) -> str:
        """Describes the prerequisites for the package"""
        return self.__prerequisites

    @property
    def package_description(self) -> str:
        """Description for the package"""
        return self.__package_description

    @property
    def package_type(self) -> NebPackageType:
        """Type of the nebOS installation package"""
        return self.__package_type

    @property
    def package_priority(self) -> NebPackagePriority:
        """Indicates the importance for installing a nebulon package"""
        return self.__package_priority

    @property
    def package_deprecated(self) -> bool:
        """Indicates it the package is deprecated and no longer available"""
        return self.__package_deprecated

    @property
    def release_unix(self) -> int:
        """The release date as a UNIX timestamp"""
        return self.__release_unix

    @property
    def eligible_npod_uuids(self) -> list:
        """List of nPod unique identifiers that can install this package"""
        return self.__eligible_npod_uuids

    @property
    def version_number(self) -> str:
        """The version number if it is a nebOS package"""
        return self.__version_number

    @property
    def patch_number(self) -> str:
        """The patch number if it is a patch"""
        return self.__patch_number

    @staticmethod
    def fields():
        return [
            "packageName",
            "packageSize",
            "releaseNotesURL",
            "prerequisites",
            "packageDescription",
            "packageType",
            "packagePriority",
            "packageDeprecated",
            "releaseUnix",
            "eligiblePods{uid}",
            "versionNumber",
            "patchNumber",
        ]


class RecommendedPackages:
    """Recommended packages for customers

    Recommended packages indicate the currently recommended packages for
    customers given their current version and hardware.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new recommended packages object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__spu_type = read_value(
            "spuType", response, str, True)
        self.__base_version = read_value(
            "baseVersion", response, str, True)
        self.__package_name = read_value(
            "packageName", response, str, True)
        self.__package_info = read_value(
            "packageInfo", response, PackageInfo, False)

    @property
    def spu_type(self) -> str:
        """Indicates the type of SPU for which the package is recommended"""
        return self.__spu_type

    @property
    def base_version(self) -> str:
        """Indicates the base version for the recommended package"""
        return self.__base_version

    @property
    def package_name(self) -> str:
        """The name of the package that is recommended"""
        return self.__package_name

    @property
    def package_info(self) -> PackageInfo:
        """Information concerning the update pacakge"""
        return self.__package_info

    @staticmethod
    def fields():
        return [
            "spuType",
            "baseVersion",
            "packageName",
            "packageInfo{%s}" % ",".join(PackageInfo.fields()),
        ]


class UpdatePackages:
    """An object describing nebOS software packages

    Describes software packages that are available for installation and
    recommended for customers.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new update packages object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__available = read_value(
            "available", response, PackageInfo, False)
        self.__recommended = read_value(
            "recommended", response, RecommendedPackages, False)
        self.__latest = read_value(
            "latest", response, str, True)

    @property
    def available(self) -> [PackageInfo]:
        """List of available nebulon software packages"""
        return self.__available

    @property
    def recommended(self) -> [RecommendedPackages]:
        """List or recommended nebulon software packages"""
        return self.__recommended

    @property
    def latest(self) -> str:
        """The latest available nebulon software package"""
        return self.__latest

    @staticmethod
    def fields():
        return [
            "available{%s}" % ",".join(PackageInfo.fields()),
            "recommended{%s}" % ",".join(RecommendedPackages.fields()),
            "latest",
        ]


class UpdateStateSpu:
    """An object describing the current state of an update installation"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new update status object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__update_id = read_value(
            "updateID", response, str, True)
        self.__spu_serial = read_value(
            "SPUSerial", response, str, True)
        self.__package_name = read_value(
            "packageName", response, str, True)
        self.__download_progress_pct = read_value(
            "downloadProgressPct", response, int, True)
        self.__waiting_for_spu_serial = read_value(
            "waitingForSPUSerial", response, str, True)
        self.__started_install = read_value(
            "startedInstall", response, bool, True)
        self.__restarting = read_value(
            "restarting", response, bool, True)
        self.__restart_complete = read_value(
            "restartComplete", response, bool, True)
        self.__failure_log = read_value(
            "failureLog", response, str, False)
        self.__last_changed = read_value(
            "lastChanged", response, datetime, True)

    @property
    def update_id(self) -> str:
        """The identifier of the update"""
        return self.__update_id

    @property
    def spu_serial(self) -> str:
        """The serial number for the SPU on which the update is installed"""
        return self.__spu_serial

    @property
    def package_name(self) -> str:
        """The name of the package that is installed"""
        return self.__package_name

    @property
    def download_progress_pct(self) -> int:
        """Download progress in percent"""
        return self.__download_progress_pct

    @property
    def waiting_for_spu_serial(self) -> str:
        """Indicates if the SPU is waiting for a SPU to complete its update"""
        return self.__waiting_for_spu_serial

    @property
    def started_install(self) -> bool:
        """Indicates if the SPU has started installing the SPU"""
        return self.__started_install

    @property
    def restarting(self) -> bool:
        """Indicates if nebOS is restarting"""
        return self.__restarting

    @property
    def restart_complete(self) -> bool:
        """Indicates if nebOS has completed the restart"""
        return self.__restart_complete

    @property
    def failure_log(self) -> str:
        """Contains information about update errors"""
        return self.__failure_log

    @property
    def last_changed(self) -> datetime:
        """Date and time when the SPU last reported update status"""
        return self.__last_changed

    @staticmethod
    def fields():
        return [
            "updateID",
            "SPUSerial",
            "packageName",
            "downloadProgressPct",
            "waitingForSPUSerial",
            "startedInstall",
            "restarting",
            "restartComplete",
            "failureLog",
            "lastChanged",
        ]


class UpdateHistory:
    """An object describing past updates"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new update history object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__update_id = read_value(
            "updateID", response, str, True)
        self.__package_name = read_value(
            "packageName", response, str, True)
        self.__start = read_value(
            "start", response, datetime, True)
        self.__finish = read_value(
            "finish", response, datetime, False)
        self.__success = read_value(
            "success", response, bool, True)

    @property
    def update_id(self) -> str:
        """The identifier of the update"""
        return self.__update_id

    @property
    def package_name(self) -> str:
        """The name of the package that is installed"""
        return self.__package_name

    @property
    def start(self) -> datetime:
        """Date and time when the update started"""
        return self.__start

    @property
    def finish(self) -> datetime:
        """Date and time when the update completed"""
        return self.__finish

    @property
    def success(self) -> bool:
        """Indicates if the update completed successully"""
        return self.__success

    @staticmethod
    def fields():
        return [
            "updateID",
            "packageName",
            "start",
            "finish",
            "success",
        ]


class UpdatesMixin(NebMixin):
    """Mixin to add update related methods to the GraphQL client"""

    def get_update_packages(self) -> UpdatePackages:
        """Retrieves a list of update packages

        :returns UpdatePackages: An object describing latest, available, and
            recommended nebOS software packages

        :raises GraphQLError: An error with the GraphQL endpoint
        """

        # make the request
        response = self._query(
            name="updatePackages",
            params=None,
            fields=UpdatePackages.fields()
        )

        # convert to object
        return UpdatePackages(response)

    def __run_update_precheck(
            self,
            npod_uuid: str,
            package_name: str
    ) -> Issues:
        """Runs diagnostics before an update is installed

        Ensures that an nPod is in a healthy state and that there are no issues
        preventing a successful update

        :param npod_uuid: The unique identifier of the nPod for which the
            update pre-check is performed
        :type npod_uuid: str
        :param package_name: The package name to be installed
        :type package_name: str

        :returns Issues: A list of warnings and errors discovered during the
            pre-check

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["podUID"] = GraphQLParam(
            npod_uuid, "String", True)
        parameters["packageName"] = GraphQLParam(
            package_name, "String", True)

        # make the request
        response = self._query(
            name="updatePrecheck",
            params=parameters,
            fields=Issues.fields()
        )

        # convert to object
        return Issues(response)

    def update_npod_firmware(
            self,
            npod_uuid: str,
            package_name: str,
            schedule_at: datetime = None,
            ignore_warnings: bool = False
    ):
        """Update nPod firmware to specified package

        :param npod_uuid: The unique identifier of the nPod to update
        :type npod_uuid: str
        :param package_name: The package name to install
        :type package_name: str
        :param schedule_at: Allows scheduling the installation of a package
            at the specified date and time. If omitted, the package will be
            installed immediately
        :type schedule_at: datetime, optional
        :param ignore_warnings: If specified warnings that are discovered during
            the update pre-check are ignored (not recommended). If omitted or
            set to ``False`` will cause the update to stop.
        :type ignore_warnings: bool, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises ValueError: If illegal parameters are specified
        :raises Exception: If token delivery fails
        """

        # basic input validation
        if npod_uuid is None or len(npod_uuid) == 0:
            raise ValueError("npod_uuid must be a valid UUID string")

        if package_name is None or len(package_name) == 0:
            raise ValueError("package_name must be specified")

        if schedule_at is not None and schedule_at < datetime.now():
            raise ValueError("scheduled time may not be in the past")

        # first run an update pre-check
        issues = self.__run_update_precheck(
            npod_uuid=npod_uuid,
            package_name=package_name
        )
        issues.assert_no_issues(ignore_warnings=ignore_warnings)

        # setup query parameters
        parameters = dict()
        parameters["podUID"] = GraphQLParam(
            npod_uuid, "String", True)
        parameters["packageName"] = GraphQLParam(
            package_name, "String", True)
        parameters["scheduled"] = GraphQLParam(
            schedule_at, "Time", False)

        # make the request
        response = self._mutation(
            name="updatePodFirmware",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def get_update_state(
            self,
            npod_uuid: str = None,
            update_uuid: str = None
    ) -> [UpdateStateSpu]:
        """Retrieves a list of active updates

        Allows querying for currently ongoing updates and their status
        information.

        :param npod_uuid: Filter active updates for a specific nPod by providing
            its unique identifier
        :type npod_uuid: str
        :param update_uuid: The unique identifier of an ongoing update
        :type update_uuid: str

        :returns [UpdateStateSpu]: A list of ongoing updates

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["podUID"] = GraphQLParam(
            npod_uuid, "String", False)
        parameters["updateID"] = GraphQLParam(
            update_uuid, "String", False)

        # make the request
        response = self._query(
            name="updateState",
            params=parameters,
            fields=UpdateStateSpu.fields()
        )

        # convert to object
        return [UpdateStateSpu(i) for i in response]

    def update_spu_firmware(
            self,
            spu_serial: str,
            package_name: str,
            force: bool = False
    ):
        """Update nebOS of an SPU to a specific package

        :param spu_serial: The serial number of the SPU to update
        :type spu_serial: str
        :param package_name: The name of the update package to install
        :type package_name: str
        :param force: If set to ``True`` the update will bypass any safeguards
        :type force: bool

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: If token delivery failed
        """

        # setup query parameters
        parameters = dict()
        parameters["serial"] = GraphQLParam(
            spu_serial, "String", True)
        parameters["packageName"] = GraphQLParam(
            package_name, "String", True)
        parameters["force"] = GraphQLParam(
            force, "Boolean", False)

        # make the request
        response = self._mutation(
            name="updateSPUFirmware",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def abort_spu_firmware(
            self,
            spu_serial: str = None,
            npod_uuid: str = None
    ):
        """Abort an ongoing firmware update

        Either ``spu_serial`` or ``npod_uuid`` must be specified.

        :param spu_serial: The serial number of the SPU
        :type spu_serial: str, optional
        :param npod_uuid: The unique identifier of the nPod
        :type npod_uuid: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: If token delivery failed
        """

        # setup query parameters
        parameters = dict()
        parameters["serial"] = GraphQLParam(
            spu_serial, "String", False)
        parameters["podUID"] = GraphQLParam(
            npod_uuid, "String", False)

        # make the request
        response = self._mutation(
            name="abortUpdateSPUFirmware",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()
