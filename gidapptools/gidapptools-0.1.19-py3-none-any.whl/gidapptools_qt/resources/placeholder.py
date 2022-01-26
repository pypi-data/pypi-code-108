"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QIcon, QPixmap

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.data.images import PLACEHOLDER_IMAGE, StoredImage

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidQtPlaceholderImage:

    def __init__(self, stored_image: StoredImage) -> None:
        self.stored_image = stored_image
        self._pixmap: QPixmap = None
        self._icon = QIcon = None

    @property
    def pixmap(self) -> QPixmap:
        if self._pixmap is None:
            self._pixmap = QPixmap(self.stored_image.path)
        return self._pixmap

    @property
    def icon(self) -> QIcon:
        if self._icon is None:
            self._icon = QIcon(self.pixmap)
        return self._icon


QT_PLACEHOLDER_IMAGE = GidQtPlaceholderImage(PLACEHOLDER_IMAGE)

# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
