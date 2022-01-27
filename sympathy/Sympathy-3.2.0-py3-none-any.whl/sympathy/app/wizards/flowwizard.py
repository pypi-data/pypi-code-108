# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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
import re
from Qt import QtWidgets
from Qt import QtCore
from .. import settings
from .. import util
from sympathy.utils import prim
from sympathy.platform import widget_library as sywidgets
from sympathy.platform import library as library_platform
from sympathy.platform.library import is_combine_library_id


class LibraryComboBox(QtWidgets.QComboBox):

    def __init__(self, paths, all_libraries, parent=None):
        super().__init__(parent=parent)

        platform_developer = settings.instance()['Gui/platform_developer']

        for lib in all_libraries:

            if not lib.installed and not any(prim.samefile(lib.uri, path)
                                             for path in paths):
                continue

            ident = lib.identifier
            library_path = lib.uri
            library_path = library_platform.library_path(library_path)
            if is_combine_library_id(ident) and not platform_developer:
                continue

            self.addItem(lib.name)
            i = self.count() - 1
            self.setItemData(
                i, lib.uri, role=QtCore.Qt.ToolTipRole)
            self.setItemData(
                i, {'id': ident, 'root_path': lib.uri,
                    'library_path': library_path},
                role=QtCore.Qt.UserRole)

    def value(self):
        return self.itemData(self.currentIndex(), role=QtCore.Qt.UserRole)


class TagComboBox(QtWidgets.QComboBox):
    def __init__(self, tag, tags_root, parent=None):
        self._tag_key_dict = {}
        super().__init__(parent=parent)

        def flatten(lists):
            return [i for list in lists for i in list]

        def list_tags(tags):
            if tags.term:
                return [tags]
            return [list_tags(tag) for tag in tags]

        def build_tags(path, tags):
            if tags.term:
                return '/'.join(path)
            else:
                return [build_tags(path + [tag.name], tag) for tag in tags]

        def build_tags_keys(path, tags):
            if tags.term:
                return '.'.join(path)
            else:
                return [build_tags_keys(path + [tag.key], tag) for tag in tags]

        tag_list = flatten(
            build_tags([], tags_root))

        self._tag_key_dict = dict(zip(flatten(
            build_tags_keys([], tags_root)), tag_list))

        self.addItems(tag_list)

        tag_idx = self.findText(
            self._tag_key_dict.get(tag, ''))
        self.setCurrentIndex(tag_idx)

    def value(self):
        return dict(zip(self._tag_key_dict.values(),
                        self._tag_key_dict.keys())).get(
            self.currentText(), '')


class ChooseLibraryPage(QtWidgets.QWizardPage):
    def __init__(self, paths, all_libraries, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()

        self._library = LibraryComboBox(paths, all_libraries)
        self._library.setCurrentIndex(-1)

        layout.addWidget(self._library)

        self.setTitle('Choose Library')
        self.setLayout(layout)

    def library(self):
        return self._library.value()

    def validatePage(self):
        return self._library.currentIndex() > -1


def wizard_form_layout():
    layout = QtWidgets.QFormLayout()
    layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
    layout.setFormAlignment(QtCore.Qt.AlignLeft)
    layout.setLabelAlignment(QtCore.Qt.AlignVCenter)
    layout.setVerticalSpacing(15)
    return layout


class ChooseDetailsPage(QtWidgets.QWizardPage):

    def __init__(self, flow_, tags, parent=None):
        super().__init__(parent=parent)
        layout = wizard_form_layout()

        self._flow = flow_
        self._tag = TagComboBox(None, tags)
        self._identifier_re = '.*'
        self._identifier = sywidgets.ValidatedTextLineEdit()
        self._identifier.set_keep_last_valid_value(False)
        self._identifier.setBuilder(self._validate_identifier)
        self._identifier.setToolTip(
            "Identifier for the flow should start with the library identifier "
            "and consist of segments of lower case letters separated by "
            "periods.")

        layout.addRow('Tag', self._tag)
        layout.addRow('Identifier', self._identifier)

        self.setTitle('Choose Details')
        self.setLayout(layout)

    def _validate_identifier(self, text):
        root_path = self.wizard().library()['root_path']

        if self._identifier_re.match(text) is None:
            raise sywidgets.ValidationError(
                'Identifier must be dotted path of lower case segments')

        if self.wizard().flow.app_core.is_node_in_library(
                text, [root_path]):
            raise sywidgets.ValidationError(
                'Identifier must be unique in library')

        return text

    def identifier(self):
        return self._identifier.text()

    def tag(self):
        return self._tag.value()

    def initializePage(self):
        library_id = self.wizard().library()['id']
        self._identifier_re = re.compile(
            ''.join([
                '^',
                library_id.replace('.', '\\.'),
                '\\.flows',
                '(\\.[a-z]([a-z0-9]){2,})+$']))

        flow_id = re.sub(r'[^a-z0-9]', '', self._flow.name.lower())
        self._identifier.setText(library_id + '.flows.' + flow_id)

    def validatePage(self):
        tag_ok = self._tag.currentIndex() > -1
        ident_ok = self._identifier.valid()
        return tag_ok and ident_ok

    def details(self):
        return {
            'identifier': self._identifier.text(),
            'tag': self._tag.value(),
            'tag_text': self._tag.currentText()}


class SummaryPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = wizard_form_layout()

        self.setTitle('Summary')
        self.setLayout(layout)

        self._filename = QtWidgets.QLineEdit()
        self._tag = QtWidgets.QLineEdit()
        self._identifier = QtWidgets.QLineEdit()

        self._details = {'identifier': '', 'tag': '', 'tag_text': ''}

        self._filename.setReadOnly(True)
        self._tag.setReadOnly(True)
        self._identifier.setReadOnly(True)

        layout.addRow('Filename', self._filename)
        layout.addRow('Tag', self._tag)
        layout.addRow('Identifier', self._identifier)
        self.setLayout(layout)

    def initializePage(self):
        self._details = self.wizard().details()
        ident = self._details['identifier']
        self._library = self.wizard().library()
        library_path = self._library['library_path']

        seg = self._details['identifier'].split(self._library['id'] + '.')[-1]
        segs = seg.split('.')
        segs = segs[:-1] + ['flow_' + segs[-1] + '.syx']

        filename = os.path.join(*(
            [prim.nativepath_separators(p) for p in
             [library_path] + segs]))

        self._filename.setText(filename)
        self._identifier.setText(ident)
        self._tag.setText(self._details['tag_text'])

    def filename(self):
        return self._filename.text()

    def validatePage(self):
        return True


class SaveSubflowAsNodeWizard(QtWidgets.QWizard):
    def __init__(self, flow_, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('Configure project environment')
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # On Windows the Wizard shows the WindowTitle in the wrong
        # place if we use the native style
        self.setWizardStyle(QtWidgets.QWizard.ClassicStyle)

        self.flow = flow_

        tags = flow_.app_core.library_root().tags.root
        library_paths = util.library_paths(flow=flow_)
        all_libraries = flow_.app_core.library_root().libraries

        self._library_page = ChooseLibraryPage(library_paths, all_libraries)
        self._details_page = ChooseDetailsPage(flow_, tags)
        self._summary_page = SummaryPage()

        self.addPage(self._library_page)
        self.addPage(self._details_page)
        self.addPage(self._summary_page)

    def library(self):
        return self._library_page.library()

    def details(self):
        return self._details_page.details()

    def filename(self):
        return self._summary_page.filename()
