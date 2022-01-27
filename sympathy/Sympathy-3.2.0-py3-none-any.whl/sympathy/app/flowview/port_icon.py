# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
import svgutils
import os
from sympathy.platform import types
from ..util import icon_path


def icon(datatype, icons):
    root = _Node()
    _tokenize(root, datatype, icons)
    return(_build_icon(root.list()))


_HEIGHT = '16'
_unknown = icon_path('ports/unknown.svg')
_lambda = icon_path('ports/lambda.svg')
_comma = icon_path('ports/comma.svg')
_left_bracket = icon_path('ports/left_bracket.svg')
_right_bracket = icon_path('ports/right_bracket.svg')
_left_brace = icon_path('ports/left_brace.svg')
_right_brace = icon_path('ports/right_brace.svg')
_left_paren = icon_path('ports/left_parenthesis.svg')
_right_paren = icon_path('ports/right_parenthesis.svg')
_list = 'list'
_tuple = 'tuple'
_dict = 'dict'


class _Node(object):
    def __init__(self, data=None):
        super(_Node, self).__init__()
        self._data = data
        self._children = []

    def add_child(self, data):
        node = _Node(data)
        self._children.append(node)
        return node

    def list(self):
        """Post order traversal."""
        ll = []
        for child in self._children:
            ll.extend(child.list())
        if len(self._children) == 0:
            if self._data is None:
                ll.append(_unknown)
            elif not os.path.isabs(self._data):
                ll.append(icon_path(self._data))
            else:
                ll.append(self._data)
        elif self._data == _list:
            ll.insert(0, _left_bracket)
            ll.append(_right_bracket)
        elif self._data == _tuple:
            ll.insert(0, _left_paren)
            ll.append(_right_paren)
        elif self._data == _dict:
            ll.insert(0, _left_brace)
            ll.append(_right_brace)
        return ll


def _build_icon(symbols):
    svg = svgutils.transform.SVGFigure(1, 1)
    offset = 0
    for s in symbols:
        try:
            element = svgutils.transform.fromfile(s)
            height = float(element.get_size()[1])
            if int(height) != int(_HEIGHT):
                scale = float(_HEIGHT) / height
                length = int(_HEIGHT)
            else:
                scale = 1
                length = int(element.get_size()[0])
            root = element.getroot()
            root.moveto(offset, 0, scale)
            svg.append(root)
            offset += length
        except (OSError, IOError):
            continue
    if offset != 0:
        svg.set_size((str(offset), _HEIGHT))
        # The viewbox attribute in the generated SVG's are
        # incorrect. Due to spelling misstake in svgutil-0.2.2 this
        # was never a problem. In later svgutils this spelling have
        # been corrected and thus now give incorrect SVG's.
        #
        # Ugly hack: replace "viewBox" with "ignored_viewbox" fixes
        # the problem for now
        as_str = svg.to_str()
        as_str = as_str.replace(b'ASCII', b'UTF-8')
        as_str = as_str.replace(b'viewBox', b'ignored_viewbox')
        return as_str

    with open(_unknown, 'rb') as file:
        return file.read()


def _tokenize(node, datatype, icons):
    if isinstance(datatype, types.TypeAlias):
        try:
            node = node.add_child(icons[str(datatype)])
        except KeyError:
            # Datatype is missing
            node = node.add_child(_unknown)
    elif isinstance(datatype, types.TypeFunction):
        node = node.add_child(_lambda)
    elif isinstance(datatype, types.TypeGeneric):
        node = node.add_child(_unknown)
    elif isinstance(datatype, types.TypeList):
        node = node.add_child(_list)
        for item in datatype.items():
            _tokenize(node, item, icons)
    elif isinstance(datatype, types.TypeDict):
        node = node.add_child(_dict)
        item = datatype.element()
        if item is not None:
            _tokenize(node, item, icons)
    elif isinstance(datatype, types.TypeTuple):
        node = node.add_child(_tuple)
        for i, item in enumerate(datatype):
            if i > 0:
                node.add_child(_comma)
            _tokenize(node, item, icons)
    return node
