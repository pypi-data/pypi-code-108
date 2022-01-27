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
import tarfile
from sylib.export import datasource as exportdatasource
from sympathy.platform.exceptions import sywarn


class DataExtractTar(exportdatasource.DatasourceArchiveBase):
    """Extractor for TAR files."""

    EXPORTER_NAME = "TAR Extractor"
    FILENAME_EXTENSION = None

    @staticmethod
    def hide_filename():
        return True

    def export_data(self, in_datasource, directory, progress=None):
        file = in_datasource.decode_path()
        members = self._members(file)
        if len(members):
            tar = tarfile.TarFile(file)
            tar.extractall(directory, members)
        else:
            sywarn(file + ' is either empty or not a valid TAR file.')
        return self._create_filenames(members)

    def create_filenames(self, input_list, filename, *args):
        filenames = []
        for path in input_list:
            filenames.extend(
                self._create_filenames(self._members(path.decode_path())))
        return filenames

    def _members(self, path):
        members = []
        if os.path.isfile(path) and tarfile.is_tarfile(path):
            tar = tarfile.TarFile(path)
            member = tar.next()
            while member:
                if not member.isdir():
                    members.append(member)
                member = tar.next()
        return members

    def _create_filenames(self, members):
        return sorted([m.name for m in members])

    def cardinality(self):
        return self.one_to_many
