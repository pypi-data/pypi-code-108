# This file is part of Sympathy for Data.
# Copyright (c) 2020 Combine Control Systems AB
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
import sys
import json
from sympathy.utils import prim


_external_config = None
_internal_config = None


def external():
    global _external_config
    if _external_config is None:
        try:
            path = os.path.join(sys.prefix, '..', 'InstallConfig.json')
            with open(path) as f:
                _external_config = json.load(f)
        except Exception:
            _external_config = False
    return _external_config or None


def config():
    global _internal_config
    if _internal_config is None:
        _internal_config = prim.config()
    return _internal_config


def active():
    _external_config = external()
    if _external_config:
        return _external_config
    else:
        return config()
