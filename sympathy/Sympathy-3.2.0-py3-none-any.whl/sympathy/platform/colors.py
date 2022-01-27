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
from sympathy.platform import qt_compat2
QtGui = qt_compat2.import_module('QtGui')

DEFAULT_TEXT_COLOR = QtGui.QColor.fromRgb(0, 0, 0)
DEFAULT_BG_COLOR   = QtGui.QColor.fromRgb(255, 255, 255)
WARNING_BG_COLOR   = QtGui.QColor.fromRgb(254, 217, 166)
WARNING_TEXT_COLOR = QtGui.QColor.fromRgb(0, 0, 0)
DANGER_BG_COLOR    = QtGui.QColor.fromRgb(251, 180, 174)
DANGER_TEXT_COLOR  = QtGui.QColor.fromRgb(0, 0, 0)

DANGER_TEXT_NORMAL_BG_COLOR    = QtGui.QColor.fromRgb(139, 0, 0)
