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

from datetime import datetime
from .common import NebEnum, read_value
from .graphqlclient import NebMixin, GraphQLParam

__all__ = [
    "RecipeRecord",
    "RecipeType",
    "RecipeRecordList",
    "RecipeState",
    "RecipeMixin"
]


class RecipeState(NebEnum):
    """Status of the recipe execution"""
    Queued = "Queued"
    Running = "Running"
    Completed = "Completed"
    Failed = "Failed"
    Timeout = "Timeout"
    Cancelling = "Cancelling"
    Cancelled = "Cancelled"


class RecipeType(NebEnum):
    """Type of recipe"""
    Unknown = "Unknown"
    Claim = "Claim"
    CreateVolume = "CreateVolume"
    CreatePod = "CreatePod"
    ValidatePod = "ValidatePod"
    ConfirmPod = "ConfirmPod"
    CreateSnapshot = "CreateSnapshot"
    CreateScheduledSnapshot = "CreateScheduledSnapshot"
    Update = "Update"
    AbortUpdate = "AbortUpdate"
    RemoveSnapshotSchedule = "RemoveSnapshotSchedule"
    SendSPUDebugInfo = "SendSPUDebugInfo"
    RunTest = "RunTest"
    WipePod = "WipePod"
    DeleteVolume = "DeleteVolume"
    SetVSphereCredentials = "SetVSphereCredentials"
    ResetOrganization = "ResetOrganization"
    PingSPU = "PingSPU"
    CreateLUN = "CreateLUN"
    DeleteLUN = "DeleteLUN"
    SetProxy = "SetProxy"
    SetNTP = "SetNTP"
    UpdatePhysicalDrive = "UpdatePhysicalDrive"
    SetTimezone = "SetTimezone"
    CloneVolume = "CloneVolume"
    LocatePhysicalDrive = "LocatePhysicalDrive"
    ReplaceSPU = "ReplaceSPU"
    SecureEraseSPU = "SecureEraseSPU"


class NPodRecipeFilter:
    """A filter object to filter recipes.

    Allows filtering active and completed recipes. Recipes are the result
    of mutations of mutations or modifications of on-premises
    infrastructure. As commands may require some time to complete, the
    recipe filter allows the query for their status.
    """

    def __init__(
            self,
            npod_uuid: str,
            recipe_uuid: str = None,
            completed: bool = None
    ):
        """Constructs a new filter object for recipes

        Allows filtering active and completed recipes. Recipes are the result
        of mutations of mutations or modifications of on-premises
        infrastructure. As commands may require some time to complete, the
        recipe filter allows the query for their status.

        At least one parameter must be specified for filtering.

        :param npod_uuid: Filter for recipes for the specified nPod. If not
            provided, recipes of all nPods will be returned
        :type npod_uuid: str, optional
        :param recipe_uuid: Filter for a specific recipe.
        :type recipe_uuid: str, optional
        :param completed: Filter for recipe completion status. If set to ``True``
            only completed recipes are returned, if set to ``False`` only active
            recipes are returned
        :type completed: bool, optional
        """

        self.__npod_uuid = npod_uuid
        self.__recipe_uuid = recipe_uuid
        self.__completed = completed

    @property
    def npod_uuid(self):
        """Filter for recipes for a specific nPod with the given UUID"""
        return self.__npod_uuid

    @property
    def recipe_uuid(self):
        """Filter for a specific recipe matching the provided UUID"""
        return self.__recipe_uuid

    @property
    def completed(self):
        """Filter for completed recipes"""
        return self.__completed

    @property
    def as_dict(self):
        result = dict()
        result["nPodUUID"] = self.npod_uuid
        result["recipeUUID"] = self.recipe_uuid
        result["completed"] = self.completed
        return result


class RecipeRecord:
    """A recipe record

    A recipe record describes the status of the execution of a mutation that
    affects on-premises infrastructure. Status information of such mutations
    are recorded in recipe records.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new RecipeRecord object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__recipe_uuid = read_value(
            "recipeUUID", response, str, True)
        self.__cancel_recipe_uuid = read_value(
            "cancelRecipeUUID", response, str, True)
        self.__npod_uuid = read_value(
            "nPodUUID", response, str, True)
        self.__state = read_value(
            "state", response, RecipeState, True)
        self.__status = read_value(
            "status", response, str, True)
        self.__start = read_value(
            "start", response, datetime, True)
        self.__last_update = read_value(
            "lastUpdate", response, datetime, True)
        self.__coordinator_spu_serial = read_value(
            "coordinatorSPUSerial", response, str, True)
        self.__type = read_value(
            "type", response, RecipeType, True)

    @property
    def recipe_uuid(self) -> str:
        """Unique identifier of the recipe"""
        return self.__recipe_uuid

    @property
    def cancel_recipe_uuid(self) -> str:
        """The identifier of the recipe used for canceling"""
        return self.__cancel_recipe_uuid

    @property
    def npod_uuid(self) -> str:
        """The identifier of the nPod that is involved in the recipe"""
        return self.__npod_uuid

    @property
    def state(self) -> RecipeState:
        """Status of the recipe execution"""
        return self.__state

    @property
    def status(self) -> str:
        """Status description of the recipe execution"""
        return self.__status

    @property
    def start(self) -> datetime:
        """Date and time when the recipe execution started"""
        return self.__start

    @property
    def last_update(self) -> datetime:
        """Date and time when nebulon ON last got an update on recipe status"""
        return self.__last_update

    @property
    def coordinator_spu_serial(self) -> str:
        """The serial number of the SPU that coordinates recipe execution"""
        return self.__coordinator_spu_serial

    @property
    def type(self) -> RecipeType:
        """Type of recipe"""
        return self.__type

    @staticmethod
    def fields():
        return [
            "recipeUUID",
            "cancelRecipeUUID",
            "nPodUUID",
            "state",
            "status",
            "start",
            "lastUpdate",
            "coordinatorSPUSerial",
            "type",
        ]


class RecipeRecordList:
    """List of recipes"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new RecipeRecordList object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__cursor = read_value(
            "cursor", response, str, False)
        self.__items = read_value(
            "items", response, RecipeRecord, True)

    @property
    def cursor(self) -> str:
        """Cursor used for pagination"""
        return self.__cursor

    @property
    def items(self) -> [RecipeRecord]:
        """List of recipe items"""
        return self.__items

    @staticmethod
    def fields():
        return [
            "cursor",
            "items{%s}" % (",".join(RecipeRecord.fields())),
        ]


class RecipeMixin(NebMixin):
    """Mixin to add recipe functions to the GraphQL client"""

    def get_npod_recipes(
            self,
            npod_uuid: str,
            recipe_uuid: str = None,
            completed: bool = None
    ) -> RecipeRecordList:
        """Retrieves a list of recipes

        Recipes are the result of mutations of mutations or modifications of
        on-premises infrastructure. As commands may require some time to
        complete, the recipe filter allows the query for their status.

        :param npod_uuid: The unique identifier of the nPod for which recipes
            shall be returned
        :type npod_uuid: str
        :param recipe_uuid: The unique identifier of the recipe to retrieve. If
            not specified all recipes for the specified nPod will be returned
            that match the remaining filter criteria.
        :type recipe_uuid: str, optional
        :param completed: If provided and set to ``True`` only completed recipes
            are returned. If provided and set to ``False`` only active recipes
            are returned. If omitted, all recipes, independent of their status,
            are returned, provided they match the remaining criteria.
        :type completed: bool, optional

        :returns RecipeRecordList: A paginated list of recipes.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["filter"] = GraphQLParam(
            NPodRecipeFilter(
                npod_uuid=npod_uuid,
                recipe_uuid=recipe_uuid,
                completed=completed
            ),
            "NPodRecipeFilter",
            False
        )

        # make the request
        response = self._query(
            name="getNPodRecipes",
            params=parameters,
            fields=RecipeRecordList.fields()
        )

        # convert to object
        return RecipeRecordList(response)
