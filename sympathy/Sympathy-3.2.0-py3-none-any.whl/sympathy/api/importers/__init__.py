# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
from ... dataimporters.base import (
    available_plugins,
    plugin_for_file,
    configuration_widget,
    IDataImporter,
    ADAFDataImporterBase,
    TableDataImporterBase,
    TextDataImporterBase,
    JsonDataImporterBase,
    AutoImporterMixin,
    DATASOURCE,
    IDataSniffer)

# TODO(erik): Deprecate use of base (full, internal) api.
from ... dataimporters import base

__all__ = [
    'available_plugins',
    'plugin_for_file',
    'configuration_widget',
    'IDataImporter',
    'ADAFDataImporterBase',
    'TableDataImporterBase',
    'TextDataImporterBase',
    'JsonDataImporterBase',
    'AutoImporterMixin',
    'DATASOURCE',
    'IDataSniffer',
    'base',
]
