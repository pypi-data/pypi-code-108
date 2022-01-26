"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Hashable, Optional
from pathlib import Path
from threading import Lock

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_signal.signal_registry import signal_registry
from gidapptools.gid_signal.signals.basic_signal import GidSignal

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gid_signal.signals.abstract_signal import AbstractSignal

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

GET_SIGNAL_LOCK = Lock()


def get_signal(key: Hashable, klass: Optional["AbstractSignal"] = None) -> "AbstractSignal":
    klass = GidSignal if klass is None else klass
    with GET_SIGNAL_LOCK:
        signal = signal_registry.get(key, None)
        if signal is None:
            signal = klass(key=key)
            signal_registry.register(signal)

    return signal


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
