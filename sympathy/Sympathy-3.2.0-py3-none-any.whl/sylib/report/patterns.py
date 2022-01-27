# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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

import re


re_numeric = re.compile(r'-?\d+(\.\d+)?')
re_color = re.compile(r'#[0-9a-f]{6}', flags=re.IGNORECASE)
re_number_list = re.compile(r'^(-?\d+(\.\d+)?)(,\s*-?\d+(\.\d+)?)*$')
re_number_or_color_list = re.compile(r'^((-?\d+(\.\d+)?)(,\s*-?\d+(\.\d+)?)*|'
                                     '(#[0-9a-f]{6})(,\s*#[0-9a-f]{6})*)$',
                                     flags=re.IGNORECASE)

re_autogen_adaf_name = re.compile(r'^_adaf(\d+)')
