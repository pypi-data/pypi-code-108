"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import TYPE_CHECKING, Union, Optional
from pathlib import Path
from weakref import WeakSet

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QIcon, QImage, QPixmap, QGuiApplication
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QApplication, QSystemTrayIcon

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gidapptools_qt.resources.placeholder import QT_PLACEHOLDER_IMAGE

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.resources.resources_helper import PixmapResourceItem

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidQtApplication(QApplication):

    def __init__(self,
                 argvs: list[str] = None,
                 icon: Union["PixmapResourceItem", QPixmap, QImage, str, QIcon] = None):
        argvs = argvs or sys.argv
        super().__init__(self.argv_hook(argvs))
        self.main_window: QMainWindow = None
        self.sys_tray: QSystemTrayIcon = None
        self.icon = self._icon_conversion(icon)
        self.extra_windows = WeakSet()

    @classmethod
    def with_pre_flags(cls,
                       argvs: list[str] = None,
                       icon: Union["PixmapResourceItem", QPixmap, QImage, str, QIcon] = None,
                       pre_flags: dict[Qt.ApplicationAttribute:bool] = None,
                       desktop_settings_aware: bool = True):
        argvs = argvs or sys.argv
        QGuiApplication.setDesktopSettingsAware(desktop_settings_aware)
        for flag, value in pre_flags.items():
            cls.setAttribute(flag, value)
        return cls(argvs=argvs, icon=icon)

    def setup(self) -> "GidQtApplication":
        self.setWindowIcon(self.icon)
        return self

    def argv_hook(self, argvs: list[str]) -> list[str]:
        return argvs

    @staticmethod
    def _icon_conversion(icon: Union["PixmapResourceItem", QPixmap, QImage, str, QIcon] = None) -> Optional[QIcon]:
        if icon is None:
            return QT_PLACEHOLDER_IMAGE.icon

        if isinstance(icon, QIcon):
            return icon

        if isinstance(icon, (QPixmap, QImage, str)):
            return QIcon(icon)

        return icon.get_as_icon()

    def show_about_qt(self) -> None:
        self.aboutQt()

    def _get_about_text(self) -> str:
        text_parts = {"Name": self.applicationDisplayName(),
                      "Author": self.organizationName(),
                      "Link": f'<a href="{self.organizationDomain()}">{self.organizationDomain()}</a>',
                      "Version": self.applicationVersion()}

        return '<br>'.join(f"<b>{k:<20}:</b>{v:>50}" for k, v in text_parts.items())

    def show_about(self) -> None:
        title = f"About {self.applicationDisplayName()}"
        text = self._get_about_text()
        QMessageBox.about(self.main_window, title, text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.applicationDisplayName()!r})"


# region[Main_Exec]
if __name__ == '__main__':
    app = GidQtApplication(sys.argv)
    m = QMainWindow()
    m.show()
    app.exec_()

# endregion[Main_Exec]
