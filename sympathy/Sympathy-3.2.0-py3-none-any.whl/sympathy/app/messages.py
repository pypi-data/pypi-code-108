# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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
import uuid
import enum
import weakref
import datetime
import collections
from typing import Any


class Levels(enum.Enum):
    notice = 'Notice'
    warning = 'Warning'
    error = 'Error'
    exception = 'Exception'


class DisplayMessage:
    """
    Message to show in messages view or terminal.
    """

    _type = 'text'

    def __init__(
            self, *,
            title: str = None,
            level: Levels = None,
            brief: str = None,
            details: str = None,
            source: str = None,
            node: 'NodeInterface' = None,
            id: Any = None,
            type: str = None,
    ):
        self._time = datetime.datetime.now()
        self._title = title
        self._level = level or Levels.notice
        self._brief = brief
        self._details = details
        self._source = source or title
        self._node = None
        if node:
            self._node = weakref.ref(node)
        self._id = id or str(uuid.uuid4())
        if type:
            self._type = type

    def time(self) -> datetime.datetime:
        return self._time

    def level(self) -> Levels:
        return self._level

    def source(self) -> str:
        return self._source

    def id(self) -> Any:
        return self._id

    def title(self) -> str:
        return self._title

    def brief(self) -> str:
        return self._brief

    def details(self) -> str:
        return self._details

    def node(self) -> 'NodeInterface':
        if self._node:
            return self._node()

    def type(self) -> str:
        """
        Customize view in Message View, text representation is still needed for
        command line interface.
        """
        return self._type


class NodeMessage(DisplayMessage):

    def __init__(self, *, title=None, id=None, node=None, source=None,
                 **kwargs):
        source = source or node.full_uuid
        title = title or node.name
        super().__init__(id=id, title=title, source=source, node=node,
                         **kwargs)


class StreamMessage(NodeMessage):
    _type = 'stream'


class ResultMessage(DisplayMessage):
    def __init__(self, *, result=None, title=None, node=None, source=None,
                 id=None, **kwargs):
        if node is not None:
            source = source or node.full_uuid
            title = title or node.name
        if id is None:
            self._id = result.id
        super().__init__(title=title, source=source, node=node, id=id,
                         **kwargs)

    def id(self):
        return self._id


class ErrorResultMessageBuilder:
    # Could be a function, the class is only for the signature.
    # Functions can not be subclassed.
    def build(self, *, error, result, title, level, brief, details,
              **kwargs) -> ResultMessage:
        return ResultMessage(
            result=result,
            title=title,
            level=Levels.error,
            brief=brief,
            details=details,
            **kwargs)


_default_error_result_message_builder = ErrorResultMessageBuilder()
_error_result_message_builders = collections.defaultdict(
    lambda: _default_error_result_message_builder)


def register_error_result_message_builder(error_type, builder):
    _error_result_message_builders[error_type] = builder


def error_result_message_builder(error):
    return _error_result_message_builders[type(error)]
