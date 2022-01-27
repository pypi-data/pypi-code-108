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
import tarfile
from sylib.export import datasource as importdatasource


class DataArchiveTar(importdatasource.DatasourceArchiveBase):
    """Archiver for TAR files. Takes all datasources in input and puts
    them in one (uncompressed) TAR file. Folder structure is discarded.
    """

    EXPORTER_NAME = "TAR Archiver"
    FILENAME_EXTENSION = 'tar'

    @staticmethod
    def hide_filename():
        return False

    def export_data(self, in_datasources, location, progress=None):
        if len(in_datasources):
            with tarfile.open(location, 'w') as f:
                for ds in in_datasources:
                    path = ds.decode_path()
                    f.add(path, os.path.basename(path))
        return [location]

    def create_filenames(self, input_list, filename, *args):
        return super(DataArchiveTar, self).create_filenames(
            input_list, filename, *args)

    def cardinality(self):
        return self.many_to_one
