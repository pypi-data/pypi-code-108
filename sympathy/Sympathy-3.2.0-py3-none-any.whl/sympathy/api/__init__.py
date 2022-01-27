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
"""The Sympathy for Data API."""

# Node API, for implementing library modules.
from .. platform import node

# Node parameter API, for accessing fields and building the structure.
# Also available from node.parameters
from .. platform.parameter_helper_gui import ParameterView
from .. platform.parameter_helper_gui import sy_parameters as parameters

# Data type utility modules.
from .. typeutils import adaf
from .. typeutils import datasource
from .. typeutils import table
from .. typeutils import text
from .. typeutils import report
from .. typeutils import figure
from .. typeutils import json

# Data type utility wrapper modules.
from .. common import adaf_wrapper
from .. common import table_wrapper
from .. common import fx_wrapper
from .. common import fx_wrapper as fx

# For defining Data type utility modules.
from .. import types

# For using QT (to create GUI:s, etc.). Use this to ensure compatibility
# Old compat api.
from .. platform import qt_compat as qt

# For using QT (to create GUI:s, etc.). Use this to ensure compatibility
from .. platform import qt_compat2 as qt2

# Node generator functions
from .. utils import node_helper

# Helper functions for working with numpy dtypes
from .. utils import dtypes

# Helper functions for working with numpy masked arrays
from .. utils import masked


from .. utils.filebase import from_type


__all__ = ['node', 'parameters', 'ParameterView', 'adaf', 'datasource',
           'table', 'text', 'report', 'figure', 'json', 'adaf_wrapper',
           'table_wrapper', 'fx_wrapper', 'fx', 'types',
           'qt', 'qt2', 'node_helper', 'dtypes', 'masked', 'from_type']
