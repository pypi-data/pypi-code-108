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
from sympathy.api import exporters
from sympathy.api import node as synode
import sylib.table_sources


class DataExportText(exporters.TextDataExporterBase):
    """Exporter for Text files."""
    EXPORTER_NAME = "Text"
    FILENAME_EXTENSION = "txt"

    def __init__(self, parameters):
        super().__init__(parameters)
        if 'encoding' not in parameters:
            parameters.set_string(
                'encoding', label='Output encoding',
                description='Encoding to use for created file',
                editor=synode.Util.combo_editor(
                    options=list(
                        sylib.table_sources.CODEC_LANGS.keys())),
                value='UTF-8')

    def parameter_view(self, node_context_input):
        return self._parameters['encoding'].gui()

    def create_filenames(self, input_list, filename, *args):
        return super(DataExportText, self).create_filenames(
            input_list, filename, *args)

    def export_data(self, in_sytext, fq_outfilename,
                    **kwargs):
        encoding = sylib.table_sources.CODEC_LANGS[
            self._parameters['encoding'].value]

        with open(fq_outfilename, 'w', encoding=encoding, newline="") as f:
            f.write(in_sytext.get())
