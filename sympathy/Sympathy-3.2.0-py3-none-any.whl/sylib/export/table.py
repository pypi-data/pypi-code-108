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
import os
from sympathy.api import exporters
from sympathy.api.exceptions import sywarn, NoDataError


class TableDataExporterBase(exporters.DataExporterBase):

    @staticmethod
    def plugin_base_name():
        return 'Export Table'

    def create_filenames(self, input_list, filename, *args):
        """
        Base implementation of create_filenames.
        Please override for custom behavior.
        """
        if not self.file_based():
            return super(exporters.TableDataExporterBase,
                         self).create_filenames(input_list, filename)

        elif ('table_names' in self._parameters and
                self._parameters['table_names'].value):
            ext = self._parameters['filename_extension'].value
            if ext != '':
                ext = '{}{}'.format(os.path.extsep, ext)
            try:
                filenames = [u'{}{}'.format(
                    t.get_name(), ext) for t in input_list
                    if t.get_name() is not None]

                if len(set(filenames)) == len(input_list):
                    return (filename for filename in filenames)
                else:
                    sywarn(
                        'The Tables in the incoming list do not '
                        'have unique names. The table names are '
                        'therefore not used as filenames.')
            except (IOError, OSError, NoDataError):
                pass

        return super(TableDataExporterBase, self).create_filenames(
            input_list, filename, *args)
