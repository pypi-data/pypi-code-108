# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
import os
import shutil
import codecs
import re
from Qt import QtCore
from Qt import QtWidgets
from sympathy.utils import prim
from sympathy.app import settings
from . wizard_helper_functions import (ValidatingLineEdit,
                                       python_identifier_validator,
                                       name_validator,
                                       identifier_validator,
                                       string_to_identifier,
                                       format_python_string,
                                       RED_STYLE, GRAY_STYLE,
                                       SuperWizard, LIBRARY_INI, create_ini)


NODE_NAMES = [
    'Hello world example',
    'Hello world customizable example',
    'Output example',
    'Error example',
    'All parameters example',
    'Progress example',
    'Controller example',
    'Read/write example'
]
PLUGIN = 'plugin_calculator.py'
PLUGIN_DATA='''"""
A short example of how to make a calculator plugin. Put a copy of this file
in your library's package folder in Common, and it will be imported
automatically. The file name must start with 'plugin_'.
"""
from sylib.calculator import plugins
import collections
import inspect
import numpy as np

PLUGIN_ID = 'custom_plugin'   # Will be used as a namespace for the functions.
PLUGIN_NAME = 'CustomPlugin'  # The displayed name in the Calculator node.


class Section1(object):

    @staticmethod
    def example_function1(signal1, signal2):
        """Add two signals element by element.

        **Parameters**
            signal1: np.array
                The first signal.
            signal2: np.array
                The second signal

        **Returns**
            np.array
                The sum of the signals
        """
        return signal1 + signal2

    @staticmethod
    def example_function2(signal1, signal2):
        """Subtract two signals element by element.

        **Parameters**
            signal1: np.array
                The first signal.
            signal2: np.array
                The second signal

        **Returns**
            np.array
                The difference of the signals
        """
        return signal1 - signal2


class Section2(object):

    @staticmethod
    def example_function3(signal1, constant):
        """Add a constant to each element.

        **Parameters**
            signal1: np.array
                The first signal.
            signal2: np.array
                The second signal

        **Returns**
            np.array
                The sum of the signals
        """
        return signal1 + constant


SECTION1 = [
    (
        # Set a display name for the function
        "Example Function 1",
        # This is what will be put in the calculator window
        # if signal1 and signal 2 are defined in the class CustomPlugin,
        # this line can be run as a test
        PLUGIN_ID + ".example_function1(arg['signal1'], arg['signal2'])",
        # This fetches the documentation so that it can be shown on mouse over
        inspect.getdoc(Section1.example_function1)
    ),
    (
        "Example Function 2",
        PLUGIN_ID + ".example_function2(arg['signal1'], arg['signal2'])",
        inspect.getdoc(Section1.example_function2)
    )
]

SECTION2 = [
    (
        "Example Function 3",
        PLUGIN_ID + ".example_function3(arg['signal1'], value)",
        inspect.getdoc(Section2.example_function3)
    )
]

# CustomPlugin is the name that will be displayed in the Calculator.
# An ordered dict is used so that the sections are displayed in given order
GUI_DICT = {
    PLUGIN_NAME: collections.OrderedDict([
        ("Section1", SECTION1),
        ("Section2", SECTION2)])
}


class CustomPlugin(plugins.ICalcPlugin):
    """Custom plugin for calculator node. Wraps the above into something
    the Calculator can import.
    """

    # Can be used to set the position of the plugin in the Calculator GUI.
    # A higher value indicates a higher position.
    WEIGHT = 0

    @staticmethod
    def gui_dict():
        """This method does not require any user changes by default"""
        gui_dict = collections.OrderedDict()
        gui_dict.update(GUI_DICT)
        return gui_dict

    @staticmethod
    def globals_dict():
        """Add your classes here"""
        return {PLUGIN_ID: plugins.PluginWrapper(Section1, Section2)}

    @staticmethod
    def signals_dict():
        """Define signals that are needed to run the functions as written in
        eval texts, when running the tests.
        Must have the same length.
        """
        return {
            'signal1': np.array([1, 2, 3, 4, 5]),
            'signal2': np.array([1, 2, 3, 4, 5])}

    @staticmethod
    def variables_dict():
        """Define variables that are needed to run the functions as written in
        eval texts, when running the tests.
        """
        return {
            'value': 0}
'''


class LibraryWizardDirectoryPage(QtWidgets.QWizardPage):
    def __init__(self, title, model, parent=None):

        super().__init__(parent)
        self._model = model

        self._lib_path = QtWidgets.QLineEdit()
        self._lib_path.setFocusPolicy(QtCore.Qt.NoFocus)
        self._lib_path.setReadOnly(True)
        self._lib_path.setStyleSheet(RED_STYLE)
        self._path_btn = QtWidgets.QPushButton('...')
        self._package_name = ValidatingLineEdit(python_identifier_validator)
        self._package_name.setStyleSheet(GRAY_STYLE)

        self._package_name.setMaxLength(40)
        self._package_name.setToolTip(
            'Set the name of the package, where code shared between '
            'nodes may be placed. Default name is the same as the library '
            'name sans whitespace.')

        self._lib_stack = QtWidgets.QStackedWidget()
        self._lib_preview_old = QtWidgets.QTreeWidget()
        self._lib_preview_new = QtWidgets.QTreeWidget()
        self._lib_preview_old.header().close()
        self._lib_preview_new.header().close()
        self._create_base_tree()
        self._lib_preview_old.insertTopLevelItem(0, self._old_top_level_item)
        self._old_top_level_item.setHidden(True)
        self._lib_preview_new.insertTopLevelItem(0, self._new_top_level_item)
        self._new_top_level_item.setHidden(True)

        self._lib_stack.addWidget(self._lib_preview_old)
        self._lib_stack.addWidget(self._lib_preview_new)

        layout = QtWidgets.QGridLayout()

        self._version_group = QtWidgets.QButtonGroup()
        self._version_group.setExclusive(True)
        button_layout = QtWidgets.QVBoxLayout()
        version_box = QtWidgets.QGroupBox()
        self._new_button = QtWidgets.QRadioButton('New')
        self._new_button.setToolTip(
            'New structure available since version 2.0.0, organizes the '
            'library as a python package. (Recommended for new libraries)')
        self._old_button = QtWidgets.QRadioButton('Old')
        self._new_button.setToolTip(
            'Old structure available since version 1.0.0, organizes the '
            'library in a way that is compatible with older versions.')
        button_layout.addWidget(self._new_button)
        button_layout.addWidget(self._old_button)
        self._version_group.addButton(self._new_button)
        self._version_group.addButton(self._old_button)
        version_box.setLayout(button_layout)

        layout.addWidget(QtWidgets.QLabel('Library structure'), 0, 0, 1, 1)
        layout.addWidget(version_box, 1, 0, 2, 3)
        layout.addWidget(QtWidgets.QLabel('Library path'), 3, 0, 1, 1)
        layout.addWidget(self._lib_path, 3, 1, 1, 1)
        layout.addWidget(self._path_btn, 3, 2, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Package name'), 4, 0, 1, 1)
        layout.addWidget(self._package_name, 4, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel(
            'Library file structure preview'), 5, 0, 1, 1)
        layout.addWidget(self._lib_stack, 5, 0, 1, 3)
        self.setLayout(layout)

        self._path_btn.clicked.connect(self._get_directory_path)
        self._version_group.buttonToggled.connect(self._version_toggled)
        self._package_name.validated.connect(self._set_package_name)

        self._new_button.setChecked(True)

        self.setFinalPage(True)
        self.setTitle(title)
        self._update()

    def isComplete(self):
        return (
            self._package_name.isValid() and
            len(self._model.library_path))

    def initializePage(self):
        self._model.validate()
        self._package_name.setText(self._model.package_name)

    def _version_toggled(self, *args):
        self._model.new_version = self._new_button.isChecked()
        self._update_preview()

    def _create_base_tree(self):
        icon_provider = QtWidgets.QFileIconProvider()
        folder_icon = icon_provider.icon(QtWidgets.QFileIconProvider.Folder)
        file_icon = icon_provider.icon(QtWidgets.QFileIconProvider.File)

        # Old style tree.
        self._old_top_level_item = QtWidgets.QTreeWidgetItem()
        self._old_top_level_item.setIcon(0, folder_icon)

        common = self._add_item_to_tree(
            self._old_top_level_item, folder_icon, 'Common')
        library = self._add_item_to_tree(
            self._old_top_level_item, folder_icon, 'Library')
        test = self._add_item_to_tree(
            self._old_top_level_item, folder_icon, 'Test')
        self._info = self._add_item_to_tree(
            self._old_top_level_item, file_icon, LIBRARY_INI)

        self._add_item_to_tree(test, folder_icon, 'Workflow')
        self._add_item_to_tree(test, file_icon, 'test.py')

        self._old_com_libname = self._add_item_to_tree(common, folder_icon)
        self._old_lib_libname = self._add_item_to_tree(library, folder_icon)

        nodes = self._add_item_to_tree(
            self._old_lib_libname, folder_icon, 'nodes')

        flows = self._add_item_to_tree(
            self._old_lib_libname, folder_icon, 'flows')

        plugins = self._add_item_to_tree(
            self._old_com_libname, folder_icon, 'plugins')

        self._add_item_to_tree(
            self._old_com_libname, file_icon, '__init__.py')
        self._add_item_to_tree(
            plugins, file_icon, PLUGIN)

        self._add_item_to_tree(
            nodes, file_icon, 'node_examples.py')

        # TODO(erik): restore svg examples?
        # self._add_item_to_tree(
        #     self._old_lib_libname, file_icon, 'example.svg')
        # self._add_item_to_tree(
        #     self._old_lib_libname, file_icon, 'example_error.svg')

        # New style tree.
        self._new_top_level_item = QtWidgets.QTreeWidgetItem()
        self._new_top_level_item.setIcon(0, folder_icon)

        src = self._add_item_to_tree(
            self._new_top_level_item, folder_icon, 'src')

        self._add_item_to_tree(
            self._new_top_level_item, file_icon, 'setup.py')
        test = self._add_item_to_tree(
            self._new_top_level_item, folder_icon, 'test')

        self._add_item_to_tree(test, folder_icon, 'flows')
        self._add_item_to_tree(test, file_icon, 'test.py')

        self._new_com_libname = self._add_item_to_tree(src, folder_icon)

        self._add_item_to_tree(
            self._new_com_libname, file_icon, '__init__.py')

        nodes = self._add_item_to_tree(
            self._new_com_libname, folder_icon, 'nodes')

        flows = self._add_item_to_tree(
            self._new_com_libname, folder_icon, 'flows')

        plugins = self._add_item_to_tree(
            self._new_com_libname, folder_icon, 'plugins')

        self._add_item_to_tree(
            plugins, file_icon, PLUGIN)

        self._add_item_to_tree(
            nodes, file_icon, 'node_examples.py')

        # TODO(erik): restore svg examples?
        # self._add_item_to_tree(
        #     nodes, file_icon, 'example.svg')
        # self._add_item_to_tree(
        #     nodes, file_icon, 'example_error.svg')


    def _add_item_to_tree(self, parent, icon, name=''):
        item = QtWidgets.QTreeWidgetItem()
        item.setIcon(0, icon)
        item.setText(0, name)
        parent.addChild(item)
        return item

    def _get_directory_path(self):
        old = self._model.library_path
        default_path = ('../' + old if len(old) else
                        settings.instance()['default_folder'])
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Create Library", default_path)
        self._model.library_path = path if len(path) else old
        self._update()

    def _set_package_name(self):
        self._model.package_name = self._package_name.text()
        self._update()

    def _update_preview(self):
        self._lib_stack.setCurrentIndex(
            1 if self._new_button.isChecked() else 0)

        if self.isComplete():
            self._old_top_level_item.setText(0, self._model.library_path)
            self._new_top_level_item.setText(0, self._model.library_path)
            self._old_com_libname.setText(0, self._model.package_name)
            self._old_lib_libname.setText(0, self._model.package_name)
            self._new_com_libname.setText(0, self._model.package_name)
            self._old_top_level_item.setHidden(False)
            self._new_top_level_item.setHidden(False)
            self._lib_preview_old.expandAll()
            self._lib_preview_new.expandAll()
        else:
            self._old_top_level_item.setHidden(True)
            self._new_top_level_item.setHidden(True)

        if self._model.new_version:
            preview = self._lib_preview_new
        else:
            preview = self._lib_preview_old

        self._model.structure = QtWidgets.QTreeWidgetItemIterator(
            preview,
            QtWidgets.QTreeWidgetItemIterator.NoChildren)

    def _update(self):
        self._lib_path.setText(self._model.library_path)
        if not self._lib_path.text():
            self._lib_path.setStyleSheet(RED_STYLE)
        else:
            self._lib_path.setStyleSheet(GRAY_STYLE)
        self._update_preview()
        self.completeChanged.emit()


class LibraryWizardMetaPage(QtWidgets.QWizardPage):
    def __init__(self, title, model, parent=None):
        super().__init__(parent)
        self._model = model
        self._id_changed = False

        self._name = ValidatingLineEdit(name_validator)
        self._description = QtWidgets.QLineEdit()
        self._identifier = ValidatingLineEdit(identifier_validator)
        self._maintainer = QtWidgets.QLineEdit()
        self._copyright = QtWidgets.QLineEdit()
        self._repo_path = QtWidgets.QLineEdit()
        self._docu_path = QtWidgets.QLineEdit()
        self._home_path = QtWidgets.QLineEdit()

        self._name.setMaxLength(40)
        self._description.setMaxLength(256)
        self._identifier.setMaxLength(40)
        self._maintainer.setMaxLength(256)
        self._copyright.setMaxLength(256)
        self._repo_path.setMaxLength(256)
        self._docu_path.setMaxLength(256)
        self._home_path.setMaxLength(256)

        self._description.setStyleSheet(GRAY_STYLE)
        self._maintainer.setStyleSheet(GRAY_STYLE)
        self._copyright.setStyleSheet(GRAY_STYLE)
        self._repo_path.setStyleSheet(GRAY_STYLE)
        self._docu_path.setStyleSheet(GRAY_STYLE)
        self._home_path.setStyleSheet(GRAY_STYLE)

        self._name.setToolTip(
            "The name of the library which will be displayed in Sympathy's "
            "library view. Mandatory.")
        self._description.setToolTip(
            'A small description of the library. Optional.')
        self._identifier.setToolTip(
            'A string that will be used in the nodes to give them a unique id.'
            'For example, the identifier "test" will result in nodes with an '
            'id on the form "test.examplenode". Mandatory.')
        self._maintainer.setToolTip(
            'Name and contact information for library maintainer. Optional.')
        self._copyright.setToolTip(
            'A copyright message. Optional.')
        self._repo_path.setToolTip(
            'A repository url to the library. Optional.')
        self._docu_path.setToolTip(
            'A documentation url to the library. Optional.')
        self._home_path.setToolTip(
            'A home url to the library. Optional.')

        layout = QtWidgets.QFormLayout()
        layout.addRow('Library name', self._name)
        layout.addRow('Description', self._description)
        layout.addRow('Identifier', self._identifier)
        layout.addRow('Maintainer', self._maintainer)
        layout.addRow('Copyright', self._copyright)
        layout.addRow('Repository URL', self._repo_path)
        layout.addRow('Documentation URL', self._docu_path)
        layout.addRow('Home URL', self._home_path)
        layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.setLayout(layout)

        self._name.validated.connect(self._meta_changed)
        self._description.textChanged.connect(self._meta_changed)
        self._identifier.validated.connect(self._identifier_changed)
        self._maintainer.textChanged.connect(self._meta_changed)
        self._copyright.textChanged.connect(self._meta_changed)
        self._repo_path.textChanged.connect(self._meta_changed)
        self._docu_path.textChanged.connect(self._meta_changed)
        self._home_path.textChanged.connect(self._meta_changed)

        self.setTitle(title)

    def isComplete(self):
        return (
            len(self._model.identifier) and
            len(self._model.library_name) and
            self._name.isValid() and
            self._identifier.isValid())

    def _meta_changed(self):
        if self._name.isValid() or not len(self._name.text()):
            self._model.library_name = self._name.text()
        self._model.description = self._description.text()
        self._model.maintainer = self._maintainer.text()
        self._model.copyright = self._copyright.text()
        self._model.repo = self._repo_path.text()
        self._model.docu = self._docu_path.text()
        self._model.home = self._home_path.text()
        self._update()

    def _identifier_changed(self):
        if self.focusWidget() == self._identifier:
            self._id_changed = True
        if self._identifier.isValid() or not len(self._identifier.text()):
            self._model.identifier = self._identifier.text()
        self._update()

    def _update(self):
        if not self._id_changed:
            identifier = string_to_identifier(self._model.library_name)
            self._identifier.setText(identifier)
            self._model.identifier = identifier
        self.completeChanged.emit()


class LibraryWizard(SuperWizard):
    def __init__(self, parent=None):
        super().__init__('Library wizard', parent)
        self._model = LibraryWizardModel()

        meta_page = LibraryWizardMetaPage(
            'Library information', self._model, self)
        directory_page = LibraryWizardDirectoryPage(
            'Library location', self._model, self)
        self.addPage(meta_page)
        self.addPage(directory_page)

    def done(self, result):
        if result == QtWidgets.QDialog.Accepted:
            success = self._create_file_structure()
            if success:
                self._add_library_to_settings()
                super().done(result)
        if result == QtWidgets.QDialog.Rejected:
            super().done(result)

    def _create_file_structure(self):
        path = self._model.library_path

        if os.path.isdir(path):
            QtWidgets.QMessageBox.warning(
                self, 'Creation error',
                'The folder already exists, choose another location.')
            return False

        for path in self._model.structure:
            _, ext = os.path.splitext(path)
            folder = os.path.dirname(path)
            try:
                if len(ext):
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                    self._create_example_file(path)
                elif not os.path.isdir(path):
                    os.makedirs(path)
            except (OSError, IOError):
                raise
                QtWidgets.QMessageBox.warning(
                    self, 'Creation error',
                    'The Library cannot be created, ' +
                    'possibly because of a permission error.')
                self._cleanup()
                return False
            except Exception:
                raise
                QtWidgets.QMessageBox.warning(
                    self, 'Creation error',
                    'The Library cannot be created. Reason unknown.')
                self._cleanup()
                return False
        return True

    def _add_library_to_settings(self):
        setting = settings.instance()
        libraries = setting['Python/library_path']
        library_path = self._model.library_path
        if self._model.new_version:
            library_path = os.path.join(
                library_path, 'src', self._model.package_name)
        libraries.append(library_path)
        setting['Python/library_path'] = libraries

    def _create_example_file(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if path.endswith('node_examples.py'):
            example = f'''from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyNodeError, sywarn

class HelloWorld(synode.Node):
    """
    This, minimal, example prints a fixed "Hello world!" greeting when
    executed.

    See :ref:`nodewriting` for more information about writing nodes.
    """

    name = 'Hello world example ({self._model.library_name})'
    nodeid = '{self._model.identifier}.examples.helloworld'
    tags = Tags(Tag.Development.Example)

    def execute(self, node_context):
        print('Hello world!')
'''

            name, ext = os.path.splitext(path)
            new_path = '{}_{}{}'.format(
                name, self._model.library_name, ext)
            with open(new_path, 'w') as f:
                f.write(example)

        elif path.endswith('test.py'):
            flows_dir = 'flows'
            if not self._model.new_version:
                flows_dir = 'Workflow'
            test = f'''import os
from sympathy.test import run_workflow

test_root = os.path.dirname(os.path.abspath(__file__))


def test_workflows():
    """
    Test all workflows in library workflow test directories.
    Test workflows using command line tool cli.
    """
    run_workflow.run_flows_in_path(os.path.join(test_root, '{flows_dir}'))
'''
            with open(path, 'w') as f:
                f.write(test)

        elif path.endswith(LIBRARY_INI):
            create_ini(
                path, self._model.library_name, self._model.description,
                self._model.identifier, self._model.package_name,
                self._model.package_name, self._model.copyright,
                self._model.maintainer, self._model.repo, self._model.docu,
                self._model.home)
        elif path.endswith(PLUGIN):
            self._create_example_plugin(path)

        elif path.endswith('setup.py'):
            setup = f'''from setuptools import setup, find_namespace_packages

package = '{self._model.library_name}'

setup(
    name='{self._model.library_name}',
    version='0.1',
    install_requires=['Sympathy>=2.0'],
    packages=find_namespace_packages(where='src'),
    package_dir={{
        '': 'src',
    }},
    entry_points={{
          'sympathy.library.plugins': [
              '{self._model.package_name} = {self._model.package_name}'
          ],
    }})
'''
            with open(path, 'w') as f:
                f.write(setup)

        elif path.endswith('__init__.py'):
            if self._model.new_version:
                init = f'''def identifier():
    return '{self._model.identifier}'


def name():
    return '{self._model.library_name}'


def description():
    return '{self._model.description}'


def maintainer():
    return '{self._model.maintainer}'


def copyright():
    return '{self._model.copyright}'


def repository_url():
    return '{self._model.repo}'


def documentation_url():
    return '{self._model.docu}'


def home_url():
    return '{self._model.home}'

'''
                with open(path, 'w') as f:
                    f.write(init)

        else:
            print(f'Ignored unhandled file: {path}')

    def _create_example_plugin(self, new_plugin_path):
        plugin_path = os.path.join(
            prim.examples_path(), 'CalculatorPlugin', 'plugin_example.py')
        plugin_path = self._prepare_path(plugin_path)
        plugin = PLUGIN_DATA
        plugin = plugin.replace(
            'custom_plugin', self._model.package_name, 1)
        plugin = plugin.replace('CustomPlugin', self._model.library_name, 1)

        with open(new_plugin_path, 'w') as f:
            f.write(plugin)

    def _prepare_path(self, path):
        return os.path.normpath(os.path.realpath(path))

    def _cleanup(self):
        """If something was created but then failed, remove everything."""
        try:
            if os.path.isdir(self._model.library_path):
                shutil.rmtree(self._model.library_path)
        except Exception:
            pass


class LibraryWizardModel(QtCore.QObject):

    def __init__(self):
        self._lib_name = ''
        self._lib_path = ''
        self._package_name = ''
        self._paths = []
        self._description = ''
        self._identifier = ''
        self._maintainer = ''
        self._copyright = ''
        self._repo = ''
        self._new_version = True

    def validate(self):
        self._lib_name = self._lib_name.strip()
        if self.identifier[-1] == '.':
            self._identifier = self.identifier[:-1]

    @property
    def new_version(self):
        return self._new_version

    @new_version.setter
    def new_version(self, value):
        self._new_version = value

    @property
    def library_name(self):
        return self._lib_name

    @library_name.setter
    def library_name(self, value):
        value = value.strip()
        self._lib_name = value
        pkg_name = format_python_string(value).lower()
        self._package_name = pkg_name

    @property
    def package_name(self):
        return self._package_name

    @package_name.setter
    def package_name(self, value):
        self._package_name = value

    @property
    def library_path(self):
        return self._lib_path

    @library_path.setter
    def library_path(self, value):
        self._lib_path = os.path.normpath(value + '/' + self._lib_name)

    @property
    def structure(self):
        return self._paths

    @structure.setter
    def structure(self, value):
        self._paths = []
        while value.value():
            child = value.value()
            parent = child.parent()
            path = child.text(0)
            while parent:
                path = parent.text(0) + '/' + path
                parent = parent.parent()
            self._paths.append(os.path.normpath(path))

            try:
                next(value)
            except TypeError:
                value += 1

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        value = re.sub('[^a-z0-9\\.]', '', value.lower())
        self._identifier = value

    @property
    def copyright(self):
        return self._copyright

    @copyright.setter
    def copyright(self, value):
        self._copyright = value

    @property
    def maintainer(self):
        return self._maintainer

    @maintainer.setter
    def maintainer(self, value):
        self._maintainer = value

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, value):
        self._repo = value

    @property
    def docu(self):
        return self._docu

    @docu.setter
    def docu(self, value):
        self._docu = value


    @property
    def home(self):
        return self._home

    @home.setter
    def home(self, value):
        self._home = value
