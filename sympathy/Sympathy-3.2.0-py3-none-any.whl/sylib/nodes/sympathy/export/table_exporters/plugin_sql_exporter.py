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
import sys
from sylib.export import table as exporttable
from sylib import url
from sylib import odbc
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api import qt2 as qt_compat
from sympathy.utils import credentials
from sympathy.utils import parameters as utils_parameters
from sympathy.api.exceptions import SyDataError
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')
sql = table.table_sql()

_legacy_sqlalchemy_str = 'db_sqlalchemy_engine_url'
_legacy_odbc_str = 'connection_string'


class DataExportSQLWidget(QtWidgets.QWidget):
    def __init__(self, parameters, node_context_input):
        super(DataExportSQLWidget, self).__init__()
        self._parameters = parameters
        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        odbc_vlayout = QtWidgets.QVBoxLayout()
        sqlalchemy_vlayout = QtWidgets.QVBoxLayout()
        drop_table = self._parameters['drop_table'].gui()
        use_nvarch = self._parameters['use_nvarchar_size'].gui()

        self._sqlalchemy_group = QtWidgets.QGroupBox('SQLAlchemy settings')
        self._sqlalchemy_group.setLayout(sqlalchemy_vlayout)
        self._odbc_group = QtWidgets.QGroupBox('ODBC settings')
        self._odbc_group.setLayout(odbc_vlayout)

        self._db_methods = dict(
            zip(_db_modes,
                [[self._odbc_group, drop_table, use_nvarch],
                 # Table creation is not yet implemented for
                 # SQLAlchemy.
                 [self._sqlalchemy_group]]))

        self._db_method = (
            self._parameters['db_method'].gui())

        self._odbc_connection_widget = self._parameters[
            utils_parameters.odbc_connection_name].gui()

        odbc_vlayout.addWidget(self._parameters['odbc'].gui())
        odbc_vlayout.addWidget(self._odbc_connection_widget)

        self._sqlalchemy_connection_widget = self._parameters[
            utils_parameters.sqlalchemy_connection_name].gui()
        sqlalchemy_vlayout.addWidget(self._sqlalchemy_connection_widget)

        vlayout.addWidget(self._db_method)
        vlayout.addWidget(self._sqlalchemy_group)
        vlayout.addWidget(self._odbc_group)

        vlayout.addWidget(self._parameters['table_name'].gui())
        vlayout.addWidget(drop_table)
        vlayout.addWidget(use_nvarch)
        self.setLayout(vlayout)

        self._db_method_changed(self._parameters['db_method'].value)
        self._db_method.valueChanged.connect(
            self._db_method_changed)

        self._odbc_connection_widget.valueChanged.connect(
            self._odbc_connection_changed)
        self._sqlalchemy_connection_widget.valueChanged.connect(
            self._sqlalchemy_connection_changed)

    def _store_legacy_parameter(self, connection_widget, string_parameter):
        utils_parameters.set_string_from_connection(
            connection_widget.editor().parameter_model, string_parameter)

    def _sqlalchemy_connection_changed(self):
        self._store_legacy_parameter(
            self._sqlalchemy_connection_widget,
            self._parameters[_legacy_sqlalchemy_str])

    def _odbc_connection_changed(self):
        self._store_legacy_parameter(
            self._odbc_connection_widget,
            self._parameters[_legacy_odbc_str])

    def _db_method_changed(self, value):
        for key, db_method in self._db_methods.items():
            for item in db_method:
                item.setEnabled(key == value)


_sqlalchemy_mode = 'SQLAlchemy'
_odbc_mode = 'ODBC'
_db_modes = [_odbc_mode, _sqlalchemy_mode]


class DataExportSQL(exporttable.TableDataExporterBase):
    """
    Exporter for SQL files.

    If URL the resource contains credential variables for login or token
    credentials these will be entered as part of the URL.

    See :ref:`Credentials Preferences<preferences_credentials>` for more info.
    """

    EXPORTER_NAME = "SQL"
    FILENAME_EXTENSION = ""

    def __init__(self, parameters):
        super(DataExportSQL, self).__init__(parameters)
        self._init_parameters()

    def _init_parameters(self):
        if 'table_name' not in self._parameters:
            self._parameters.set_string(
                'table_name', label='Table name',
                description='The table name used when exporting.')

        if _legacy_odbc_str not in self._parameters:
            self._parameters.set_string(
                _legacy_odbc_str, label='Connection string',
                description=(
                    'String used by pyodbc to make a connection.'))

        if 'drop_table' not in self._parameters:
            self._parameters.set_boolean(
                'drop_table', label='Drop table',
                description='Drop table before adding data.')

        if 'use_nvarchar_size' not in self._parameters:
            self._parameters.set_boolean(
                'use_nvarchar_size', label='Use nvarchar(size)',
                description='Use nvarchar(size) instead of nvarchar(MAX).')

        if 'odbc' not in self._parameters:
            self._parameters.set_list(
                'odbc', ['default', 'pyodbc', 'ceODBC'],
                label='ODBC method', order=0,
                description='ODBC method to use.', value=[0],
                editor=synode.Util.combo_editor())

        if 'db_method' not in self._parameters:
            self._parameters.set_string(
                'db_method',
                label='Database connection method',
                editor=synode.Util.combo_editor(options=_db_modes),
                value=_db_modes[0],
                description=(
                    'Select which Database connection method that you want to '
                    'use.'))

        if _legacy_sqlalchemy_str not in self._parameters:
            self._parameters.set_string(
                _legacy_sqlalchemy_str, label='SQLAlchemy engine URL',
                value='mssql+pyodbc:///',
                description=(
                    'SQLAlchemy engine URL for connecting to the database.'))

        for new_key, old_key, setter in [
                (utils_parameters.odbc_connection_name, _legacy_odbc_str,
                 utils_parameters.set_odbc_connection),
                (utils_parameters.sqlalchemy_connection_name,
                 _legacy_sqlalchemy_str,
                 utils_parameters.set_sqlalchemy_connection),
        ]:
            if new_key not in self._parameters:
                setter(self._parameters)
                try:
                    old_parameter = self._parameters[old_key]
                    new_parameter = self._parameters[new_key]
                    utils_parameters.set_connection_from_string(
                        old_parameter, new_parameter)
                except KeyError:
                    pass

    @staticmethod
    def file_based():
        return False

    def parameter_view(self, node_context_input):
        return DataExportSQLWidget(
            self._parameters, node_context_input)

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        """Export Table to SQL."""
        table_name = self._parameters.value_or_default(
            'table_name', 'test')
        drop_table = self._parameters.value_or_default(
            'drop_table', False)
        use_nvarchar_size = self._parameters.value_or_default(
            'use_nvarchar_size', False)

        try:
            odbc_name = self._parameters['odbc'].selected
        except KeyError:
            odbc_name = 'odbc'

        db_method = self._parameters.value_or_default(
            'db_method', _odbc_mode)

        assert db_method in _db_modes, f'Unknown Database: {db_method}'

        interface_args = []
        if db_method == _odbc_mode:
            parameter = utils_parameters.odbc_connection_name
            expand_login = odbc.expand_login
            interface_factory = sql.get_interface_odbc
            interface_args = [odbc_name]
        elif db_method == _sqlalchemy_mode:
            parameter = utils_parameters.sqlalchemy_connection_name
            expand_login = url.expand_login
            interface_factory = sql.get_interface_sqlalchemy

        connection_dict = self._parameters[parameter].value
        resource = credentials.get_credentials_expanded_resource(
            self.node(), connection_dict, expand_login)
        db_interface = interface_factory(resource, *interface_args)
        if db_interface.is_null():
            print('Unsupported database', file=sys.stderr)

        try:
            db_interface.from_table(
                table_name, in_sytable, drop_table=drop_table,
                use_nvarchar_size=use_nvarchar_size)
        except KeyError:
            raise SyDataError(
                f'Selected table name: {table_name} does not exist.')
