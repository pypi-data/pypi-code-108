"""
Contains:

* Old (pre-declarative) ``Cloud`` class
  * (This also acts as a base class for declarative Cloud, since I didn't bother factoring out methods that are
    agnostic to the declarative/pre-declaraive split.)
* functions that won't exist in declarative.

TODO: move functions with common implementations to "core.py"
"""
from __future__ import annotations, with_statement

import asyncio
import contextlib
import copy
import datetime
import json
import logging
import numbers
import os
import pathlib
import platform
import sys
import threading
import time
import warnings
import weakref
from contextlib import contextmanager
from json.decoder import JSONDecodeError
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

import aiohttp
import backoff
import dask
import dask.distributed
import distributed
import rich
import toolz
import yaml
from coiled.exceptions import (
    AccountConflictError,
    ApiResponseStatusError,
    AWSCredentialsParameterError,
    GCPCredentialsError,
    GCPCredentialsParameterError,
    RegistryParameterError,
    UnsupportedBackendError,
)
from distributed.comm import parse_address
from distributed.utils import Log, Logs, LoopRunner, sync
from rich.console import Console
from rich.table import Table
from rich.text import Text
from tornado.ioloop import IOLoop
from typing_extensions import Literal, Protocol

from .compatibility import COILED_VERSION, DISTRIBUTED_VERSION, PY_VERSION
from .context import COILED_SESSION_ID, TRACE_CONFIG, track_context
from .declarative_states import ClusterStateEnum
from .utils import (
    ALLOWED_PROVIDERS,
    COILED_LOGGER_NAME,
    GatewaySecurity,
    Spinner,
    VmType,
    experimental,
    get_auth_header_value,
    handle_api_exception,
    handle_credentials,
    in_async_call,
    instance_type_table,
    parse_gcp_region_zone,
    parse_identifier,
    rich_console,
    use_declarative,
    validate_account,
    verify_aws_credentials,
)
from .websockets import ConfigureBackendConnector, WebsocketConnector

logger = logging.getLogger(COILED_LOGGER_NAME)
console = Console()
SUPPORTED_BACKENDS = {"aws", "gcp"}


def delete_docstring(func):
    delete_doc = """ Delete a {kind}

Parameters
---------
name
    Name of {kind} to delete.
"""
    func_name = func.__name__
    kind = " ".join(
        func_name.split("_")[1:]
    )  # delete_software_environments -> software environments
    func.__doc__ = delete_doc.format(kind=kind)
    return func


def list_docstring(func):

    list_doc = """ List {kind}s

Parameters
---------
account
    Name of the Coiled account to list {kind}s.
    If not provided, will use the ``coiled.account`` configuration
    value.

Returns
-------
:
    Dictionary with information about each {kind} in the
    specified account. Keys in the dictionary are names of {kind}s,
    while the values contain information about the corresponding {kind}.
"""
    func_name = func.__name__
    kind = " ".join(func_name.split("_")[1:])
    kind = kind[:-1]  # drop trailing "s"
    func.__doc__ = list_doc.format(kind=kind)
    return func


# This lock helps avoid a race condition between cluster creation in the
# in process backend, which temporarily modify coiled's dask config values,
# and the creation of new Cloud objects, with load those same config values.
# This works, but is not ideal.
_cluster_creation_lock = threading.RLock()


# Generic TypeVar for return value from sync/async function.
_T = TypeVar("_T")


# A generic that can only be True/False, allowing us to type async/sync
# versions of coiled objects.
Async = Literal[True]
Sync = Literal[False]
IsAsynchronous = TypeVar("IsAsynchronous", Async, Sync, bool)


# Short of writing type stubs for distributed or typing the underlying package,
# this is a useful cast.
class _SyncProtocol(Protocol):
    def __call__(
        self,
        loop: IOLoop,
        func: Callable[..., Awaitable[_T]],
        *args: Any,
        callback_timeout: numbers.Number,
        **kwargs: Any,
    ) -> _T:
        ...


sync = cast(_SyncProtocol, sync)


class Cloud(Generic[IsAsynchronous]):
    """Connect to Coiled

    Parameters
    ----------
    user
        Username for Coiled account. If not specified, will check the
        ``coiled.user`` configuration value.
    token
        Token for Coiled account. If not specified, will check the
        ``coiled.token`` configuration value.
    server
        Server to connect to. If not specified, will check the
        ``coiled.server`` configuration value.
    account
        The coiled account to use. If not specified,
        will check the ``coiled.account`` configuration value.
    asynchronous
        Set to True if using this Cloud within ``async``/``await`` functions or
        within Tornado ``gen.coroutines``. Otherwise this should remain
        ``False`` for normal use. Default is ``False``.
    loop
        If given, this event loop will be re-used, otherwise an appropriate one
        will be looked up or created.
    default_cluster_timeout
        Default timeout in seconds to wait for cluster startup before raising ``TimeoutError``.
        Pass ``None`` to wait forever, otherwise the default is 20 minutes.
    """

    _recent_sync: list[weakref.ReferenceType[Cloud[Sync]]] = list()
    _recent_async: list[weakref.ReferenceType[Cloud[Async]]] = list()

    @overload
    def __init__(
        self: Cloud[Sync],
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        asynchronous: Sync = False,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        ...

    @overload
    def __init__(
        self: Cloud[Async],
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        asynchronous: Async = True,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        ...

    @overload
    def __init__(
        self,
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        asynchronous: bool = False,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        ...

    def __init__(
        self,
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        asynchronous: bool = False,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        with _cluster_creation_lock:
            self.user = user or dask.config.get("coiled.user")
            self.token = token or dask.config.get("coiled.token")
            self.server = server or dask.config.get("coiled.server")
            if "://" not in self.server:
                self.server = "http://" + self.server
            self.server = self.server.rstrip("/")
            self._default_account = account or dask.config.get("coiled.account")
            self._default_backend_options = (
                dask.config.get("coiled.backend-options", None) or {}
            )
        self.session: Optional[aiohttp.ClientSession] = None
        self.status = "init"
        self.cluster_id: Optional[int] = None
        self._asynchronous = asynchronous
        self._loop_runner = LoopRunner(loop=loop, asynchronous=asynchronous)
        self._loop_runner.start()
        self.default_cluster_timeout = default_cluster_timeout

        if asynchronous:
            Cloud._recent_async.append(weakref.ref(cast(Cloud[Async], self)))
        else:
            Cloud._recent_sync.append(weakref.ref(cast(Cloud[Sync], self)))

        if not self.asynchronous:
            self._sync(self._start)

    def __repr__(self):
        return f"<Cloud: {self.user}@{self.server} - {self.status}>"

    def _repr_html_(self):
        text = (
            '<h3 style="text-align: left;">Cloud</h3>\n'
            '<ul style="text-align: left; list-style: none; margin: 0; padding: 0;">\n'
            f"  <li><b>User: </b>{self.user}</li>\n"
            f"  <li><b>Server: </b>{self.server}</li>\n"
            f"  <li><b>Account: </b>{self.default_account}</li>\n"
        )

        return text

    @property
    def loop(self):
        return self._loop_runner.loop

    @overload
    @classmethod
    def current(cls, asynchronous: Sync) -> Cloud[Sync]:
        ...

    @overload
    @classmethod
    def current(cls, asynchronous: Async) -> Cloud[Async]:
        ...

    @overload
    @classmethod
    def current(cls, asynchronous: bool) -> Cloud:
        ...

    @classmethod
    def current(cls, asynchronous: bool) -> Cloud:
        recent: list[weakref.ReferenceType[Cloud]]
        if asynchronous:
            recent = cls._recent_async
        else:
            recent = cls._recent_sync
        try:
            cloud = recent[-1]()
            while cloud is None or cloud.status != "running":
                recent.pop()
                cloud = recent[-1]()
        except IndexError:
            if asynchronous:
                return Cloud(asynchronous=True)
            else:
                return Cloud(asynchronous=False)
        else:
            return cloud

    @property
    def closed(self) -> bool:
        if self.session:
            return self.session.closed
        # If we haven't opened, we must be closed?
        return True

    @backoff.on_predicate(backoff.expo, lambda resp: resp.status in [502, 503])
    async def _do_request(self, *args, ensure_running: bool = True, **kwargs):
        """
        This wraps the session.request call and injects a per-call UUID.

        Most of the time we check that this is in a "running" state before making
        requests. However, we can disable that by passing in ensure_running=False
        """
        session = self._ensure_session(ensure_running)
        response = await session.request(*args, **kwargs)
        return response

    def _ensure_session(self, ensure_running=True) -> aiohttp.ClientSession:
        if self.session and (not ensure_running or self.status == "running"):
            return self.session
        else:
            raise RuntimeError("Cloud is not running, did you forget to await it?")

    @track_context
    async def _start(self: Cloud[IsAsynchronous]) -> Cloud[IsAsynchronous]:
        if self.status != "init":
            return self
        # Check that server and token are valid
        self.user, self.token, self.server = await handle_credentials(
            server=self.server, token=self.token, save=False
        )
        # TODO: revert when we remove versioneer
        if dask.config.get("coiled.no-minimum-version-check", False):
            client_version = "coiled-frontend-js"
        else:
            client_version = COILED_VERSION

        self.session = aiohttp.ClientSession(
            trace_configs=[TRACE_CONFIG],
            headers={
                "Authorization": get_auth_header_value(self.token),
                "Client-Version": client_version,
                "coiled-session-id": COILED_SESSION_ID,
            },
        )
        # do normal queries
        response = await self._do_request(
            "GET", self.server + "/api/v1/users/me/", ensure_running=False
        )
        if response.status == 426:
            # Upgrade required
            await handle_api_exception(response)
        if response.status >= 400:
            await handle_api_exception(response)

        data = await response.json()
        self.accounts = {
            d["account"]["slug"]: toolz.merge(
                d["account"],
                {"admin": d["is_admin"]},
            )
            for d in data["membership_set"]
        }
        if self._default_account:
            self._verify_account(self._default_account)

        self.status = "running"

        return self

    @property
    def default_account(self):
        if self._default_account:
            return self._default_account
        elif len(self.accounts) == 1:
            return toolz.first(self.accounts)
        elif self.user in self.accounts:
            return self.user
        elif self.user.lower() in self.accounts:
            return self.user.lower()
        else:
            raise ValueError(
                "Please provide an account among the following options",
                list(self.accounts),
            )

    async def _close(self) -> None:
        if self.session:
            await self.session.close()
        self.status = "closed"

    @overload
    def close(self: Cloud[Sync]) -> None:
        ...

    @overload
    def close(self: Cloud[Async]) -> Awaitable[None]:
        ...

    def close(self) -> Optional[Awaitable[None]]:
        """Close connection to Coiled"""
        result = self._sync(self._close)
        self._loop_runner.stop()
        return result

    def __await__(self: Cloud[Async]) -> Generator[None, None, Cloud[Async]]:
        return self._start().__await__()

    async def __aenter__(self: Cloud[Async]) -> Cloud[Async]:
        return await self._start()

    async def __aexit__(self: Cloud[Async], typ, value, tb) -> None:
        await self._close()

    def __enter__(self: Cloud[Sync]) -> Cloud[Sync]:
        return self

    def __exit__(self: Cloud[Sync], typ, value, tb) -> None:
        self.close()

    @property
    def asynchronous(self) -> bool:
        """Are we running in the event loop?"""
        return in_async_call(self.loop, default=self._asynchronous)

    @overload
    def _sync(
        self: Cloud[Sync],
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Union[Sync, Literal[None]] = None,
        callback_timeout=None,
        **kwargs,
    ) -> _T:
        ...

    @overload
    def _sync(
        self: Cloud[Async],
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Union[bool, Literal[None]] = None,
        callback_timeout=None,
        **kwargs,
    ) -> Awaitable[_T]:
        ...

    def _sync(
        self,
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Optional[bool] = None,
        callback_timeout=None,
        **kwargs,
    ) -> Union[_T, Awaitable[_T]]:
        callback_timeout = dask.utils.parse_timedelta(callback_timeout, "s")
        if asynchronous is None:
            asynchronous = self.asynchronous
        if asynchronous:
            future = func(*args, **kwargs)
            if callback_timeout is not None:
                future = asyncio.wait_for(future, callback_timeout)
            return future
        else:
            return sync(
                self.loop, func, *args, callback_timeout=callback_timeout, **kwargs
            )

    async def _get_cluster_details_declarative(
        self, cluster_id: int, account: str = None
    ):
        account = account or self.default_account
        r = await self._do_request(
            "GET", self.server + f"/api/v2/clusters/account/{account}/id/{cluster_id}"
        )
        if r.status >= 400:
            await handle_api_exception(r)
        return await r.json()

    async def _list_clusters_page_declarative(
        self, page: int, account: str = None
    ) -> Tuple[dict, Optional[str]]:
        account = account or self.default_account
        # /api/v2/clusters/account/<account>/
        response = await self._do_request(
            "GET",
            self.server
            + f"/api/v2/clusters/account/{account}/",  # , params={"page": page}
        )
        if response.status >= 400:
            await handle_api_exception(response)

        results = await response.json()
        results = {d["name"]: d for d in results}
        # TODO: need an appropriate "next" instead of None to get all pages
        return results, None

    @track_context
    async def _create_cluster_declarative(
        self,
        # todo: make name optional and pick one for them, like pre-declarative?
        # https://gitlab.com/coiled/cloud/-/issues/4305
        name: str,
        *,
        configuration: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        region_name: str = "us-east-1",  # TODO: better default https://gitlab.com/coiled/cloud/-/issues/4305
    ) -> int:
        # TODO (Declarative): support these args, or decide not to
        # https://gitlab.com/coiled/cloud/-/issues/4305
        if worker_class is not None:
            raise ValueError("worker_class is not supported in beta/new Coiled yet")
        if worker_options:
            raise ValueError("worker_options is not supported in beta/new Coiled yet")
        if scheduler_class is not None:
            raise ValueError("scheduler_class is not supported in beta/new Coiled yet")
        if scheduler_options:
            raise ValueError(
                "scheduler_options is not supported in beta/new Coiled yet"
            )
        if environ:
            raise ValueError("environ is not supported in beta/new Coiled yet")
        if worker_gpu_type is not None:
            raise ValueError("worker_gpu_type is not supported in beta/new Coiled yet")

        account = account or self.default_account
        account, name = self._normalize_name(
            name,
            context_account=account,
            allow_uppercase=True,
        )
        self._verify_account(account)
        data = {
            "name": name,
            "workers": workers,
            "worker_instance_types": worker_vm_types,
            "scheduler_instance_types": scheduler_vm_types,
            "configuration": configuration,
        }
        if region_name:
            data["options"] = {"region_name": region_name}

        response = await self._do_request(
            "POST", self.server + f"/api/v2/clusters/account/{account}/", json=data
        )
        if response.status >= 400:
            await handle_api_exception(response)
        json = await response.json()
        return json["id"]

    @track_context
    async def _list_clusters(self, account: str = None):
        if use_declarative():
            get_one_page = self._list_clusters_page_declarative
        else:
            get_one_page = self._list_clusters_page

        return await self._depaginate(get_one_page, account=account)

    @track_context
    async def _list_clusters_page(
        self, page: int, account: str = None
    ) -> Tuple[dict, Optional[str]]:
        account = account or self.default_account
        response = await self._do_request(
            "GET", self.server + f"/api/v1/{account}/clusters/", params={"page": page}
        )
        if response.status >= 400:
            await handle_api_exception(response)

        response_json = await response.json()
        results = {
            d["name"]: format_cluster_output(d, self.server)
            for d in response_json["results"]
            if d["status"] in ("pending", "running")
        }
        return results, response_json["next"]

    @overload
    def list_clusters(self: Cloud[Sync], account: str = None) -> dict:
        ...

    @overload
    def list_clusters(self: Cloud[Async], account: str = None) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_clusters(self, account: str = None) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_clusters, account)

    def _create_cluster_declarative_synced(
        self,
        name: str = None,
        *,
        configuration: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        region_name: str = None,
    ) -> Union[int, Awaitable[int]]:

        return self._sync(
            self._create_cluster_declarative,
            name=name,
            configuration=configuration,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            account=account,
            workers=workers,
            environ=environ,
            scheduler_vm_types=scheduler_vm_types,
            worker_gpu_type=worker_gpu_type,
            worker_vm_types=worker_vm_types,
            region_name=region_name,
        )

    @overload
    def create_cluster(
        self: Cloud[Sync],
        name: str = None,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        use_scheduler_public_ip: Optional[bool] = True,
    ) -> int:
        ...

    @overload
    def create_cluster(
        self: Cloud[Async],
        name: str = None,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        use_scheduler_public_ip: Optional[bool] = True,
    ) -> Awaitable[int]:
        ...

    def create_cluster(
        self,
        name: str = None,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        use_scheduler_public_ip: Optional[bool] = True,
    ) -> Union[int, Awaitable[int]]:

        return self._sync(
            self._create_cluster,
            name=name,
            configuration=configuration,
            software=software,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            account=account,
            workers=workers,
            backend_options=backend_options,
            environ=environ,
            scheduler_vm_types=scheduler_vm_types,
            worker_gpu_type=worker_gpu_type,
            worker_vm_types=worker_vm_types,
            use_scheduler_public_ip=use_scheduler_public_ip,
        )

    @track_context
    async def _create_cluster(
        self,
        name: str,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: Optional[list] = None,
        worker_vm_types: Optional[list] = None,
        use_scheduler_public_ip: Optional[bool] = True,
    ) -> int:
        account, name = self._normalize_name(
            name,
            context_account=account,
            allow_uppercase=True,
        )
        session = self._ensure_session()
        self._verify_account(account)
        backend_options = {
            **self._default_backend_options,
            **(backend_options or {}),
        }
        # prevent network options from being set per cluster
        self._verify_per_cluster_backend_options(backend_options)
        environ = environ or {}
        data = {
            "type": "create_cluster",
            "name": name,
            "server": self.server,
            "configuration": configuration,
            "software": software,
            "worker_cpu": worker_cpu,
            "worker_gpu": worker_gpu,
            "worker_memory": max(dask.utils.parse_bytes(worker_memory) // 2 ** 30, 1)
            if worker_memory
            else None,
            "worker_class": worker_class,
            "worker_options": worker_options,
            "scheduler_cpu": scheduler_cpu,
            "scheduler_memory": max(
                dask.utils.parse_bytes(scheduler_memory) // 2 ** 30, 1
            )
            if scheduler_memory
            else None,
            "scheduler_class": scheduler_class,
            "scheduler_options": scheduler_options,
            "workers": workers,
            "options": backend_options,
            "environ": environ,
            "scheduler_vm_types": scheduler_vm_types,
            "worker_gpu_type": worker_gpu_type,
            "worker_vm_types": worker_vm_types,
            "use_scheduler_public_ip": use_scheduler_public_ip,
        }
        ws_server = self.server.replace("http", "ws", 1)

        ws = WebsocketConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/clusters/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'create clusters in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(data)
        await ws.stream_messages()
        return await self._get_cluster_by_name(name=name, account=account)

    @track_context
    async def _delete_cluster(self, cluster_id: int, account: str = None) -> None:
        account = account or self.default_account

        if use_declarative():
            route = f"/api/v2/clusters/account/{account}/id/{cluster_id}"
        else:
            route = f"/api/v1/{account}/cluster/{cluster_id}/"

        response = await self._do_request(
            "DELETE",
            self.server + route,
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print("[green]Cluster deleted successfully.")

    @overload
    def delete_cluster(self: Cloud[Sync], cluster_id: int, account: str = None) -> None:
        ...

    @overload
    def delete_cluster(
        self: Cloud[Async], cluster_id: int, account: str = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring  # TODO: this docstring erroneously says "Name of cluster" when it really accepts an ID
    def delete_cluster(
        self, cluster_id: int, account: str = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_cluster, cluster_id, account)

    @overload
    def get_cluster_by_name(
        self: Cloud[Sync],
        name: str,
        account: str = None,
    ) -> int:
        ...

    @overload
    def get_cluster_by_name(
        self: Cloud[Async],
        name: str,
        account: str = None,
    ) -> Awaitable[int]:
        ...

    def get_cluster_by_name(
        self,
        name: str,
        account: str = None,
    ) -> Union[int, Awaitable[int]]:
        return self._sync(
            self._get_cluster_by_name,
            name=name,
            account=account,
        )

    @track_context
    async def _get_cluster_by_name_declarative(
        self, name: str, account: str = None
    ) -> int:
        account, name = self._normalize_name(
            name, context_account=account, allow_uppercase=True
        )

        response = await self._do_request(
            "GET",
            self.server + f"/api/v2/clusters/account/{account}/name/{name}",
        )
        if response.status >= 400:
            await handle_api_exception(response)

        cluster = await response.json()
        return cluster["id"]

    @track_context
    async def _get_cluster_by_name(self, name: str, account: str = None) -> int:
        """Fetch the latest cluster (pending/running) and store it under cluster_id"""
        if use_declarative():
            return await self._get_cluster_by_name_declarative(name, account)

        account, name = self._normalize_name(
            name, context_account=account, allow_uppercase=True
        )

        params = {"exclude_statuses": "stopping,stopped"}
        path = self.server + f"/api/v1/{account}/clusters/{name}/"
        response = await self._do_request(
            "GET",
            path,
            params=params,
        )

        if response.status >= 400:
            await handle_api_exception(response)

        cluster = await response.json()
        if cluster["id"] is None:
            raise Exception(f"Could not find cluster '{account}/{name}'")

        self.cluster_id = cast(int, cluster["id"])
        return self.cluster_id

    @track_context
    async def _cluster_status(
        self, cluster_id: int, account: str = None, exclude_stopped: bool = True
    ) -> dict:
        if use_declarative():
            raise NotImplementedError
        account = account or self.default_account
        params = {}
        if exclude_stopped:
            params = {"exclude_statuses": "stopping,stopped"}
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/{}/cluster/{}/".format(account, cluster_id),
            params=params,
        )
        if response.status >= 400:
            await handle_api_exception(response)
        data = await response.json()
        return data

    @track_context
    async def _security_declarative(
        self, cluster_id: int, account: str = None
    ) -> Tuple[dask.distributed.Security, dict]:
        times_waited = 0
        while True:
            cluster = await self._get_cluster_details_declarative(
                cluster_id=cluster_id, account=account
            )

            state = ClusterStateEnum(cluster["current_state"]["state"])
            if state == ClusterStateEnum.ready:
                public_ip = cluster["scheduler"]["instance"]["public_ip_address"]
                private_ip = cluster["scheduler"]["instance"]["private_ip_address"]
                tls_cert = cluster["cluster_options"]["tls_cert"]
                tls_key = cluster["cluster_options"]["tls_key"]

                # TODO (Declarative): pass extra_conn_args if we care about proxying through Coiled to the scheduler
                security = GatewaySecurity(tls_key, tls_cert)

                return security, {
                    # TODO (Declarative):
                    #  if Declarative ever supports schedulers on other ports, stop hard-coding the portop
                    "private_address": f"tls://{private_ip}:8786",
                    "public_address": f"tls://{public_ip}:8786",
                    "dashboard_address": f"http://{public_ip}:8787",
                }

            elif state.awaiting_readiness():
                if times_waited % 10 == 0:
                    logger.info("waiting for cluster")
                times_waited += 1
                await asyncio.sleep(1.0)
            else:
                # TODO (Declarative): give more info about what the problem is
                raise ValueError(f"Cluster status is {state.value}")

    @track_context
    async def _security(
        self, cluster_id: int, account: str = None
    ) -> Tuple[dask.distributed.Security, dict]:
        """
        Returns (security, result)

        result should have keys:
          - public_address
          - private_address
          - ... and maybe some other stuff
        """
        if use_declarative():
            return await self._security_declarative(cluster_id, account)
        while True:
            data = await self._cluster_status(
                cluster_id=cluster_id, account=account, exclude_stopped=False
            )
            if data["status"] in ["stopped", "stopping"]:
                # cluster is stopped, probably very shortly after starting
                raise ValueError(
                    "Cluster status is unexpectedly STOPPED: it was either unable to start up or died very quickly."
                )
            if data["status"] != "pending" and data["public_address"]:
                break
            else:
                await asyncio.sleep(1.0)

        result = format_security_output(data, cluster_id, self.server, self.token)
        security = GatewaySecurity(
            result.get("tls_key"),
            result.get("tls_cert"),
            extra_conn_args=result.get("extra_conn_args"),
        )

        return security, result

    @overload
    def security(
        self: Cloud[Sync], cluster_id: int, account: str = None
    ) -> Tuple[dask.distributed.Security, dict]:
        ...

    @overload
    def security(
        self: Cloud[Async], cluster_id: int, account: str = None
    ) -> Awaitable[Tuple[dask.distributed.Security, dict]]:
        ...

    def security(
        self, cluster_id: int, account: str = None
    ) -> Union[
        Tuple[dask.distributed.Security, dict],
        Awaitable[Tuple[dask.distribued.Security, dict]],
    ]:
        return self._sync(self._security, cluster_id, account)

    @track_context
    async def _requested_workers(
        self, cluster_id: int, account: str = None
    ) -> Set[str]:
        # TODO: declarative
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server
            + "/api/v1/{}/cluster/{}/requested_workers/".format(account, cluster_id),
        )
        if response.status >= 400:
            await handle_api_exception(response)
        data = await response.json()
        return set(data["workers"])

    @overload
    def requested_workers(
        self: Cloud[Sync], cluster_id: int, account: str = None
    ) -> Set[str]:
        ...

    @overload
    def requested_workers(
        self: Cloud[Async], cluster_id: int, account: str = None
    ) -> Awaitable[Set[str]]:
        ...

    def requested_workers(
        self, cluster_id: int, account: str = None
    ) -> Union[Set[str], Awaitable[Set[str]],]:
        return self._sync(self._requested_workers, cluster_id, account)

    @track_context
    async def _scale_up(
        self, cluster_id: int, n: int, account: str = None
    ) -> Optional[Dict]:
        account = account or self.default_account
        response = await self._do_request(
            "PATCH",
            f"{self.server}/api/v1/{account}/cluster/{cluster_id}/scale_up/",
            data={"worker_count_requested": n},
        )
        if response.status >= 400:
            await handle_api_exception(response)

        with contextlib.suppress(aiohttp.ContentTypeError, json.JSONDecodeError):
            result = await response.json()
            if "workers" not in result:
                warning_style = "[bold][yellow]Warning:[/yellow][/bold] "
                try:
                    message = (
                        f"{result['message']}\n"
                        f"code: {result['code']}\n"
                        f"exception: {result['exception']}"
                    )
                    console.print(f"{warning_style} {message}")
                except KeyError:
                    console.print(f"{warning_style} {result}")
                return
            return result

    @overload
    def scale_up(
        self: Cloud[Sync], cluster_id: int, n: int, account: str = None
    ) -> Optional[Dict]:
        ...

    @overload
    def scale_up(
        self: Cloud[Async], cluster_id: int, n: int, account: str = None
    ) -> Awaitable[Optional[Dict]]:
        ...

    def scale_up(
        self, cluster_id: int, n: int, account: str = None
    ) -> Union[Optional[Dict], Awaitable[Optional[Dict]]]:
        """Scale cluster to ``n`` workers

        Parameters
        ----------
        cluster_id
            Unique cluster identifier.
        n
            Number of workers to scale cluster size to.
        account
            Name of Coiled account which the cluster belongs to.
            If not provided, will default to ``Cloud.default_account``.

        """
        return self._sync(self._scale_up, cluster_id, n, account)

    @track_context
    async def _scale_down(
        self, cluster_id: int, workers: Set[str], account: str = None
    ) -> None:
        account = account or self.default_account
        response = await self._do_request(
            "PATCH",
            f"{self.server}/api/v1/{account}/cluster/{cluster_id}/scale_down/",
            data={"del_workers": workers},  # TODO: Hook here
        )
        if response.status >= 400:
            await handle_api_exception(response)

    @overload
    def scale_down(
        self: Cloud[Sync], cluster_id: int, workers: Set[str], account: str = None
    ) -> None:
        ...

    @overload
    def scale_down(
        self: Cloud[Async], cluster_id: int, workers: Set[str], account: str = None
    ) -> Awaitable[None]:
        ...

    def scale_down(
        self, cluster_id: int, workers: Set[str], account: str = None
    ) -> Optional[Awaitable[None]]:
        """Scale cluster to ``n`` workers

        Parameters
        ----------
        cluster_id
            Unique cluster identifier.
        workers
            Set of workers to scale down to.
        account
            Name of Coiled account which the cluster belongs to.
            If not provided, will default to ``Cloud.default_account``.

        """
        return self._sync(self._scale_down, cluster_id, workers, account)

    def _verify_account(self, account: str):
        """Perform sanity checks on account values

        In particular, this raises and informative error message if the
        account is not found, and provides a list of possible options.
        """
        account = account or self.default_account
        validate_account(account)
        if account not in self.accounts:
            raise PermissionError(
                "Account not found: '{}'\n"
                "Possible accounts: {}".format(account, sorted(self.accounts))
            )

    def _verify_per_cluster_backend_options(
        self, backend_options: Optional[dict] = None
    ):
        """Validation for cluster- (vs account-) level specified options."""
        backend_options = backend_options or {}
        if "network" in backend_options:
            raise PermissionError(
                "Network options cannot be specified per cluster. "
                "Use coiled.set_backend_options() to set for account."
            )

    @overload
    def create_api_token(
        self: Cloud[Sync],
        *,
        label: Optional[str] = None,
        days_to_expire: Optional[int] = None,
    ) -> dict:
        ...

    @overload
    def create_api_token(
        self: Cloud[Async],
        *,
        label: Optional[str] = None,
        days_to_expire: Optional[int] = None,
    ) -> Awaitable[dict]:
        ...

    def create_api_token(
        self, *, label: Optional[str] = None, days_to_expire: Optional[int] = None
    ) -> Union[dict, Awaitable[dict]]:
        return self._sync(
            self._create_api_token, label=label, days_to_expire=days_to_expire
        )

    @overload
    def list_api_tokens(
        self: Cloud[Sync], include_inactive: bool = False
    ) -> dict[str, dict]:
        ...

    @overload
    def list_api_tokens(
        self: Cloud[Async], include_inactive: bool = False
    ) -> Awaitable[dict[str, dict]]:
        ...

    def list_api_tokens(
        self, include_inactive: bool = False
    ) -> Union[Awaitable[dict[str, dict]], dict[str, dict]]:
        return self._sync(self._list_api_tokens, include_inactive=include_inactive)

    @overload
    def revoke_all_api_tokens(self: Cloud[Sync]) -> None:
        ...

    @overload
    def revoke_all_api_tokens(self: Cloud[Async]) -> Awaitable[None]:
        ...

    def revoke_all_api_tokens(self) -> Optional[Awaitable[None]]:
        return self._sync(
            self._revoke_all_api_tokens,
        )

    async def _revoke_all_api_tokens(self) -> None:
        tokens = await self._list_api_tokens(include_inactive=True)
        logged_in_token_id = None
        # we could be more asyncy here by kicking off multiple revokes
        # at once but this seems fine
        for token_id in tokens.keys():
            if self.token.startswith(token_id):
                # this is the current token! revoke it last
                logged_in_token_id = token_id
            else:
                await self._revoke_api_token(identifier=token_id)

        # after transitioning to new api tokens, we expect we would
        # find the in-use token in the tokens list
        # but in the meantime the in-use token might be an old-style one we can't revoke
        if logged_in_token_id is None:
            rich.print("Did not revoke the token you're logged in with now.")
        else:
            await self._revoke_api_token(identifier=logged_in_token_id)

    @overload
    def revoke_api_token(
        self: Cloud[Sync],
        *,
        identifier: Optional[str] = None,
        label: Optional[str] = None,
    ) -> None:
        ...

    @overload
    def revoke_api_token(
        self: Cloud[Async],
        *,
        identifier: Optional[str] = None,
        label: Optional[str] = None,
    ) -> Awaitable[None]:
        ...

    def revoke_api_token(
        self, *, identifier: Optional[str] = None, label: Optional[str] = None
    ) -> Union[None, Awaitable[None]]:
        return self._sync(self._revoke_api_token, identifier=identifier, label=label)

    @overload
    def create_software_environment(
        self: Cloud[Sync],
        name: str = None,
        *,
        account: Optional[str] = None,
        conda: Union[list, dict, str] = None,
        pip: Union[list, str] = None,
        container: str = None,
        post_build: Union[list, str] = None,
        conda_env_name: str = None,
        backend_options: Optional[Dict] = None,
        log_output=sys.stdout,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> None:
        ...

    @overload
    def create_software_environment(
        self: Cloud[Async],
        name: str = None,
        *,
        account: Optional[str] = None,
        conda: Union[list, dict, str] = None,
        pip: Union[list, str] = None,
        container: str = None,
        post_build: Union[list, str] = None,
        conda_env_name: str = None,
        backend_options: Optional[Dict] = None,
        log_output=sys.stdout,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> Awaitable[None]:
        ...

    def create_software_environment(
        self,
        name: str = None,
        *,
        account: Optional[str] = None,
        conda: Union[list, dict, str] = None,
        pip: Union[list, str] = None,
        container: str = None,
        post_build: Union[list, str] = None,
        conda_env_name: str = None,
        backend_options: Optional[Dict] = None,
        log_output=sys.stdout,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> Optional[Awaitable[None]]:
        return self._sync(
            self._create_software_environment,
            name=name,
            account=account,
            conda=conda,
            pip=pip,
            container=container,
            post_build=post_build,
            log_output=log_output,
            conda_env_name=conda_env_name,
            backend_options=backend_options,
            private=private,
            force_rebuild=force_rebuild,
            environ=environ,
        )

    @track_context
    async def _create_software_environment(
        self,
        name=None,
        *,
        account: Optional[str] = None,
        conda=None,
        pip=None,
        container=None,
        post_build=None,
        conda_env_name: str = None,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> None:
        """
        :param name:
        :param conda:
        :param pip:
        :param container:
        :param post_build:
        :param conda_env_name:
        :param log_output:
        :param backend_options: Dict or None
          backend_options["container_registry"]
        :param private:
        :param force_rebuild:
        :param environ: Dict or None
        :return:
        """
        session = self._ensure_session()
        if conda is None and container is None and pip is not None:
            v = ".".join(map(str, sys.version_info[:2]))
            conda = {"dependencies": [f"python={v}", {"pip": []}]}
        elif isinstance(conda, list):
            conda = {"dependencies": conda}
        elif isinstance(conda, (str, pathlib.Path)):
            # Local conda environment YAML file
            with open(conda, mode="r") as f:
                conda = yaml.safe_load(f)

        if isinstance(pip, (str, pathlib.Path)):
            # Local pip requirements file
            with open(pip, mode="r") as f:
                pip = f.read().splitlines()

        if isinstance(post_build, (str, pathlib.Path)):
            # Post-build script
            with open(post_build, mode="r") as f:
                post_build = f.read().splitlines()

        # Conda supports specifying pip packages via their CLI, but not when
        # using conda.api.Solver. So we move any pip packages to the pip portion
        # of this software environment
        if conda is not None:
            for idx, dep in enumerate(conda["dependencies"]):
                if isinstance(dep, dict) and list(dep.keys()) == ["pip"]:
                    # Copy conda to avoid mutating input from users
                    conda = copy.deepcopy(conda)
                    pip_packages = conda["dependencies"].pop(idx)["pip"]
                    if pip is not None:
                        pip = pip + pip_packages
                    else:
                        pip = pip_packages

        # Remove duplicates and ensure consistent package ordering which helps with
        # downstream tokenization of package spec
        if pip is not None:
            pip = sorted(set(pip))
        if conda is not None:
            conda["dependencies"] = sorted(set(conda["dependencies"]))

        if name is None and conda is not None and "name" in conda:
            name = conda["name"]
        if name is None:
            raise ValueError("Must provide a name when creating a software environment")

        account, name = self._normalize_name(
            str(name), context_account=account, raise_on_account_conflict=True
        )

        # Connect to the websocket, send the data and get some logs
        data = {
            "type": "build",
            "container": container,
            "conda": conda,
            "conda_env_name": conda_env_name,
            "pip": pip,
            "post_build": post_build,
            "options": {**self._default_backend_options, **(backend_options or {})},
            "private": private,
            "force_rebuild": force_rebuild,
            "environ": environ or {},
        }

        ws_server = self.server.replace("http", "ws", 1)

        ws = WebsocketConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/software_environments/{name}/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'create environments in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(data)
        await ws.stream_messages()

    @track_context
    async def _create_api_token(
        self, label: Optional[str] = None, days_to_expire: Optional[int] = None
    ) -> dict:
        label_str = "no label" if label is None else f"label '{label}'"
        rich.print(
            f"Generating an API token with {label_str} expiring in {days_to_expire} days..."
        )

        data = {}
        if label is not None:
            data["label"] = label
        if days_to_expire is not None:
            expiry = datetime.datetime.utcnow() + datetime.timedelta(
                days=days_to_expire
            )
            data["expiry"] = expiry.isoformat()
        response = await self._do_request(
            "POST",
            self.server + "/api/v1/api-tokens/",
            json=data,
        )
        if response.status >= 400:
            await handle_api_exception(response)

        return await response.json()

    @track_context
    async def _list_api_tokens(self, include_inactive) -> dict[str, dict]:
        tokens = await self._depaginate(self._list_api_tokens_page)
        if include_inactive:
            return tokens
        else:
            return {
                t_id: t_details
                for t_id, t_details in tokens.items()
                if not t_details["revoked"] and not t_details["expired"]
            }

    @track_context
    async def _list_api_tokens_page(
        self, page: int
    ) -> Tuple[dict[str, dict], Optional[str]]:
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/api-tokens/",
            params={"page": page},
        )
        if response.status >= 400:
            await handle_api_exception(response)
            return {}, None
        else:
            response_json = await response.json()
            results = {r["identifier"]: r for r in response_json["results"]}
            return results, response_json["next"]

    @track_context
    async def _revoke_api_token(
        self, *, identifier: Optional[str] = None, label: Optional[str] = None
    ) -> None:
        if label is None and identifier is None:
            raise ValueError("We need a label or identifier to revoke a token.")

        if label is not None:
            if identifier is not None:
                raise ValueError(
                    "Only a label or identifier should be provided, but not both."
                )

            tokens = await self._list_api_tokens(include_inactive=False)
            identifiers_found = [
                token_id
                for token_id, details in tokens.items()
                if details["label"] == label
            ]

            if len(identifiers_found) == 0:
                raise ValueError(f"Found no tokens with label '{label}'.")
            elif len(identifiers_found) > 1:
                raise ValueError(
                    f"Found multiple tokens with label '{label}'. Please revoke with the `identifier` instead."
                )

            else:
                [identifier] = identifiers_found

        rich.print(f"Revoking API token with identifier '{identifier}' ...")

        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/api-tokens/{identifier}/revoke",
        )

        if response.status >= 400:
            if response.status == 404:
                raise ValueError(
                    f"Could not find an API token with identifier {identifier}"
                )
            await handle_api_exception(response)

    @staticmethod
    async def _depaginate(
        func: Callable[..., Awaitable[Tuple[dict, Optional[str]]]],
        *args,
        **kwargs,
    ) -> dict:
        results_all = {}
        page = 1
        while True:
            kwargs["page"] = page
            results, next = await func(*args, **kwargs)
            results_all.update(results)
            page += 1
            if (not results) or next is None:
                break
        return results_all

    @track_context
    async def _list_software_environments(self, account: Optional[str] = None) -> dict:
        return await self._depaginate(
            self._list_software_environments_page, account=account
        )

    @track_context
    async def _list_software_environments_page(
        self, page: int, account: Optional[str] = None
    ) -> Tuple[dict, Optional[str]]:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/software_environments/",
            params={"page": page},
        )
        if response.status >= 400:
            await handle_api_exception(response)
            return {}, None
        else:
            response_json = await response.json()
            results = {
                f"{format_account_output(r['account'])}/{r['name']}": format_software_environment_output(
                    r
                )
                for r in response_json["results"]
            }

            return results, response_json["next"]

    @track_context
    async def _list_instance_types(
        self,
        backend: Optional[str] = None,
        min_cores: Optional[int] = 0,
        min_gpus: Optional[int] = 0,
        min_memory: Optional[int] = 0,
        json: bool = False,
    ) -> Union[dict[str, VmType] | None]:

        if backend:
            user_provider = backend
        else:
            user_provider = await self.get_account_provider_name(
                account=self.default_account
            )

        if user_provider and user_provider not in ALLOWED_PROVIDERS:
            raise UnsupportedBackendError(
                (
                    f"Unknown cloud provider provided - {user_provider} is not"
                    f" one of {ALLOWED_PROVIDERS}"
                )
            )

        instance_types = await self._get_instance_types(
            backend=user_provider,
            min_cores=min_cores,
            min_gpus=min_gpus,
            min_memory=min_memory,
        )

        if not json:
            instance_type_table(instance_types)
            return

        return instance_types

    @track_context
    async def _list_instance_types_page(
        self,
        page: int,
        min_cores: Optional[int] = 0,
        min_gpus: Optional[int] = 0,
        min_memory: Optional[int] = 0,
    ) -> Tuple[dict, Optional[str]]:
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/vm-types/",
            params={
                "page": page,
                "min_cores": min_cores,
                "min_memory": min_memory,
                "min_gpus": min_gpus,
            },
        )

        if response.status == 200:
            body = await response.json()

            results = {f"{r['name']}": r for r in body["results"]}
            return results, body["next"]

        else:
            msg = (
                f"Coiled API responded with a {response.status} status code "
                + "while fetching available instance types."
            )
            raise ApiResponseStatusError(msg)

    @overload
    def list_software_environments(
        self: Cloud[Sync], account: Optional[str] = None
    ) -> dict:
        ...

    @overload
    def list_software_environments(
        self: Cloud[Async], account: Optional[str] = None
    ) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_software_environments(
        self, account: Optional[str] = None
    ) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_software_environments, account=account)

    def _normalize_name(
        self,
        name: str,
        context_account: Optional[str] = None,
        raise_on_account_conflict: bool = False,
        allow_uppercase: bool = False,
    ) -> Tuple[str, str]:
        account, parsed_name, _ = parse_identifier(
            name, allow_uppercase=allow_uppercase
        )
        if (
            raise_on_account_conflict
            and context_account is not None
            and account is not None
            and context_account != account
        ):
            raise AccountConflictError(
                unparsed_name=name,
                account_from_name=account,
                account=context_account,
            )
        account = account or context_account or self.default_account
        return account, parsed_name

    @overload
    def delete_software_environment(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> None:
        ...

    @overload
    def delete_software_environment(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring
    def delete_software_environment(
        self, name: str, account: Optional[str] = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_software_environment, name, account)

    @track_context
    async def _delete_software_environment(
        self, name: str, account: Optional[str] = None
    ) -> None:
        context_account = account
        account, name, tag = parse_identifier(name)
        account = account or context_account or self.default_account
        if tag:
            name = ":".join([name, tag])
        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/software_environments/{name}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print("[green]Software environment deleted successfully.")

    @overload
    def create_cluster_configuration(
        self: Cloud[Sync],
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int = 1,
        worker_gpu: int = 0,
        worker_memory: str = "4 GiB",
        worker_class: str = "dask.distributed.Nanny",
        worker_options: dict = None,
        scheduler_cpu: int = 1,
        scheduler_memory: str = "4 GiB",
        scheduler_class: str = "dask.distributed.Scheduler",
        scheduler_options: dict = None,
        private: bool = False,
    ) -> None:
        ...

    @overload
    def create_cluster_configuration(
        self: Cloud[Async],
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int = 1,
        worker_gpu: int = 0,
        worker_memory: str = "4 GiB",
        worker_class: str = "dask.distributed.Nanny",
        worker_options: dict = None,
        scheduler_cpu: int = 1,
        scheduler_memory: str = "4 GiB",
        scheduler_class: str = "dask.distributed.Scheduler",
        scheduler_options: dict = None,
        private: bool = False,
    ) -> Awaitable[None]:
        ...

    def create_cluster_configuration(
        self,
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int = 1,
        worker_gpu: int = 0,
        worker_memory: str = "4 GiB",
        worker_class: str = "dask.distributed.Nanny",
        worker_options: dict = None,
        scheduler_cpu: int = 1,
        scheduler_memory: str = "4 GiB",
        scheduler_class: str = "dask.distributed.Scheduler",
        scheduler_options: dict = None,
        private: bool = False,
    ) -> Optional[Awaitable[None]]:
        return self._sync(
            self._create_cluster_configuration,
            name=name,
            software=software,
            account=account,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            private=private,
        )

    @track_context
    async def _create_cluster_configuration(
        self,
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int,
        worker_gpu: int,
        worker_memory: str,
        worker_class: str,
        worker_options: dict,
        scheduler_cpu: int,
        scheduler_memory: str,
        scheduler_class: str,
        scheduler_options: dict,
        private: bool,
    ) -> None:
        account, name = self._normalize_name(name, context_account=account)
        data = {
            "software_environment": software,
            "worker_cpu": worker_cpu,
            "worker_gpu": worker_gpu,
            "worker_memory": max(
                # TODO we should be throwing an error instead of choosing
                # 1 if they give use something below 1.
                dask.utils.parse_bytes(worker_memory) // 2 ** 30,
                1,
            ),
            "worker_class": worker_class,
            "worker_options": worker_options or {},
            "scheduler_cpu": scheduler_cpu,
            "scheduler_memory": max(
                dask.utils.parse_bytes(scheduler_memory) // 2 ** 30, 1
            ),
            "scheduler_class": scheduler_class,
            "scheduler_options": scheduler_options or {},
            # TODO environments
            "private": private,
        }
        # Check if we already have a config
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/cluster_configurations/{name}/",
        )
        if response.status == 404:
            rich.print(f"Attempting to create cluster configuration '{name}'...")
            data.update({"name": name})
            response = await self._do_request(
                "POST",
                self.server + f"/api/v1/{account}/cluster_configurations/",
                json=data,
            )
        else:
            rich.print(
                f"Found cluster configuration '{name}', updating this configuration..."
            )
            response = await self._do_request(
                "PATCH",
                self.server + f"/api/v1/{account}/cluster_configurations/{name}/",
                json=data,
            )

        if response.status >= 400:
            await handle_api_exception(response)

    @overload
    def list_cluster_configurations(self: Cloud[Sync], account=None) -> dict:
        ...

    @overload
    def list_cluster_configurations(
        self: Cloud[Async], account=None
    ) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_cluster_configurations(self, account=None) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_cluster_configurations, account=account)

    @track_context
    async def _list_cluster_configurations(self, account=None) -> dict:
        return await self._depaginate(
            self._list_cluster_configurations_page, account=account
        )

    @track_context
    async def _list_cluster_configurations_page(
        self, page: int, account=None
    ) -> Tuple[dict, Optional[str]]:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/cluster_configurations/",
            params={"page": page},
        )
        if response.status >= 400:
            await handle_api_exception(response)  # will always raise

        response_json = await response.json()
        results = {
            f"{format_account_output(r['account'])}/{r['name']}": format_cluster_configuration_output(
                r
            )
            for r in response_json["results"]
        }
        return results, response_json["next"]

    @overload
    def delete_cluster_configuration(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> None:
        ...

    @overload
    def delete_cluster_configuration(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring
    def delete_cluster_configuration(
        self, name: str, account: Optional[str] = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_cluster_configuration, name, account)

    @track_context
    async def _delete_cluster_configuration(
        self, name: str, account: Optional[str] = None
    ):
        account, name = self._normalize_name(name, context_account=account)

        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/cluster_configurations/{name}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print("[green]Cluster configuration deleted successfully.")

    @overload
    def set_backend_options(
        self: Cloud[Sync],
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> str:
        ...

    @overload
    def set_backend_options(
        self: Cloud[Async],
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> Awaitable[str]:
        ...

    def set_backend_options(
        self,
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> Union[str, Awaitable[str]]:

        return self._sync(
            self._set_backend_options,
            backend_options,
            account=account,
            log_output=log_output,
        )

    @track_context
    async def _set_backend_options(
        self,
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> str:
        session = self._ensure_session()
        account = account or self.default_account
        self._verify_account(account)
        logging_context = {}
        default_configuration_message = {
            "type": "update_options",
            "logging_context": logging_context,
            "data": backend_options,
        }
        ws_server = self.server.replace("http", "ws", 1)
        ws = ConfigureBackendConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/cluster-info/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'edit backend_options in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(default_configuration_message)
        with Spinner():
            await ws.stream_messages()
        return f"{self.server}/{account}/account"

    @overload
    def list_instance_types(
        self: Cloud[Sync],
        backend: Optional[str],
        json: Literal[False],
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> None:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Async],
        backend: Optional[str],
        json: Literal[False],
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> Awaitable[None]:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Sync],
        backend: Optional[str],
        json: bool,
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> Optional[dict[str, VmType]]:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Async],
        backend: Optional[str],
        json: bool,
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> Awaitable[Optional[dict[str, VmType]]]:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Sync],
        backend: Optional[str],
        json: Literal[True],
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> dict[str, VmType]:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Async],
        backend: Optional[str],
        json: Literal[True],
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> Awaitable[dict[str, VmType]]:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Sync],
        backend: Optional[str],
        json: Literal[False],
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> None:
        ...

    @overload
    def list_instance_types(
        self: Cloud[Async],
        backend: Optional[str],
        json: Literal[False],
        min_cores: int,
        min_gpus: int,
        min_memory: int,
    ) -> Awaitable[None]:
        ...

    def list_instance_types(
        self,
        backend: Optional[str] = None,
        json: bool = False,
        min_cores: int = 0,
        min_gpus: int = 0,
        min_memory: int = 0,
    ):
        return self._sync(
            self._list_instance_types,
            backend=backend,
            json=json,
            min_cores=min_cores,
            min_gpus=min_gpus,
            min_memory=min_memory,
        )

    async def _get_instance_types(
        self,
        backend: Optional[str],
        min_cores: Optional[int] = 0,
        min_gpus: Optional[int] = 0,
        min_memory: Optional[int] = 0,
    ) -> dict[str, VmType]:
        """Retrieve available instance types from API. Filter based on user cloud provider setting

        Parameters
        ----------
        backend
            User backend type. Used for filtering cloud provider machine types.

        min_cores
            Minimum number of desired cores. Defaults to 0.

        min_gpus
            Minimum number of desired GPUs. Defaults to 0.

        min_memory
            Minimum amount of RAM in Mb. Defaults to 0.

        Returns
        -------
        all_types
            List of available VmType objects
        """

        all_types = await self._depaginate(
            self._list_instance_types_page,
            min_cores=min_cores,
            min_gpus=min_gpus,
            min_memory=min_memory,
        )

        if backend in ALLOWED_PROVIDERS:
            return {
                f"{name}": i
                for name, i in all_types.items()
                if i["backend_type"] == f"vm_{backend}"
            }
        else:
            return {f"{name}": i for name, i in all_types.items()}

    @overload
    def list_gpu_types(self: Cloud[Sync], json: Literal[True]) -> dict:
        ...

    @overload
    def list_gpu_types(self: Cloud[Async], json: Literal[True]) -> Awaitable[dict]:
        ...

    @overload
    def list_gpu_types(self: Cloud[Sync], json: bool) -> Optional[dict]:
        ...

    @overload
    def list_gpu_types(self: Cloud[Async], json: bool) -> Awaitable[Optional[dict]]:
        ...

    def list_gpu_types(self, json: bool = False):
        return self._sync(self._list_gpu_types, json=json)

    @track_context
    async def _list_gpu_types(self, json: bool = False):
        title = "GCP GPU Types"
        allowed_gpus = "nvidia-tesla-t4"
        if json:
            return {title: allowed_gpus}

        table = Table(title=title)
        table.add_column("Backend")
        table.add_column("GPU Type")

        table.add_row("GCP", allowed_gpus)

        console = Console()
        console.print(table)

    @overload
    def cluster_logs(
        self: Cloud[Sync],
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Logs:
        ...

    @overload
    def cluster_logs(
        self: Cloud[Async],
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Awaitable[Logs]:
        ...

    def cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Union[Logs, Awaitable[Logs]]:
        return self._sync(self._cluster_logs, cluster_id, account, scheduler, workers)

    @track_context
    async def _cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Logs:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/{}/cluster/{}/logs/".format(account, cluster_id),
        )
        if response.status >= 400:
            await handle_api_exception(response)

        data = await response.json()
        # munge the response to match the signature of Cluster's parent class
        out = {}
        if scheduler:
            out["Scheduler"] = Log(data["scheduler"]["logs"])
        if workers:
            for w in data["workers"]:
                out[w["name"]] = Log(w["logs"])

        return Logs(out)

    @track_context
    async def get_aws_credentials(self, account: str = None):
        """Return the logged in user's AWS credentials"""
        backend_options = await self.get_backend_options(account)
        if backend_options["backend"] != "ecs":
            return {}

        credentials = backend_options.get("options", {}).get("credentials", {})
        return credentials

    @track_context
    async def get_backend_options(self, account: str = None) -> dict:
        """Queries the API to get the backend options from account."""
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/backend_options/",
        )
        if response.status >= 400:
            await handle_api_exception(response)

        backend_options = await response.json()
        return backend_options

    @track_context
    async def get_account_provider_name(self, account: str = None) -> str:
        """Get the provider name used by the account.

        Currently we are using this method only for the validation of instance
        types when users provide them. So we are handling the three clouds only
        otherwise we will return whatever is in the backend or an empty string.

        """
        backend_options = await self.get_backend_options(account)

        if backend_options.get("backend") == "vm":
            provider_name = backend_options.get("options", {}).get("provider_name", "")

        elif backend_options.get("backend") == "vm_aws":
            provider_name = "aws"
        elif backend_options.get("backend") == "vm_gcp":
            provider_name = "gcp"
        else:
            provider_name = backend_options.get("backend", "")

        return provider_name

    @overload
    def get_software_info(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> dict:
        ...

    @overload
    def get_software_info(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[dict]:
        ...

    def get_software_info(
        self, name: str, account: Optional[str] = None
    ) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._get_software_info, name=name, account=account)

    @track_context
    async def _get_software_info(
        self, name: str, account: Optional[str] = None
    ) -> dict:
        """Retrieve solved spec for a Coiled software environment

        Parameters
        ----------
        name
            Software environment name

        Returns
        -------
        results
            Coiled software environment information
        """
        account, name = self._normalize_name(name, context_account=account)

        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/software_environments/{name}/",
        )
        if response.status >= 400:
            text = await response.text()
            if "Not found" in text:
                raise ValueError(
                    f"Could not find a '{account}/{name}' Coiled software environment"
                )
            else:
                await handle_api_exception(response)

        results = await response.json()
        return results

    @overload
    def list_core_usage(
        self: Cloud[Sync], json: Literal[False], account: str = None
    ) -> None:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Async], json: Literal[False], account: str = None
    ) -> Awaitable[None]:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Sync], json: Literal[True], account: str = None
    ) -> dict:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Async], json: Literal[True], account: str = None
    ) -> Awaitable[dict]:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Async], json: bool, account: str = None
    ) -> Awaitable[Optional[dict]]:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Sync], json: bool, account: str = None
    ) -> Optional[dict]:
        ...

    def list_core_usage(
        self, json: bool = False, account: str = None
    ) -> Union[Awaitable[Optional[dict]], Optional[dict]]:
        return self._sync(self._list_core_usage, json=json, account=account)

    @track_context
    async def _list_core_usage(
        self, json: bool = False, account: str = None
    ) -> Optional[dict]:
        account = account or self.default_account

        response = await self._do_request(
            "GET", f"{self.server}/api/v1/{account}/usage/cores/"
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()

        if json:
            return result

        cores_table = Table(title="Core usage")
        cores_table.add_column("Tier Limit", justify="center")
        cores_table.add_column("User Core Limit", justify="center")
        cores_table.add_column("User Total", justify="center")
        cores_table.add_column("Account Total", justify="center")
        cores_table.add_column("Cores used by Clusters", justify="center")
        cores_table.add_column("Credits Total", justify="center")
        cores_table.add_column("Credits Used", justify="center")

        cores_table.add_row(
            str(result["tier_limit"]),
            str(result["core_limit"]),
            str(result["user_total"]),
            str(result["account_total"]),
            str(result["clusters_total"]),
            str(result["quota"]),
            str(result["spent"]),
        )

        console = Console()
        console.print(cores_table)
        return None

    async def _list_local_versions(self, json: bool = False) -> Union[dict, None]:
        versions_table = Table(title="Versions")
        versions_table.add_column("Operating System", justify="center")
        versions_table.add_column("Python Version", justify="center")
        versions_table.add_column("Pip Version", justify="center"),
        versions_table.add_column("Conda Version", justify="center")
        versions_table.add_column("Coiled Version", justify="center")
        versions_table.add_column("Dask Version", justify="center")
        versions_table.add_column("Distributed Version", justify="center")

        try:
            import conda

            conda_version = conda.__version__
        except ModuleNotFoundError:
            conda_version = "None"

        try:
            import pip

            pip_version = pip.__version__
        except ModuleNotFoundError:
            pip_version = "None"

        versions_table.add_row(
            platform.platform(),
            str(PY_VERSION),
            pip_version,
            conda_version,
            str(COILED_VERSION),
            dask.__version__,
            distributed.__version__,
        )

        if json:
            return {
                "operating_system": platform.platform(),
                "python_version": PY_VERSION,
                "pip_version": pip_version,
                "conda_version": conda_version,
                "coiled_version": COILED_VERSION,
                "dask_version": dask.__version__,
                "distributed_version": distributed.__version__,
            }

        console.print(versions_table)
        return None

    @overload
    def list_local_versions(self: Cloud[Sync], json: Literal[False]) -> None:
        ...

    @overload
    def list_local_versions(
        self: Cloud[Async], json: Literal[False]
    ) -> Awaitable[None]:
        ...

    @overload
    def list_local_versions(self: Cloud[Sync], json: Literal[True]) -> dict:
        ...

    @overload
    def list_local_versions(self: Cloud[Async], json: Literal[True]) -> Awaitable[dict]:
        ...

    @overload
    def list_local_versions(self: Cloud[Sync], json: bool) -> Optional[dict]:
        ...

    @overload
    def list_local_versions(
        self: Cloud[Async], json: bool
    ) -> Awaitable[Optional[dict]]:
        ...

    def list_local_versions(
        self, json: bool = False
    ) -> Union[Awaitable[Optional[dict]], Optional[dict]]:
        return self._sync(self._list_local_versions, json=json)

    @overload
    def get_notifications(
        self: Cloud[Sync],
        json: Literal[True],
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> List[dict]:
        ...

    @overload
    def get_notifications(
        self: Cloud[Async],
        json: Literal[True],
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Awaitable[List[dict]]:
        ...

    @overload
    def get_notifications(
        self: Cloud[Sync],
        json: bool,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Optional[List[dict]]:
        ...

    @overload
    def get_notifications(
        self: Cloud[Async],
        json: bool,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Awaitable[Optional[List[dict]]]:
        ...

    def get_notifications(
        self,
        json: bool = False,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Union[Awaitable[Optional[List[dict]]], Optional[List[dict]]]:
        return self._sync(
            self._get_notifications,
            json=json,
            account=account,
            limit=limit,
            level=level,
        )

    @track_context
    async def _get_notifications(
        self,
        json: bool = False,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Optional[List[dict]]:
        account = account or self.default_account

        response = await self._do_request(
            "GET",
            f"{self.server}/api/v1/{account}/notifications/",
            params={"limit": limit, "level": level},
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        notifications: List[dict] = result["notifications"]

        if json:
            return notifications

        notifications_table = Table(title="Notifications")
        notifications_table.add_column("time", justify="center", overflow="fold")
        notifications_table.add_column("id", justify="center", overflow="fold")
        notifications_table.add_column("level", justify="center", overflow="fold")
        notifications_table.add_column("event_type", justify="center", overflow="fold")
        notifications_table.add_column("elapsed", justify="center", overflow="fold")
        notifications_table.add_column("msg", justify="center", overflow="fold")
        notifications_table.add_column("data", justify="center", overflow="fold")

        for notification in notifications:
            try:
                local_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(notification["timestamp"])
                )
            except KeyError:
                local_time = "???"
            notifications_table.add_row(
                str(local_time),
                str(notification.get("id", "")),
                logging.getLevelName(notification.get("level", "")),
                str(notification.get("event_type", "")),
                str(notification.get("elapsed", "") or ""),
                str(notification["msg"]),
                str(notification.get("data", "")),
            )

        console = Console()
        console.print(notifications_table)
        return None

    @track_context
    async def _noop_wait(self, duration: int):
        response = await self._do_request(
            "GET", self.server + f"/api/v1/_noop_wait/{int(duration)}"
        )

        result = await response.json()
        return result

    @track_context
    async def _upload_performance_report(
        self,
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Dict:
        account = account or self.default_account

        data = aiohttp.MultipartWriter("form-data")
        part = data.append(open(content, "rb"))
        part.headers[
            aiohttp.hdrs.CONTENT_DISPOSITION
        ] = f'form-data; name="file"; filename="{filename}"; filename*="{filename}"'

        upload_type = "private" if private else "public"
        response = await self._do_request(
            "POST",
            f"{self.server}/api/v1/{account}/performance_reports/{upload_type}/",
            data=data,
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return result

    @overload
    def upload_performance_report(
        self: Cloud[Sync],
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Dict:
        ...

    @overload
    def upload_performance_report(
        self: Cloud[Async],
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Awaitable[Dict]:
        ...

    def upload_performance_report(
        self,
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Union[Dict, Awaitable[Dict]]:
        return self._sync(
            self._upload_performance_report,
            content,
            filename=filename,
            account=account,
            private=private,
        )

    @track_context
    async def _list_performance_reports(
        self,
        account: str = None,
    ) -> List[Dict]:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            f"{self.server}/api/v1/{account}/performance_reports/all/",
        )
        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return result

    @overload
    def list_performance_reports(
        self: Cloud[Async],
        account: str = None,
    ) -> Awaitable[List[Dict]]:
        ...

    @overload
    def list_performance_reports(
        self: Cloud[Sync],
        account: str = None,
    ) -> List[Dict]:
        ...

    def list_performance_reports(
        self,
        account: str = None,
    ) -> Union[List[Dict], Awaitable[List[Dict]]]:
        return self._sync(
            self._list_performance_reports,
            account=account,
        )

    @overload
    def list_user_information(self: Cloud[Sync]) -> dict:
        ...

    @overload
    def list_user_information(self: Cloud[Async]) -> Awaitable[dict]:
        ...

    def list_user_information(self) -> Union[Awaitable[dict], dict]:
        return self._sync(self._list_user_information)

    @track_context
    async def _list_user_information(
        self,
    ) -> dict:
        response = await self._do_request("GET", self.server + "/api/v1/users/me/")
        if response.status >= 400:
            await handle_api_exception(response)
        result = await response.json()

        return result

    @track_context
    async def _health_check(self) -> dict:
        response = await self._do_request("GET", self.server + "/api/v1/health")
        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return result

    @overload
    def health_check(self: Cloud[Sync]) -> dict:
        ...

    @overload
    def health_check(self: Cloud[Async]) -> Awaitable[dict]:
        ...

    def health_check(self) -> Union[Awaitable[dict], dict]:
        return self._sync(self._health_check)


# Utility functions for formatting list_* endpoint responses to be more user-friendly


def format_security_output(data, cluster_id, server, token):
    d = data.copy()
    scheme, _ = parse_address(d["public_address"])
    if scheme.startswith("ws"):
        address = f"{server.replace('http', 'ws')}/cluster/{cluster_id}/"
        d["public_address"] = address
        d["extra_conn_args"] = {
            "headers": {"Authorization": get_auth_header_value(token)}
        }
        d["dashboard_address"] = f"{server}/dashboard/{cluster_id}/status"
        d.pop("tls_key")
        d.pop("tls_cert")
    else:
        # can delete after backend no longer sends extra_conn_args
        d.pop("extra_conn_args", None)
    return d


def format_account_output(d):
    return d["slug"]


def format_software_environment_output(d):
    exclude_list = [
        "id",
        "name",
        "content_hash",
        "builds",
    ]
    d = {k: v for k, v in d.items() if k not in exclude_list}
    d["account"] = format_account_output(d["account"])
    return d


def format_cluster_configuration_output(d):
    d = d.copy()
    d.pop("id")
    d.pop("name")
    d["account"] = format_account_output(d["account"])
    for process in ["scheduler", "worker"]:
        d[process].pop("id")
        d[process].pop("name")
        d[process].pop("account")
        d[process]["software"] = d[process]["software_environment"]
        d[process].pop("software_environment")
    return d


def format_cluster_output(d, server):
    d = d.copy()
    for key in ["auth_token", "name", "last_seen"]:
        d.pop(key)
    d["account"] = format_account_output(d["account"])
    # Rename "public_address" to "address"
    address = d.pop("public_address")
    scheme, _ = parse_address(address)
    if scheme.startswith("ws"):
        address = f"{server.replace('http', 'ws')}/cluster/{d['id']}/"
    d["address"] = address
    # Use proxied dashboard address if we're in a hosted notebook
    # or proxying through websockets
    if dask.config.get("coiled.dashboard.proxy", False) or scheme.startswith("ws"):
        d["dashboard_address"] = f"{server}/dashboard/{d['id']}/status"
    return d


# Public API


def create_api_token(
    *, label: Optional[str] = None, days_to_expire: Optional[int] = None
) -> dict:
    """Create a new API token.

    Parameters
    ---------
    label
        A label associated with the new API token, helpful for identifying it later.
    days_to_expire
        A number of days until the new API token expires.
    """
    with Cloud() as cloud:
        return cloud.create_api_token(
            label=label,
            days_to_expire=days_to_expire,
        )


def list_api_tokens(include_inactive=False) -> dict[str, dict]:
    """List your API tokens.

    Note that this does not provide the actual key value, which is only available when creating the key.

    Returns
    -------
    Dictionary with information about each API token for your account. Keys in the dictionary are the API tokens'
    identifiers of {kind}s, while the values contain information about the corresponding API token.
    """
    with Cloud() as cloud:
        return cloud.list_api_tokens(include_inactive=include_inactive)


def revoke_api_token(
    *, identifier: Optional[str] = None, label: Optional[str] = None
) -> None:
    """Revoke an API token. Note that this cannot be undone.

    Exactly one of ``identifier`` and ``label`` should be provided.

    Parameters
    ---------
    identifier
        The identifier of the API token.
    label
        The label of the API token(s) to revoke.
    """
    with Cloud() as cloud:
        return cloud.revoke_api_token(identifier=identifier, label=label)


def revoke_all_api_tokens() -> None:
    """Revoke all API tokens. Note that this cannot be undone."""
    with Cloud() as cloud:
        return cloud.revoke_all_api_tokens()


def create_software_environment(
    name: str = None,
    *,
    account: Optional[str] = None,
    conda: Union[list, dict, str] = None,
    pip: Union[list, str] = None,
    container: str = None,
    log_output=sys.stdout,
    post_build: Union[list, str] = None,
    conda_env_name: str = None,
    backend_options: Optional[Dict] = None,
    private: bool = False,
    force_rebuild: bool = False,
    environ: Optional[Dict] = None,
) -> None:
    """Create a software environment

    Parameters
    ---------
    name
        Name of software environment. Name can't contain uppercase letters.
    account
        The account in which to create the software environment, if not given in the name.
    conda
        Specification for packages to install into the software environment using conda.
        Can be a list of packages, a dictionary, or a path to a conda environment YAML file.
    pip
        Packages to install into the software environment using pip.
        Can be a list of packages or a path to a pip requirements file.
    container
        Docker image to use for the software environment. Must be the name of a docker image
        on Docker hub. Defaults to ``coiled/default``.
    post_build
        List of commands or path to a local executable script to run after pip and conda packages
        have been installed.
    log_output
        Stream to output logs to. Defaults to ``sys.stdout``.
    conda_env_name
        Name of conda environment to install packages into. Note that this should *only* be used
        when specifying a non-default value for ``container`` *and* when the non-default Docker
        image used expects commands to run in a conda environment not named "coiled".
        Defaults to "coiled".
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` configuration value.
    private
        Whether this software environment is private or public. Defaults to ``False``
    force_rebuild
        By default, if an existing software environment with the same name and dependencies already
        exists, a rebuild is aborted. If this is set to True, those checks are skipped and the
        environment will be rebuilt. Defaults to ``False``
    environ
        Dictionary of environment variables.
    """
    with Cloud() as cloud:
        return cloud.create_software_environment(
            name=name,
            account=account,
            conda=conda,
            pip=pip,
            container=container,
            post_build=post_build,
            log_output=log_output,
            conda_env_name=conda_env_name,
            backend_options=backend_options,
            private=private,
            force_rebuild=force_rebuild,
            environ=environ,
        )


@list_docstring
def list_software_environments(account=None):
    with Cloud(account=account) as cloud:
        return cloud.list_software_environments(account=account)


@delete_docstring
def delete_software_environment(name):
    with Cloud() as cloud:
        return cloud.delete_software_environment(name=name)


def get_software_info(name: str, account: Optional[str] = None) -> dict:
    """Retrieve solved spec for a Coiled software environment

    Parameters
    ----------
    name
        Software environment name

    Returns
    -------
    results
        Coiled software environment information
    """
    with Cloud() as cloud:
        return cloud.get_software_info(name=name, account=account)


def create_cluster_configuration(
    name: str,
    software: str,
    *,
    account: str = None,
    worker_cpu: int = 1,
    worker_gpu: int = 0,
    worker_memory: str = "4 GiB",
    worker_class: str = "dask.distributed.Nanny",
    worker_options: dict = None,
    scheduler_cpu: int = 1,
    scheduler_memory: str = "4 GiB",
    scheduler_class: str = "dask.distributed.Scheduler",
    scheduler_options: dict = None,
    private: bool = False,
) -> None:
    """Create a cluster configuration

    Parameters
    ----------
    name
        Name of cluster configuration.
        Optionally prefixed with an account name like "myaccount/myname"
    software
        Identifier of the software environment to use, in the format (<account>/)<name>. If the software environment
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.

        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have an environment
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".

        The "name" portion of (<account>/)<name> can only contain ASCII letters, hyphens and underscores.
    account
        The account in which to create the cluster configuration, if not given in the name.
    worker_cpu
        Number of CPUs allocated for each worker. Defaults to 1.
    worker_gpu
        Number of GPUs allocated for each worker. Defaults to 0 (no GPU support). Note that this will _always_
        allocate GPU-enabled workers, so is expensive.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 4 GiB.
    worker_class
        Worker class to use. Defaults to "dask.distributed.Nanny".
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    scheduler_class
        Scheduler class to use. Defaults to "dask.distributed.Scheduler".
    scheduler_options
        Mapping with keyword arguments to pass to ``scheduler_class``. Defaults to ``{}``.
    private
        Whether this cluster configuration is private or public. Defaults to ``False``

    See Also
    --------
    dask.utils.parse_bytes
    """
    with Cloud() as cloud:
        return cloud.create_cluster_configuration(
            name=name,
            software=software,
            account=account,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            private=private,
        )


@list_docstring
def list_cluster_configurations(account=None):
    with Cloud() as cloud:
        return cloud.list_cluster_configurations(account=account)


@delete_docstring
def delete_cluster_configuration(name):
    with Cloud() as cloud:
        return cloud.delete_cluster_configuration(name=name)


def create_cluster(
    name: str = None,
    *,
    configuration: str,
    software: str = None,
    worker_cpu: int = None,
    worker_gpu: int = None,
    worker_memory: str = None,
    worker_class: str = None,
    worker_options: dict = None,
    scheduler_cpu: int = None,
    scheduler_memory: str = None,
    scheduler_class: str = None,
    scheduler_options: dict = None,
    account: str = None,
    workers: int = 0,
    backend_options: Optional[Dict] = None,
    environ: Optional[Dict] = None,
    log_output=sys.stdout,
) -> int:
    """Create a cluster
    Parameters
    ---------
    name
        Name of cluster.
    configuration
        Identifier of the cluster configuration to use, in the format (<account>/)<name>. If the configuration
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.
        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have a configuration
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".
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
        allocate GPU-enabled workers, so is expensive.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 8 GiB.
    worker_class
        Worker class to use. Defaults to "dask.distributed.Nanny".
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    scheduler_class
        Scheduler class to use. Defaults to "dask.distributed.Scheduler".
    scheduler_options
        Mapping with keyword arguments to pass to ``scheduler_class``. Defaults to ``{}``.
    account
        Name of the Coiled account to create the cluster in.
        If not provided, will default to ``Cloud.default_account``.
    workers
        Number of workers we to launch.
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` cofiguration value.
    environ
        Dictionary of environment variables.
    See Also
    --------
    coiled.Cluster
    """
    # TODO cleanup repetition of explaining a configuration identifier (see docstring for
    # creating software_environments)
    warnings.warn(
        "Please use coiled.Cluster() for creating clusters instead of coiled.create_cluster()."
        "coiled.Cluster() offers more control over the cluster you create and is the recommended approach."
    )
    with Cloud(account=account) as cloud:
        return cloud.create_cluster(
            name=name,
            configuration=configuration,
            software=software,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            account=account,
            workers=workers,
            backend_options=backend_options,
            environ=environ,
            log_output=log_output,
        )


@list_docstring
def list_clusters(account=None):
    with Cloud() as cloud:
        return cloud.list_clusters(account=account)


@delete_docstring
def delete_cluster(name: str, account: str = None):
    with Cloud() as cloud:
        cluster_id = cloud.get_cluster_by_name(name=name, account=account)
        if cluster_id is not None:
            return cloud.delete_cluster(cluster_id=cluster_id, account=account)


def cluster_logs(name: str, account: str = None) -> Logs:
    """Retrieve logs from a Coiled cluster.

    Parameters
    ----------
    name
        Cluster name

    account
        The account in which the cluster is running

    Returns
    -------
    logs
        The logs from the cluster.
    """
    with Cloud() as cloud:
        cluster_id = cloud.get_cluster_by_name(name=name, account=account)
        if cluster_id is not None:
            return cloud.cluster_logs(cluster_id=cluster_id, account=account)


@overload
def list_core_usage(json: Literal[True], account: str = None) -> dict:
    ...


@overload
def list_core_usage(json: Literal[False] = False, account: str = None) -> None:
    ...


def list_core_usage(json: bool = False, account: str = None) -> Union[dict, None]:
    """Get a list of used cores.

    Returns a table that shows the limit of cores that the user can use
    and a breakdown of the core usage split up between account, user and clusters.

    Parameters
    ----------
    account
        Name of the Coiled account to list core usage. If not provided,
        will use the coiled.account configuration value.
    json
        If set to ``True``, it will return this list in json format instead of
        a table.
    """
    with Cloud() as cloud:
        return cloud.list_core_usage(json=json, account=account)


def get_notifications(
    json: bool = False,
    account: str = None,
    limit: int = 100,
    level: Union[int, str] = logging.NOTSET,
) -> Union[List[dict], None]:
    """Get a list of all recent notifications.

    Parameters
    ----------
    account
        Name of the Coiled account to list notifications. If not provided,
        will use the coiled.account configuration value.
    json
        If set to ``True``, it will return this list in json format instead of
        a table.
    limit
        The max number of notifications to return.
    level
        A constant from the standard python logging library (e.g., ``logging.INFO``),
        or a string of one of the following: ``debug``, ``info``, ``warning``, ``error``,
        or ``critical``. This will be used to filter the returned notifications.
    """
    with Cloud() as cloud:
        return cloud.get_notifications(
            json=json, account=account, limit=limit, level=level
        )


@overload
def list_local_versions(json: Literal[False] = False) -> None:
    ...


@overload
def list_local_versions(json: Literal[True]) -> dict:
    ...


def list_local_versions(json: bool = False) -> Optional[dict]:
    """Get information about local versions.

    Returns the versions of Python, Coiled, Dask and Distributed that
    are installed locally. This information could be useful when
    troubleshooting issues.

    Parameters
    ----------
    json
        If set to ``True``, it will return this list in json format instead of a
        table.
    """
    with Cloud() as cloud:
        return cloud.list_local_versions(json=json)


def diagnostics(account: str = None) -> dict:
    """Run a diagnose check aimed to help support with any issues.

    This command will call others to dump information that could help
    in troubleshooting issues. This command will return a json that will
    make it easier for you to share with the Coiled support team if needed.

    Parameters
    ----------
    account
        Name of the Coiled account to list core usage. If not provided,
        will use the coiled.account configuration value.
    """
    console = rich_console()
    with console.status("Gathering diagnostics..."):
        with Cloud() as cloud:
            data = {}

            health_check = cloud.health_check()
            status = health_check.get("status", "Issues found")

            data["health_check"] = health_check
            console.print(f"Performing health check.... Status: {status}")
            time.sleep(0.5)

            console.print("Gathering information about local environment...")
            local_versions = cloud.list_local_versions(json=True)
            data["local_versions"] = local_versions
            time.sleep(0.5)

            configuration = dask.config.config
            configuration["coiled"]["token"] = "hidden"
            data["coiled_configuration"] = configuration
            time.sleep(0.5)

            console.print("Getting user information...")
            user_info = cloud.list_user_information()
            data["user_information"] = user_info
            time.sleep(0.5)

            usage = cloud.list_core_usage(json=True, account=account)
            data["core_usage"] = usage
            time.sleep(0.5)

            notifications = cloud.get_notifications(json=True, account=account)
            data["notifications"] = notifications

            return data


def list_user_information() -> dict:
    """List information about your user.

    This command will give you more information about your account,
    which teams you are part of and any limits that your account might
    have.
    """
    with Cloud() as cloud:
        cloud.list_user_information()
        return cloud.list_user_information()


def _upload_report(filename, private=False, account=None) -> dict:
    """Private method for uploading report to Coiled"""
    if not os.path.isfile(filename):
        raise ValueError("Report file does not exist.")

    statinfo = os.stat(filename)
    if statinfo.st_size >= 1048576 * 10:
        raise ValueError("Report file size greater than 10mb limit")

    # At this point Dask has generated a local file with the performance report contents
    with Cloud() as cloud:
        result = cloud.upload_performance_report(
            filename, filename=filename, private=private, account=account
        )
        return result


@experimental
@contextmanager
def performance_report(
    filename="dask-report.html",
    private=False,
    account=None,
) -> Generator[None, None, None]:
    """Generates a static performance report and saves it to Coiled Cloud

    This context manager lightly wraps Dask's performance_report. It generates a static performance
    report and uploads it to Coiled Cloud. After uploading, it prints out the url where the report is
    hosted. For a list of hosted performance reports, utilize coiled.list_performance_reports(). Note
    each user is limited to 5 hosted reports with each a maximum file size of 10mb.

    Parameters
    ----------

    filename
        The file name of the performance report file.
    private
        If set to ``True``, the uploaded performance report is only accessible to logged in Coiled users who
        are members of the current / default or specified account.
    account
        Associated the account which user wishes to upload to. If not specified, current / default
        account will be utilized.

    """

    # stacklevel= is newer kwarg after version check below
    try:
        report_kwargs = {"stacklevel": 3} if DISTRIBUTED_VERSION >= "2021.05.0" else {}
        with dask.distributed.performance_report(filename=filename, **report_kwargs):
            yield
    except Exception as ex:
        raise Exception(
            "Exception in coiled.performance_report() context"
        ).with_traceback(ex.__traceback__)
    finally:
        results = _upload_report(filename, private=private, account=account)
        console = Console()
        text = Text(
            f'Performance Report Available at: {results["url"]}',
            style=f"link {results['url']}",
        )
        console.print(text)


@experimental
def list_performance_reports(account=None) -> List[Dict]:
    """List performance reports stored on Coiled Cloud

    Returns a list of dicts that contain information about Coiled Cloud hosted performance reports

    Parameters
    ----------

    account
        Associated account for which the user wishes to get reports from. If not specified, current / default
        account will be utilized.

    """
    with Cloud() as cloud:
        result = cloud.list_performance_reports(account=account)
        return result


def _parse_gcp_creds(
    gcp_service_creds_dict: Optional[Dict], gcp_service_creds_file: Optional[str]
) -> Dict:
    if not any([gcp_service_creds_dict, gcp_service_creds_file]):
        raise GCPCredentialsParameterError(
            "Parameter 'gcp_service_creds_file' or 'gcp_service_creds_dict' must be supplied"
        )

    if gcp_service_creds_file:
        if not os.path.isfile(gcp_service_creds_file):
            raise GCPCredentialsError(
                "The parameter 'gcp_service_creds_file' must be a valid file"
            )
        try:
            with open(gcp_service_creds_file, "r") as json_file:
                creds = json.load(json_file)

                required_keys = [
                    "type",
                    "project_id",
                    "private_key_id",
                    "private_key",
                    "client_email",
                    "client_id",
                    "auth_uri",
                    "token_uri",
                    "auth_provider_x509_cert_url",
                    "client_x509_cert_url",
                ]
                missing_keys = [key for key in required_keys if key not in creds]
                if missing_keys:
                    raise GCPCredentialsError(
                        message=(
                            f"The supplied file '{gcp_service_creds_file}' is missing the keys: "
                            f"{', '.join(missing_keys)}"
                        )
                    )

                return creds
        except JSONDecodeError:
            raise GCPCredentialsError(
                f"The supplied file '{gcp_service_creds_file}' is not a valid JSON file."
            )
    if gcp_service_creds_dict and not gcp_service_creds_dict.get("project_id"):
        raise GCPCredentialsError(
            "Unable to find 'project_id' in 'gcp_service_creds_dict', make sure this key exists in the dictionary"
        )

    # Type checker doesn't know that this should no longer
    # be None.
    return cast(Dict, gcp_service_creds_dict)


@experimental
def set_backend_options(
    use_coiled_defaults: bool = False,
    account: str = None,
    backend: Literal["aws", "gcp"] = "aws",
    customer_hosted: bool = False,
    create_vpc: bool = False,
    firewall: Optional[Dict] = None,
    network: Optional[Dict] = None,
    aws_region: str = "us-east-1",
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    gcp_service_creds_file: str = None,
    gcp_service_creds_dict: dict = None,
    gcp_project_id: str = None,
    gcp_region: Optional[str] = None,
    gcp_zone: Optional[str] = None,
    zone: Optional[str] = None,
    registry_type: Literal["ecr", "docker_hub", "gar", "acr"] = "ecr",
    registry_namespace: str = None,
    registry_access_token: str = None,
    registry_uri: str = "docker.io",
    registry_username: str = None,
    log_output=sys.stdout,
    **kwargs,
):
    """Configure account level settings for cloud provider and container registry.

    This method configures account level backend settings for cloud providers, container registries,
    and setting up an account-level VPC for running clusters and other Coiled managed resources.


    Parameters
    ----------

    use_coiled_default
        Boolean to reset backend options to Coiled default settings which are for the AWS VM
        backend with default region of us-east-1.

    account
        Coiled account to configure if user has access. If not specified, current / default
        account will be utilized.

    backend_type
        Supported backends such as AWS VM (vm_aws) and GCP VM (vm_gcp).

    firewall
        Specification for your firewall/security group, this dictionary takes a list of ports and a cidr block value
        which will be used to configure your firewall/security group that Coiled creates when creating Clusters. This
        value can be used as {"ports" [22], "cidr": "0.0.0.0/0"}, you don't need to specify both if you don't wish.

    network
        Specification for your network/subnets, dictionary can take ID(s) for existing network and/or subnet(s).

    customer_hosted
        Set to True when setting up a backend that will be hosted in your own cloud provider. Note that supplying valid
        credentials for cloud provider is required for Coiled to manage the setup, configure and access policies for
        users of this account.

    create_vpc
        Deprecated; use ``customer_hosted`` instead.

    aws_region
        The region which Coiled cloud resources will be deployed to and where other resources
        such as the docker registry are located or where a specified VPC will be created.

    aws_access_key_id
        For AWS support backend, this argument is required to create or use an existing Coiled managed VPC.

    aws_secret_access_key
        For AWS support backend, this argument is required to create or use an existing Coiled managed VPC.

    use_scheduler_public_ip
        Determines if the client connects to the Dask scheduler using it's public or internal address.

    gcp_service_creds_file
        A string filepath to a Google Cloud Compute service account json credentials file used for creating and
        managing a Coiled VPC.

    gcp_service_creds_dict
        A dictionary of the contents of a Google Cloud Compute service account json credentials file used for
        creating a VPC to host Coiled Cloud related assets.

    gcp_project_id
        The Google Cloud Compute project id in which a VPC will be created to host Coiled Cloud related assets.

    gcp_region
        The Google Cloud Compute region name in which a VPC will be created.

    gcp_zone
        The Google Cloud Compute zone name in which clusters will be create (Zone should be <region>-<zone letter>)
        for example zone C for ``us-east1`` should be specified as ``us-east1-c``.
        Deprecated; ``zone`` will override this.

    zone
        Optional; used to specify zone to use for clusters (for either AWS or GCP).

    registry_type
        Custom software environments are stored in a docker container registry. By default, container images will be
        stored in AWS ECR. Users are able to store contains on a private registry by providing additional
        configuration registry_* arguments and specifying registry_type='docker_hub'. To use
        Google Artifact Registry, pass registry_type='gar', gcp_project_name, gcp_region_name,
        and one of gcp_service_creds_dict or gcp_service_creds_file.

    registry_uri
        The container registry URI. Defaults to docker.io. Only required if
        registry_type='docker_hub'.

    registry_username
        A registry username (should be lowercased). Only required if
        registry_type='docker_hub'.

    registry_namespace
        A namespace for storing the container images. Defaults to username if not specified. More information
        about docker namespaces can be found here: https://docs.docker.com/docker-hub/repos/#creating-repositories.
        Only required if registry_type='docker_hub'.

    registry_access_token
        A token to access registry images. More information about access tokens ca be found here:
        https://docs.docker.com/docker-hub/access-tokens/. Only required if registry_type='docker_hub'.

    """
    # TODO - see if way to add default in BE to avoid re-versioning of this
    backend_options = {
        "backend": "vm_aws",
        "options": {
            "aws_region_name": aws_region,
            "account_role": "",
            "credentials": {"aws_access_key_id": "", "aws_secret_access_key": ""},
            "firewall": firewall or {},
            "network": network or {},
            "zone": zone,
        },
        "registry": {"type": "ecr", "credentials": {}, "public_ecr": False},
    }

    # TODO Provide Backwards compatibility to old keywords remove once experimental is removed
    region = kwargs.get("region")
    if region:
        aws_region = region
    backend_type = kwargs.get("backend_type")
    if backend_type:
        backend = backend_type
    gcp_project_name = kwargs.get("gcp_project_name")
    if gcp_project_name:
        gcp_project_id = gcp_project_name
    gcp_region_name = kwargs.get("gcp_region_name")
    if gcp_region_name:
        gcp_region = gcp_region_name

    # override gcp_zone with zone, if set
    if zone and gcp_project_name:
        gcp_zone = zone

    output_msg = ""
    # Used to print warnings to the user
    console = Console()

    if backend not in SUPPORTED_BACKENDS:
        raise UnsupportedBackendError(
            f"Supplied backend: {backend} not in supported types: {SUPPORTED_BACKENDS}"
        )

    if create_vpc:
        # we don't always create VPC for customer hosted backend, so we should give
        # the parameter a more accurate name
        customer_hosted = create_vpc
        warning_message = Text(
            text=(
                "WARNING: The 'create_vpc' parameter is being deprecated in favor of "
                "'customer_hosted', which has same functionality. \n"
            ),
            style="yellow",
        )
        console.print(warning_message)

    if aws_access_key_id and aws_secret_access_key:
        # verify that these are vaild credentials
        verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    parsed_gcp_credentials: Optional[Dict] = None

    # Parse GCP region/zones or return default region/zone
    gcp_region, gcp_zone = parse_gcp_region_zone(region=gcp_region, zone=gcp_zone)
    if use_coiled_defaults is True:
        # use default options
        output_msg = "Successfully, set your backend options to Coiled Defaults."
        pass

    elif backend == "aws":
        if customer_hosted:
            backend_options["backend"] = "vm"
            backend_options["options"]["aws_region_name"] = aws_region
            if aws_access_key_id and aws_secret_access_key:
                backend_options["options"]["credentials"] = {
                    "aws_access_key": aws_access_key_id,
                    "aws_secret_key": aws_secret_access_key,
                }

                backend_options["options"]["provider_name"] = "aws"
                backend_options["options"]["type"] = "aws_cloudbridge_backend_options"
                output_msg = "Successfully, set your backend options to Coiled Customer Hosted on AWS VM."
            else:
                raise AWSCredentialsParameterError(
                    "Creating an AWS VPC requires params: aws_access_key_id and aws_secret_access_key."
                )
        else:
            if aws_secret_access_key and aws_access_key_id:
                warning_message = Text(
                    text=(
                        "WARNING: Credentials provided without using 'customer_hosted=True', please use this "
                        "parameter if you want to use Coiled on your AWS account. \n"
                    ),
                    style="yellow",
                )
                console.print(warning_message)
            backend_options["backend"] = "vm_aws"
            backend_options["options"]["aws_region_name"] = aws_region
            output_msg = (
                "Successfully, set your backend options to Coiled Hosted on AWS VM."
            )
    elif backend == "gcp":
        if customer_hosted:
            parsed_gcp_credentials = _parse_gcp_creds(
                gcp_service_creds_dict=gcp_service_creds_dict,
                gcp_service_creds_file=gcp_service_creds_file,
            )
            if not gcp_project_id:
                gcp_project_id = parsed_gcp_credentials.get("project_id", "")
            backend_options["options"][
                "gcp_service_creds_dict"
            ] = parsed_gcp_credentials

            backend_options["backend"] = "vm"

            backend_options["options"]["provider_name"] = "gcp"
            backend_options["options"]["type"] = "gcp_cloudbridge_backend_options"

            backend_options["options"]["gcp_project_name"] = gcp_project_id
            backend_options["options"]["gcp_region_name"] = gcp_region
            backend_options["options"]["gcp_zone_name"] = gcp_zone

            output_msg = "Successfully set your backend options to Coiled Customer Hosted on GCP VM."

        else:
            if gcp_service_creds_dict or gcp_service_creds_file:
                warning_message = Text(
                    text=(
                        "WARNING: Credentials provided without using 'customer_hosted=True', please use this "
                        "parameter if you want to use Coiled on your GCP account. \n"
                    ),
                    style="yellow",
                )
                console.print(warning_message)
            backend_options["backend"] = "vm_gcp"
            if gcp_region:
                backend_options["options"] = {
                    "gcp_region_name": gcp_region,
                    "gcp_zone_name": gcp_zone,
                }
            else:
                backend_options["options"] = {}

            output_msg = (
                "Successfully set your backend options to Coiled Hosted on GCP VM."
            )

    ### container registry
    if use_coiled_defaults is True:
        pass
    elif registry_type == "ecr":
        # TODO add aws credentials in here for VPCs
        backend_options["registry"]["region"] = aws_region
        if aws_access_key_id and aws_secret_access_key:
            backend_options["registry"]["credentials"][
                "aws_access_key_id"
            ] = aws_access_key_id
            backend_options["registry"]["credentials"][
                "aws_secret_access_key"
            ] = aws_secret_access_key

    elif registry_type == "docker_hub":
        registry = {
            "account": registry_namespace or registry_username,
            "password": registry_access_token,
            "type": registry_type,
            "uri": registry_uri,
            "username": registry_username,
        }

        # any missing values
        empty_registry_values = [f"registry_{k}" for k, v in registry.items() if not v]
        if any(empty_registry_values):
            raise RegistryParameterError(
                f"For setting your registry credentials, these fields cannot be empty: {empty_registry_values}"
            )

        # docker username /// account name cannot be uppercase
        if (
            registry_username
            and any(ele.isupper() for ele in registry_username) is True
        ):
            raise RegistryParameterError(
                "Your dockerhub [registry_username] must be lowercase"
            )

        backend_options["registry"] = registry
    elif registry_type == "gar":
        if parsed_gcp_credentials is None:
            parsed_gcp_credentials = _parse_gcp_creds(
                gcp_service_creds_dict=gcp_service_creds_dict,
                gcp_service_creds_file=gcp_service_creds_file,
            )
        if not gcp_project_id:
            gcp_project_id = parsed_gcp_credentials.get("project_id", "")
        gar_required_kwargs = {
            "gcp_region_name": gcp_region,
            "gcp_project_name": gcp_project_id,
            "one of gcp_service_creds_dict / gcp_service_creds_file": parsed_gcp_credentials,
        }
        missing_gar_kwargs = ", ".join(
            [kw for kw, val in gar_required_kwargs.items() if not val]
        )
        if missing_gar_kwargs:
            raise RegistryParameterError(
                f"Missing required args for Google Artifact Registry: {missing_gar_kwargs}"
            )
        backend_options["registry"] = {
            "type": registry_type,
            "location": gcp_region,
            "project_id": gcp_project_id,
            "credentials": parsed_gcp_credentials,
        }

    with Cloud(account=account) as cloud:
        account_options_url = cloud.set_backend_options(
            backend_options,
            account=account,
            log_output=log_output,
        )

        text = Text()
        text.append(output_msg, style="green")
        text.append("\n\n")
        text.append(
            f"Please confirm your account backend options here: {account_options_url}",
            style=f"link {account_options_url}",
        )
        console.print(text)


@overload
def list_instance_types(
    json: Literal[True],
) -> dict[str, VmType]:
    ...


@overload
def list_instance_types(
    json: Literal[False],
) -> None:
    ...


def list_instance_types(
    json: bool = False,
    backend: Optional[str] = None,
    min_cores: int = 0,
    min_gpus: int = 0,
    min_memory: int = 0,
) -> Union[Awaitable[dict[str, VmType]] | dict[str, VmType] | Awaitable[None] | None]:
    """List allowed instance types for the cloud provider configured on your account.

    Parameters
    ----------
    backend:
        Relevant cloud provider (aws or gcp) to get a list of allowed instance types. If
        not provided the list will show the instances for your account cloud provider.
    min_cores
        Filter results on minimum number of required cores
    min_gpus
        Filter results on minimum number of required GPUs
    min_memory
        Filter results on minimum amount of memory in megabytes
    json
        If set to ``True``, it will return this list in json format instead of a table.
    """
    with Cloud() as cloud:
        return cloud.list_instance_types(
            backend=backend,
            json=json,
            min_cores=min_cores,
            min_gpus=min_gpus,
            min_memory=min_memory,
        )


@overload
def list_gpu_types(json: Literal[False] = False) -> None:
    ...


@overload
def list_gpu_types(json: Literal[True] = True) -> Dict:
    ...


def list_gpu_types(json: bool = False) -> Optional[Dict]:
    """List allowed GPU Types.

    For AWS the GPU types are tied to the instance type, but for GCP you can
    add different GPU types to GPU enabled instances. Please refer to
    :doc:`tutorials/select_gpu_type` for more information.

    Parameters
    ----------
    json
        if set to ``True``, it will return this list in json format instead of a table.

    """
    with Cloud() as cloud:
        return cloud.list_gpu_types(json=json)


if use_declarative():
    Cloud.create_cluster = Cloud._create_cluster_declarative_synced  # type: ignore
