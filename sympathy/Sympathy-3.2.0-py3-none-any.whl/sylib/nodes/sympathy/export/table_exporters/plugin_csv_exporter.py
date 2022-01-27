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
import collections
import csv
import io
from sympathy.api import qt2 as qt_compat
from sylib.export import table as exporttable
from sympathy.api import node as synode

QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


# We are currently unable to support UTF-16 encodings since this plugin uses
# pythons csv module and from python docs
# (https://docs.python.org/2/library/csv.html#examples):
#
#     The csv module doesn't directly support reading and writing Unicode, but
#     it is 8-bit-clean save for some problems with ASCII NUL characters. So
#     you can write functions or classes that handle the encoding and decoding
#     for you as long as you avoid encodings like UTF-16 that use NULs. UTF-8
#     is recommended.
#
# So if we ever want to support UTF-16 we would have to use a different
# backend.
CODEC_LANGS = collections.OrderedDict((
    ('Western (ASCII)', 'ascii'),
    ('Western (ISO 8859-1)', 'iso8859_1'),
    ('Western (ISO 8859-15)', 'iso8859_15'),
    ('Western (Windows 1252)', 'windows-1252'),
    ('UTF-8', 'utf_8'),
    ('UTF-8 with signature byte', 'utf_8_sig')
))


def _pandas_to_csv(tabledata, fq_outfilename, header, encoding, delimiter,
                   quotechar):
    tabledata.to_dataframe().to_csv(fq_outfilename,
                                    sep=delimiter,
                                    index=False,
                                    quotechar=quotechar,
                                    doublequote=True,
                                    quoting=csv.QUOTE_MINIMAL,
                                    encoding=encoding)


class DataExportCSVWidget(QtWidgets.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, *args, **kwargs):
        super(DataExportCSVWidget, self).__init__(*args, **kwargs)
        self._parameter_root = parameter_root
        self._init_gui()

    def _init_gui(self):
        table_names_gui = self._parameter_root['table_names'].gui()
        table_names_gui.valueChanged.connect(self._filename_changed)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._parameter_root['encoding'].gui())
        vlayout.addWidget(table_names_gui)
        vlayout.addWidget(self._parameter_root['header'].gui())
        vlayout.addWidget(self._parameter_root['fast'].gui())
        self.setLayout(vlayout)

    def _filename_changed(self):
        self.filename_changed.emit()


class DataExportCSV(exporttable.TableDataExporterBase):
    """Exporter for CSV files."""
    EXPORTER_NAME = "CSV"
    FILENAME_EXTENSION = "csv"

    def __init__(self, parameters):
        super(DataExportCSV, self).__init__(parameters)
        if 'table_names' not in parameters:
            parameters.set_boolean(
                'table_names', label='Use table names as filenames',
                description='Use table names as filenames')

        if 'header' not in parameters:
            parameters.set_boolean(
                'header', value=True, label='Export header',
                description='Export column names')

        if 'encoding' not in parameters:
            parameters.set_list(
                'encoding', label='Character encoding',
                list=CODEC_LANGS.keys(), value=[4],
                description='Character encoding determines how different '
                            'characters are represented when written to disc, '
                            'sent over a network, etc.',
                editor=synode.Util.combo_editor())

        if 'fast' not in parameters:
            parameters.set_boolean(
                'fast', value=False, label='Use fast exporter',
                description=('Fast exporter uses pandas and may produce '
                             'different results than the default one.'))

    def parameter_view(self, node_context_input):
        return DataExportCSVWidget(self._parameters)

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        """Export Table to CSV."""
        header = self._parameters['header'].value

        delimiter = ';'
        quotechar = '"'
        encoding = CODEC_LANGS[
            self._parameters['encoding'].selected]

        kwargs = {
            'header': header, 'encoding': encoding,
            'delimiter': delimiter, 'quotechar': quotechar}

        if self._parameters['fast'].value:
            _pandas_to_csv(in_sytable, fq_outfilename, **kwargs)
        else:
            in_sytable.to_csv(fq_outfilename, **kwargs)
