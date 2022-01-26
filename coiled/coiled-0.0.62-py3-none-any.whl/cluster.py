from __future__ import annotations

import asyncio
import enum
import logging
import os
import sys
import time
import uuid
import warnings
from asyncio import wait_for
from contextlib import suppress
from typing import (
    Awaitable,
    Callable,
    Dict,
    Generic,
    Optional,
    Set,
    TypeVar,
    Union,
    cast,
    overload,
)

import aiobotocore.session
import boto3
import botocore
import dask
import dask.distributed
import distributed.deploy
import tlz as toolz
from coiled.context import track_context
from coiled.exceptions import ArgumentCombinationError, InstanceTypeError
from distributed.core import Status
from distributed.deploy.adaptive import Adaptive
from rich.text import Text
from typing_extensions import Literal

from .compatibility import DISTRIBUTED_VERSION
from .core import Async, Cloud, IsAsynchronous, Sync
from .utils import (
    name_exists_in_dict,
    parse_backend_options,
    parse_identifier,
    rich_console,
    scheduler_ports,
    use_declarative,
    validate_instance_type,
)


@enum.unique
class CredentialsPreferred(enum.Enum):
    LOCAL = "local"
    # USER = 'user'
    ACCOUNT = "account"
    NONE = None


_T = TypeVar("_T")


class CoiledAdaptive(Adaptive):
    async def scale_up(self, n):
        await self.cluster.scale_up(n)

    async def scale_down(self, workers):
        if not workers:
            return
        await self.cluster.scale_down(workers)


class Cluster(distributed.deploy.Cluster, Generic[IsAsynchronous]):
    """Create a Dask cluster with Coiled

    Parameters
    ----------
    n_workers
        Number of workers in this cluster. Defaults to 4.
    configuration
        Name of cluster configuration to create cluster from.
        If not specified, defaults to ``coiled/default`` for the
        current Python version.
    name
        Name to use for identifying this cluster. Defaults to ``None``.
    software
        Identifier of the software environment to use, in the format (<account>/)<name>. If the software environment
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.

        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have an environment
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".

        The "name" portion of (<account>/)<name> can only contain ASCII letters, hyphens and underscores.
    worker_cpu
        Number of CPUs allocated for each worker. Defaults to 2.
    worker_gpu
        Number of GPUs allocated for each worker. Defaults to 0 (no GPU support). Note that this will _always_
        allocate GPU-enabled workers, so is expensive. This option will always allocate on demand instances, you
        can change this behaviour by using ``"spot": False`` on the ``backend_options`` parameter.
    worker_gpu_type
        Type of GPU to use for this cluster. For AWS GPU types are tied to the instance type, but for
        GCP you can add different GPU types to an instance. Please refer to :doc:`tutorials/select_gpu_type` for
        more information.
        You can run the command ``coiled.list_gpu_types()`` to see a list of allowed GPUs.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 8 GiB.
    worker_class
        Worker class to use. Defaults to "dask.distributed.Nanny".
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    worker_vm_types
        List of instance types that you would like workers to use, this list can have up to five items.
        You can use the command ``coiled.list_instance_types()`` to se a list of allowed types.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    scheduler_class
        Scheduler class to use. Defaults to "dask.distributed.Scheduler".
    scheduler_options
        Mapping with keyword arguments to pass to ``scheduler_class``. Defaults to ``{}``.
    scheduler_vm_types
        List of instance types that you would like the scheduler to use, this list can have up to
        five items.
        You can use the command ``coiled.list_instance_types()`` to se a list of allowed types.
    asynchronous
        Set to True if using this Cloud within ``async``/``await`` functions or
        within Tornado ``gen.coroutines``. Otherwise this should remain
        ``False`` for normal use. Default is ``False``.
    cloud
        Cloud object to use for interacting with Coiled.
    account
        Name of Coiled account to use. If not provided, will
        default to the user account for the ``cloud`` object being used.
    shutdown_on_close
        Whether or not to shut down the cluster when it finishes.
        Defaults to True, unless name points to an existing cluster.
    use_scheduler_public_ip
        Boolean value that determines if the Python client connects to the Dask scheduler using the scheduler machine's
        public IP address. The default behaviour when set to True is to connect to the scheduler using its public IP
        address, which means traffic will be routed over the public internet. When set to False, traffic will be
        routed over the local network the scheduler lives in, so make sure the scheduler private IP address is
        routable from where this function call is made when setting this to False.
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` cofiguration value.
    credentials
        Which credentials to use for Dask operations and forward to Dask clusters --
        options are "account", "local", or "none". The default behavior is to prefer
        credentials associated with the Coiled Account, if available, then try to
        use local credentials, if available.
        NOTE: credential handling currently only works with AWS credentials.
    timeout
        Timeout in seconds to wait for a cluster to start, will use ``default_cluster_timeout``
        set on parent Cloud by default.
    environ
        Dictionary of environment variables.
    protocol
        Communication protocol for the cluster. Default is ``tls``.
    """

    @overload
    def __init__(
        self: Cluster[Sync],
        name: Optional[str] = None,
        *,
        n_workers: int = 4,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_gpu_type: Optional[str] = None,
        worker_memory: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_vm_types: Optional[list] = None,
        scheduler_cpu: int = None,
        scheduler_memory: str = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_vm_types: Optional[list] = None,
        asynchronous: Sync = False,
        cloud: Literal[None] = None,
        account: str = None,
        shutdown_on_close=None,
        backend_options: Optional[Dict] = None,
        credentials: Optional[str] = "account",
        timeout: Optional[int] = None,
        environ: Optional[Dict[str, str]] = None,
        protocol: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Cluster[Sync],
        name: Optional[str] = None,
        *,
        n_workers: int = 4,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_gpu_type: Optional[str] = None,
        worker_memory: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_vm_types: Optional[list] = None,
        scheduler_cpu: int = None,
        scheduler_memory: str = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_vm_types: Optional[list] = None,
        asynchronous: bool = False,
        cloud: Cloud[Sync],
        account: str = None,
        shutdown_on_close=None,
        backend_options: Optional[Dict] = None,
        credentials: Optional[str] = "account",
        timeout: Optional[int] = None,
        environ: Optional[Dict[str, str]] = None,
        protocol: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Cluster[Async],
        name: Optional[str] = None,
        *,
        n_workers: int = 4,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_gpu_type: Optional[str] = None,
        worker_memory: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_vm_types: Optional[list] = None,
        scheduler_cpu: int = None,
        scheduler_memory: str = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_vm_types: Optional[list] = None,
        asynchronous: Async = True,
        cloud: Literal[None] = None,
        account: str = None,
        shutdown_on_close=None,
        backend_options: Optional[Dict] = None,
        credentials: Optional[str] = "account",
        timeout: Optional[int] = None,
        environ: Optional[Dict[str, str]] = None,
        protocol: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Cluster[Async],
        name: Optional[str] = None,
        *,
        n_workers: int = 4,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_gpu_type: Optional[str] = None,
        worker_memory: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_vm_types: Optional[list] = None,
        scheduler_cpu: int = None,
        scheduler_memory: str = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_vm_types: Optional[list] = None,
        asynchronous: bool = False,
        cloud: Cloud[Async],
        account: str = None,
        shutdown_on_close=None,
        backend_options: Optional[Dict] = None,
        credentials: Optional[str] = "account",
        timeout: Optional[int] = None,
        environ: Optional[Dict[str, str]] = None,
        protocol: Optional[str] = None,
    ):
        ...

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        n_workers: int = 4,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_gpu_type: Optional[str] = None,
        worker_memory: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_vm_types: Optional[list] = None,
        scheduler_cpu: int = None,
        scheduler_memory: str = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_vm_types: Optional[list] = None,
        asynchronous: bool = False,
        cloud: Cloud = None,
        account: str = None,
        shutdown_on_close=None,
        use_scheduler_public_ip: Optional[bool] = None,
        backend_options: Optional[Dict] = None,
        credentials: Optional[str] = "account",
        timeout: Optional[int] = None,
        environ: Optional[Dict[str, str]] = None,
        protocol: Optional[str] = None,
    ):
        # Determine consistent sync/async
        if cloud and asynchronous is not None and cloud.asynchronous != asynchronous:
            warnings.warn(
                f"Requested a Cluster with asynchronous={asynchronous}, but "
                f"cloud.asynchronous={cloud.asynchronous}, so the cluster will be"
                f"{cloud.asynchronous}"
            )
            asynchronous = cloud.asynchronous

        self.scheduler_comm: Optional[dask.distributed.rpc] = None

        self.cloud: Cloud[IsAsynchronous] = cloud or Cloud.current(
            asynchronous=asynchronous
        )

        # As of distributed 2021.12.0, deploy.Cluster has a ``loop`` attribute on the
        # base class. We add the attribute manually here for backwards compatibility.
        # TODO: if/when we set the minimum distributed version to be >= 2021.12.0,
        # remove this check.
        if DISTRIBUTED_VERSION >= "2021.12.0":
            kwargs = {"loop": self.cloud.loop}
        else:
            kwargs = {}
            self.loop = self.cloud.loop

        # we really need to call this first before any of the below code errors
        # out; otherwise because of the fact that this object inherits from
        # deploy.Cloud __del__ (and perhaps __repr__) will have AttributeErrors
        # because the gc will run and attributes like `.status` and
        # `.scheduler_comm` will not have been assigned to the object's instance
        # yet
        super().__init__(asynchronous, **kwargs)

        self.timeout = (
            timeout if timeout is None else self.cloud.default_cluster_timeout
        )
        if configuration is None:
            v = "".join(map(str, sys.version_info[:2]))
            configuration = f"coiled/default-py{v}"
        self.configuration = configuration
        self.software = software
        self.worker_cpu = worker_cpu
        self.worker_gpu = worker_gpu
        self.worker_memory = worker_memory
        self.worker_class = worker_class
        self.worker_options = {
            **(dask.config.get("coiled.worker-options", {})),
            **(worker_options or {}),
        }
        self.worker_vm_types = worker_vm_types
        self.worker_gpu_type = worker_gpu_type
        self.scheduler_cpu = scheduler_cpu
        self.scheduler_memory = scheduler_memory
        self.scheduler_class = scheduler_class
        self.scheduler_options = {
            **(dask.config.get("coiled.scheduler-options", {})),
            **(scheduler_options or {}),
        }
        self.scheduler_vm_types = scheduler_vm_types
        self.name = name
        self.account = account
        self._start_n_workers = n_workers
        self._lock = None
        self._asynchronous = asynchronous
        self.shutdown_on_close = shutdown_on_close
        self.environ = {k: str(v) for (k, v) in (environ or {}).items() if v}
        self.credentials = CredentialsPreferred(credentials)
        self._default_protocol = dask.config.get("coiled.protocol", "tls")
        self._requested: Set[str] = set()
        self._plan: Set[str] = set()
        self._adaptive_options: Dict[str, Union[str, int]] = {}
        self.cluster_id: Optional[int] = None
        self.use_scheduler_public_ip: bool = (
            dask.config.get("coiled.use_scheduler_public_ip", True)
            if use_scheduler_public_ip is None
            else use_scheduler_public_ip
        )
        self.backend_options = {
            **(dask.config.get("coiled.backend-options", None) or {}),
            **(backend_options or {}),
        }

        self._name = "coiled.Cluster"  # Used in Dask's Cluster._ipython_display_

        if self.scheduler_options:
            if "protocol" in self.scheduler_options:
                if protocol:
                    raise RuntimeError(
                        "Top level `protocol` collides with `scheduler_options`"
                    )
            else:
                self.scheduler_options.update(
                    {"protocol": protocol or self._default_protocol}
                )
            if "port" not in self.scheduler_options:
                self.scheduler_options.update(
                    {"port": scheduler_ports(self.scheduler_options["protocol"])}
                )
        else:
            self.scheduler_options = {
                "protocol": protocol or self._default_protocol,
                "port": scheduler_ports(protocol or self._default_protocol),
            }

        if self.worker_options:
            if "protocol" in self.worker_options:
                if protocol:
                    raise RuntimeError(
                        "Top level `protocol` collides with `worker_options`"
                    )
            else:
                self.worker_options.update(
                    {"protocol": protocol or self._default_protocol}
                )
        else:
            self.worker_options = {"protocol": protocol or self._default_protocol}

        if not self.asynchronous:
            self.sync(self._start)

    @property
    def requested(self):
        return self._requested

    @property
    def plan(self):
        return self._plan

    @overload
    def sync(
        self: Cluster[Sync],
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Union[Sync, Literal[None]] = None,
        callback_timeout=None,
        **kwargs,
    ) -> _T:
        ...

    @overload
    def sync(
        self: Cluster[Async],
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Union[bool, Literal[None]] = None,
        callback_timeout=None,
        **kwargs,
    ) -> Awaitable[_T]:
        ...

    def sync(
        self,
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: bool = None,
        callback_timeout=None,
        **kwargs,
    ) -> Union[_T, Awaitable[_T]]:
        return super().sync(
            func,
            *args,
            asynchronous=asynchronous,
            callback_timeout=callback_timeout,
            **kwargs,
        )

    def _ensure_scheduler_comm(self) -> dask.distributed.rpc:
        """
        Guard to make sure that the scheduler comm exists before trying to use it.
        """
        if not self.scheduler_comm:
            raise RuntimeError(
                "Scheduler comm is not set, have you been disconnected from Coiled?"
            )
        return self.scheduler_comm

    @track_context
    async def _start(self):
        console = rich_console()
        with console.status(
            Text(
                "Creating Cluster. This might take a few minutes...", style="bold green"
            )
        ):
            # When invoked using distributed.utils.sync, sub-invocations are all async.
            # As long as we are in a private API that is always called that way,
            # we should be able to safely cast this to async.
            cloud = await cast(Cloud[Async], self.cloud)
            self.backend_options = parse_backend_options(
                backend_options=self.backend_options,
                account=self.account or self.cloud.default_account,
                accounts=self.cloud.accounts,
                worker_gpu=self.worker_gpu,
            )
            should_create = True
            available_configs = None

            if self.name:
                try:
                    self.cluster_id = await cloud._get_cluster_by_name(
                        name=self.name,
                        account=self.account,
                    )
                except Exception:
                    # if there's no such cluster, we'll get an Exception
                    pass
                else:
                    console.print(
                        f"Using existing cluster: '{self.name}'"
                    )  # TODO: add timer
                    should_create = False
                    if self.shutdown_on_close is None:
                        self.shutdown_on_close = False

            self.name = (
                self.name
                or (self.account or cloud.default_account)
                + "-"
                + str(uuid.uuid4())[:10]
            )

            if should_create:
                instance_types_to_validate = []

                if self.worker_vm_types:
                    if self.worker_cpu or self.worker_memory:
                        raise ArgumentCombinationError(
                            "Argument 'worker_vm_types' used together with 'worker_cpu' or 'worker_memory' only "
                            "'worker_vm_types' or 'worker_cpu'/'worker_memory' should be used."
                        )

                    instance_types_to_validate.extend(self.worker_vm_types)

                if self.scheduler_vm_types:
                    instance_types_to_validate.extend(self.scheduler_vm_types)

                if instance_types_to_validate:
                    try:
                        provider_name = await cloud.get_account_provider_name(
                            self.account
                        )
                    except TypeError:
                        error_msg = (
                            f"Instance type selection is not supported for the backend"
                            f"configured for your account: '{self.account}'"
                        )
                        raise InstanceTypeError(error_msg)

                    user_instance_types = await self.cloud._get_instance_types(
                        backend=provider_name
                    )

                    validate_instance_type(
                        instance_type_list=instance_types_to_validate,
                        allowed_instance_types=user_instance_types,
                        provider_name=provider_name,
                    )

                # TODO: should this check also be upstream on the server?
                software_env = await self._check_software_environment_exists(cloud)
                available_configs = await self._check_cluster_configuration_exists(
                    cloud,
                    software_env,
                )
                self.cluster_id = await cloud.create_cluster(
                    account=self.account,
                    configuration=self.configuration,
                    name=self.name,
                    workers=self._start_n_workers,
                    backend_options=self.backend_options,
                    software=self.software,
                    worker_cpu=self.worker_cpu,
                    worker_gpu=self.worker_gpu,
                    worker_memory=self.worker_memory,
                    worker_class=self.worker_class,
                    worker_options=self.worker_options,
                    scheduler_cpu=self.scheduler_cpu,
                    scheduler_memory=self.scheduler_memory,
                    scheduler_class=self.scheduler_class,
                    scheduler_options=self.scheduler_options,
                    environ=self.environ,
                    scheduler_vm_types=self.scheduler_vm_types,
                    worker_vm_types=self.worker_vm_types,
                    worker_gpu_type=self.worker_gpu_type,
                    use_scheduler_public_ip=self.use_scheduler_public_ip,
                )
                if self._start_n_workers:
                    # this _scale call is probably unnecessary even before declarative but I'll leave it in for now
                    # definitely not necessary in declarative, so this whole block can be deleted when we delete
                    # non-declarative code
                    if not use_declarative():
                        await self._scale(self._start_n_workers)
            if not self.cluster_id:
                raise RuntimeError(f"Failed to find/create cluster {self.name}")

            # this is what waits for the cluster to be "ready"
            self.security, info = await cloud.security(
                cluster_id=self.cluster_id, account=self.account
            )
            self._proxy = bool(self.security.extra_conn_args)

            # TODO (Declarative): (or also relevant for non-declarative?):
            # dashboard address should be private IP when use_scheduler_public_ip is False
            self._dashboard_address = info["dashboard_address"]

            if self.use_scheduler_public_ip:
                rpc_address = info["public_address"]
            else:
                rpc_address = info["private_address"]
                console.print(
                    f"Connecting to scheduler on its internal address: {rpc_address}"
                )

            try:
                self.scheduler_comm = dask.distributed.rpc(
                    rpc_address,
                    connection_args=self.security.get_connection_args("client"),
                )
                # TODO (Declarative): I see errors about this in scheduler logs
                #  due declarative shedulers lack the aws_update_credentials plugin?
                # (doesn't seem to kill the scheduler, so leaving in for now)
                # https://gitlab.com/coiled/cloud/-/issues/4304
                await self._send_credentials(cloud)
            except IOError as e:
                if "Timed out" in "".join(e.args):
                    raise RuntimeError(
                        "Unable to connect to Dask cluster. This may be due "
                        "to different versions of `dask` and `distributed` "
                        "locally and remotely.\n\n"
                        f"You are using distributed={DISTRIBUTED_VERSION} locally.\n\n"
                        "With pip, you can upgrade to the latest with:\n\n"
                        "\tpip install --upgrade dask distributed"
                    )
                raise

            await super()._start()

            if should_create is False:
                if use_declarative():
                    pass
                    # TODO (Declarative): make declarative support adaptive scaling
                    #  (https://gitlab.com/coiled/cloud/-/issues/4292)
                else:
                    requested = await cloud.requested_workers(
                        cluster_id=self.cluster_id, account=self.account
                    )
                    self._requested = requested
                    self._plan = requested

            # Set adaptive maximum value based on available config and user quota
            self._set_adaptive_options(info)

            # TODO: Come up with a better long-term solution. Below we raise an informative error message
            # when workers with GPUs take a long time to arrive (due to GPU availability on AWS)
            if (
                should_create
                and self._start_n_workers
                and available_configs
                and (
                    self.worker_gpu
                    or available_configs[self.configuration]["worker"]["gpu"]
                )
            ):
                try:
                    await self._wait_for_workers(1, timeout="10 minutes")
                except TimeoutError as e:
                    await self._close()
                    raise e

    @track_context
    async def _wait_for_workers(self, n_workers, timeout=None, err_msg=None) -> None:
        if timeout is None:
            deadline = None
        else:
            timeout = dask.utils.parse_timedelta(timeout, "s")
            deadline = time.time() + timeout
        while n_workers and len(self.scheduler_info["workers"]) < n_workers:
            if deadline and time.time() > deadline:
                err_msg = err_msg or (
                    f"Timed out after {timeout} seconds waiting for {n_workers} workers to arrive, "
                    "check your notifications with coiled.get_notifications() for further details"
                )
                raise TimeoutError(err_msg)
            await asyncio.sleep(1)

    async def _check_software_environment_exists(
        self, cloud: Cloud[Async]
    ) -> Optional[dict]:
        """Check if software environment exists.

        When we list software environments, we get the user software environments
        and any software environments from the team that the user belongs to. We
        should check if the software environment name that he user is trying to use
        exists. If we can't find the software environment with the given name, we
        will use coiled's default one and tell the user about this. That way we
        don't stop the Cluster creation process if the software env doesn't exist.

        """
        if self.software:
            account, software_name, revision = parse_identifier(
                self.software,
                property_name="software_environment",
                can_have_revision=True,
            )

            software_envs = await cloud.list_software_environments(account=account)

            if name_exists_in_dict(
                user=self.account or cloud.default_account,
                name=self.software,
                dictionary=software_envs,
            ):

                return software_envs

            raise ValueError(
                f" Unable to create Cluster: Software environment with the name '{software_name}' "
                "not found. Have you created this software environment or have you specified your "
                "software environment in the format '<account>/<software environment>'?"
            )

        return None

    async def _check_cluster_configuration_exists(
        self, cloud: Cloud[Async], software_environments: dict = None
    ):
        """Check if the cluster configuration exists.

        We will list cluster configurations and check if the configuration exists within the
        user account or any teams that the user belongs to. We will also check if the user
        attempted to pass a software environment name as the configuration and raise an
        exception indicating that we found a software environment with that name and that
        the user needs to create a configuration with that software name.

        We are getting the software_environments from ``self._check_software_environment_exists``
        so we don't have to do another API call.

        """
        acct, name, _ = parse_identifier(self.configuration, "configuration")
        if not acct:
            # Cluster configs are returned with '<account>/<name>' if no account passed,
            # let's add it ourselves.
            self.configuration = f"{self.account or cloud.default_account}/{name}"
        available_configs = await cloud.list_cluster_configurations(
            account=acct or self.account or cloud.default_account
        )

        if not software_environments:
            software_environments = await cloud.list_software_environments(
                account=acct or self.account or cloud.default_account
            )

        if not name_exists_in_dict(
            user=acct, name=self.configuration, dictionary=available_configs
        ):
            error_msg = f"Cluster configuration '{self.configuration}' not found."
            if not self.software:
                software_environments = await cloud.list_software_environments(
                    account=self.account or cloud.default_account
                )

            if name_exists_in_dict(
                user=cloud.user,
                name=self.configuration,
                dictionary=software_environments,
            ):
                error_msg += (
                    "\n"
                    f"We did find a software environment '{self.configuration}'.\n"
                    "You may need to make a cluster configuration with this \n"
                    "software environment:\n\n"
                    f"  coiled.create_cluster_configuration(name='{self.configuration}', software='{self.configuration}')"  # noqa: E501
                )
            raise ValueError(error_msg)
        return available_configs

    async def _send_credentials(self, cloud: Cloud[Async]):
        """
        Get credentials and pass them to the scheduler.
        """
        if True:  # TODO: delete this and undindent it all
            aws_creds = {}
            try:
                if self.credentials is CredentialsPreferred.ACCOUNT:
                    aws_creds = await cloud.get_aws_credentials(self.account)
                    # Setup the default session & environment variables so that
                    # account creds are used for other AWS things (e.g. local Dask
                    # client)
                    boto3.setup_default_session(**aws_creds)
                    for k, v in aws_creds.items():
                        os.environ[k.upper()] = v
                # elif self.credentials == CredentialsPreferred.USER:
                #     aws_creds = cloud.get_aws_credentials(self.user)
                creds = {}
                session = aiobotocore.session.get_session()
                async with session.create_client("sts", **aws_creds) as sts:
                    try:
                        credentials = await sts.get_session_token()
                        credentials = credentials["Credentials"]
                        creds = {
                            k: credentials[k]
                            for k in ["AccessKeyId", "SecretAccessKey", "SessionToken"]
                        }
                    except botocore.errorfactory.ClientError as e:
                        if "session credentials" in str(e):
                            # STS session. Can't request a new session token
                            credentials = await session.get_credentials()
                            credentials = await credentials.get_frozen_credentials()
                            creds = {
                                "AccessKeyId": credentials.access_key,
                                "SecretAccessKey": credentials.secret_key,
                                "SessionToken": credentials.token,
                            }
                    if creds:
                        # TODO: set up TTL, and update these credentials periodically
                        scheduler_comm = self._ensure_scheduler_comm()
                        await scheduler_comm.aws_update_credentials(
                            credentials={
                                k: creds.get(k)
                                for k in [
                                    "AccessKeyId",
                                    "SecretAccessKey",
                                    "SessionToken",
                                ]
                            }
                        )
            except (
                botocore.exceptions.ProfileNotFound,
                botocore.exceptions.NoCredentialsError,
            ):
                # no AWS credentials (maybe not running against AWS?), fail gracefully
                pass
            except Exception as e:
                # warn, but don't crash
                logging.warning(f"error sending AWS credentials to cluster: {e}")

    def __await__(self: Cluster[Async]):
        async def _():
            if self._lock is None:
                self._lock = asyncio.Lock()
            async with self._lock:
                if self.status == Status.created:
                    await wait_for(self._start(), self.timeout)
                assert self.status == Status.running
            return self

        return _().__await__()

    @overload
    def close(self: Cluster[Sync]) -> None:
        ...

    @overload
    def close(self: Cluster[Async]) -> Awaitable[None]:
        ...

    def close(self) -> Union[None, Awaitable[None]]:
        """
        Close the cluster.
        """
        return self.sync(self._close)

    @track_context
    async def _close(self) -> None:
        # Send a profile snapshot on close, before workers have been torn down.
        # If profiling data has been sent recently, this should be a no-op.
        if self.scheduler_comm:
            await self.scheduler_comm.send_profile()
        if not self.cluster_id:
            raise ValueError("No cluster available to close!")
        cloud = cast(Cloud[Async], self.cloud)
        with suppress(AttributeError):
            self._adaptive.stop()

        # Stop here because otherwise we get intermittent `OSError: Timed out` when
        # deleting cluster takes a while and callback tries to poll cluster status.
        for pc in self.periodic_callbacks.values():
            pc.stop()

        if self.shutdown_on_close in (True, None):
            await cloud.delete_cluster(
                account=self.account,
                cluster_id=self.cluster_id,
            )
        await super()._close()

    @track_context
    async def _scale(self, n: int) -> None:
        if not self.cluster_id:
            raise ValueError("No cluster available to scale!")
        recommendations = await self.recommendations(n)
        status = recommendations.pop("status")
        if status == "same":
            return
        if status == "up":
            return await self.scale_up(**recommendations)
        if status == "down":
            return await self.scale_down(**recommendations)

    @overload
    def scale(self: Cluster[Sync], n: int) -> None:
        ...

    @overload
    def scale(self: Cluster[Async], n: int) -> Awaitable[None]:
        ...

    def scale(self, n: int) -> Optional[Awaitable[None]]:
        """Scale cluster to ``n`` workers

        Parameters
        ----------
        n
            Number of workers to scale cluster size to.
        """
        return self.sync(self._scale, n=n)

    @track_context
    async def scale_up(self, n: int) -> None:
        if not self.cluster_id:
            raise ValueError(
                "No cluster available to scale! "
                "Check cluster was not closed by another process."
            )
        cloud = cast(Cloud[Async], self.cloud)
        response = await cloud._scale_up(
            account=self.account,
            cluster_id=self.cluster_id,
            n=n,
        )
        if response:
            self._plan.update(set(response.get("workers", [])))
            self._requested.update(set(response.get("workers", [])))

    @track_context
    async def scale_down(self, workers: set) -> None:
        if not self.cluster_id:
            raise ValueError("No cluster available to scale!")
        cloud = cast(Cloud[Async], self.cloud)
        try:
            scheduler_comm = self._ensure_scheduler_comm()
            await scheduler_comm.retire_workers(
                names=workers,
                remove=True,
                close_workers=True,
            )
        except Exception as e:
            logging.warning(f"error retiring workers {e}. Trying more forcefully")
        # close workers more forcefully
        await cloud._scale_down(
            account=self.account,
            cluster_id=self.cluster_id,
            workers=workers,
        )
        self._plan.difference_update(workers)
        self._requested.difference_update(workers)

    async def recommendations(self, target: int) -> dict:
        """
        Make scale up/down recommendations based on current state and target
        """
        plan = self.plan
        requested = self.requested
        observed = self.observed

        if target == len(plan):
            return {"status": "same"}

        if target > len(plan):
            return {"status": "up", "n": target}

        not_yet_arrived = requested - observed
        to_close = set()
        if not_yet_arrived:
            to_close.update(toolz.take(len(plan) - target, not_yet_arrived))

        if target < len(plan) - len(to_close):
            L = await self.workers_to_close(target=target)
            to_close.update(L)
        return {"status": "down", "workers": list(to_close)}

    async def workers_to_close(self, target: int):
        """
        Determine which, if any, workers should potentially be removed from
        the cluster.

        Notes
        -----
        ``Cluster.workers_to_close`` dispatches to Scheduler.workers_to_close(),
        but may be overridden in subclasses.

        Returns
        -------
        List of worker addresses to close, if any

        See Also
        --------
        Scheduler.workers_to_close
        """
        scheduler_comm = self._ensure_scheduler_comm()
        ret = await scheduler_comm.workers_to_close(
            target=target,
            attribute="name",
        )
        return ret

    def adapt(self, Adaptive=CoiledAdaptive, **kwargs) -> Adaptive:
        """Dynamically scale the number of workers in the cluster
        based on scaling heuristics.

        Parameters
        ----------
        minimum : int
            Minimum number of workers that the cluster should have while
            on low load, defaults to 1.
        maximum : int
            Maximum numbers of workers that the cluster should have while
            on high load. If maximum is not set, this value will be based
            on your core count limit. This value is also capped by your
            core count limit.
        wait_count : int
            Number of consecutive times that a worker should be suggested
            for removal before the cluster removes it, defaults to 60.
        interval : timedelta or str
            Milliseconds between checks, default sto 5000 ms.
        target_duration : timedelta or str
            Amount of time we want a computation to take. This affects how
            aggressively the cluster scales up, defaults to 5s.

        """
        if use_declarative():
            # TODO (Declarative): support adaptive
            # https://gitlab.com/coiled/cloud/-/issues/4292
            raise NotImplementedError
        maximum = kwargs.pop("maximum", None)
        if maximum is not None:
            kwargs["maximum"] = min(maximum, self._adaptive_options["maximum"])
        return super().adapt(Adaptive=Adaptive, **kwargs)

    def _set_adaptive_options(self, info):
        if use_declarative():
            # TODO (Declarative): support adaptive scaling
            # https://gitlab.com/coiled/cloud/-/issues/4292
            #
            # Samantha says:
            #
            # this might be a good use case for returning a detailed  VmType object instead of reducing it to just the
            # vm name. It contains the vCPUs. Although having mixed instance type clusters messes with this.
            return
        cpu = info["configuration"]["worker"]["cpu"]
        limit = self.cloud.accounts[self.account or self.cloud.default_account][
            "user_limit"
        ]
        self._adaptive_options = {
            "interval": "5s",
            "wait_count": 60,
            "minimum": 1,
            "maximum": int(limit / cpu),
        }

    def __enter__(self: Cluster[Sync]) -> Cluster[Sync]:
        return self.sync(self.__aenter__)

    def __exit__(self: Cluster[Sync], *args, **kwargs) -> None:
        return self.sync(self.__aexit__, *args, **kwargs)

    @overload
    def get_logs(self: Cluster[Sync], scheduler: bool, workers: bool = True) -> dict:
        ...

    @overload
    def get_logs(
        self: Cluster[Async], scheduler: bool, workers: bool = True
    ) -> Awaitable[dict]:
        ...

    def get_logs(
        self, scheduler: bool = True, workers: bool = True
    ) -> Union[dict, Awaitable[dict]]:
        """Return logs for the scheduler and workers
        Parameters
        ----------
        scheduler : boolean
            Whether or not to collect logs for the scheduler
        workers : boolean
            Whether or not to collect logs for the workers
        Returns
        -------
        logs: Dict[str]
            A dictionary of logs, with one item for the scheduler and one for
            the workers
        """
        return self.sync(self._get_logs, scheduler=scheduler, workers=workers)

    @track_context
    async def _get_logs(self, scheduler: bool = True, workers: bool = True) -> dict:
        if not self.cluster_id:
            raise ValueError("No cluster available for logs!")
        cloud = cast(Cloud[Async], self.cloud)
        return await cloud.cluster_logs(
            cluster_id=self.cluster_id,
            account=self.account,
            scheduler=scheduler,
            workers=workers,
        )

    @property
    def dashboard_link(self):
        # Only use proxied dashboard address if we're in a hosted notebook
        # Otherwise fall back to the non-proxied address
        if self._proxy or dask.config.get("coiled.dashboard.proxy", False):
            return f"{self.cloud.server}/dashboard/{self.cluster_id}/status"
        else:
            return self._dashboard_address
