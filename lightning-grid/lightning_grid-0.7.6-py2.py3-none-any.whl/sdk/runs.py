import contextlib
import textwrap
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional, Union, Dict

from grid.sdk import env
from grid.sdk.affirmations import affirm, is_not_deleted, is_created, is_not_created, is_not_shallow
from grid.sdk.run_components import Resources, Actions, ScratchSpace
from grid.sdk.utilities import (
    read_config,
    check_run_name_is_valid,
    check_description_isnt_too_long,
    resolve_instance_type_nickname,
    SPECIAL_NAME_TO_SKIP_OBJECT_INIT,
)
from grid.sdk.client import create_swagger_client
from grid.sdk.datastores import Datastore
from grid.sdk.experiments import Experiment
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.runs import create_run, get_run_from_name, cancel_run, delete_run, get_run_from_id
from grid.sdk.rest.runs import list_runs as rest_list_runs
from grid.sdk.utils import fill_object_from_response
from grid.sdk.source_code.repository import GitRepository, LocalSourceCodeDir
from grid.sdk.user import user_from_logged_in_account, User
from grid.sdk.utils.name_generator import unique_name

from grid.openapi import V1Run, V1RunState


class Run:
    """A ``Run`` is a container for a set of computations executed over search space.

    This object can be instantiated with constructor args below in
    order to create/start a new set of computations (``Experiments``)
    which make up the ``Run``.

    Alternatively, an existig ``Run`` ``name`` can be passed in the
    constructor, and the SDK will load all the associated ``Run`` /
    ``Experiment`` details in this structure automatically.

    !!! note
        This class provides properties to access run attributes
        which can be read at any time, or set before the ``Run``
        objects ``.start()`` method is called.
    """
    _user: User
    _id: str

    _name: str
    _run_command: str
    _url: str
    _path: Path
    _description: str
    _strategy: str
    _strategy_options: Dict[str, str]
    _num_trials: int
    _env_vars: Dict[str, str]
    _framework: str
    _dependency_file: Union[str, Path]
    _localdir: bool
    _relative_working_dir: Path
    _dockerfile: Union[str, Path]
    _auto_resume: bool
    _resources: Resources
    _datastore: Optional[Datastore]
    _datastore_mount_dir: Optional[str]
    _actions: Actions
    _scratch: ScratchSpace
    _cluster_id: str
    _dry_run: bool
    _status: 'RunState'

    _cost: Union[int, float]
    _estimated_hourly_cost: Union[int, float]
    _desired_status: 'RunState'
    _created_at: datetime
    _updated_at: datetime
    _experiments: List['Experiment']
    _experiment_counts: Dict[str, int]

    _client: GridRestClient

    _is_deleted: bool  # TODO use _status instead
    _is_created: bool
    _is_shallow: bool

    def __init__(
        self,
        name: Optional[str] = None,
        run_command: Optional[str] = None,
        description: Optional[str] = None,
        strategy: Optional[str] = "grid_search",
        strategy_options: Optional[Dict[str, str]] = None,
        num_trials: Optional[int] = 0,  # if strategy == random
        env_vars: Optional[Dict[str, str]] = None,
        framework: Optional[str] = "lightning",
        dependency_file: Optional[Union[str, Path]] = "./requirements.txt",
        localdir: Optional[bool] = False,
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        dockerfile: Optional[Union[str, Path]] = None,
        auto_resume: Optional[bool] = False,
        resources: Resources = None,
        datastore: Optional[Datastore] = None,
        datastore_mount_dir: Optional[str] = None,
        actions: Optional[Actions] = None,
        scratch: Optional[ScratchSpace] = None,
        cluster_id: Optional[str] = None,
        config_file: Optional[Union[str, Path]] = None,
        dry_run: bool = False
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
            # if user passed a name, try to fetch the run from BE
            try:
                run = get_run_from_name(client=self._client, cluster_id=cluster_id, run_name=name)
                self._setup_from_response(run)
                return
            except KeyError:
                self._is_deleted = False  # the run has not been deleted
                self._is_created = False  # it doesn't exists in the grid backend.
                pass
        check_run_name_is_valid(name)
        self._name = name
        if description:
            check_description_isnt_too_long(description)
        if resources is None:
            resources = Resources()
        if scratch is None:
            scratch = ScratchSpace()
        if env_vars is None:
            env_vars = {}
        if actions is None:
            actions = Actions()

        if resources.instance_type:
            resolve_instance_type_nickname(resources.instance_type)

        if framework and framework not in ['lightning', 'torch', 'tensorflow', 'julia', 'torchelastic']:
            raise ValueError(framework)

        if config_file:
            config = read_config(config_file)
            # from provider sub-key.
            cluster_id = config.get('compute', {}).get('provider', {}).get('cluster', cluster_id)

            # from config/hyper_params sub-key.
            _hparam_cfg = config.get("hyper_params", {})
            strategy = _hparam_cfg.get('settings', {}).get('strategy', strategy)
            strategy_options = _hparam_cfg.get("settings", {}).get("strategy_options", strategy_options)
            num_trials = _hparam_cfg.get('params', {}).get('n_experiments', num_trials)

            # from config/compute/train sub-key
            _train_cfg = config.get('compute', {}).get('train', {})
            env_vars = _train_cfg.get("environment", env_vars)
            dry_run = _train_cfg.get('dry_run', dry_run)
            framework = _train_cfg.get('framework', framework)
            dependency_file = _train_cfg.get('dependency_file_info', {}).get('path', dependency_file)
            resources.instance_type = _train_cfg.get('instance', resources.instance_type)
            resources.use_spot = _train_cfg.get('use_spot', resources.use_spot)
            resources.cpus = _train_cfg.get('cpus', resources.cpus)
            resources.gpus = _train_cfg.get('gpus', resources.gpus)
            resources.storage_gb = _train_cfg.get('storage_gb', resources.storage_gb)
            localdir = _train_cfg.get('localdir', localdir)
            dockerfile = _train_cfg.get('dockerfile', dockerfile)
            auto_resume = _train_cfg.get('auto_resume', auto_resume)

            _dstore_config = [_train_cfg.get('datastore_name'), _train_cfg.get('datastore_version')]
            if any(_dstore_config) and not all(_dstore_config):
                raise ValueError(
                    "name and version are both required if one of datastore_name or datastore_version is set"
                )
            if all(_dstore_config):
                _dstore_name = _train_cfg.get('datastore_name')
                _dstore_version = _train_cfg.get('datastore_version')
                datastore_mount_dir = _train_cfg.get('datastore_mount_dir', datastore_mount_dir)
                datastore = Datastore(name=_dstore_name, version=_dstore_version, cluster_id=cluster_id)

            _actions_cfg = _train_cfg.get("actions", {})
            if len(_actions_cfg) != 0:
                actions = Actions(
                    on_build=_actions_cfg.get("on_build", actions.on_build),
                    on_build_start=_actions_cfg.get("on_build_start", actions.on_build_start),
                    on_build_end=_actions_cfg.get("on_build_end", actions.on_build_end),
                    on_experiment_start=_actions_cfg.get("on_experiment_start", actions.on_experiment_start),
                    on_experiment_end=_actions_cfg.get("on_experiment_end", actions.on_experiment_end),
                )
            _scratch = _train_cfg.get("scratch", [])
            if len(_scratch) != 0:
                if len(_scratch) > 1:
                    raise ValueError("Only one scratch space is allowed")
                scratch = ScratchSpace(
                    size_gb=_scratch.get("size_gb", scratch.size_gb),
                    mount_path=_scratch.get("mount_path", scratch.mount_path),
                )

        if resources.storage_gb is not None and resources.storage_gb < 100:
            raise ValueError("Invalid disk size, should be greater than 100Gb")

        relative_working_dir = None
        if not url:
            path = Path(path) if path else Path.cwd()
            path = path.absolute()
            if dockerfile:
                with contextlib.suppress(ValueError):
                    dockerfile = str(Path(dockerfile).relative_to(path))
            if dependency_file:
                with contextlib.suppress(ValueError):
                    dependency_file = str(Path(dependency_file).relative_to(path))
            if not localdir:
                # in the case of localdir, we'll upload the code to the URL
                # server returns on run creation
                git_repo = GitRepository(path)
                url = git_repo.url()
                relative_working_dir = git_repo.relative_working_dir()

        if not datastore_mount_dir and isinstance(datastore, Datastore):
            datastore_mount_dir = f'/datastores/{datastore.name}'

        self._user = None
        self._cluster_id = cluster_id
        self._url = url
        self._path = path
        self._relative_working_dir = relative_working_dir
        self._env_vars = env_vars
        self._run_command = run_command
        self._description = description
        self._strategy = strategy
        self._strategy_options = strategy_options
        self._num_trials = num_trials
        self._framework = framework
        self._dependency_file = dependency_file
        self._localdir = localdir
        self._dockerfile = dockerfile
        self._auto_resume = auto_resume
        self._resources = resources
        self._datastore = datastore
        self._datastore_mount_dir = datastore_mount_dir
        self._actions = actions
        self._scratch = scratch
        self._dry_run = dry_run

        self._id = None
        self._desired_status = None
        self._created_at = None
        self._updated_at = None
        self._status = None
        self._experiments = []
        self._experiment_counts = None
        self._cost = None
        self._estimated_hourly_cost = None

    @property
    @affirm(is_not_shallow)
    def exists(self) -> bool:
        return self._is_created

    @classmethod
    def _from_id(cls, run_id: str, cluster_id: Optional[str] = env.CONTEXT) -> "Run":
        instance = cls(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT, cluster_id=cluster_id)
        instance._id = run_id
        instance._is_shallow = True
        return instance

    def _setup_from_response(self, run: 'V1Run'):
        """Set up the run from the response from the API."""
        self._is_created = True
        self._is_deleted = run.status.phase == V1RunState.DELETED
        self._is_shallow = False

        self._name = run.name
        self._id = run.id
        self._dry_run = run.spec.dry_run

        self._run_command = run.spec.run_controller_command
        self._description = run.description
        self._cluster_id = run.spec.cluster_id
        self._strategy = run.spec.sweep_type
        self._strategy_options = run.spec.sweep_options
        self._framework = run.spec.image.framework
        self._dockerfile = run.spec.image.dockerfile
        self._localdir = bool('s3:' in run.spec.source_code)

        if run.spec.image.dependency_file_info:
            self._dependency_file = run.spec.image.dependency_file_info.path

        self._desired_status = RunState.from_api_spec(run.spec.desired_state)
        self._status = RunState.from_api_spec(run.status.phase)
        self._created_at = run.created_at
        self._updated_at = run.updated_at

        self._experiment_counts = {}
        if run.status.experiment_counts:
            self._experiment_counts = run.status.experiment_counts.to_dict()

        self._experiments = []
        for exp_id in run.status.experiment_ids:
            try:
                # noinspection PyProtectedMember
                exp = Experiment._from_id(cluster_id=run.spec.cluster_id, exp_id=exp_id)
                self._experiments.append(exp)
            except Exception as e:
                # Experiment might be deleted
                if not hasattr(e, 'reason') or e.reason != 'Not Found':  # noqa
                    raise e
        storage_gb = int(run.spec.resources.storage_gb) if run.spec.resources.storage_gb else None
        cpus = int(run.spec.resources.cpu) if run.spec.resources.cpu else None
        gpus = int(run.spec.resources.gpu) if run.spec.resources.gpu else None
        self._resources = Resources(
            instance_type=run.spec.instance_type,
            use_spot=run.spec.use_spot,
            storage_gb=storage_gb,
            cpus=cpus,
            gpus=gpus,
            extra=run.spec.resources.extra,
        )

        for datastore_mount in run.spec.datastores:
            # noinspection PyProtectedMember
            self._datastore = Datastore._from_id(cluster_id=run.spec.cluster_id, datastore_id=datastore_mount.id)
            self._datastore_mount_dir = datastore_mount.mount_path

        if len(run.spec.scratch) == 1:
            scratch = run.spec.scratch[0]
            self._scratch = ScratchSpace(size_gb=scratch.size_gb, mount_path=scratch.mount_path)
        if len(run.spec.scratch) > 1:
            raise ValueError(f"Expected only one scratch space, but got {len(run.spec.scratch)}")

        self._cost = run.status.cost
        self._estimated_hourly_cost = run.status.hourly_cost
        self._user = User(user_id=run.spec.user_id, username="", first_name="", last_name="")

    @property
    def id(self) -> str:
        return self._id

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def name(self) -> str:
        """Name of the Run

        Returns
        -------
        str
            The specified (or autogenerated) Run name.
        """
        return self._name

    @name.setter
    @affirm(is_not_deleted, is_not_created)
    def name(self, val: str):
        self._name = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def run_command(self) -> str:
        """The command you would you to start the main script from the root of the source tree.

        For example:

            python scripts/start_foo.py --arg "[1, 2]" --flag
        """
        return self._run_command

    @run_command.setter
    @affirm(is_not_deleted, is_not_created)
    def run_command(self, val: str):
        self._run_command = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def url(self) -> str:
        """Remote URL to the repository
        """
        return self._url

    @url.setter
    @affirm(is_not_deleted, is_not_created)
    def url(self, val: str):
        self._url = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def relative_working_dir(self) -> Path:
        """local path to the repository
        """
        return self._relative_working_dir

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def path(self) -> Path:
        """local path to the repository
        """
        return self._path

    @path.setter
    @affirm(is_not_deleted, is_not_created)
    def path(self, val: Path):
        self._path = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def description(self) -> str:
        """Human readable description of the Run's contents

        Returns
        -------
        str
            A description string if one was attached to the Run.
        """
        return self._description

    @description.setter
    @affirm(is_not_deleted, is_not_created)
    def description(self, val: str):
        self._description = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def strategy(self) -> str:
        """Hyperparameter search strategy.

        Returns
        -------
        str
            One of `['grid_search', 'random_search']`
        """
        return self._strategy

    @strategy.setter
    @affirm(is_not_deleted, is_not_created)
    def strategy(self, val: str):
        self._strategy = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def strategy_options(self) -> Dict[str, str]:
        return self._strategy_options

    @strategy_options.setter
    @affirm(is_not_deleted, is_not_created)
    def strategy_options(self, val: Dict[str, str]):
        self._strategy_options = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def num_trials(self) -> int:
        """How many samples of full search space are used using the ``'random_search'`` strategy.

        Returns
        -------
        int
            Number of trials.
        """
        return self._num_trials

    @num_trials.setter
    @affirm(is_not_deleted, is_not_created)
    def num_trials(self, val: int):
        self._num_trials = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def env_vars(self) -> Dict[str, str]:
        return self._env_vars

    @env_vars.setter
    @affirm(is_not_deleted, is_not_created)
    def env_vars(self, val: Dict[str, str]):
        self._env_vars = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def framework(self) -> str:
        """Determines the ML framework used.

        Returns
        -------
        str
            One of ``["lightning", "pytorch", "tensorflow", "julia"]``.
        """
        return self._framework

    @framework.setter
    @affirm(is_not_deleted, is_not_created)
    def framework(self, val: str):
        self._framework = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def dependency_file(self) -> Union[str, Path]:
        """Path to a dependency file to use to install runtime requirements.

        Returns
        -------
        Union[str, Path]
            Path to a dependency file.
        """
        return self._dependency_file

    @dependency_file.setter
    @affirm(is_not_deleted, is_not_created)
    def dependency_file(self, val: Union[str, Path]):
        self._dependency_file = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def localdir(self) -> bool:
        return self._localdir

    @localdir.setter
    @affirm(is_not_deleted, is_not_created)
    def localdir(self, val: bool):
        self._localdir = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def dockerfile(self) -> Union[str, Path]:
        return self._dockerfile

    @dockerfile.setter
    @affirm(is_not_deleted, is_not_created)
    def dockerfile(self, val: Union[str, Path]):
        self._dockerfile = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def auto_resume(self) -> bool:
        return self._auto_resume

    @auto_resume.setter
    @affirm(is_not_deleted, is_not_created)
    def auto_resume(self, val: bool):
        self._auto_resume = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def resources(self) -> Resources:
        return self._resources

    @resources.setter
    @affirm(is_not_deleted, is_not_created)
    def resources(self, val: Resources):
        self._resources = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def datastore(self) -> Datastore:
        return self._datastore

    @datastore.setter
    @affirm(is_not_deleted, is_not_created)
    def datastore(self, val: Datastore):
        self._datastore = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def datastore_mount_dir(self) -> str:
        return self._datastore_mount_dir

    @datastore_mount_dir.setter
    @affirm(is_not_deleted, is_not_created)
    def datastore_mount_dir(self, val: str):
        self._datastore_mount_dir = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def actions(self) -> Actions:
        return self._actions

    @actions.setter
    @affirm(is_not_deleted, is_not_created)
    def actions(self, val: Actions):
        self._actions = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def scratch(self) -> ScratchSpace:
        return self._scratch

    @scratch.setter
    @affirm(is_not_deleted, is_not_created)
    def scratch(self, val: ScratchSpace):
        self._scratch = val

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def cluster_id(self) -> str:
        return self._cluster_id

    @cluster_id.setter
    @affirm(is_not_deleted, is_not_created)
    def cluster_id(self, cluster: str):
        self._cluster_id = cluster

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def dry_run(self) -> bool:
        return self._dry_run

    @dry_run.setter
    @affirm(is_not_deleted, is_not_created)
    def dry_run(self, dry_run: bool):
        self._dry_run = dry_run

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def status(self) -> 'RunState':
        return self._status

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def desired_status(self) -> 'RunState':
        return self._desired_status

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def created_at(self) -> datetime:
        return self._created_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def experiments(self) -> List['Experiment']:
        return self._experiments

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def experiment_counts(self) -> Dict[str, int]:
        return self._experiment_counts

    @property
    @affirm(is_not_shallow, is_not_deleted)
    def user(self) -> User:
        if self._user is None:
            self._user = user_from_logged_in_account()
        return self._user

    @property
    def cost(self) -> Union[int, float]:
        return self._cost

    @property
    def estimated_hourly_cost(self) -> Union[int, float]:
        """Estimated hourly cost of the run.

        Returns
        -------
        Union[int, float]
            Value corresponding to (estimated) cost / hr in US Dollars.

        TODO(rlizzo): Update to use the "dry-run" API to get the estimated cost.
        """
        return self._estimated_hourly_cost

    @affirm(is_not_created)
    def start(self) -> bool:
        """Launches the hyper-parameter sweep computations on the cluster.

        After starting a Run, most of the run configuration cannot be changed.
        If successful, the machine resources requested will be provisioned and
        begin billing your account until the run completes, fails, is cancelled,'
        or your account runs out of funds.
        """
        if not self.cluster_id:
            raise ValueError("Couldn't find cluster info. Try logging in again!")
        datastores = {self.datastore.id: self.datastore_mount_dir} if self.datastore else None
        res = create_run(
            client=self._client,
            cluster_id=self.cluster_id,
            run_name=self.name,
            run_description=self.description,
            run_controller_command=self.run_command,
            source_code=self.url,
            localdir=self.localdir,
            run_sweep_type=self.strategy,
            run_sweep_options=self.strategy_options,
            scratch_mount_path=self.scratch.mount_path,
            scratch_size_gb=self.scratch.size_gb,
            instance_type=self.resources.instance_type,
            use_spot=self.resources.use_spot,
            per_exp_resources_cpu=self.resources.cpus,
            per_exp_resources_gpu=self.resources.gpus,
            per_exp_resources_storage_gb=self.resources.storage_gb,
            per_exp_resources_extra=self.resources.extra,
            on_build_actions=self.actions.on_build,
            on_build_start_actions=self.actions.on_build_start,
            on_build_end_actions=self.actions.on_build_end,
            on_experiment_start_actions=self.actions.on_experiment_start,
            on_experiment_end_actions=self.actions.on_experiment_end,
            image_dockerfile=self.dockerfile,
            image_framework=self.framework,
            image_dep_file=self.dependency_file,
            per_exp_env_vars=self.env_vars,
            datastores=datastores,
            relative_work_dir=str(self.relative_working_dir) if self.relative_working_dir else None,
            dry_run=False,  # TODO
            auto_resume=self.auto_resume,
        )

        # trigger the repo upload if localdir is true
        if self.localdir:
            if not self.path.is_dir():
                raise NotADirectoryError(f'localdir_source_root: {self.path} is not a directory')
            if res.status.phase == V1RunState.FAILED:
                raise RuntimeError(f'Run creation failed: {res.status.message}')
            repository = LocalSourceCodeDir(path=self.path)
            repository.package()
            if not res.status.upload_url:
                raise ValueError("Couldn't get upload url for localdir source")
            repository.upload(url=res.status.upload_url)

        self._setup_from_response(res)
        return True

    @affirm(is_not_deleted, is_created)
    def delete(self) -> bool:
        """
        Deletes the run.
        """
        delete_run(self._client, run_id=self._id, cluster_id=self.cluster_id)
        self._is_deleted = True
        return True

    def __repr__(self) -> str:
        """Pretty printed output detailing current state of the run.

        Primarily for use as a quick way to execute objects in juyterlab and
        output some info about the run.

        Returns
        -------
        str
            A string detailing the current state of the run.
        """
        if self.exists:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                {"name": <10} = \"{self.name}\",
                {"description": <10} = \"{self.description}\",
                {"run_command": <10} = \"{self.run_command}\",
                {"num_experiments": <10} = \"{len(self.experiments)}\",
                {"status": <10} = \"{self.status.value}\",
                {"user": <10} = \"{self.user.user_id}\",
                {"created_at": <10} = \"{self.created_at}\",
                {"cluster": <10} = \"{self.cluster_id}\",
                )"""
            )
        else:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                {"name": <10} = \"{self.name}\",
                {"description": <10} = \"{self.description}\",
                {"run_command": <10} = \"{self.run_command}\",
                {"num_experiments": <10} = \"{len(self.experiments)}\",
                {"status": <10} = \"{self.status.value}\",
                {"user": <10} = \"{self.user.user_id}\",
                {"cluster": <10} = \"{self.cluster_id}\",
                )"""
            )
        return res

    def __contains__(self, item: str) -> bool:
        """Check if an experiment with the provided name exists in the Run.

        Parameters
        ----------
        item
            The name of the experiment to check for.

        Returns
        -------
        bool
            True if the experiment exists, otherwise False.
        """
        return item in [exp.name for exp in self.experiments]

    def __len__(self) -> int:
        """Check how many experiments are recorded in the Run.

        Returns
        -------
        int
            Number of experiments recorded in the Run.
        """
        return len(self.experiments)

    def __iter__(self) -> Iterable['Experiment']:
        """Allows for iteration over the run, yielding every Experiment object recorded.
        """
        for exp in self.experiments:
            yield exp

    def _unshallow(self):
        """ If the object is a shallow (i.e. only has an id and `_is_shallow` attribute is True)
        object, this method can be triggered to get the full object from the BE. It is designed
        to be called only from the `is_not_shallow` decorator and should not be called directly.
        """
        if not self._is_shallow:
            raise RuntimeError('Run is already unshallow')
        if not hasattr(self, '_id') or self._id is None:
            raise RuntimeError("Cannot unshallow resource without a valid run id")
        self._is_shallow = False
        run = get_run_from_id(self._client, run_id=self._id, cluster_id=self.cluster_id)
        self._setup_from_response(run)

    @affirm(is_not_deleted, is_created)
    def cancel(self) -> bool:
        """Requests the grid platform cancels every Experiment in the Run.

        Returns
        -------
        List[str]
            a collection of experiment names if each experiment was successfully
            cancelled or had previously reached a terminal status ("CANCELLED",
            "FAILED", "COMPLETED").
        """
        if self._created_at is None:
            raise RuntimeError(f"cannot a run which has not been started.")
        updated_run = cancel_run(client=self._client, cluster_id=self.cluster_id, run_id=self._id)
        self._setup_from_response(updated_run)
        return True


def list_runs(cluster_id: Optional[str] = None, is_global: bool = False) -> List[Run]:
    """
    List all runs on the cluster with the provided cluster id

    Parameters
    ----------
    cluster_id:
        The id of the cluster to list runs for. If None, the default cluster (as listed
        in settings.json) is used.
    is_global:
        If True, return runs of all users in the team
    """
    cluster_id = cluster_id or env.CONTEXT
    client = GridRestClient(api_client=create_swagger_client())
    users = {}
    if is_global:
        from grid.cli.core import Team
        # TODO - this needs to be moved to REST
        for team in Team.get_all():
            for user_details in team.data.get("members", {}):
                users[user_details["id"]] = user_details
    all_runs = []
    for run_resp in rest_list_runs(client=client, cluster_id=cluster_id, user_ids=list(users.keys())):
        run_obj = Run(name=SPECIAL_NAME_TO_SKIP_OBJECT_INIT)
        fill_object_from_response(run_obj, run_resp)
        user_details = users.get(run_obj.user.user_id, {})
        user = User(
            user_id=user_details.get("id"),
            username=user_details.get("username"),
            first_name=user_details.get("firstName"),
            last_name=user_details.get("lastName")
        )
        run_obj._user = user
        all_runs.append(run_obj)
    return all_runs


class RunState(Enum):
    """
    Enumeration of the possible run statuses.
    """
    UNSPECIFIED = "unspecified"
    BUILDING = "building"
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELETED = "deleted"

    @classmethod
    def from_api_spec(cls, status: V1RunState) -> 'RunState':
        parsed = str(status).lower().split('_', maxsplit=2)[-1]
        if parsed == 'canceled':  # TODO - spelling mistake in BE
            return cls.CANCELLED
        return cls(parsed)
