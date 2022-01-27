# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import re
import os

import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

from sympathy.platform import workflow_converter
from sympathy.platform import version_support as vs
from sympathy.utils import process, log
from . import config
from . import flow_serialization
from . import settings
from . import user_statistics
from . util import bulk_context

core_logger = log.get_logger('core')
app_logger = log.get_logger('app')
backup_logger = log.get_logger('app.backup')
num_recent_flows = 15

# Text ordering options
FRONT = 'Bring to front'
FORWARD = 'Bring forward'
BACKWARD = 'Send backward'
BACK = 'Send to back'


class TermColors(object):
    """
    Available formatting constants are:

    FORE: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE.
    BACK: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE.
    Style: DIM, NORMAL, BRIGHT

    >>> print(RED('Hello World', style='BRIGHT'))
    Hello World
    """

    def __init__(self):
        try:
            # Terminal color support is optional.
            from colorama import init, Fore, Back, Style
            self.__initialized = False
            self.__init = init
            self.Fore = Fore
            self.Back = Back
            self.Style = Style
            self._grounds = {'FORE': self.Fore, 'BACK': self.Back}
        except ImportError:
            pass

    def initialize(self):
        if not self.__initialized:
            self.__initialized = True
            self.__init(wrap=False)

    def _color_text(self, text, color, ground, style):
        try:
            return '{} {} {} {} {}'.format(
                color, self.Style.__getattribute__(style), text,
                ground.RESET, self.Style.RESET_ALL)
        except Exception:
            return text

    def __getattr__(self, name):
        def inner(text, ground_str='FORE', style='NORMAL'):
            self.initialize()
            try:
                ground = self._grounds[ground_str]
                color = ground.__getattribute__(name.upper())
            except Exception:
                return text
            return self._color_text(text, color, ground, style)
        return inner


_TERM_COLORS = TermColors()


def color_functions(colors):
    return (_TERM_COLORS.__getattr__(color) for color in colors)


COLORS = ('BLACK', 'RED', 'GREEN', 'YELLOW',
          'BLUE', 'MAGENTA', 'CYAN', 'WHITE')
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = color_functions(COLORS)


def hash_support(app, app_core):
    pass


def log_environ(app, app_core):
    pass


error_codes = config.active()['error_codes']


def return_value(description):
    return error_codes[description]['code']


def error_description(name):
    return error_codes[name]['description']


def print_error(error_name):
    core_logger.error('error: {}\n'.format(error_description(error_name)))


def execution_error(output):
    errors = ('exception_string', 'stderr', 'exception_trace')
    return any((bool(output[k]) for k in errors))


class SaveCancelled(Exception):
    pass


def persistent_save_flow_to_file(flow_, default_filename=None):
    """
    Ask for a filename and try to save a flow. Keep trying until saving worked
    or until user cancelled.

    If the user cancels a SaveCancelled exception is raised. Otherwise the
    final filename is returned.

    If default_filename is set the method will try to save the flow there
    first without asking for a filename. If it fails it will go on to ask the
    user for another filename as usual.
    """
    saved = False
    while not saved:
        filename = default_filename or ask_for_filename(flow_)
        saved = save_flow_to_file(flow_, filename)
        default_filename = None  # Don't try again with this filename.
    return filename


def save_flow_to_file(flow_, filename, auto=False):
    """Save a flow to a file"""
    res = _write_flow(flow_, filename)
    if not res:
        return False
    if not flow_.is_subflow() or flow_.is_linked:
        flow_.set_clean()
    if not flow_.is_subflow() or not flow_.is_linked:
        add_flow_to_recent_flows_list(filename)
    if not auto:
        user_statistics.user_saved_workflow(flow_)
    return True


def get_backup_filename(flow):
    """Return the backup filename for filename."""
    backup_folder = os.path.join(
        settings.instance()['session_folder'], 'backups')
    if flow.filename:
        filename = os.path.abspath(flow.filename)
        filename = filename.replace('!', '!!')
        filename = filename.replace(os.path.sep, '!')
        filename = re.sub(r'^([a-z]):', r'\1!', filename)
        return os.path.join(backup_folder, filename)
    else:
        filename = f'_!{flow.uuid[1:-1]}!.syx'
        return os.path.join(backup_folder, filename)


def filename_from_backup(backup_filename):
    """Return the original filename for backup_filename."""
    backup_basename = os.path.basename(backup_filename)

    if re.match(r'_!.*!.syx', backup_basename):
        # This flow was never saved
        return ''

    sep = os.path.sep.replace('\\', r'\\')
    filename = os.path.basename(backup_basename)
    filename = re.sub(r'^([a-z]):', r'\1!', filename)
    filename = re.sub(r'!(?!!)', sep, filename)
    filename = filename.replace('!!', '!')
    return filename


def backup_flow(flow_):
    """Save a backup of flow_."""
    filename = get_backup_filename(flow_)
    folder = os.path.dirname(filename)
    os.makedirs(folder, exist_ok=True)
    res = _write_flow(flow_, filename)
    if res:
        backup_logger.info(
            "Backed up flow %s to %s", flow_, filename)
    else:
        backup_logger.warning(
            "Unable to back up flow %s to %s", flow_, filename)
    return res


def remove_backup(flow_):
    """Remove backup files associated with flow_."""
    backup_filename = get_backup_filename(flow_)
    try:
        os.unlink(backup_filename)
    except FileNotFoundError:
        pass
    except OSError:
        backup_logger.warning(
            "Unable to remove backup for flow %s (%s).",
            flow_, backup_filename)
    else:
        backup_logger.info(
            "Removed backup for flow %s (%s).",
            flow_, backup_filename)


def _write_flow(flow_, filename):
    flow_dict = flow_.to_dict(stub=False)
    converter = workflow_converter.JsonToXml.from_dict(flow_dict)
    xml_data = converter.xml()
    try:
        with open(filename, 'wb') as flow_file:
            flow_file.write(vs.encode(xml_data, 'UTF-8'))
    except EnvironmentError:
        return False
    return True


def ask_for_filename(flow_):
    """
    Ask the user for a filename where a workflow should be saved.
    If the user cancels a SaveCancelled exception is raised.
    """
    # Find a good directory to present in the file dialog.
    flow_filename = flow_.root_or_linked_flow_filename
    if flow_filename:
        default_dir = os.path.dirname(flow_filename)
    else:
        default_dir = settings.instance()['default_folder']

    # Convert whitespaces to single space and remove trailing and leading
    # whitespace.
    default_filename = '{}.{}'.format(
        re.sub(r'\s+', ' ', flow_.name, flags=re.UNICODE).strip(),
        flow_.app_core.flow_suffix())

    # If colon or any ascii control character is in the filename the Windows
    # save file dialog returns empty strings (the same as if the user cancelled
    # the dialog) without ever showing the dialog. To get around this remove
    # any such characters from the default filename.
    if sys.platform == 'win32':
        bad_chars = set(list(map(chr, range(32))) + [':'])
        default_filename = ''.join(
            c for c in default_filename if c not in bad_chars).strip()

    filename = QtWidgets.QFileDialog.getSaveFileName(
        None, 'Save flow', os.path.join(default_dir, default_filename),
        filter='Sympathy flow (*.syx)')[0]

    if len(filename) == 0:
        raise SaveCancelled()

    return filename


class UnsavedFilesDialog(QtWidgets.QDialog):
    """
    A dialog which shows a tree of flows and lets the user check those that
    should be saved.
    """

    def __init__(self, root_flows, include_root, discard, parent=None):
        super(UnsavedFilesDialog, self).__init__(parent)
        self._discard = False
        self._uuid_to_flow = {}

        if include_root:
            flows = root_flows
        else:
            flows = []
            for root_flow in root_flows:
                flows.extend(root_flow.shallow_subflows())

        self.setWindowTitle("Save changed flows?")
        text = QtWidgets.QLabel("Some flows or subflows have unsaved changes. "
                                "Would you like to save them?")

        self._flow_list = QtWidgets.QTreeWidget(self)
        self._flow_list.setColumnCount(3)
        self._flow_list.setHeaderLabels(
            ["Flow name", "Save?", "File"])
        dirty_uuids = set()
        for flow_ in flows:
            dirty_uuids.update(self._get_dirty_uuids(flow_))
        items = self._populate_model(flows, dirty_uuids=dirty_uuids)
        self._flow_list.addTopLevelItems(items)
        self._flow_list.expandAll()
        self._flow_list.resizeColumnToContents(0)

        if discard:
            self._buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Save |
                QtWidgets.QDialogButtonBox.Discard |
                QtWidgets.QDialogButtonBox.Cancel,
                parent=self)
        else:
            self._buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Save |
                QtWidgets.QDialogButtonBox.Cancel,
                parent=self)
        self._buttons.clicked.connect(self._clicked)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self._flow_list)
        layout.addWidget(self._buttons)
        self.setLayout(layout)

    def _populate_model(self, flows, dirty_uuids, parent_item=None):
        """Populate the QTreeWidget item model using flows."""
        if parent_item is None:
            parent_item = self._flow_list

        items = []
        for flow_ in flows:
            if flow_.full_uuid in dirty_uuids:
                if not flow_.filename:
                    filename = None
                else:
                    filename = os.path.relpath(
                        flow_.filename, os.path.dirname(
                            flow_.root_or_linked_flow_filename))
                if flow_.is_linked or flow_.flow is None:
                    display_filename = filename or "<Not saved>"
                else:
                    display_filename = ""
                item = QtWidgets.QTreeWidgetItem(
                    parent_item, [flow_.display_name, '', display_filename])
                item.setFlags(
                    QtCore.Qt.ItemIsUserCheckable |
                    QtCore.Qt.ItemIsEnabled)
                item.setData(0, QtCore.Qt.UserRole, flow_.namespace_uuid())
                item.setData(2, QtCore.Qt.ToolTipRole, flow_.filename)
                self._uuid_to_flow[flow_.namespace_uuid()] = flow_
                if not flow_.is_clean() and (flow_.is_linked or
                                             flow_.flow is None):
                    item.setCheckState(1, QtCore.Qt.Checked)

                self._populate_model(
                    flow_.shallow_subflows(), dirty_uuids, item)
                items.append(item)
        return items

    def _get_dirty_uuids(self, root_flow):
        if root_flow.is_clean():
            dirty_subflows = []
        else:
            dirty_subflows = [root_flow]
        dirty_subflows.extend([f for f in root_flow.all_subflows()
                               if f.is_linked and not f.is_clean()])
        parent_flows = []
        for flow_ in dirty_subflows:
            while flow_ is not None:
                parent_flows.append(flow_)
                flow_ = flow_.flow
        return set([f.full_uuid for f in parent_flows + dirty_subflows])

    def _clicked(self, button):
        """Handle when the user clicks a dialog button (Save/Cancel)."""
        button = self._buttons.standardButton(button)
        if button == QtWidgets.QDialogButtonBox.StandardButton.Save:
            self.accept()
        elif button == QtWidgets.QDialogButtonBox.StandardButton.Discard:
            self._discard = True
            self.accept()
        elif button == QtWidgets.QDialogButtonBox.StandardButton.Cancel:
            self.reject()

    def _item_to_flow(self, item):
        uuid = item.data(0, QtCore.Qt.UserRole)
        return self._uuid_to_flow[uuid]

    def selected_flows(self):
        """Return a set with the flows that were selected to be saved."""
        if self._discard:
            return []

        def item_to_flows(item):
            flows = set()
            if item.checkState(1) == QtCore.Qt.Checked:
                flows.add(self._item_to_flow(item))
            for i in range(item.childCount()):
                child_item = item.child(i)
                flows.update(item_to_flows(child_item))
            return flows

        flows = set()
        for i in range(self._flow_list.topLevelItemCount()):
            item = self._flow_list.topLevelItem(i)
            flows.update(item_to_flows(item))
        return flows

    def unselected_flows(self):
        """Return a set with the flows that were not selected to be saved."""
        def item_to_flows(item):
            flows = set()
            if self._discard or item.checkState(1) == QtCore.Qt.Unchecked:
                flows.add(self._item_to_flow(item))
            for i in range(item.childCount()):
                child_item = item.child(i)
                flows.update(item_to_flows(child_item))
            return flows

        flows = set()
        for i in range(self._flow_list.topLevelItemCount()):
            item = self._flow_list.topLevelItem(i)
            flows.update(item_to_flows(item))
        return flows


def ask_about_saving_flows(root_flows, include_root=False, discard=False):
    """
    Show a dialog to let the user choose to save or discard any changes in the
    flows in root_flows or their subflows.

    If there are no unsaved changes in any of the flows in root_flows
    (including subflows), no dialog is shown.

    Parameters
    ----------
    root_flows : list of flows
    include_root : bool, optional
        If True, both the flows in root_flows and all their subflows will be
        considered. If False, only the subflows are checked.
    discard : bool, optional
        If True, adds a button that lets the user discard all the flows. This
        is only needed when closing a flow tab or quiting the application, and
        the button can have a text like "Quit without saving" on some
        platforms.
    """
    if include_root:
        flows = root_flows
    else:
        flows = []
        for root_flow in root_flows:
            flows.extend(root_flow.shallow_subflows())

    if all([f.subflows_are_clean() for f in flows]):
        return

    dialog = UnsavedFilesDialog(root_flows, include_root, discard)
    result = dialog.exec_()
    if result == QtWidgets.QDialog.Accepted:
        for flow_ in dialog.selected_flows():
            persistent_save_flow_to_file(flow_, flow_.filename or None)
    elif result == QtWidgets.QDialog.Rejected:
        raise SaveCancelled()


def check_backup_files():
    """Return a list of filenames of all active backup files."""
    def sha1(filename_):
        import hashlib
        hasher = hashlib.sha1()
        with open(filename_, 'rb') as f:
            while True:
                chunk = f.read(4096)
                hasher.update(chunk)
                if not chunk:
                    break
        return hasher.hexdigest()

    def try_remove(filename_):
        try:
            os.unlink(filename_)
        except OSError:
            pass

    def list_backup_files(sessions_folder):
        """List all backup files in all non-active session folders."""
        session_folders = [
            os.path.join(sessions_folder, d)
            for d in os.listdir(sessions_folder) if d.startswith('20')
        ]

        for session_folder in session_folders:
            backup_folder = os.path.join(session_folder, 'backups')
            if not os.path.isdir(backup_folder):
                continue

            owner = os.path.join(session_folder, 'owner')
            if not process.is_expired(owner, 10):
                # Process that created this session folder still exists!
                continue

            for filename in os.listdir(backup_folder):
                yield os.path.join(backup_folder, filename)

    try:
        sessions_folder = settings.instance().sessions_folder
        if not os.path.exists(sessions_folder):
            return []

        backup_files = []
        for backup_filename in list_backup_files(sessions_folder):
            backup_basename = os.path.basename(backup_filename)
            filename = filename_from_backup(backup_basename)
            if filename:
                if os.path.getmtime(backup_filename) <= os.path.getmtime(filename):
                    try_remove(backup_filename)
                    continue
                if sha1(filename) == sha1(backup_filename):
                    try_remove(backup_filename)
                    continue
            backup_files.append(backup_filename)
        return backup_files
    except OSError:
        # Catch all file system related problems
        import traceback
        backup_logger.warning(
            "Unable to list backup files:\n%s", traceback.format_exc())


def load_flow_action(app_core, flow, filename, deserializer, is_linked=False,
                     warn_on_errors=None, validate=True, parent_flow=None):
    validate_enabled = app_core.validate_enabled()
    with bulk_context(flow), flow.propagate_ctx():
        try:
            app_core.set_validate_enabled(False)
            flow.filename = filename
            deserializer.build_flow(flow, warn_on_errors=warn_on_errors,
                                    parent_flow=parent_flow)
        finally:
            app_core.set_validate_enabled(validate_enabled)
        if validate:
            flow.validate_action()


def load_flow_from_file(app_core, filename, flows=None,
                        open_window=lambda new_flow: None,
                        warn_on_errors=None, validate=True):
    """
    Read flow with given file name.

    flows is a list to which the new flow gets appended. open_window is a
    function which takes the new flow and opens it. This is intended for GUI
    mode, the default is a function that does nothing to the flow argument.
    """
    filename = vs.fs_decode(filename)
    cwd = os.getcwd()
    deserializer = flow_serialization.FlowDeserializer(app_core)
    deserializer.load_xml_file(filename)
    if not deserializer.is_valid():
        core_logger.critical('Failed to load {}'.format(filename))

    new_flow = app_core.create_flow(deserializer.to_dict()['uuid'])
    if flows is not None:
        flows.append(new_flow)

    try:
        filename = os.path.abspath(filename)
        os.chdir(os.path.dirname(filename))
        load_flow_action(app_core, new_flow, filename, deserializer,
                         warn_on_errors=warn_on_errors, validate=validate)
    except Exception:
        os.chdir(cwd)
        raise

    open_window(new_flow)
    return new_flow


def add_flow_to_recent_flows_list(filename):
    """Helper: Update the recent flows list."""
    if filename == "":
        app_logger.debug("Not adding empty string to recent files.")
        return
    elif os.path.isdir(filename):
        app_logger.debug("Not adding directory {} to recent files."
                         .format(filename))
        return

    recent_flows = settings.instance()['Gui/recent_flows']
    recent_flows.insert(0, os.path.abspath(filename))
    recent_flows = [x for x in recent_flows if x]
    # Uniquify recent flows
    seen = set()
    recent_flows = [x for x in recent_flows
                    if (os.path.normpath(x) not in seen and
                        not seen.add(os.path.normpath(x)))][:num_recent_flows]

    settings.instance()['Gui/recent_flows'] = recent_flows
