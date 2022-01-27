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
"""Interfaces for Messages Window."""
import enum
import typing
import dataclasses
from Qt import QtCore
from Qt import QtWidgets
from .. messages import DisplayMessage


@dataclasses.dataclass
class Store:
    """
    Extra indirection to prevent Qt from trying to copy or keep track of
    the list content.
    """
    data: typing.Any


class MessageItemRoles(enum.IntEnum):
    """
    Roles for associating item data.

    message: DisplayMessage, the original message.
    text:  str, the main text shown.
    store: Store, custom data store.
    """
    (message,
     text,
     store,
     archived,
     root_uuid,
     full_uuid) = range(QtCore.Qt.UserRole, QtCore.Qt.UserRole + 6)


class DetailsWidget(QtWidgets.QWidget):
    """
    Baseclass for DetailsWidgets.

    Associated item data can be stored using item.setData(role, value)
    See MessageItemRoles.
    """

    _type = None
    requested_remove = QtCore.Signal(QtWidgets.QListWidgetItem)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._item = None

    def type(self) -> str:
        """
        Return type of messages handled by this DetailsWidget.
        """
        assert self._type
        return self._type

    def clear(self) -> None:
        """
        Clear signalled. Perform cleanup before the associated item is removed.
        """
        self._item = None

    def _remove(self) -> None:
        """
        Request the associated to be removed by emitting requested_remove with
        the current item.
        """
        self.requested_remove.emit(self._item)

    def add_display_message(self, item: QtWidgets.QListWidgetItem,
                            message: DisplayMessage) -> None:
        """
        Called when new message is received. Item is the associated item
        newly created or pre-existing.
        """
        pass

    def text(self, item: QtWidgets.QListWidgetItem) -> str:
        """
        Textual representation for item.
        """
        self._item = item
        item.setData(MessageItemRoles.text, self.text())

    def update_data(self, item: QtWidgets.QListWidgetItem) -> None:
        """
        Called when item is selected.
        """
        self._item = item
        item.setData(MessageItemRoles.text, self.text())
