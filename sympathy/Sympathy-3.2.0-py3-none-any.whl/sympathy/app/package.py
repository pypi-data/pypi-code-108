# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os
import platform
import json
import re
import tempfile
import pkg_resources
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui
from sympathy.utils import pip_util
from . import version
from . import settings
from . settings import Keys as setkeys
from sympathy.platform.hooks import pip_install_options
from sympathy.version import package_name
from . tasks.task_worker2 import datalines


class Python:
    executable = sys.executable
    version = platform.python_version()
    architecture = platform.architecture()[0]
    packages = []

    @classmethod
    def to_dict(cls, include_python):
        # executable is intentionally omitted
        # Sympathy version is added here for to simplify
        res = {
            'python_version': '',
            'python_architecture': '',
            'sympathy_version': version.version,
        }
        if include_python:
            res['python_version'] = cls.version
            res['python_architecture'] = cls.architecture

        return res

    @classmethod
    def to_dict_from_settings(cls):
        instance = settings.instance()
        return cls.to_dict(
            include_python=instance[setkeys.collect_include_python])


class System:
    system = platform.system()
    machine = platform.machine()
    release = platform.release()
    version = platform.version()
    processor = platform.processor()

    @classmethod
    def to_dict(cls, include_system):
        res = {
            'system': '',
            'machine': '',
            'system_release': '',
            'system_version': '',
            'processor': '',
        }
        if include_system:
            res = {
                'system': cls.system,
                'machine': cls.machine,
                'system_release': cls.release,
                'system_version': cls.version,
                'processor': cls.processor,
            }
        return res

    @classmethod
    def to_dict_from_settings(cls):
        instance = settings.instance()
        return cls.to_dict(
            include_system=instance[setkeys.collect_include_system])


class Collect:

    @classmethod
    def to_dict(cls, include_python, include_system, include_packages):
        # executable is intentionally omitted
        # Sympathy version is added here for to simplify
        python_packages = {}

        if include_packages:
            python_packages = cls.packages()

        return {
            'python': Python.to_dict(include_python),
            'python_packages': python_packages,
            'system': System.to_dict(include_system),
        }

    @classmethod
    def to_dict_from_settings(cls):
        instance = settings.instance()
        return cls.to_dict(
            include_python=instance[
                setkeys.collect_include_python],
            include_system=instance[
                setkeys.collect_include_system],
            include_packages=instance[
                setkeys.collect_include_packages])

    @classmethod
    def pretty_dict(cls, data):
        """
        Used to show detailed data for sending issues.
        Moves sympathy_version to version under sympathy.
        Shortens names of keys for readability.
        """
        def remove_prefix(data, prefix):
            data = dict(data)
            for key in list(data):
                if key.startswith(prefix):
                    value = data.pop(key)
                    new_key = key[len(prefix):]
                    data[new_key] = value
            return data

        def pretty_data(data):
            data = dict(data)
            python_dict = data['python']
            system_dict = data['system']
            sympathy_version = python_dict.pop('sympathy_version')

            data['python'] = remove_prefix(python_dict, 'python_')
            data['system'] = remove_prefix(system_dict, 'system_')
            data['sympathy'] = {'version': sympathy_version}
            data['packages'] = data.pop('python_packages')
            return data

        return pretty_data(data)

    @classmethod
    def packages(cls):
        # Use common utility from pip util with shared global store.
        required_file = os.path.join(
            settings.instance()['install_folder'], 'Package', 'requires.txt')
        required = pip_util.requirements(required_file).keys()
        installed = pip_util.freeze()
        return {k: v for k, v in installed.items() if k in required}


class TextDialog(QtWidgets.QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        text_edit = QtWidgets.QTextEdit()
        text_edit.setPlainText(text)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(text_edit)
        self.setLayout(layout)
        self.setMinimumWidth(400)


class JsonDialog(TextDialog):
    def __init__(self, data, parent=None):
        text = json.dumps(
            data,
            indent=4,
            sort_keys=True)
        super().__init__(text, parent=parent)


_package_name_re = re.compile('^[0-9a-z-_]+$', re.IGNORECASE)
_package_ver_re = re.compile('^[<>!=]{0,2}[0-9a-z-_\\.]*$', re.IGNORECASE)


def _text_dialog(title, text, parent):
    dialog = TextDialog(
        text, parent=parent)
    dialog.setWindowTitle(title)
    dialog.exec_()


def _invalid_name_dialog(title, name, parent):
    _text_dialog(title, f'Invalid package name: "{name}"', parent=parent)


def _invalid_version_dialog(title, version, parent):
    _text_dialog(title, f'Invalid package version: "{version}"', parent=parent)


def _required_dialog(title, package, required_by, parent):
    _text_dialog(title, f'Package: "{package}" is required by: {required_by}',
                 parent=parent)


def _distribution_key(package):
    try:
        distribution = pkg_resources.get_distribution(package)
        return distribution.key
    except Exception:
        # Probably not installed.
        pass


def _requirements_graph():
    distribution_names = set(pkg_resources.AvailableDistributions())
    graph = {}
    for distribution_name in distribution_names:
        distribution = pkg_resources.get_distribution(distribution_name)
        graph[distribution_name] = [r.key for r in distribution.requires()]
    return graph


def _freeze_dependencies(package_keys, graph):
    def inner(package):
        if package not in visited:
            visited.add(package)
            res[package] = pkg_resources.get_distribution(package).version

            for dependent_package in graph[package]:
                inner(dependent_package)
    visited = set()
    res = {}
    for key in package_keys:
        inner(key)
    return res


def _all_distribution_keys(exclude=None):
    distribution_names = set(pkg_resources.AvailableDistributions())
    if exclude:
        distribution_key = _distribution_key(exclude)
        if distribution_key is not None:
            distribution_names.discard(distribution_key)
    return _unique_list(distribution_names)


def _all_install_requires(exclude=None):
    requirements = {}

    for distribution_name in _all_distribution_keys(exclude=exclude):
        try:
            distribution = pkg_resources.get_distribution(
                distribution_name)
            for requirement in distribution.requires():
                requirements.setdefault(requirement.key, set()).update(
                    requirement.specs)
        except Exception:
            # TODO: should log here!
            pass
    return requirements


def _all_install_required(package):
    res = []
    for distribution_name in _all_distribution_keys():
        try:
            distribution = pkg_resources.get_distribution(
                distribution_name)
            for requirement in distribution.requires():
                if requirement.key == package:
                    res.append(distribution_name)
                    break
        except Exception:
            # TODO: should log here!
            pass
    return res


def _make_specifiers(requirements_dict):
    """
    Distribution specifiers to requirements.
    """
    def make_specifier(key, specifiers):
        res = key
        if specifiers:
            combined = ','.join([
                f'{op}{version}'
                for op, version in sorted(specifiers)])
            res = f'{key}{combined}'
        return res
    return '\n'.join(
        make_specifier(key, specifiers)
        for key, specifiers in sorted(requirements_dict.items()))


def _make_requirements(requirements_list):
    """
    [(key, version)] to requirements.
    """
    return '\n'.join(f'{package}=={version}'
                     for package, version in requirements_list)


def _platform_plugins():
    # Identifiers repeated to avoid unecessary imports.
    # TODO(erik): move all plugin identifiers to one place.
    distribution_keys = set()
    for identifier in [
            'sympathy.user_statistics.plugins',
            'sympathy.feature.plugins',
            'sympathy.library.plugins',
            'sympathy.credential.azure.plugins',
            'sympathy.editor.plugins',
    ]:
        for entry_point in pkg_resources.iter_entry_points(identifier):
            distribution_keys.add(entry_point.dist.key)
    return _unique_list(distribution_keys)


def _platform_dependencies():
    """
    Get all dependencies for the platform including requirements
    from installed plugins.
    """
    sympathy_key = _distribution_key(
        pkg_resources.safe_name(package_name()))
    plugin_keys = _platform_plugins()
    package_keys = _unique_list([sympathy_key] + plugin_keys)

    return _freeze_dependencies(
        package_keys,
        _requirements_graph())


def _platform_requirements():
    return _make_requirements(_unique_list(_platform_dependencies().items()))


def _unique_list(elements):
    return list(sorted(elements))


class InstallWidget(QtWidgets.QWidget):
    install_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        name = QtWidgets.QLabel('Name')
        version = QtWidgets.QLabel('Version')
        self._name = QtWidgets.QLineEdit()
        self._version = QtWidgets.QLineEdit()
        self._version.setPlaceholderText('Optional')
        self._add_button = QtWidgets.QPushButton('Add')
        self._remove_button = QtWidgets.QPushButton('Remove')
        self._add_button.setToolTip(
            'Install a package. Installation ensures that no package required'
            'by Sympathy or its current plugins are updated')
        self._remove_button.setToolTip(
            'Uninstall a package. Uninstall ensures that no package required'
            'by Sympathy or its current plugins are removed and that '
            'there are no packages depending on the package that is removed.')

        hlayout.addWidget(name)
        hlayout.addWidget(self._name)
        hlayout.addWidget(version)
        hlayout.addWidget(self._version)
        hlayout.addWidget(self._add_button)
        hlayout.addWidget(self._remove_button)
        self.setLayout(hlayout)
        self._add_button.clicked.connect(self._add)
        self._remove_button.clicked.connect(self._remove)

    def _add(self):
        title = 'Installing packages'

        name = self._name.text().strip()
        version = self._version.text().strip()

        if not _package_name_re.match(name):
            _invalid_name_dialog(title, name, self)
            return
        if not _package_ver_re.match(version):
            _invalid_version_dialog(title, version, self)
            return

        instance = settings.instance()

        with tempfile.NamedTemporaryFile(
                mode='w',
                prefix='pip_install_constraints',
                suffix='.txt',
                delete=False,
                dir=instance['session_folder'], encoding='utf8') as f:
            f.write(_platform_requirements())
            constraints = f.name
        try:
            if version:
                if not any(version.startswith(v) for v in '<>='):
                    version = f'=={version}'
            arg = f'{name}{version}'
            dialog = ProcessFeedbackDialog(
                pip_util.install_args(
                    arg, *pip_install_options.value(),
                    constraints=constraints),
                parent=self)
            dialog.setWindowTitle(title)
            dialog.exec_()
            self.install_changed.emit()
        finally:
            os.unlink(constraints)

    def _remove(self):
        title = 'Removing packages'

        name = self._name.text().strip()
        if not _package_name_re.match(name):
            _invalid_name_dialog(title, name, self)
            return

        key = _distribution_key(name)
        if key is not None:
            if key in _platform_dependencies():
                _required_dialog(
                    title, key, 'Sympathy or its current plugins', self)
                return
            required_by = _all_install_required(key)
            if required_by:
                required_by = ', '.join(required_by)
                _required_dialog(
                    title, key, required_by, self)
                return

        dialog = ProcessFeedbackDialog(
            pip_util.uninstall_args(name), parent=self)
        dialog.setWindowTitle(title)
        dialog.exec_()
        self.install_changed.emit()

    def set_package(self, name, version):
        self._name.setText(name)
        self._version.setText(version)


def _create_process(args, parent):
    program = args[0]
    arguments = args[1:]
    process = QtCore.QProcess(parent)
    process.setProgram(program)
    process.setArguments(arguments)
    return process


class ProcessReader(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, args, parent=None):
        super().__init__(parent=parent)
        self._process = _create_process(args, self)
        self._data = []
        self._process.readyReadStandardError.connect(
            self._handle_ready_read_standard_error)
        self._process.readyReadStandardOutput.connect(
            self._handle_ready_read_standard_output)
        self._process.started.connect(self._handle_started)
        self._process.finished.connect(self._handle_finished)
        self._process.errorOccurred.connect(self._handle_error)
        self._process.start()

    def _store_data(self, data):
        self._data.append(data)

    def _handle_ready_read_standard_output(self):
        self._store_data(self._process.readAllStandardOutput())

    def _handle_ready_read_standard_error(self):
        self._store_data(self._process.readAllStandardError())

    def _handle_started(self):
        pass

    def _handle_finished(self, exitCode, exitStatus):
        self.finished.emit()

    def _handle_error(self):
        try:
            self._process.kill()
        except Exception():
            pass

    def output(self):
        data = b''.join(self._data)
        return data.decode('utf8', errors='replace')


class ProcessFeedbackDialog(QtWidgets.QDialog):
    def __init__(self, args, parent=None):
        super().__init__(parent=parent)
        self._view = QtWidgets.QTextEdit(parent=self)
        self._status = QtWidgets.QLabel(parent=self)
        self._process = _create_process(args, self)
        self._buffer = []
        self._process.readyReadStandardError.connect(
            self._handle_ready_read_standard_error)
        self._process.readyReadStandardOutput.connect(
            self._handle_ready_read_standard_output)
        self._process.started.connect(self._handle_started)
        self._process.finished.connect(self._handle_finished)
        self._process.errorOccurred.connect(self._handle_error)
        self._process.start()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._view)
        layout.addWidget(self._status)
        self.setLayout(layout)
        self.setMinimumWidth(800)

    def _append(self, data):
        # Append which does not create newlines and keeps cursor pos.
        textcursor = self._view.textCursor()
        self._view.moveCursor(QtGui.QTextCursor.End)
        self._view.insertPlainText(data)
        self._view.setTextCursor(textcursor)

    def _output_lines(self, lines):
        data = b'\n'.join(lines)
        text = data.decode('utf8', errors='replace')
        self._append(text)

    def _output_data(self, data):
        new_lines = datalines(bytes(data), self._buffer)
        if new_lines:
            new_lines.append(b'')
        self._output_lines(new_lines)

    def _handle_ready_read_standard_output(self):
        self._output_data(self._process.readAllStandardOutput())

    def _handle_ready_read_standard_error(self):
        self._output_data(self._process.readAllStandardError())

    def _handle_started(self):
        self._status.setText('In progress')

    def _handle_finished(self, exitCode, exitStatus):
        self._output_lines(self._buffer)
        self._buffer.clear()
        self._status.setText(f'Finished with code {exitCode}')

    def _handle_error(self):
        self._status.setText('Error ocurred')
        try:
            self._process.kill()
        except Exception():
            pass

    def reject(self):
        try:
            self._process.kill()
        except Exception:
            pass
        return super().reject()


class PackagesWidget(QtWidgets.QWidget):
    selected_package = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self._package_widget = QtWidgets.QTableView()
        self._package_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self._package_widget.verticalHeader().hide()
        self._package_widget.setAlternatingRowColors(True)
        self._package_widget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self._package_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self._package_model = QtGui.QStandardItemModel()
        self._package_model.insertColumns(0, 2)
        self._package_model.setHeaderData(0, QtCore.Qt.Horizontal, 'Name')
        self._package_model.setHeaderData(1, QtCore.Qt.Horizontal, 'Value')

        self._package_widget.setModel(self._package_model)
        layout.addWidget(self._package_widget)
        self.setLayout(layout)
        self._updated = False
        self._process = None
        self._emit_selected_package = True

        self._package_widget.selectionModel().currentRowChanged.connect(
            self._handle_row_changed)

    def toPlainText(self):
        return True

    def update(self):
        if not self._process:
            self._process = ProcessReader(pip_util.freeze_args(), self)
            self._process.finished.connect(self._handle_finished)

    def _update_data(self, data):
        current_index = self._package_widget.selectionModel().currentIndex()
        selected_row_data = []
        if current_index.isValid():
            selected_row_data = self._row_data(current_index)

        names, versions = zip(*sorted(pip_util.freeze_from_str(data).items()))
        self._package_model.removeRows(0, self._package_model.rowCount())
        rows = list(zip(names, versions))
        self._package_model.insertRows(0, len(rows))

        for row, values in enumerate(rows):
            index = None
            for column, value in enumerate(values):
                index = self._package_model.index(row, column)
                self._package_model.setData(index, value)

            # Restore selection without emitting selected_package
            if index and values == selected_row_data:
                try:
                    self._emit_selected_package = False
                    self._package_widget.selectionModel().setCurrentIndex(
                        index,
                        QtCore.QItemSelectionModel.Select |
                        QtCore.QItemSelectionModel.Rows)
                finally:
                    self._emit_selected_package = True

    def _handle_finished(self):
        if self._process:
            self._process.finished.disconnect(self._handle_finished)
            output = self._process.output()
            self._process.setParent(None)
            self._process = None
            self._update_data(output)

    def _row_data(self, index):
        row = index.row()
        return tuple([
            self._package_model.data(self._package_model.index(
                row, column))
            for column in range(self._package_model.columnCount())])

    def _handle_row_changed(self, current, previous):
        if self._emit_selected_package and current.isValid():
            selected_data = self._row_data(current)
            self.selected_package.emit(*selected_data)
