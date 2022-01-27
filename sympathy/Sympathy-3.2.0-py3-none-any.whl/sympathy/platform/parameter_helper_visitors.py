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
from sympathy.utils.context import trim_doc
from sympathy.utils.context import indent_doc


class IParameterVisitor(object):
    def visit_root(self, root):
        pass

    def visit_group(self, group):
        pass

    def visit_page(self, page):
        pass

    def visit_integer(self, value):
        pass

    def visit_float(self, value):
        pass

    def visit_string(self, value):
        pass

    def visit_boolean(self, value):
        pass

    def visit_datetime(self, value):
        pass

    def visit_list(self, plist):
        pass

    def visit_json(self, value):
        pass

    def visit_custom(self, custom):
        pass


class ShowParameterVisitor(object):
    """
    Builds a string of all visited parameter leaf entities, the string result
    is available in instance.result. The format of the string compatible with
    the documentation format used, and is valid Restructured Text.

    This useful for generating the documentation for the configuration options.
    """
    def __init__(self):
        self.result = None

    def visit_root(self, root):
        self.visit_group(root)

    def visit_group(self, group):
        results = []
        for item in group.children():
            visitor = ShowParameterVisitor()
            item.accept(visitor)
            results.append(visitor.result)
        self.result = u'\n'.join(results)

    def visit_page(self, page):
        self.visit_group(page)

    def visit_integer(self, value):
        self.visit_value(value)

    def visit_float(self, value):
        self.visit_value(value)

    def visit_string(self, value):
        self.visit_value(value)

    def visit_boolean(self, value):
        self.visit_value(value)

    def visit_datetime(self, value):
        self.visit_value(value)

    def visit_connection(self, value):
        self.visit_value(value)

    def visit_json(self, value):
        self.visit_value(value)

    def visit_list(self, plist):
        self.visit_value(plist)

    def visit_value(self, value):
        self.result = u'**{}** ({})\n{}'.format(
            value.label or '(no label)',
            value.name,
            indent_doc(
                trim_doc(value.description or '(no description)'), 4))


class ReorderVisitor(IParameterVisitor):
    """Order elements."""
    def visit_root(self, root):
        self.visit_group(root)

    def visit_group(self, group):
        group.reorder()
        for item in group.children():
            item.accept(self)

    def visit_page(self, page):
        self.visit_group(page)
