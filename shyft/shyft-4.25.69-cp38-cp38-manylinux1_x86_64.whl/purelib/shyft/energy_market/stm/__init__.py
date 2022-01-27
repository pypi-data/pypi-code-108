from ...utilities import environ_util
from typing import Union
from ..core import ModelInfo, run_state
from ..core import _core  # need to pull in dependent base-types
from ._stm import *

# backward compatible names after renaming
Aggregate=Unit
AggregateList=UnitList
WaterRoute=Waterway
PowerStation=PowerPlant
HydroPowerSystem.create_aggregate=HydroPowerSystem.create_unit
HydroPowerSystem.create_power_station=HydroPowerSystem.create_power_plant
HydroPowerSystem.create_water_route=HydroPowerSystem.create_waterway
# end backward compat section

# Optional Shop integration
# Set Shop API specific environment variable ICC_COMMAND_PATH,
# value pointing to the shared library path where the solver libraries
# and license file should be located.
# Note: Needed by DStmServer.do_optimize, as well as subpackage shop.
environ_util.set_environment('ICC_COMMAND_PATH', environ_util.lib_path)


class ReadAccess:
    """
    Context manager for read-only operation with a SharedMutex
    """
    def __init__(self, mtx: SharedMutex):
        self.mtx = mtx

    def __enter__(self):
        self.read_lock = ReadLock(self.mtx)
        return self.read_lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.read_lock.unlock()


class WriteAccess:
    """
    Context manager for exclusive right to a mutex.
    """
    def __init__(self, rl: Union[UpgradableLock, SharedMutex]):
        self.rl = rl

    def __enter__(self):
        if isinstance(self.rl, UpgradableLock):
            self.lock = UpgradeLock(self.rl)
        elif isinstance(self.rl, SharedMutex):
            self.lock = WriteLock(self.rl)
        else:
            raise RuntimeError(f"Unable to create write lock for input to WriteAccess")
        return self.lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.lock


class UpgradableAccess:
    """
    Context manager for shared-access to a mutex. Can then later be upgraded to exclusive access rights.
    """
    def __init__(self, mtx: SharedMutex):
        self.mtx = mtx

    def __enter__(self):
        self.lock = UpgradableLock(self.mtx)
        return self.lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.unlock()

__all__ = [
    "UpgradableAccess",
    "WriteAccess",
    "ReadAccess",
    "WriteLock",
    "ReadLock",
    "UpgradableLock",
    "SharedMutex",
    "HydroPowerSystem",
    "StmSystem",
    "MarketArea",
    "StmSystemContext",
    "ModelState",
    "ModelState",
    "Unit",
    "Reservoir",
    "PowerPlant",
    "Gate",
    "UnitGroup",
    "t_xy",
    "DStmClient", "DStmServer",
    "HpsClient", "HpsServer",
    "StmClient", "StmServer",
    "StmTaskServer", "StmTaskClient"
]