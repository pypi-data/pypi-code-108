#!/usr/bin/env python
# -*- coding: latin-1 -*-
# Date Format: YYYY-MM-DD

"""
PIL Text Scaler:
    Automatically scale text in a PIL image to fit in an area.

https://github.com/TheElementalOfDestruction/pts
"""

# --- LICENSE.txt -----------------------------------------------------------------
#
#    Copyright 2021 Destiny Peterson and Liam Moriarty
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Destiny Peterson (The Elemental of Destruction)'
__date__ = '2021-01-24'
__version__ = '1.4.8'

from PTS.core import listFonts, loadTTF, fitText, getSize, setSize
from PTS.errors import FontError
