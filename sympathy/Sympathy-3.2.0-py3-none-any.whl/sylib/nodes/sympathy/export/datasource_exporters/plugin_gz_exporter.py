# This file is part of Sympathy for Data.
# Copyright (c) 2015, 2017 Combine Control Systems AB
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
import gzip
from sympathy.api.exceptions import SyDataError
from sylib.export import datasource as exportdatasource


class DataExtractGz(exportdatasource.DatasourceArchiveBase):
    """Extractor for GZIP files."""

    EXPORTER_NAME = "GZIP Extractor"
    FILENAME_EXTENSION = None

    @staticmethod
    def hide_filename():
        return True

    def export_data(self, in_datasource, filename, progress=None):
        gz_file = in_datasource.decode_path()
        try:
            with gzip.open(gz_file, 'rb') as f:
                content = f.read()
        except gzip.BadGzipFile as e:
            raise SyDataError(
                f'Error extracting, due to: {e}.')
        with open(filename, 'wb') as f:
            f.write(content)
        return [filename]

    def create_filenames(self, input_list, filename, *args):
        return [os.path.splitext(os.path.basename(path.decode_path()))[0]
                for path in input_list]
