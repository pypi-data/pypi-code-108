import textwrap
from datetime import datetime
from enum import Enum
from typing import Dict, NamedTuple, Optional, List

from grid.openapi.rest import ApiException
from grid.sdk.datastores import Datastore
from grid.sdk.run_components import Actions, Resources, ScratchSpace
from grid.sdk import env
from grid.sdk.rest.client import GridRestClient
from grid.sdk.affirmations import affirm, is_not_deleted, is_created, is_not_shallow
from grid.sdk.rest.experiments import get_experiment_from_id, get_experiment_by_name, update_experiment, \
    delete_experiment
from grid.sdk.user import User
from grid.sdk.client import create_swagger_client

from grid.openapi.models import (V1ExperimentState, V1PackageManager, Externalv1Experiment)
from grid.sdk.utilities import SPECIAL_NAME_TO_SKIP_OBJECT_INIT


class ExperimentName(NamedTuple):
    name: str
    username: Optional[str]

    @classmethod
    def from_external_format(cls, name: str):
        """User can pass experiments as username:experiment_name to fetch other users experiments.
        """
        username = None
        split = name.split(":")
        if len(split) > 2:
            raise ValueError(f"Error while parsing {name}. Use the format <username>:<experiment-name>")
        elif len(split) == 2:
            username = split[0]
            name = split[1]

        return cls(name=name, username=username)


class Experiment:
    _client: GridRestClient

    _created_at: datetime
    _description: str
    _id: str
    _name: str
    _updated_at: datetime
    _actions: Actions
    _cluster_id: str
    _command: List[str]
    _datastore: Datastore
    _datastore_mount_dir: str
    _desired_state: 'ExperimentState'
    _dry_run: bool
    _env: Dict[str, str]
    _runner_framework: str
    _runner_dockerfile: str
    _runner_requirements_file: str
    _runner_package_manager: str
    _instance_type: str
    _resources: Resources
    _run_controller_id: str
    _scratch: ScratchSpace
    _source_code: str
    _use_spot: bool
    _user_id: str
    _cost: float
    _deleted_timestamp: datetime
    _finish_timestamp: datetime
    _hourly_cost: float
    _message: str
    _status: 'ExperimentState'
    _start_timestamp: datetime
    _user: User

    _is_deleted: bool
    _is_created: bool
    _is_shallow: bool

    def __init__(
        self,
        name: str,
        cluster_id: Optional[str] = None,
    ):
        # --------------------------------------------------------------------------- #
        #    This should be the first block that goes into the constructor of the     #
        #    resource object. This block sets the correct values for the private      #
        #    attributes which is then later picked up by the decorator(s) to take     #
        #    right actions. It also initialize the _client object and cluster_id      #
        #    which is required by the downstream methods regardless of the object     #
        #    is completely initialized or not. Most importantly, this blocks checks   #
        #    for the name argument to decide if it's a call from other internal       #
        #    methods to create a shallow object. This is done by checking the         #
        #    special name variable. Other methods that already has the backend        #
        #    response fetched, can use this to create the object without the backend  #
        #    call and then fill-in the response they already have.                    #
        #                                                                             #
        self._client = GridRestClient(api_client=create_swagger_client())
        cluster_id = cluster_id or env.CONTEXT
        self._is_shallow = False
        self._cluster_id = cluster_id
        if name == SPECIAL_NAME_TO_SKIP_OBJECT_INIT:
            self._is_shallow = True
            self._is_created = False
            self._is_deleted = False
            return
        #                                                                             #
        # --------------------------------------------------------------------------- #
        try:
            exp = get_experiment_by_name(client=self._client, cluster_id=self._cluster_id, experiment_name=name)
            self._setup_from_response(exp)
            return
        except KeyError:
            raise RuntimeError(
                f"Experiment {name} does not exist. If you are here "
                f"for creating experiment, use Run(...) since experiments "
                f"are grouped under Run object and can only be created "
                f"using the Run abstraction"
            ) from None

    @property
    @affirm(is_not_shallow)
    def exists(self) -> bool:
        return self._is_created

    @classmethod
    def _from_id(cls, exp_id: str, cluster_id: Optional[str] = env.CONTEXT) -> "Experiment":
        instance = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT, cluster_id=cluster_id)
        instance._id = exp_id
        return instance

    def _setup_from_response(self, exp: 'Externalv1Experiment'):
        self._is_deleted = exp.status.phase == V1ExperimentState.DELETED
        self._is_created = True
        self._is_shallow = False

        spec = exp.spec
        status = exp.status
        image = spec.image

        # TODO - setup datastore
        self._name = exp.name
        self._id = exp.id
        self._created_at = exp.created_at
        self._description = exp.description
        self._updated_at = exp.updated_at

        # spec attributes
        self._cluster_id = spec.cluster_id
        self._command = spec.command
        self._desired_state = ExperimentState.from_api_spec(spec.desired_state)
        self._dry_run = spec.dry_run
        self._env = spec.env
        self._instance_type = spec.instance_type
        self._run_controller_id = spec.run_controller_id
        self._source_code = spec.source_code
        self._use_spot = spec.use_spot
        self._user_id = spec.user_id
        # TODO - set actions, resources and scratch

        # image attributes
        self._runner_framework = image.framework
        self._runner_dockerfile = image.dockerfile
        # TODO - understand why these values could be empty from the BE
        self._runner_requirements_file = image.dependency_file_info.path if image.dependency_file_info else None
        self._runner_package_manager = image.dependency_file_info.package_manager if image.dependency_file_info else None

        # status attributes
        self._cost = status.cost
        self._deleted_timestamp = status.deleted_timestamp
        self._finish_timestamp = status.finish_timestamp
        self._hourly_cost = status.hourly_cost
        self._message = status.message
        self._status = ExperimentState.from_api_spec(status.phase)
        self._start_timestamp = status.start_timestamp

        if not hasattr(self, '_user') or self._user is None:
            # TODO - fetch user from ID - we don't have that in BE
            self._user = User(user_id=spec.user_id, username="", first_name="", last_name="")

    @property
    def id(self) -> str:
        return self._id

    @affirm(is_not_shallow, is_not_deleted)
    def __repr__(self):
        return textwrap.dedent(
            f"""\
            {self.__class__.__name__}(
                {"name": <18} = {self._name},
                {"desired_state": <18} = {self.desired_state.value},
                {"status": <18} = {self.status.value},
                {"source_code": <18} = {self._source_code},
                {"command": <18} = {self._command},
                {"user": <18} = {self.user.user_id},
                {"cluster_id": <18} = {self._cluster_id},
                {"created_at": <18} = {self._created_at},
                {"start_timestamp": <18} = {self._start_timestamp},
                {"finished_timestamp": <18} = {self._finish_timestamp},
            )"""
        )

    def _unshallow(self):
        """ If the object is a shallow (i.e. only has an id and `_is_shallow` attribute is True)
        object, this method can be triggered to get the full object from the BE. It is designed
        to be called only from the `is_not_shallow` decorator and should not be called directly.
        """
        if not self._is_shallow:
            raise RuntimeError('Experiment is already unshallow')
        if not hasattr(self, '_id') or self._id is None:
            raise RuntimeError("Cannot unshallow resource without a valid Experiment id")
        self._is_shallow = False
        try:
            exp = get_experiment_from_id(self._client, experiment_id=self._id, cluster_id=self._cluster_id)
        except ApiException as e:  # TODO change to GridException
            if hasattr(e, 'reason') and e.reason == "Not Found":
                self._is_deleted = True
                self._status = ExperimentState.DELETED
        else:
            self._setup_from_response(exp)

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def created_at(self) -> datetime:
        """created_at of the experiment configured as part of the run.
        """
        return self._created_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def description(self) -> str:
        """description of the experiment configured as part of the run.
        """
        return self._description

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def name(self) -> str:
        """name of the experiment configured as part of the run.
        """
        return self._name

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def actions(self) -> Actions:
        """actions of the experiment configured as part of the run.
        """
        return self._actions

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def cluster_id(self) -> str:
        """cluster_id of the experiment configured as part of the run.
        """
        return self._cluster_id

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def command(self) -> List[str]:
        """command of the experiment configured as part of the run.
        """
        return self._command

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def datastore(self) -> Datastore:
        """datastores of the experiment configured as part of the run.
        """
        return self._datastore

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def datastore_mount_dir(self) -> str:
        return self._datastore_mount_dir

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def desired_state(self) -> 'ExperimentState':
        """desired_state of the experiment configured as part of the run.
        """
        return self._desired_state

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def dry_run(self) -> bool:
        """dry_run of the experiment configured as part of the run.
        """
        return self._dry_run

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def env(self) -> Dict[str, str]:
        """env of the experiment configured as part of the run.
        """
        return self._env

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def runner_framework(self) -> str:  # from _image: 'Externalv1ImageSpec'
        """runner_framework of the experiment configured as part of the run.
        """
        return self._runner_framework

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def runner_dockerfile(self) -> str:  # from _image: 'Externalv1ImageSpec'
        """runner_dockerfile of the experiment configured as part of the run.
        """
        return self._runner_dockerfile

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def runner_requirements_file(self) -> str:  # from _image: 'Externalv1ImageSpec'
        """runner_requirements_file of the experiment configured as part of the run.
        """
        return self._runner_requirements_file

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def runner_package_manager(self) -> 'V1PackageManager':  # from _image: 'Externalv1ImageSpec'
        """runner_package_manager of the experiment configured as part of the run.
        """
        return self._runner_package_manager

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def instance_type(self) -> str:
        """instance_type of the experiment configured as part of the run.
        """
        return self._instance_type

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def resources(self) -> Resources:
        """resources of the experiment configured as part of the run.
        """
        return self._resources

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def run_controller_id(self) -> str:
        """run_controller_id of the experiment configured as part of the run.
        """
        return self._run_controller_id

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def scratch(self) -> ScratchSpace:
        """scratch of the experiment configured as part of the run.
        """
        return self._scratch

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def source_code(self) -> str:
        """source_code of the experiment configured as part of the run.
        """
        return self._source_code

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def use_spot(self) -> bool:
        """use_spot of the experiment configured as part of the run.
        """
        return self._use_spot

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def user(self) -> User:
        """user who owns the of the experiment/run.
        """
        return self._user

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def cost(self) -> float:
        """cost of the experiment configured as part of the run.
        """
        return self._cost

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def deleted_timestamp(self) -> datetime:
        """deleted_timestamp of the experiment configured as part of the run.
        """
        return self._deleted_timestamp

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def finish_timestamp(self) -> datetime:
        """finish_timestamp of the experiment configured as part of the run.
        """
        return self._finish_timestamp

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def hourly_cost(self) -> float:
        """hourly_cost of the experiment configured as part of the run.
        """
        return self._hourly_cost

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def message(self) -> str:
        """message of the experiment configured as part of the run.
        """
        return self._message

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def status(self) -> 'ExperimentState':
        """status of the experiment configured as part of the run.
        """
        return self._status

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def start_timestamp(self) -> datetime:
        """start_timestamp of the experiment configured as part of the run.
        """
        return self._start_timestamp

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def cancel(self) -> bool:
        """Request the grid platform cancels the experiment
        """
        # do not perform POST if we know that we don't have to
        exp = update_experiment(
            client=self._client,
            cluster_id=self._cluster_id,
            experiment_id=self._id,
            desired_state=V1ExperimentState.CANCELLED
        )
        self._setup_from_response(exp)
        self._is_deleted = True
        return True

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def delete(self) -> bool:
        """Request the grid platform cancels the experiment
        """
        # do not perform POST if we know that we don't have to
        delete_experiment(client=self._client, cluster_id=self._cluster_id, experiment_id=self._id)
        self._is_deleted = True
        self._is_created = False
        return True


class ExperimentState(Enum):
    """
    The state of an experiment.
    """
    UNSPECIFIED = "unspecified"
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELETED = "deleted"
    PAUSED = "paused"
    IMAGE_BUILDING = "image_building"

    @classmethod
    def from_api_spec(cls, status: V1ExperimentState) -> 'ExperimentState':
        parsed = str(status).lower().split('_', maxsplit=2)[-1]
        return cls(parsed)
