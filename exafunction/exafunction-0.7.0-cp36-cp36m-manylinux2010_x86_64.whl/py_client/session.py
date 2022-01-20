# Copyright Exafunction, Inc.

from dataclasses import dataclass
import inspect
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

import exa._C as _C
from exa.common_pb.common_pb2 import ValueMetadata
from exa.py_client.module import Module
from exa.py_client.profiler import Profiler
from exa.py_value.value import Value
from exa.py_value.value import ValueCompressionType


@dataclass
class ModuleContextSpec:
    """Specification for a single module context"""

    module_tag: Optional[str] = None
    """The module tag. Should be left empty if module hash is specified."""
    module_hash: Optional[str] = None
    """The module hash. Should be left empty if module tag is specified."""
    cpu_memory_limit_mb: int = 0
    """The CPU memory limit for the module context in MiB. The interpretation of this is module-dependent."""
    gpu_memory_limit_mb: int = 0
    """The GPU memory limit for the module context in MiB. The interpretation of this is module-dependent."""
    ignore_exec_serialize: bool = False
    """
    If set to true, we always run modules in this module context without
    serializing with other "RunMethod" calls even if serialize_all is set to
    true in the config file.
    """


@dataclass
class PlacementGroupSpec:
    """Specification for a placement group.

    A placement group contains one or more module contexts that will be placed on the same runner.
    """

    module_contexts: List[ModuleContextSpec]
    """List of module contexts within this placement group"""

    value_pool_size: int = 100 * 1024 * 1024
    """Remote memory pool size (default is 100 MiB)"""

    runner_fraction: float = 0.1
    """Estimated fraction of a runner that will be consumed by this placement
    group in terms of compute resources. This is used by the autoscaler as
    a hint for how many sessions can be placed on a single runner for this
    placement group."""

    constraint_config: Optional[Dict[str, str]] = None
    """Constraint configuration used to constraint runner (i.e. where it runs,
    reousrces used). These configurations can be used to override the default
    service config map."""

    load_balancing_enabled: bool = False
    """If set to true, load balancing is enabled. The load from each client
    on this placement group will be distributed evenly across multiple runners.
    Note that the scheduler must also have load balancing enabled in the config
    map, or else this setting is ignored."""

    autoscaling_enabled: bool = False
    """If set to true, autoscaling is enabled. The system will measure the
    actual load from each client on this placement group and adjust the number
    of clients per runner accordingly. Note that the scheduler must also have
    autoscaling enabled in the config map, or else this setting is ignored."""

    max_cpu_pool_size: int = 0
    """If this is set, defines the total CPU memory pool size for the placement group.
    Otherwise, the value will default to
    `ceil(value_pool_size / runner_fraction)`. It must be the case that
    `max_cpu_pool_size >= max_gpu_pool_size >= value_pool_size`."""

    max_gpu_pool_size: int = 0
    """If this is set, defines the total GPU memory pool size for the placement group.
    Otherwise, the value will default to
    `ceil(value_pool_size / runner_fraction)`. It must be the case that
    `max_cpu_pool_size >= max_gpu_pool_size >= value_pool_size`."""

    default_compression_type: ValueCompressionType = ValueCompressionType.UNCOMPRESSED
    """Default compression type for all values being pushed to the placement group.
    If this value is set to something other than UNCOMPRESSED, it will overwrite the
    session's defualt compression type."""


# Hack to override inspect.getfile to work in IPython
def new_getfile(object, _old_getfile=inspect.getfile):
    if not inspect.isclass(object):
        return _old_getfile(object)

    # Lookup by parent module (as in current inspect)
    if hasattr(object, "__module__"):
        object_ = sys.modules.get(object.__module__)
        if hasattr(object_, "__file__"):
            return object_.__file__

    # If parent module is __main__, lookup by methods (NEW)
    for name, member in inspect.getmembers(object):
        if (
            inspect.isfunction(member)
            and object.__qualname__ + "." + member.__name__ == member.__qualname__
        ):
            return inspect.getfile(member)
    else:
        raise TypeError("Source for {!r} not found".format(object))


inspect.getfile = new_getfile


class Session:
    """The Session object manages all Exafunction resources for a given session."""

    def __init__(
        self,
        scheduler_address: str,
        external_scheduler: bool = False,
        placement_groups: Dict[str, PlacementGroupSpec] = {},
        disable_fault_tolerance: bool = False,
        profile_log_file_path: str = "",
        local_pool_size: int = 2 * 1024 * 1024 * 1024,
        pin_local_pool: bool = False,
        default_compression_type: ValueCompressionType = ValueCompressionType.UNCOMPRESSED,
        colocated_with_runner: bool = False,
        tmp_dir: str = "/tmp/exafunction/session",
    ):
        """
        Creates an Exafunction session.

        :param scheduler_address: Exafunction scheduler address (eg. "scheduler-service:1234").
        :param external_scheduler: Set to true if client is not running in the same Kubernetes cluster as the service.
        :param placement_groups: The placement groups required by this session.
        :param disable_fault_tolerance: Whether to run with fault tolerance.
        :param profile_log_path: Optional path to log profiling stats.
        :param local_pool_size: Maximum allocation size for local values.
        :param pin_local_pool: Whether to pin the memory (mainly useful for Cuda applications)
        :param default_compression_type: Default compression used for all values sent from client.
        :param colocated_with_runner: Specifies whether runner and client are colocated and can pass data over shared memory.
        :param tmp_dir: Temporary directory for session data.
        """
        if not isinstance(default_compression_type, ValueCompressionType):
            raise TypeError(
                "default_compression_type must be of type ValueCompressionType"
            )
        self._c = _C.Session(
            scheduler_address,
            external_scheduler,
            placement_groups,
            disable_fault_tolerance,
            profile_log_file_path,
            local_pool_size,
            pin_local_pool,
            int(default_compression_type),
            colocated_with_runner,
            tmp_dir,
        )

    def close(self):
        """Closes the session. Using the context manager interface is preferred."""
        self._c = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def _check_closed(self):
        if self._c is None:
            raise ValueError("Session is closed")

    def session_id(self) -> int:
        """
        Returns the session id.

        :return: The session id.
        """
        self._check_closed()
        return self._c.session_id()

    def new_module(self, module_tag: str, config: Dict[str, bytes] = {}) -> Module:
        """
        Creates a new instance of a module from a module tag.

        :param module_tag: The module tag.
        :param config: The module configuration dictionary.
        :return: The created module instance.
        """
        self._check_closed()
        return Module(self._c.new_module(module_tag, config))

    def new_module_from_hash(
        self, module_hash: str, config: Dict[str, bytes] = {}
    ) -> Module:
        """
        Creates a new instance of a module from a module hash.

        :param module_hash: The module hash.
        :param config: The module configuration dictionary.
        :return: The created module instance.
        """
        self._check_closed()
        return Module(self._c.new_module_from_hash(module_hash, config))

    def new_module_from_cls(self, module_cls, config: Dict[str, bytes] = {}):
        """
        Creates a new instance of a module from a Python class.

        Note that ``SerializedPythonModule`` must be included in the session's
        placement groups to use this function.

        :param module_cls: The module class. Must derive from exa.BaseModule.
        :param config: The module configuration dictionary.
        :return: The created module instance.
        """
        config = config.copy()
        if "_py_module_cls" in config:
            raise ValueError(
                "Config for SerializedPythonModule may not contain key _py_module_cls"
            )
        if "_py_module_name" in config:
            raise ValueError(
                "Config for SerializedPythonModule may not contain key _py_module_name"
            )
        config["_py_module_cls"] = inspect.getsource(module_cls).encode()
        config["_py_module_name"] = module_cls.__name__.encode()
        return self.new_module("SerializedPythonModule", config)

    def _allocate_value(self, metadata: ValueMetadata):
        ser_metadata = b""
        if metadata is not None:
            ser_metadata = metadata.SerializeToString()
        return Value(self._c.allocate_value(ser_metadata))

    def allocate_bytes(self, size: int) -> Value:
        """
        Creates an empty value representing a byte array.

        These values are mapped to Exafunction Bytes values.

        :param size: The size of the byte array
        :return: The created value.
        """
        self._check_closed()
        metadata = ValueMetadata()
        metadata.size = size
        metadata.bytes.SetInParent()
        return self._allocate_value(metadata)

    def from_bytes(self, val: bytes) -> Value:
        """
        Creates a new Exafunction value by copying an existing byte array.

        These values are mapped to Exafunction Bytes values.

        :param val: The byte array
        :return: The created value.
        """
        self._check_closed()
        v = self.allocate_bytes(len(val))
        v.set_bytes(val)
        return v

    def _allocate_numpy(
        self,
        dtype: np.dtype,
        shape: Sequence[int],
    ) -> Value:
        """
        Creates an empty Exafunction value representing a NumPy array.

        These values are mapped to Exafunction Tensor values.

        :param dtype: The array datatype
        :param shape: The shape of the array
        :return: The created value.
        """
        metadata = Value._get_tensor_metadata(dtype, shape)
        v = self._allocate_value(metadata)
        return v

    def from_numpy(self, val: np.ndarray) -> Value:
        """
        Creates an empty Exafunction value by copying an existing NumPy array.

        These values are mapped to Exafunction Tensor values.

        :param val: The byte array
        :return: The created value.
        """
        self._check_closed()
        v = self._allocate_numpy(val.dtype, val.shape)
        v.numpy()[:] = val
        return v

    def start_profiling(self):
        """
        Creates a new profiler.

        :return: The created profiler.
        """
        return Profiler(self._c.start_profiling())

    def _enable_glog_stacktrace(self):
        self._check_closed()
        self._c._enable_glog_stacktrace()
