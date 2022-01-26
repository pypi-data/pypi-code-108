import os.path
from PySide2 import QtWidgets, QtCore
from propsettings.setting import Setting
from propsettings.setting_types.path_setting_type import Path
from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer


class PathSettingDrawer(SettingDrawer):

    def __init__(self, path: Path, setting_owner, setting: Setting):
        super(PathSettingDrawer, self).__init__(setting_owner, setting)
        self._path = path

        self._path_widget = PathWidget(self, path)
        self._path_widget.signal_path_changed.connect(self._on_path_changed)
        self._path_widget.set_value(self._get_value())

    def get_widget(self):
        return self._path_widget

    def _on_path_changed(self, new_path: str):
        self._set_value(new_path)


class PathWidget(QtWidgets.QWidget):
    signal_path_changed = QtCore.Signal(str)

    def __init__(self, drawer: PathSettingDrawer, path: Path, *args, **kwargs):
        super(PathWidget, self).__init__(*args, **kwargs)
        self._drawer = drawer
        self._path = path
        self._current_path: str = ""

        self._layout = QtWidgets.QHBoxLayout()
        self.setLayout(self._layout)

        self._edit = QtWidgets.QLineEdit()
        self._edit.editingFinished.connect(self._on_text_edited)

        self._button = QtWidgets.QPushButton()
        self._button.clicked.connect(self._on_button_clicked)
        self._button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))

        self._layout.addWidget(self._edit)
        self._layout.addWidget(self._button)

    def set_value(self, path: str):
        self._set_value(path, False)

    def _set_value(self, path: str, notify: bool) -> bool:
        exists = os.path.exists(path)
        _, ext = os.path.splitext(path)
        ext = ext[1:]  # remove dot
        valid_extension = ext in self._path.extensions
        is_folder = self._path.is_folder
        valid_type = (
                is_folder and os.path.isdir(path) or
                not is_folder and os.path.isfile(path)
        )
        if exists and (is_folder or valid_extension) and valid_type:
            self._edit.setText(path)
            self._current_path = path
            if notify:
                self.signal_path_changed.emit(path)
            return True

        return False

    @QtCore.Slot()
    def _on_text_edited(self):
        path = self._edit.text()
        success = self._set_value(path, True)
        if not success:
            self._edit.setText(self._current_path)
            # TODO show error message

    @QtCore.Slot()
    def _on_button_clicked(self):
        workdir = os.getcwd()
        if self._path.is_folder:
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                self.tr("Select folder"),
                workdir,
            )
        else:
            extensions_filter = ", ".join([f'*.{ext}' for ext in self._path.extensions])
            file_filter = self.tr(f"Files ({extensions_filter});;All files (*)")
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                self.tr("Select file"),
                workdir,
                file_filter
            )
        if path != "":
            self._set_value(path, True)


if __name__ == '__main__':
    import sys
    from PySide2.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = PathWidget(None, Path(False, [".jpg", "png"]))
    widget.show()

    sys.exit(app.exec_())