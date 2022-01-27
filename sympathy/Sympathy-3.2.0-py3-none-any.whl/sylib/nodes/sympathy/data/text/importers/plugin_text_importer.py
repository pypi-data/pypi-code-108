# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
import codecs
import os
from sympathy.api import importers
from sympathy.api import node as synode
from sympathy.api import qt2 as qt_compat
from sympathy.api import exceptions
import sylib.table_sources
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


def all_equal(iterator):
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True


class DataImportText(importers.TextDataImporterBase):
    """Importer for Text files."""
    IMPORTER_NAME = "Text"

    def __init__(self, fq_infilename, parameters):
        super(DataImportText, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def _init_parameters(self):
        if 'source_coding' not in self._parameters:
            self._parameters.set_string(
                'source_coding',
                label='Encoding',
                editor=synode.Util.combo_editor(
                    options=list(
                        sylib.table_sources.CODEC_LANGS.keys())),
                value='UTF-8',
                description='Encoding used to decode file')

    def parameter_view(self, parameters):
        valid_for_file = self.valid_for_file()
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        if not valid_for_file:
            layout.addWidget(QtWidgets.QLabel(
                'File does not exist or cannot be read.'))
        layout.addWidget(parameters['source_coding'].gui())
        return widget

    def import_data(self, out_datafile, parameters=None, progress=None):
        encoding = sylib.table_sources.CODEC_LANGS[
            parameters['source_coding'].value]

        if not self.valid_for_file():
            raise exceptions.SyDataError(
                'Importer: {} is not valid for: {}'.format(
                    self.display_name(), self._fq_infilename))
        try:
            with codecs.open(self._fq_infilename, 'r', encoding=encoding) as f:
                out_datafile.set(f.read())
        except UnicodeError as e:
            raise exceptions.SyDataError(f'Invalid encoding: {e}.')

    def valid_for_file(self):
        """Is fq_filename valid Text."""
        return self._fq_infilename is not None and (
            os.path.isfile(self._fq_infilename))

    def is_type(self):
        return False
