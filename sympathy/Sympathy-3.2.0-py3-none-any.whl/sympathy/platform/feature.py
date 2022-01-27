# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
import typing as _t
import pkg_resources as _pkg_resources
from Qt import QtCore
from Qt import QtWidgets
from . import plugins


# Preference section interface:


class PreferenceSection(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def save(self) -> str:
        pass

    def name(self) -> str:
        return ''

    def update_data(self):
        return


# Features interface:

class Features(QtCore.QObject):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    @property
    def name(self) -> str:
        return ""

    @property
    def description(self) -> str:
        return ""

    def start(self):
        pass

    def stop(self):
        pass

    def is_active(self, feature) -> bool:
        return False

    def preference_sections(self) -> _t.List[PreferenceSection]:
        return []

    def message(self) -> str:
        return ""

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()


# Package interface:

def manager() -> Features:
    raise NotImplementedError()


def worker() -> Features:
    raise NotImplementedError()


def license_info() -> dict:
    """
    Return feature license info, similar to version.license_info().
    """
    return {}


def third_party_license_info() -> {}:
    """
    Return feature third party license info
    """
    return {'licenses': []}


# Feature plugins:

_identifier = 'sympathy.feature.plugins'
_features = plugins.Plugin(_identifier, _t.Any)


def available_features(load=True):
    if load:
        features = _features.plugins().values()
        for e in _features.errors().values():
            raise e
        return features
    else:
        return _features.entry_points().values()


# Utilities:


def satisfies(required):
    return all(any(f.instance().is_active(r)
                   for f in available_features()) for r in required)
