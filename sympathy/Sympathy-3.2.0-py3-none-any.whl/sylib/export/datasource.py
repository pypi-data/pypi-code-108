# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
from sympathy.api.exceptions import sywarn


class DatasourceArchiveBase(exporters.DatasourceDataExporterBase):

    def __init__(self, parameters, archive_type=None):
        super(DatasourceArchiveBase, self).__init__(parameters)

    @staticmethod
    def plugin_base_name():
        return 'Export Datasource'

    def warn_invalid(self, in_datasource):
        sywarn(u'{} is not a valid {} file'.format(
               in_datasource.decode_path(), self.EXPORTER_NAME))
