"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QMenu, QWidget, QMenuBar, QMessageBox, QApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseMenuBar(QMenuBar):

    def __init__(self, parent: Optional[QWidget] = None, auto_connect_standard_actions: bool = True) -> None:
        super().__init__(parent=parent)
        self.auto_connect_standard_actions = auto_connect_standard_actions
        self.about_dialog: QMessageBox = None
        self.setup_menus()

    def setup_default_menus(self) -> None:
        self.file_menu = self.add_new_menu("File")
        self.exit_action = self.add_new_action(self.file_menu, "Exit")

        self.edit_menu = self.add_new_menu("Edit")

        self.view_menu = self.add_new_menu("View")
        self.windows_menu = self.add_new_menu("Windows", parent_menu=self.view_menu)

        self.settings_menu = self.add_new_menu("Settings")

        self.help_menu = self.add_new_menu("Help")
        self.help_menu.addSeparator()
        self.help_separator = self.help_menu.addSeparator()
        self.add_action(self.help_menu, self.help_separator)
        self.about_action = self.add_new_action(self.help_menu, "About")
        self.about_qt_action = self.add_new_action(self.help_menu, "About Qt®")

        if self.auto_connect_standard_actions is True:
            self.about_action.triggered.connect(self.app.show_about)
            self.about_qt_action.triggered.connect(self.app.show_about_qt)
            if self.parent() is not None:
                self.exit_action.triggered.connect(self.parent().close)

    @property
    def app(self) -> QApplication:
        return QApplication.instance()

    def setup_menus(self) -> None:
        self.setup_default_menus()

    def add_new_menu(self, menu_title: str, icon: QIcon = None, add_before=None, parent_menu: QMenu = None) -> QMenu:
        menu = QMenu(self)
        menu.setTitle(menu_title)
        if icon is not None:
            menu.setIcon(icon)
        target_menu = parent_menu or self
        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            target_menu.insertMenu(add_before, menu)
        else:
            target_menu.addMenu(menu)
        return menu

    def add_new_action(self, menu: QMenu, action_name: str, action_title: str = None, add_before=None, action_klass: type[QAction] = QAction):
        action_title = action_title or action_name
        action_name = action_name.casefold().replace(' ', '_')
        action = action_klass(parent=menu)

        action.setText(action_title)
        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            menu.insertAction(add_before, action)
        else:
            menu.addAction(action)

        if not hasattr(menu, action_name + '_action'):
            setattr(menu, action_name + '_action', action)
        return action

    def add_action(self, menu: QMenu, action: QAction, add_before=None):

        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            menu.insertAction(add_before, action)
        else:
            menu.addAction(action)

        if not hasattr(menu, action.text() + '_action'):
            setattr(menu, action.text() + '_action', action)
        return action


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
