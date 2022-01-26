"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any
from pathlib import Path
from threading import Event

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BlockingEvent(Event):

    def __init__(self) -> None:
        super().__init__()
        self.set()

    def __enter__(self) -> None:
        self.clear()

    def __exit__(self, exception_type: type = None, exception_value: BaseException = None, traceback: Any = None) -> None:
        self.set()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
