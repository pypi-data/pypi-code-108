from datetime import datetime
import textwrap
from pathlib import Path
from enum import Enum
from typing import Optional, Union, List

from grid.openapi import V1SessionSpec, V1SessionState, V1SessionStatus, Externalv1Session
from grid.sdk import env
from grid.sdk.client import create_swagger_client
from grid.sdk.datastores import Datastore
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.sessions import list_sessions as rest_list_sessions, get_session_from_name, get_session_from_id
from grid.sdk.rest.datastores import datastore_id_from_dsn
from grid.sdk.rest.sessions import (
    change_session_instance_type,
    create_session,
    delete_session,
    pause_session,
    resume_session,
)
from grid.sdk.affirmations import affirm, is_not_deleted, is_created, is_not_created, is_not_shallow
from grid.sdk.user import get_teams, User, user_from_logged_in_account
from grid.sdk.utilities import SPECIAL_NAME_TO_SKIP_OBJECT_INIT, read_config
from grid.sdk.utils import fill_object_from_response
from grid.sdk.utils.name_generator import unique_name


class Session:
    """Specify, Modify, Create, Pause, or Delete an interactive session instance.

    Interactive sessions are optimized for development activites (before executing
    hyperparemeter sweeps in a Run). Once created, sessions can be accessed via
    VSCode, Jupyter-lab, or SSH interfaces.

    Grid manages the installation of any/all core libraries, drivers, and interfaces
    to the outside world. Sessions can be run on anything from a small 2 CPU core +
    4GB memory instance to a monster machine with 96 CPU cores + 824 GB memory + eight
    V100 GPUs + 40 GBPS network bandwidth (no, those values aren't typos!); or really
    anything in between.

    Parameters
    ----------
    name
        human addressable name to assign to the session instance
    instance_type
        compute node type which the session will be provisioned on
    disk_size_gb
        amount of storage provisioned to the root boot disk the session
        will be provisioned on (ie. disk storage provisioned to the user)
    datastore
        datastore object
    datastore_mount_dir
        directory on the session to mount the provided datastore
    use_spot
        bool indicating if a spot instance should be used when provisioining
        the underlying machine the session service operates on. If True
        then the hourly cost will be significantly reduced from the base
        (on-demand) price, but the instance can be terminated at any time.
        Upon termination your notebooks and scripts will be saved, but you may
        lose data which is "in-process".

        If False (the default), then un-interuptable on-demand instances are
        used. While this increases costs it does mean that your machine will
        not be deprovisioned if the cloud provider experiences increased
        demand for that instance type.
    cluster_id
        Bring-your-own-credential users only. specify the name of the cluster
        to operate the sesison on.
    """

    _name: str
    _id: str
    _cluster_id: str

    _datastore: Optional[Datastore]
    _datastore_mount_dir: Optional[str]
    _disk_size_gb: str
    _instance_type: str
    _use_spot: bool

    _hourly_cost: float
    _total_cost: float
    _total_run_time: float

    _desired_state: 'SessionState'
    _status: 'SessionState'

    _created_at: datetime
    _started_at: datetime
    _finished_at: datetime
    _last_state_status_transition_at: datetime

    _jupyter_lab_url: str
    _jupyter_lab_token: str
    _ssh_url: str

    _client: GridRestClient

    _user: User

    _is_deleted: bool
    _is_created: bool

    def __init__(
        self,
        name: str,
        instance_type: Optional[str] = None,
        disk_size_gb: Union[int, str] = 200,
        datastore: Optional[Datastore] = None,
        datastore_mount_dir: Optional[str] = None,
        use_spot: bool = False,
        cluster_id: Optional[str] = None,
        config_file: Optional[Union[str, Path]] = None,
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
        if name is None:
            name = unique_name()
        else:
            try:
                session = get_session_from_name(self._client, name, cluster_id)
                self._setup_from_response(session)
                return
            except KeyError:
                self._is_deleted = False  # the run has not been deleted
                self._is_created = False  # it doesn't exists in the grid backend.
                pass

        if not datastore_mount_dir and isinstance(datastore, Datastore):
            datastore_mount_dir = f'/datastores/{datastore.name}'

        # The config option should be deprecated. This just takes the file passed in an
        # attempts to get the values provided within it, defaulting back to the standard
        # CLI click option values if they are not provided.
        if config_file is not None:
            config = read_config(config_file)
            cluster_id = config.get('compute', {}).get('provider', {}).get('cluster', cluster_id)
            instance_type = config.get('compute', {}).get('train').get('instance_type', instance_type)
            disk_size_gb = config.get('compute', {}).get('train', {}).get('disk_size', disk_size_gb)
            use_spot = config.get('compute', {}).get('train', {}).get('use_spot', use_spot)
            datastore_name = config.get('compute', {}).get('train', {}).get('datastore_name')
            datastore_version = config.get('compute', {}).get('train', {}).get('datastore_version')
            datastore_mount_dir = config.get('compute', {}).get('train',
                                                                {}).get('datastore_mount_dir', datastore_mount_dir)
            _dstore_config = [datastore_name, datastore_version]
            if any(_dstore_config) and not all(_dstore_config):
                raise ValueError(
                    "name and version are both required if one of datastore_name or datastore_version is set"
                )
            if all(_dstore_config):
                datastore = Datastore(name=datastore_name, version=datastore_version)

        self._name = name
        self._instance_type = instance_type
        self._disk_size_gb = str(disk_size_gb)

        self._datastore = datastore
        self._datastore_mount_dir = datastore_mount_dir

        self._use_spot = use_spot
        self._cluster_id = cluster_id
        self._name = name
        self._user = user_from_logged_in_account()

        self._is_deleted = False
        self._is_created = False
        self._has_initialized = True

    @classmethod
    def _from_id(cls, session_id: str, cluster_id: Optional[str] = env.CONTEXT) -> "Session":
        instance = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT, cluster_id=cluster_id)
        instance._id = session_id
        instance._is_shallow = True
        return instance

    def _unshallow(self):
        """ If the object is a shallow (i.e. only has an id and `_is_shallow` attribute is True)
        object, this method can be triggered to get the full object from the BE. It is designed
        to be called only from the `is_not_shallow` decorator and should not be called directly.
        """
        if not self._is_shallow:
            raise RuntimeError('Session is already unshallow')
        if not hasattr(self, '_id') or self._id is None:
            raise RuntimeError("Cannot unshallow resource without a valid session id")
        self._is_shallow = False
        run = get_session_from_id(self._client, run_id=self._id, cluster_id=self.cluster_id)
        self._setup_from_response(run)

    @affirm(is_not_shallow, is_not_deleted)
    def __repr__(self):
        if self._is_created is True:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                    {"name": <17} = \"{self.name}\",
                    {"cluster_id": <17} = \"{self.cluster_id}\",
                    {"datastore": <17} = {self.datastore},
                    {"disk_size_gb": <17} = {self.disk_size_gb},
                    {"instance_type": <17} = \"{self.instance_type}\",
                    {"use_spot": <17} = {self.use_spot},
                    {"hourly_cost": <17} = {self.hourly_cost},
                    {"total_cost": <17} = {self.total_cost},
                    {"total_run_time": <17} = {self.total_run_time},
                    {"desired_state": <17} = {self.desired_state.value},
                    {"last_status_state": <17} = {self.status.value},
                    {"jupyter_lab_url": <17} = \"{self.jupyter_lab_url}\",
                    {"jupyter_lab_token": <17} = \"{self.jupyter_lab_token}\",
                    {"ssh_url": <17} = \"{self.ssh_url}\",
                )"""
            )
        else:
            res = textwrap.dedent(
                f"""\
            {self.__class__.__name__}(
                {"name": <17} = \"{self.name}\",
                {"cluster_id": <17} = \"{self.cluster_id}\",
                {"datastore": <17} = {self.datastore},
                {"disk_size_gb": <17} = {self.disk_size_gb},
                {"instance_type": <17} = \"{self.instance_type}\",
                {"use_spot": <17} = {self.use_spot},
            )"""
            )
        return res

    # ---------------- User Modifiable Attributes -----------------

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def name(self) -> str:
        """The name of the session."""
        return self._name

    @name.setter
    @affirm(is_not_created)
    def name(self, value: str):
        self._name = value

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def cluster_id(self) -> str:
        """The name of the cluster the session is running on.
        """
        return self._cluster_id

    @cluster_id.setter
    @affirm(is_not_shallow, is_created)
    def cluster_id(self, value: str):
        self._cluster_id = value

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def datastore(self) -> Datastore:
        return self._datastore

    @datastore.setter
    @affirm(is_not_shallow, is_created)
    def datastore(self, value: Datastore):
        self._datastore = value

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def datastore_mount_dir(self) -> str:
        return self._datastore_mount_dir

    @datastore_mount_dir.setter
    @affirm(is_not_shallow, is_created)
    def datastore_mount_dir(self, value: str):
        self._datastore_mount_dir = value

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def disk_size_gb(self) -> str:
        """The size of the home directory disk to spin up
        """
        return self._disk_size_gb

    @disk_size_gb.setter
    @affirm(is_not_shallow, is_created)
    def disk_size_gb(self, value: str):
        self._disk_size_gb = value

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def instance_type(self) -> str:
        """The type of the virtual machine used on the compute cluster when running the session.
        """
        return self._instance_type

    @instance_type.setter
    @affirm(is_not_shallow, is_created)
    def instance_type(self, value: str):
        self._instance_type = value

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def use_spot(self) -> bool:
        """If a spot instance type is used to spin up the session.
        """
        return self._use_spot

    @use_spot.setter
    @affirm(is_not_shallow, is_created)
    def use_spot(self, value: bool):
        self._use_spot = value

    # ----------------------- Fixed Attributes ---------------------------

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def hourly_cost(self) -> float:
        """The per hour cost of this session configuration when it is in a 'RUNNING' state.
        """
        return self._hourly_cost

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def total_cost(self) -> float:
        """The total cost of the session over it's entire lifetime.
        """
        return self._total_cost

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def total_run_time(self) -> float:
        """How long the session has run for (not including paused time) in second.
        """
        return self._total_run_time

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def desired_state(self) -> 'SessionState':
        """The state of the system we are trying to achieve.

        This might be one of 'PENDING', 'RUNNING', 'PAUSED'
        """
        return self._desired_state

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def status(self) -> 'SessionState':
        """The last recorded state of the session instance on the grid platform.

        This might be one of 'PENDING', 'RUNNING', 'PAUSED'
        """
        return self._status

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def created_at(self) -> datetime:
        """The timestamp when the session was first created.
        """
        return self._created_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def started_at(self) -> datetime:
        """The timestamp when the session was last started.
        """
        return self._started_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def finished_at(self) -> datetime:
        """The timestamp when the session was last stopped.
        """
        return self._finished_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def last_state_status_transition_at(self) -> datetime:
        """The last timestamp when the session's running state was changed.
        """
        return self._last_state_status_transition_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def jupyter_lab_url(self) -> str:
        """URL to access the jupyterlab server at over the public internet.
        """
        return self._jupyter_lab_url

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def jupyter_lab_token(self) -> str:
        """Security token required to access this session over the public internet.
        """
        return self._jupyter_lab_token

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def ssh_url(self) -> str:
        """URL used to SSH into this session.
        """
        return self._ssh_url

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def user(self) -> User:
        """Details of the user who is the creator of this session.
        """
        return self._user

    @property
    def exists(self) -> bool:
        """If this object refers to a session which has been created on the grid platform.

        Prior to calling `start` for the frist time, the grid platform has not created
        the actual session implementation, and the object does not exist.
        """
        return self._is_created

    # ---------------------- Interaction Methods -----------------------------------

    def start(self) -> bool:
        """Start an interactive session based on this configuration.

        If the session does not exist, a new session will be created; if the session
        exists, but is paused, then the session will be resumed; if the session exists
        and is already running, no action will be taken.
        """
        if self._is_created is True:
            session = resume_session(self._client, session_id=self._id, cluster_id=self._cluster_id)
        else:
            datastores = {self.datastore.id: self.datastore_mount_dir} if self.datastore else None
            session = create_session(
                self._client,
                name=self._name,
                instance_type=self._instance_type,
                cluster_id=self._cluster_id,
                datastores=datastores,
                disk_size_gb=self._disk_size_gb,
                use_spot=self._use_spot
            )
        self._setup_from_response(session)
        return True

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def pause(self) -> bool:
        """Pauses a session which is currently running.

        Pausing a session stops the running instance (and any computations being
        performed on it - be sure to save your work!) and and billing of your account
        for the machine. The session can be resumed at a later point with all your
        persisted files and saved work unchanged.
        """
        session = pause_session(self._client, session_id=self._id, cluster_id=self._cluster_id)
        self._setup_from_response(session)
        return True

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def delete(self) -> bool:
        """Deletes a session which is either running or paused.

        Deleting a session will stop the running instance (and any computations being
        performed on it) and billing of your account. All work done on the machine
        is permenantly removed, including all/any saved files, code, or downloaded
        data (assuming the source of the data was not a grid datastore - datastore
        data is not deleted).
        """
        delete_session(self._client, session_id=self._id, cluster_id=self._cluster_id)
        self._is_deleted = True
        return True

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def change_instance_type(self, instance_type: str, use_spot: Optional[bool] = None) -> bool:
        """Change the instance type of a session.

        The session must be paused before calling this method.

        Parameters
        ----------
        instance_type
            the new instance type the session node should use.
        use_spot
            if true, use interuptable spot instances (which come at a steap discount,
            but which can be interrupted and shut down at any point in time depending
            on cloud provider instance type demand). If false, use an on-demand instance.

            By default this value is None, indicating that no change will be made to the
            current configuratoin.
        """
        if self.status != SessionState.PAUSED:
            raise RuntimeError("session must be paused before calling `change_instance_type`.")

        resp = change_session_instance_type(
            self._client,
            session_id=self._id,
            instance_type=instance_type,
            use_spot=use_spot,
            cluster_id=self._cluster_id
        )
        self._setup_from_response(resp)
        return True

    def _setup_from_response(self, session: Externalv1Session):
        self._is_created = True
        self._is_deleted = session.status.phase == V1SessionState.DELETED
        self._is_shallow = False

        spec: V1SessionSpec = session.spec
        status: V1SessionStatus = session.status

        self._cluster_id = spec.cluster_id
        self._id = session.id
        self._name = session.name
        self._instance_type = spec.instance_type
        self._disk_size_gb = spec.resources.storage_gb
        self._use_spot = spec.use_spot
        for dstore_input in spec.datastores:
            datastore_id = datastore_id_from_dsn(dstore_input.dsn)
            # noinspection PyProtectedMember
            datastore = Datastore._from_id(datastore_id, cluster_id=self.cluster_id)
            datastore._id = datastore_id
            self._datastore = datastore
            self._datastore_mount_dir = dstore_input.mount_path

        # TODO - getattr because BE is sometimes respond with different types. Unify this
        self._hourly_cost = getattr(session, "hourly_cost", None)
        self._total_cost = getattr(session, "cost", None)
        self._total_run_time = float(status.total_run_time_seconds or 0)

        self._desired_state = SessionState.from_api_spec(spec.desired_state)
        self._status = SessionState.from_api_spec(status.phase)

        self._created_at = session.created_at
        self._started_at = status.start_timestamp
        self._finished_at = status.stop_timestamp
        self._last_state_status_transition_at = status.last_state_status_transition_timestamp

        self._jupyter_lab_url = status.jupyter_lab_url
        self._jupyter_lab_token = status.jupyter_lab_token
        self._ssh_url = status.ssh_url

        # TODO: complete with owner's username, first name, & last name
        self._user = User(user_id=session.spec.user_id, username="", first_name="", last_name="")


def list_sessions(cluster_id: Optional[str] = None, include_teams: Optional[bool] = False) -> List[Session]:
    """List sessions for user/team

    Parameters
    ----------
    cluster_id:
        the cluster id to list sessions from
    include_teams:
        if True, returns a list of sessions of the everyone in the team

    Returns
    -------
    List[Session]
        sequence of session interaction objects.
    """
    cluster_id = cluster_id or env.CONTEXT
    c = GridRestClient(create_swagger_client())
    users = {}
    user_ids = None
    if include_teams is True:
        teams = get_teams()
        user_ids = []
        for team in teams.values():
            for user_id in team.members:
                users[user_id] = team.members[user_id]
                user_ids.append(user_id)
    sessions = []
    for session_def in rest_list_sessions(c, user_ids=user_ids, cluster_id=cluster_id):
        session_obj = Session(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT)
        fill_object_from_response(session_obj, session_def)
        session_obj._user = users.get(session_obj.user.user_id, session_obj.user)
        sessions.append(session_obj)
    return sessions


class SessionState(Enum):
    UNSPECIFIED = "unspecified"
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    DELETED = "deleted"
    FAILED = "failed"

    @classmethod
    def from_api_spec(cls, status: V1SessionState) -> 'SessionState':
        parsed = str(status).lower().split('_', maxsplit=2)[-1]
        return cls(parsed)
