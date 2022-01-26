"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any, Union, Callable, Iterable, Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtCore import Qt, QAbstractTableModel

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

PYSIDE_INDEX_TYPE = Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex]


class BasicTableModel(QAbstractTableModel):

    def __init__(self, parent: Optional[PySide6.QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)
        self.data_dispatch: dict[Qt.ItemDataRole:Callable[[PYSIDE_INDEX_TYPE], Any]] = {}
        self.header_dispatch: dict[Qt.ItemDataRole:Callable[[int, Qt.Orientation], Any]] = {}
        self.content: Iterable[object] = None

    def data(self, index: PYSIDE_INDEX_TYPE, role: int = ...) -> Any:
        try:
            return self.data_dispatch[role](index)
        except KeyError:
            pass

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        try:
            return self.header_dispatch[role](section, orientation)
        except KeyError:
            pass

    def rowCount(self, parent: PYSIDE_INDEX_TYPE = None) -> int:
        if self.content is None:
            return 0
        return len(self.content)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
