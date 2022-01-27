# This file is part of Sympathy for Data.
# Copyright (c) 2015, 2017, Combine Control Systems AB
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
import gzip
from sylib.export import datasource as importdatasource


class DataArchiveGz(importdatasource.DatasourceArchiveBase):
    """Compressor for GZIP files"""

    EXPORTER_NAME = "GZIP Compressor"
    FILENAME_EXTENSION = 'gz'

    @staticmethod
    def hide_filename():
        return True

    def export_data(self, in_datasource, filename, progress=None):
        in_file = in_datasource.decode_path()
        with open(in_file, 'rb') as i_f, gzip.open(filename, 'wb') as o_f:
            shutil.copyfileobj(i_f, o_f)
        return [filename]

    def create_filenames(self, input_list, filename, *args):
        return ['{}.{}'.format(
            os.path.basename(path.decode_path()), self.FILENAME_EXTENSION)
                for path in input_list]
