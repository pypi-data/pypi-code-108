from __future__ import annotations

import logging
import uuid
import warnings
from typing import Dict, Generic, Optional, Set, Union, cast

import dask
import dask.distributed
from coiled.context import track_context

from .cluster import Cluster, CredentialsPreferred
from .compatibility import DISTRIBUTED_VERSION
from .core import Async, Cloud, IsAsynchronous
from .utils import COILED_LOGGER_NAME, use_declarative

logger = logging.getLogger(COILED_LOGGER_NAME)


class DeclarativeCluster(Cluster, Generic[IsAsynchronous]):
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
    worker_class
        Worker class to use. Defaults to "dask.distributed.Nanny".
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    worker_vm_types
        List of instance types that you would like workers to use, this list can have up to five items.
        You can use the command ``coiled.list_instance_types()`` to se a list of allowed types.
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
    region_name
        Region for cluster. Defaults to default for account.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        n_workers: int = 4,
        configuration: str = None,
        worker_memory: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_vm_types: Optional[list] = None,
        scheduler_memory: str = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_vm_types: Optional[list] = None,
        asynchronous: bool = False,
        cloud: Cloud = None,
        account: str = None,
        shutdown_on_close=None,
        use_scheduler_public_ip: Optional[bool] = None,
        credentials: Optional[str] = "account",
        timeout: Optional[int] = None,
        environ: Optional[Dict[str, str]] = None,
        region_name: str = None,
    ):
        # Set log level to INFO on our logger
        # If user wants to change it, they have to do so after importing coiled
        # ...which is kinda gross. Maybe we'll revisit this later.
        logging.getLogger(COILED_LOGGER_NAME).setLevel(logging.INFO)

        # this is gross but we really want our log messages to show up, and they don't otherwise by default
        logging.basicConfig()

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
        super(Cluster, self).__init__(asynchronous, **kwargs)

        self.timeout = (
            timeout if timeout is None else self.cloud.default_cluster_timeout
        )
        self.configuration = configuration
        self.worker_memory = worker_memory
        self.worker_class = worker_class
        self.worker_options = {
            **(dask.config.get("coiled.worker-options", {})),
            **(worker_options or {}),
        }
        self.worker_vm_types = worker_vm_types
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

        self._name = "coiled.Cluster"  # Used in Dask's Cluster._ipython_display_
        self.region_name = region_name

        if not self.asynchronous:
            self.sync(self._start)

    @track_context
    async def _start(self):
        # When invoked using distributed.utils.sync, sub-invocations are all async.
        # As long as we are in a private API that is always called that way,
        # we should be able to safely cast this to async.
        cloud = await cast(Cloud[Async], self.cloud)
        should_create = True

        logger.info("Creating Cluster. This might take a few minutes...")
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
                logger.info(f"Using existing cluster: '{self.name}'")
                should_create = False
                if self.shutdown_on_close is None:
                    self.shutdown_on_close = False

        self.name = (
            self.name
            or (self.account or cloud.default_account) + "-" + str(uuid.uuid4())[:10]
        )

        if should_create:
            self.cluster_id = await cloud._create_cluster_declarative(
                account=self.account,
                name=self.name,
                workers=self._start_n_workers,
                configuration=self.configuration,
                worker_class=self.worker_class,
                worker_options=self.worker_options,
                scheduler_class=self.scheduler_class,
                scheduler_options=self.scheduler_options,
                environ=self.environ,
                scheduler_vm_types=self.scheduler_vm_types,
                worker_vm_types=self.worker_vm_types,
                region_name=self.region_name,
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
            logger.info(
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

        await super(Cluster, self)._start()

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
