import warnings
from datetime import datetime
import os
from enum import Enum

from grid.openapi.rest import ApiException
from grid.sdk.affirmations import affirm, is_not_deleted, is_not_created, is_not_shallow, is_created
from pathlib import Path
import textwrap
import time
from typing import List, Optional, Union
from urllib.parse import urlparse

import click

from grid.openapi import V1GetDatastoreResponse, V1DatastoreOptimizationStatus
from grid.sdk import env
from grid.sdk._gql.queries import delete_datastore, get_available_datastores, get_user_teams
from grid.sdk.client import create_swagger_client
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.datastores import get_datastore_from_id, get_datastore_from_name
from grid.sdk.user import Team, User, user_from_logged_in_account
from grid.sdk.utilities import SPECIAL_NAME_TO_SKIP_OBJECT_INIT
from grid.sdk.utils.datastore_uploader import create_datastore_session

DATASTORE_TERMINAL_STATES = ['FAILED', 'SUCCEEDED']


def fetch_datastore(datastore_name: str, datastore_version: int, cluster: str) -> 'Datastore':
    """
    Validate the existence of provided datastore and user's access. Inject datastore id to the
    config, based on the name and version provided. If version is not provided, this function also
    injects the maximum version to the config
    """
    split = datastore_name.split(":")
    owner = None
    if len(split) > 2:
        raise ValueError(f"Error while parsing {datastore_name}. Use the format <username>:<datastore-name>")
    elif len(split) == 2:
        datastore_name = split[1]
        owner = split[0]

    # Fetching all datastores and filter them based on the arguments
    all_datastores = list_datastores(is_global=True)
    possible_datastores = [d for d in all_datastores if d.name == datastore_name]
    if datastore_version:
        possible_datastores = [d for d in possible_datastores if d.version == datastore_version]
    if not owner:
        # TODO - this is a hack that must be fixed after proper RBAC can fetch the datastore in a team
        user = user_from_logged_in_account()
        owner = user.username
    possible_datastores = [d for d in possible_datastores if d.user.username == owner]
    if cluster:
        possible_datastores = [d for d in possible_datastores if d.cluster_id == cluster]

    # Throwing if no datastores found
    if len(possible_datastores) == 0:
        raise ValueError(
            f'No ready-to-use datastore found with name {datastore_name} '
            f'and version {datastore_version} in the cluster {cluster}'
        )

    # choosing the latest datastore if no version is provided
    if datastore_version is None:
        selected_dstore = possible_datastores[0]
        for dstore in possible_datastores:
            if dstore.version > selected_dstore.version:
                selected_dstore = dstore
        warnings.warn(
            f'No ``--datastore_version`` passed. Using datastore: {datastore_name} version: {selected_dstore.version}'
        )
    else:
        selected_dstore = possible_datastores[0]

    return selected_dstore


class Datastore:
    _name: str
    _id: str
    _version: int
    _source: Optional[Union[str, Path]]
    _team: Optional[Team]
    _compression: bool
    _snapshot_status: str
    _created_at: datetime
    _user: User
    _team: Optional[Team]
    _cluster_id: str
    _size: str

    _is_deleted: bool
    _is_created: bool
    _is_shallow: bool

    def __init__(
        self,
        name: Optional[str] = None,
        source: Optional[os.PathLike] = None,
        team: Optional[Team] = None,
        user: Optional[User] = None,
        version: int = 1,
        compression: Optional[bool] = None,
        cluster_id: Optional[str] = None,
    ):
        """Initialize a new DataStore Object.

        If a DataStore with the given name, version, team and cluster already exists,
        then the object returned will be able to interact with the existing DataStore.

        Alternatively, if the DataStore is going to be created for the first time, then
        the ``source`` and ``compression`` parameters can be used to specify the location
        of the DataStore on disk (or at a remote location). and to optionally compress the
        data before uploading.

        After initializing the datastore object, the data itself can be uploaded by calling
        the ``upload()`` method.
        # TODO - user and team shouldn't be arguments
        Parameters
        ----------
        name
            The name of the DataStore.
        version
            The version of the DataStore.
        source
            The location of the DataStore on disk or at a remote location.
        team
            The name of the team that owns the DataStore.
        user
            The user that owns the DataStore.
        compression
            True if the DataStore should be compressed before uploading. Otherwise False.
        cluster_id
            The name of the cluster that the DataStore should be uploaded to.
        """
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
            if source:
                name = parse_name_from_source(source)
            else:
                raise ValueError("Name is required if source is not provided.")
        else:
            try:
                datastore: V1GetDatastoreResponse = get_datastore_from_name(
                    client=self._client, cluster_id=cluster_id, datastore_name=name, version=version
                )
                self._setup_from_response(datastore)
                return
            except KeyError:
                self._is_deleted = False  # the datastore has not been deleted
                self._is_created = False  # it doesn't exists in the grid backend.
                pass

        if version:
            raise RuntimeError(
                f"Existing datastore with name {name} and version {version} "
                "is not found. If you are creating a new datastore,"
                " avoid passing a version as the version is "
                "auto-generated"
            )

        self._name = name
        self._version = None
        self._source = source
        self._team = team
        self._user = user
        self._compression = compression
        self._cluster_id = cluster_id
        self._id = None
        self._snapshot_status = None
        self._created_at = None
        self._size = None

    def _setup_from_response(self, datastore: V1GetDatastoreResponse):
        self._is_deleted = datastore.status.phase == V1DatastoreOptimizationStatus.DELETED
        self._is_created = True
        self._is_shallow = False

        self._id = datastore.id
        self._name = datastore.name
        self._cluster_id = datastore.spec.cluster_id
        self._version = datastore.spec.version
        self._source = datastore.spec.source
        self._snapshot_status = str(datastore.status.phase)  # TODO - rename to status
        self._created_at = datastore.created_at
        self._size = f"{datastore.spec.size_mib} MiB"
        self._user = User(user_id=datastore.spec.user_id, username="", first_name="", last_name="")

    @classmethod
    def _from_existing(
        cls,
        name: str,
        version: int,
        owner: User,
        size: str,
        created_at: datetime,
        snapshot_status: str,
        datastore_id: str,
        cluster_id: str,
        team: Optional[Team] = None,
    ):
        # TODO - remove this and use _setup_from_response when we move from gQL to REST
        dstore = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT, cluster_id=cluster_id)
        dstore._name = name
        dstore._version = version
        dstore._id = datastore_id
        dstore._size = size
        dstore._created_at = created_at
        dstore._snapshot_status = snapshot_status
        dstore._user = owner
        dstore._team = team
        dstore._cluster_id = cluster_id

        dstore._source = None
        dstore._compression = None
        dstore._is_created = True
        dstore._is_shallow = False

        return dstore

    @classmethod
    def _from_id(cls, datastore_id: str, cluster_id: Optional[str] = env.CONTEXT) -> "Run":
        instance = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT, cluster_id=cluster_id)
        instance._id = datastore_id
        instance._is_shallow = True
        return instance

    @property
    def id(self) -> str:
        return self._id

    # ------------------ Attributes Only Valid Before Upload ---------------

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def source(self) -> Union[str, Path]:
        """The directory path at which the datastore is initialized from.

        !!! Note

            This property is only availabe to the instance of this class which uploads
            the datastore. Previously existing datastores will not posses any value
            for this property.
        """
        return self._source

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def compression(self) -> bool:
        """Boolean indicating if the data should be compressed during upload.

        If True, the uploaded data will be decompressed into it's original
        directory structure before the datastore is attached to a run or session.
        This is purely a measure to save time during upload (if the data is
        known to be compressible).

        !!! Note

            This property is only availabe to the instance of this class which uploads
            the datastore. Previously existing datastores will not posses any value
            for this property.

        """
        return self._compression

    # ------------------ Attributes Fully Active After Upload ---------------

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def name(self) -> str:
        """The name of the datastore.
        """
        return self._name

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def version(self) -> int:
        """The version of the datastore.
        """
        return self._version

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def user(self) -> User:
        """Information about the owner of the datastore (name, username, etc).
        """
        return self._user

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def team(self) -> Team:
        """Information about the team which owns the datastore

        !!! info

            This will only ever populate for Grid users who are enrolled in a
            "Teams" plan. Please see https://www.grid.ai/pricing/ for more info.
        """
        return self._team

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def created_at(self) -> datetime:
        """Date-Time timestamp when this datastore was created (first uploaded).
        """
        return self._created_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def size(self) -> str:
        """Size (in Bytes) of the datastore.
        """
        return self._size

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def snapshot_status(self) -> str:
        """The status of the datastore.
        """
        if (self._snapshot_status and
            (self._snapshot_status.upper() not in DATASTORE_TERMINAL_STATES)) or ((self._snapshot_status is None) and
                                                                                  (self._is_created is True)):
            self._update_status()
        return self._snapshot_status

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def cluster_id(self) -> str:
        """ID of the cluster which this datastore is uploaded to.

        !!! info

            This feature is only available to bring-your-own-cloud-credentials
            customers. Please see https://www.grid.ai/pricing/ for more info.
        """
        return self._cluster_id

    def _unshallow(self):
        """ If the object is a shallow (i.e. only has an id and `_is_shallow` attribute is True)
        object, this method can be triggered to get the full object from the BE. It is designed
        to be called only from the `is_not_shallow` decorator and should not be called directly.
        """
        if not self._is_shallow:
            raise RuntimeError('Datastore is already unshallow')
        if not hasattr(self, '_id') or self._id is None:
            raise RuntimeError("Cannot unshallow resource without a valid Datastore id")
        self._is_shallow = False
        try:
            datastore = get_datastore_from_id(self._client, datastore_id=self._id, cluster_id=self.cluster_id)
        except ApiException as e:  # TODO change to GridException
            if hasattr(e, 'reason') and e.reason == "Not Found":
                self._is_deleted = True
                self._status = DatastoreStatus.DELETED
        else:
            self._setup_from_response(datastore)

    # -------------- Dunder Methods ----------------------

    @affirm(is_not_shallow, is_not_deleted)
    def __repr__(self):
        if self._is_created:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                    {"name": <10} = \"{self.name}\",
                    {"version": <10} = {self.version},
                    {"size": <10} = \"{self.size}\",
                    {"created_at": <10} = {self.created_at},
                    {"owner": <10} = {self.user},
                    {"team": <10} = \"{self.team}\",
                    {"cluster_id": <10} = {self.cluster_id},
                )"""
            )
        else:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                    {"name": <10} = \"{self.name}\",
                    {"version": <10} = {self.version},
                    {"source": <10} = \"{self.source}\",
                    {"compression": <10} = {self.compression},
                    {"owner": <10} = {self.user},
                    {"team": <10} = \"{self.team}\",
                    {"cluster_id": <10} = {self.cluster_id},
                )"""
            )
        return res

    @affirm(is_not_shallow, is_not_deleted)
    def __str__(self):
        return repr(self)

    @affirm(is_not_shallow, is_not_deleted)
    def __eq__(self, other: 'Datastore'):
        # TODO - handling team's datastore equality here is probably not the best. We should
        #  delegate that to the backend when Project lands
        # need to handle case where attributes of a DataStore are not `User` or `Team`
        # classes. This is the case before the datastore is uploaded.
        self_team = self._team.team_id if hasattr(self._team, 'team_id') else self._team
        other_team = other._team.team_id if hasattr(other._team, 'team_id') else self._team

        self_owner = self._user.user_id if hasattr(self._user, 'user_id') else self._user
        other_owner = other._user.user_id if hasattr(other._user, 'user_id') else other.user

        return (
            self.__class__.__qualname__ == other.__class__.__qualname__ and self._name == other._name
            and self._version == other._version and self_owner == other_owner and self_team == other_team
        )

    @affirm(is_not_shallow, is_not_deleted)
    def __hash__(self):
        return hash((
            self._name, self._id, self._version, self._size, self._created_at, self._snapshot_status, self._user,
            self._team, self._source, self._compression, self._cluster_id, self._is_deleted, self._is_created
        ))

    # ---------------------  Internal Methods ----------------------

    @affirm(is_not_shallow, is_not_deleted)
    def _update_status(self):
        """Refreshes the``snapshot_status`` attribute by querying the Grid API.
        """
        tid = None if self._team is None else self.team.team_id
        all_dstore_data = get_available_datastores(team_id=tid)

        for dstore_data in all_dstore_data:
            if dstore_data['id'] == self._id:
                self._snapshot_status = dstore_data['snapshotStatus'] or "unknown"

    # -------------------  Public Facing Methods ----------------------

    @affirm(is_not_shallow, is_not_deleted, is_created)
    def delete(self):
        """Deletes the datastore from the grid system.
        """
        delete_datastore(name=self.name, version=self.version, cluster=self.cluster_id)
        self._is_deleted = True

    @affirm(is_not_shallow, is_not_created)
    def upload(self):
        """Uploads the contents of the directories referenced by this datastore instance to Grid.

        Depending on your internet connection this may be a potentially long running process.
        If uploading is inturupsed, the upload session can be resumed by initializing this
        ``Datastore`` object again with the same parameters repeating the call to ``upload()``.
        """
        session = create_datastore_session(
            name=self.name,
            source=self.source,
            compression=self.compression,
            cluster=self.cluster_id,
        )
        session.upload()

        # Since we can't query just a single datastore by it's ID (THIS IS INSANE!)
        # we just grab the entire world of datastores and check to see which one
        # has the same attributes as this (as determined by this classes __eq__ method)

        time.sleep(1)  # give the backend time to process the new record.
        for datastore in list_datastores(is_global=True):
            if datastore == self:
                self._name = datastore._name
                self._id = datastore._id
                self._version = datastore._version
                self._source = datastore._source
                self._compression = datastore._compression
                self._snapshot_status = datastore._snapshot_status
                self._created_at = datastore._created_at
                self._user = datastore._user
                self._team = datastore._team
                self._cluster_id = datastore._cluster_id
                self._size = datastore._size

                self._is_deleted = False
                self._is_created = True


def list_datastores(cluster_id: Optional[str] = None, is_global: bool = False) -> List[Datastore]:
    """List datastores for user / teams

    Parameters
    ----------
    is_global:
        if True, returns a list of datastores of the everyone in the team
    cluster_id:
        if specified, returns a list of datastores for the specified cluster
    """
    cluster_id = cluster_id or env.CONTEXT
    datastores = []
    user_dstores_data = get_available_datastores()
    for dstore_data in user_dstores_data:
        user = User(
            username=dstore_data['userDetails']['username'],
            user_id=dstore_data['userDetails']['id'],
            first_name=dstore_data['userDetails']['firstName'],
            last_name=dstore_data['userDetails']['lastName'],
        )
        dstore = Datastore._from_existing(  # noqa
            name=dstore_data['name'],
            version=int(dstore_data['version']),
            owner=user,
            team=None,
            size=dstore_data['size'],
            created_at=datetime.fromisoformat(dstore_data['createdAt']),
            snapshot_status=dstore_data['snapshotStatus'],
            datastore_id=dstore_data['id'],
            cluster_id=dstore_data['clusterId'],
        )
        datastores.append(dstore)

    # If ``include_teams`` is set, add datastores registered to the team.

    teams = []
    if is_global:
        teams_data = get_user_teams()
        for team_data in teams_data:
            members = {}
            for member_data in team_data['members']:
                user = User(
                    username=member_data['username'],
                    user_id=member_data['id'],
                    first_name=member_data['firstName'],
                    last_name=member_data['lastName'],
                )
                members[user.username] = user

            team = Team(
                team_id=team_data['id'],
                name=team_data['name'],
                created_at=team_data['createdAt'],
                role=team_data['role'],
                members=members,
            )
            teams.append(team)

    for team in teams:
        team_dstores_data = get_available_datastores(team_id=team.team_id)
        for dstore_data in team_dstores_data:
            user = User(
                user_id=dstore_data['userDetails']['id'],
                username=dstore_data['userDetails']['username'],
                first_name=dstore_data['userDetails']['firstName'],
                last_name=dstore_data['userDetails']['lastName']
            )

            dstore = Datastore._from_existing(
                name=dstore_data['name'],
                version=int(dstore_data['version']),
                owner=user,
                team=team,
                size=dstore_data['size'],
                created_at=datetime.fromisoformat(dstore_data['createdAt']),
                snapshot_status=dstore_data['snapshotStatus'],
                datastore_id=dstore_data['id'],
                cluster_id=dstore_data['clusterId'],
            )
            datastores.append(dstore)
    # filter based on cluster ID - this will be easy once migrated to the new API
    datastores = [dstore for dstore in datastores if dstore.cluster_id == cluster_id]
    return datastores


def parse_name_from_source(source) -> str:
    """Parses datastore name from source if name isn't provided"""
    try:
        parse_result = urlparse(source)
    except ValueError:
        raise click.ClickException("Invalid source for datastore, please input only a local filepath or valid url")

    path = Path(parse_result.path)
    base = path.name.split(".")[0]
    return base.lower().strip()


class DatastoreStatus(Enum):
    UNSPECIFIED = "unspecified"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    OPTIMIZING = "optimizing"
    DELETED = "deleted"
    POD_PENDING = "pod_pending"

    @classmethod
    def from_api_spec(cls, status: V1DatastoreOptimizationStatus) -> 'DatastoreStatus':
        parsed = str(status).lower().split('_', maxsplit=3)[-1]
        return cls(parsed)
