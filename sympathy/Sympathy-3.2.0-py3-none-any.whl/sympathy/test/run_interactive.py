# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import copy
import unittest
import traceback
from nose.plugins.attrib import attr
from Qt import QtWidgets

from sympathy.utils.prim import limit_traceback
from sympathy.utils import prim
import sympathy.app.interactive


def diff_print(a, b, depth=0):
    pad = '-'*depth*2
    if isinstance(a, dict):
        for key in set(a.keys()) | set(b.keys()):
            if key not in a:
                print('{}Key {} missing in a'.format(pad, key))
            elif key not in b:
                print('{}Key {} missing in b'.format(pad, key))
            elif a[key] != b[key]:
                print('{}{}'.format(pad, key))
                diff_print(a[key], b[key], depth=depth+1)
    elif a != b:
        print('{}Different values: {} vs. {}'.format(pad, a, b))


class InteractiveTestBase(unittest.TestCase):
    """
    Library tests using interactive.

    Add your library tests and node unit tests bellow or in a separate file
    with a similar base.
    """

    library_id = None

    def setUp(self):
        self.library = sympathy.app.interactive.load_library(library_id=self.library_id)

    @attr('gui')
    def test_library_widgets(self):
        """
        Test that all configuration widgets can be created without errors.
        """
        failed = []
        tracebacks = {}
        nodeids = self.library.nodeids()
        qapp = QtWidgets.QApplication.instance()

        for nodeid in nodeids:
            try:
                testnode = self.library.node(nodeid)
                widget = testnode._SyiNode__configure_widget()
                qapp.processEvents()
                if hasattr(widget, 'cleanup'):
                    widget.cleanup()
                widget.deleteLater()
                qapp.processEvents()
            except sympathy.app.interactive.InteractiveNotNodeError:
                pass
            except:
                tb = traceback.format_exception(*sys.exc_info())
                filename = os.path.basename(testnode.filename)
                tb = limit_traceback(tb, filename=filename)

                tracebacks[nodeid] = tb
                failed.append(nodeid)

                print('{}\n{}:\n\n{}'.format('-' * 30, nodeid, tb))

        print('=' * 30)
        print('({}/{}) configuration GUIs failed:\n{}'.format(
            len(failed), len(nodeids), '\n'.join(failed)))

        assert(not len(tracebacks))

    @unittest.skip('No longer needed?')
    @attr('gui')
    def test_library_widgets_modify_parameters(self):
        """
        Test that config widgets don't modify their parameters during init.
        """
        failed = []
        tracebacks = {}
        nodeids = self.library.nodeids()
        qapp = QtWidgets.QApplication.instance()

        for nodeid in nodeids:
            try:
                testnode = self.library.node(nodeid)
                tags = testnode._SyiNode__node.tags
                if any(str(t) == 'Hidden.Deprecated' for t in tags):
                    continue
                node_context = testnode._SyiNode__build_node_context()
                adjusted = testnode._SyiNode__adjust_parameters(node_context)
                if adjusted is not None:
                    node_context = adjusted
                try:
                    old_parameters = copy.deepcopy(
                        node_context.parameters._parameter_dict)
                except AttributeError:
                    old_parameters = copy.deepcopy(
                        node_context.parameters)
                widget = testnode._SyiNode__configure_widget(
                    node_context=node_context)
                qapp.processEvents()
                # Force widget to save parameters in node_context:
                if hasattr(widget, 'save_parameters'):
                    widget.save_parameters()
                qapp.processEvents()
                if hasattr(widget, 'cleanup'):
                    widget.cleanup()
                qapp.processEvents()
                try:
                    new_parameters = node_context.parameters._parameter_dict
                except AttributeError:
                    new_parameters = node_context.parameters
                # self.assertEqual(old_parameters, new_parameters)
                if new_parameters != old_parameters:
                    failed.append(nodeid)
                    print('{}\n{}:\n\n'.format('-' * 30, nodeid))
                    diff_print(new_parameters, old_parameters)
                widget.deleteLater()
                qapp.processEvents()
            except:
                tb = traceback.format_exception(*sys.exc_info())
                tb = ''.join(tb)

                tracebacks[nodeid] = tb
                print('{}\n{}:\n\n{}'.format('-' * 30, nodeid, tb))

        print('=' * 30)
        print('({}/{}) configuration GUIs modified their parameters.'.format(
            len(failed), len(nodeids)))
        print('({}/{}) configuration GUIs failed to open.'.format(
            len(tracebacks), len(nodeids)))
        print('The following configuration GUIs modified their '
              'parameters:\n{}'.format('\n'.join(failed)))

        # This number should be decreased as nodes are fixed to ensure that we
        # eventually reach and keep it at zero.
        assert(len(failed) + len(tracebacks) <= 34)
