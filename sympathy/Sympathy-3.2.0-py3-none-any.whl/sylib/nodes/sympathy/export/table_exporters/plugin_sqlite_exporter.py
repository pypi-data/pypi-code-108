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
from sylib.export import table as exporttable
from sympathy.api import table
from sympathy.api import qt2 as qt_compat
QtGui = qt_compat.import_module('QtGui')
sql = table.table_sql()


class DataExportSQLite(exporttable.TableDataExporterBase):
    """Exporter for SQLite files."""
    EXPORTER_NAME = "SQLite"
    FILENAME_EXTENSION = "db"

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        """Export Table to SQLite."""
        db_interface = sql.SQLite3Database(fq_outfilename)
        db_interface.from_table('test', in_sytable)
