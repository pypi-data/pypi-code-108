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
import contextlib
import os
import re
import json
import datetime
import traceback
import inspect
import itertools
import builtins
import tokenize
import io
import six
import ast
import sys
import collections

import numpy as np
import pandas
import networkx as nx

from sympathy.api import qt2 as qt
from sympathy.api.nodeconfig import preview
from sympathy.platform import exceptions
from sympathy.typeutils import table
from sympathy.utils import dtypes
from sympathy.types.sygeneric import sygeneric

from sylib.calculator import plugins
from sympathy.platform import colors

QtCore = qt.QtCore
QtGui = qt.QtGui
QtWidgets = qt.QtWidgets

FUNCTION_SPLIT = '='
ENABLED_SPLIT = '#ENABLED:'

context = {'datetime': datetime,
           'np': np,
           'os': os,
           'json': json,
           'pandas': pandas,
           'six': six,
           're': re}

res_col_regex = re.compile(r"res\.col\('([^']*)'\).data")

copy_name_regex = re.compile(r"^(.* Copy) ([0-9]+)$")

fs_encoding = sys.getfilesystemencoding()


class ResCol(object):
    def __init__(self, table, name):
        self._table = table
        self._name = name

    @property
    def data(self):
        return self._table[self._name]


class ResTable(object):
    def __init__(self):
        self._cols = {}

    def __getitem__(self, col):
        return self._cols[col]

    def __setitem__(self, col, value):
        self._cols[col] = value

    def __delitem__(self, col):
        del self._cols[col]

    def __contains__(self, col):
        return col in self._cols

    def col(self, name):
        return ResCol(self, name)

    def __iter__(self):
        return iter(self._cols)


class Calc(object):

    def __init__(self, name, expr=None, enabled=False, type='calc'):
        self._name = name
        self._expr = expr
        self._enabled = enabled
        self._empty = None
        self._clean = None
        self._type = type
        self._valid = None
        self._deps = None
        self._ex = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def expr(self):
        return self._expr

    @expr.setter
    def expr(self, value):
        self._expr = value
        self._valid = None
        self._deps = None
        self._empty = None
        self._clean = None

    @property
    def is_empty(self):
        if self._empty is None:
            empty = True
            empty_tokens = {
                0: 'ENDMARKER',
                5: 'INDENT',
                6: 'DEDENT',
                4: 'NEWLINE',
                57: 'COMMENT',
                58: 'NL',
                59: 'ENCODING',
            }
            if self._expr:
                tgen = tokenize.tokenize(
                    io.BytesIO(self._expr.encode('utf8')).readline)
                tlist = []
                try:
                    tlist.extend(tgen)
                except Exception:
                    empty = False
                else:
                    empty = all(t.type in empty_tokens for t in tlist)
            self._empty = empty
        return self._empty

    @property
    def clean_expr(self):
        """
        Clean indentation from expression.
        Will set _clean as its cache.

        self._clean = False indicates that it cannot be cleaned.
        self._clean = None indicates that no cached value exists.

        Otherwise, self._clean will hold the cleaned string.
        """
        if self._clean is None:
            clean = False
            if self._expr:
                tgen = tokenize.tokenize(
                    io.BytesIO(self._expr.encode('utf8')).readline)
                tlist = []
                try:
                    tlist.extend(tgen)
                except Exception:
                    pass
                else:
                    indent_tokens = {
                        4: 'NEWLINE',
                        5: 'INDENT',
                        6: 'DEDENT',
                        57: 'COMMENT',
                        58: 'NL',
                    }
                    clean_tokens = [
                        t for t in tlist if t.type not in indent_tokens]
                    clean = tokenize.untokenize(
                        [(t.type, t.string)
                         for t in clean_tokens])
                    if isinstance(clean, bytes):
                        # Seems to depend on Python 3 version or the presence
                        # of an ENCODING token.
                        clean = clean.decode('utf8')

            self._clean = clean
        if self._clean is False or self._clean is None:
            return self._expr
        else:
            return self._clean

    @property
    def enabled(self):
        return int(self._enabled)

    @enabled.setter
    def enabled(self, value):
        self._enabled = int(value)

    @property
    def type(self):
        return self._type

    @property
    def deps(self):
        if self._deps is None:
            cols = []
            subs = []
            if self._expr and self._expr.strip():
                try:
                    expr = compile(
                        self.clean_expr, '<string>', 'eval',
                        ast.PyCF_ONLY_AST)
                    subs = [s for s in ast.walk(expr)
                            if isinstance(s, ast.Subscript)]
                except SyntaxError:
                    pass

                for sub in subs:
                    if (isinstance(sub.value, ast.Name)
                            and sub.value.id == 'res'):
                        if isinstance(sub.slice.value, ast.Str):
                            cols.append(sub.slice.value.s)
                        elif isinstance(sub.slice.value, str):
                            # Python 3.9.
                            cols.append(sub.slice.value)

            cols.extend(res_col_regex.findall(self._expr))
            self._deps = list(collections.OrderedDict.fromkeys(cols).keys())
        return self._deps

    @property
    def valid(self):
        # TODO(erik): consider setting in valid if expression forms self cycle.
        # Currently, cycle handling is all external.
        # Consider fine grained, printable exceptions.
        def check_ast(calc, ctx=None):

            def check_var(load, store, top_store, ctx):
                for l in load:
                    if (l not in store and
                            l not in [item[0] for item in inspect.getmembers(
                                builtins)] and
                            l not in ctx and
                            l not in top_store):
                        raise NameError(
                            'NameError: {} can\'t be found'.format(l))

            def find_name_errors(_ast, store, asts, ctx):
                ls = []
                ss = []

                if isinstance(_ast, ast.Name):
                    if isinstance(_ast.ctx, ast.Load):
                        ls.append(_ast.id)
                    elif isinstance(_ast.ctx, ast.Store) or isinstance(
                            _ast.ctx, ast.Param):
                        ss.append(_ast.id)
                elif hasattr(ast, 'arg') and isinstance(_ast, ast.arg):
                    ss.append(_ast.arg)

                children = ast.iter_child_nodes(_ast)
                for child in children:
                    a, b = find_name_errors(child, ss, asts, ctx)
                    ls += a
                    ss += b

                if (isinstance(_ast, ast.comprehension) or
                        isinstance(_ast, ast.Expression)):
                    check_var(ls, ss, store, ctx)

                asts.remove(_ast)
                return ls, ss

            if ctx is None:
                ctx = dict(context)

            xa = compile(calc, '<string>', 'eval', ast.PyCF_ONLY_AST)
            asts = list(ast.walk(xa))
            find_name_errors(xa, [], asts, ctx)

            if len(asts):
                raise Exception(
                    'Something went wrong while traversing asts', len(asts))

        if self._valid is None:
            exc = None
            variables = {'arg': None, 'res': table.File()}
            try:
                ctx = updated_context(variables)
                check_ast(self.clean_expr, ctx)
            except Exception as e:
                exc = e
            except SyntaxError as e:
                exc = e

            self._exc = exc
            self._valid = exc is None

        return self._valid

    @property
    def exc(self):
        """
        Return raw exception.
        """
        # Force ast check.
        self.valid
        return self._exc

    @property
    def exception(self):
        """
        Return (human?) readable exception string.
        """
        exc = self.exc
        res = ''
        if isinstance(exc, NameError):
            res = 'Analyzing {}: {}'.format(self.name, exc)
        elif isinstance(exc, SyntaxError):
            res = 'Analyzing {}: SyntaxError'.format(self.name)
        elif isinstance(exc, Exception):
            res = 'Analyzing {}: {}'.format(self.name, exc)
        return res

    def __str__(self):
        return "res['{}'] = {}".format(self._name, self._expr)

    @classmethod
    def from_calc(cls, calc):
        """
        Return a copy.
        """
        res = cls(name=calc._name, expr=calc._expr, enabled=calc._enabled,
                  type=calc._type)
        res._valid = calc._valid
        res._deps = calc._deps
        res._ex = calc._ex
        return res


def parse_nodes(calc_lines):
    return [Calc(*parse_calc(calc)) for calc in calc_lines]


class CalculationGraph(object):
    def __init__(self, calc_objs):
        self._graph = nx.DiGraph()
        self._calc_map = {}

        for calc_obj in calc_objs:
            self._graph.add_node(calc_obj)
            self._calc_map[calc_obj.name] = calc_obj

        for calc_obj in calc_objs:
            self._add_calc_edges(calc_obj)

    def _add_node(self, calc_obj):
        self._graph.add_node(calc_obj)
        self._calc_map[calc_obj.name] = calc_obj

    def _remove_node(self, calc_obj):
        self._graph.remove_node(calc_obj)
        del self._calc_map[calc_obj.name]

    def add_calc(self, calc_obj):
        curr = self._calc_map.get(calc_obj.name)
        if curr is not None:
            # In case there are already dependencies on nodes not
            # existing there will be placeholder elements of missing
            # type.
            assert curr.type == 'miss', (
                'Should not be possible to create calculation with same name.')
            self._replace_node(curr, calc_obj)
        else:
            self._add_node(calc_obj)
            self._add_calc_edges(calc_obj)

    def _add_calc_edges(self, calc_obj):
        for col in calc_obj.deps:
            dep_obj = self._calc_map.get(col)
            if dep_obj is None:
                dep_obj = Calc(col, '[]', enabled=False, type='miss')
                self._add_node(dep_obj)
            self._graph.add_edge(calc_obj, dep_obj)

    def _replace_node(self, old_calc, new_calc):
        predecessors = list(self._graph.predecessors(old_calc))
        successors = list(self._graph.successors(old_calc))
        self._remove_node(old_calc)
        self._add_node(new_calc)

        for node in predecessors:
            self._graph.add_edge(node, new_calc)

        for node in successors:
            self._graph.add_edge(new_calc, node)

        self._add_calc_edges(new_calc)

        self._remove_unused_missing()

    def remove_calc(self, calc_obj):
        predecessors = [node for node in self._graph.predecessors(calc_obj)
                        if node is not calc_obj]
        self._remove_node(calc_obj)

        if predecessors:
            dep_obj = Calc(calc_obj.name, '[]', enabled=False, type='miss')
            self._add_node(dep_obj)
            for node in predecessors:
                self._graph.add_edge(node, dep_obj)

        self._remove_unused_missing()

    def rename_calc(self, calc_obj, new_name, add_if_missing=True):
        if not add_if_missing and calc_obj not in self:
            calc_obj.name = new_name
        else:
            self.remove_calc(calc_obj)
            calc_obj.name = new_name
            self.add_calc(calc_obj)

    def change_calc_expr(self, calc_obj, new_expr):
        self.remove_calc(calc_obj)
        calc_obj.expr = new_expr
        self.add_calc(calc_obj)

    def _remove_unused_missing(self):
        for node in list(self._graph.nodes()):
            if node.type == 'miss' and len(
                    list(self._graph.predecessors(node))) == 0:
                self._graph.remove_node(node)
                del self._calc_map[node.name]

    def _calc_cycles(self):
        """
        May return duplicates when there are self cycles.
        """
        return itertools.chain([set(self.nodes_in_self_cycles())],
                               self.nodes_in_cycles())

    def nodes_in_calc_cycles(self):
        return set([node for comp in self._calc_cycles() for node in comp])

    def nodes_in_cycles(self):
        return (comp for comp in nx.strongly_connected_components(self._graph)
                if len(comp) > 1)

    def nodes_in_self_cycles(self):
        return iter({edge[0] for edge in nx.selfloop_edges(self._graph)})

    def node_valid(self, node):
        cycle_nodes = self.nodes_in_calc_cycles()
        valid_nodes = {}

        def inner(node):
            valid = False
            if node in valid_nodes:
                valid = valid_nodes[node]
            else:
                valid = node.valid
                valid_nodes[node] = valid

            if not valid:
                return False

            if node in cycle_nodes:
                return False

            return all((inner(n) for n in self._graph.successors(node)))

        return inner(node)

    def node_enabled_ancestors(self, node):
        res = True
        if not node.enabled:
            res = any(ans.enabled for ans in nx.ancestors(self._graph, node))
        return res

    def nodes_missing_ancestors(self):
        nodes = set()
        for node in self._graph.nodes():
            if node.type == 'miss':
                # Depends on missing cols.
                nodes.update(nx.ancestors(self._graph, node))
        return nodes

    def ancestor_calcs(self, calc_obj):
        return nx.ancestors(self._graph, calc_obj)

    def descendant_calcs(self, calc_obj):
        return nx.descendants(self._graph, calc_obj)

    def successor_calcs(self, calc_obj):
        try:
            return self._graph.successors(calc_obj)
        except Exception:
            return {}

    def topological_sort(self, nodes=None, nodes_in_cycles=None):
        graph = self._graph
        if nodes_in_cycles is None:
            nodes_in_cycles = self.nodes_in_calc_cycles()
        if nodes_in_cycles:
            graph = nx.DiGraph(incoming_graph_data=graph)
            graph.remove_nodes_from(nodes_in_cycles)

        if nodes is not None:
            res = list(reversed([node for node in nx.topological_sort(graph)
                                 if node.type == 'calc' and node in nodes]))
        else:
            res = list(reversed([node for node in nx.topological_sort(graph)
                                 if node.type == 'calc']))
        return res

    def nodes(self):
        return self._graph.nodes()

    def __contains__(self, node):
        return node in self._graph

    @classmethod
    def from_graph(cls, graph):
        """
        Return a copy.
        """
        def copy_graph(old_graph):
            # TODO: custom graph copy, remove when possible.
            # Workaround for graph.copy() performing deepcopy on Python 2
            # creating new Calc instances.
            # new_graph = old_graph.copy()
            new_graph = type(old_graph)()
            for node in old_graph.nodes():
                new_graph.add_node(node)
            for src, dst in old_graph.edges():
                new_graph.add_edge(src, dst)
            return new_graph

        res = cls([])
        old_graph = graph._graph
        res._graph = copy_graph(old_graph)
        res._calc_map = dict(graph._calc_map)
        return res


def execute_calcs(graph, ordered_calcs, arg, res, skip):
    def _gen_execute_calcs(graph, ordered_calcs, arg, res, skip):
        invalid = set(graph.nodes_missing_ancestors())

        for calc in ordered_calcs:

            if calc not in invalid and graph.node_enabled_ancestors(calc):
                try:
                    if calc.is_empty:
                        output = None
                    else:
                        output = python_calculator(
                            calc.clean_expr, {'res': res, 'arg': arg})
                    res[calc.name] = output
                    yield calc, output
                except Exception as e:
                    invalid.update(
                        graph.ancestor_calcs(calc))
                    if not skip:
                        raise
                    else:
                        yield calc, e
                except:  # NOQA
                    # For example if user code is a SyntaxError.
                    e = sys.exc_info()[1]
                    if not skip:
                        raise
                    else:
                        yield calc, e
    list(_gen_execute_calcs(graph, ordered_calcs, arg, res, skip))


def parse_calc(calc_line):
    var, calc = calc_line.split(FUNCTION_SPLIT, 1)
    try:
        calc, enabled = calc.split(ENABLED_SPLIT, 1)
        enabled = 1 if enabled.strip() == '1' else 0
    except ValueError:
        # Compatibility with calculations that does not have the enabled flag
        enabled = 1
    return var.strip(), calc.strip(), enabled


def python_calculator(calc_text, extra_globals=None):
    output = advanced_eval(calc_text, extra_globals)
    if not isinstance(output, np.ndarray):
        if isinstance(output, list):
            output = np.array(output)
        else:
            # Assume scalar value.
            output = np.array([output])
    return output


def advanced_eval(calc, globals_dict=None):
    """
    Evaluate expression in a standardized python environment with a few
    imports:
     - datetime
     - numpy as np
     - os
     - json
     - pandas
     - re

    globals_dict argument can be used to extend the environment.
    """
    ctx = updated_context(globals_dict)
    try:
        return eval(compile(calc, "<string>", "eval"), ctx, {})
    except Exception:
        msg = 'Error executing calculation: {}.'.format(calc)
        raise exceptions.SyUserCodeError(sys.exc_info(), msg)


def updated_context(globals_dict):
    ctx = dict(context)

    if globals_dict:
        ctx.update(globals_dict)
    for plugin in plugins.available_plugins():
        ctx.update(plugins.get_globals_dict(plugin))
    return ctx


class CalculatorCalculationItem(QtGui.QStandardItem):
    """
    A helper model item for showing the items in the calculation column.
    """

    def __init__(self, calculation):
        super().__init__()
        self._valid = True
        self._is_computing = False
        self.setText(calculation)

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, state):
        self._valid = bool(state)
        self.emitDataChanged()

    @property
    def is_computing(self):
        return self._is_computing

    @is_computing.setter
    def is_computing(self, state):
        self._is_computing = state
        self.emitDataChanged()

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundRole:
            if not self._valid:
                return colors.DANGER_BG_COLOR
            elif self.is_computing:
                return colors.WARNING_BG_COLOR
            else:
                return None
            return None
        elif role == QtCore.Qt.ToolTipRole:
            return self.text()
        else:
            return super().data(role)


class CalculatorModelItem(QtGui.QStandardItem):
    """A model item for calculated columns"""

    def __init__(self, name, calculation='', calc_item=None):
        super().__init__()
        self._errors = {}
        self._is_warned = False
        self.node = Calc(name, calculation, None)
        self._old_name = self.name
        self.message = ''
        self._attributes = []
        self._duplicate = False
        self._column_data = np.array([])
        self._calc_item = calc_item
        self._is_pending = False
        self._check_name()

    def _check_name(self):
        self._forbidden_name = '=' in self.name
        self._dangerous_name = re.search('\\s$', self.name) is not None

    def text(self):
        return self.node.name

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.node.name
        elif role == QtCore.Qt.BackgroundRole:
            if not self.valid or self._duplicate or self._forbidden_name:
                return colors.DANGER_BG_COLOR
            elif self.is_computing or self._dangerous_name or self._is_warned:
                return colors.WARNING_BG_COLOR
            else:
                return None
        elif role == QtCore.Qt.ToolTipRole:
            text = str(self.node)
            deps = self.node.deps
            if deps:
                text += '\n\nUsed columns:\n'
                text += '\n'.join(
                    ['- {}'.format(i) for i in deps])

            # TODO(erik):
            # Ask model for this information.
            # if len(self._child_columns):
            #     text += '\n\nDependent columns:\n'
            #     text += '\n'.join(['- {}'.format(i.name)
            #                        for i in self._child_columns])

            if self._forbidden_name:
                text += '\n\nColumn name must not contain equal sign'

            if self._dangerous_name:
                text += ('\n\nWarning: \n This columns name contains '
                         'whitespace at the end')
            return text
        else:
            return None

    def flags(self):
        return QtCore.Qt.ItemIsEnabled

    @property
    def enabled(self):
        return self.node.enabled

    @enabled.setter
    def enabled(self, value):
        self.node.enabled = value
        if self.model():
            self.model().data_ready.emit()

    @property
    def valid(self):
        return self.node.valid

    @property
    def warned(self):
        return self._is_warned

    @warned.setter
    def warned(self, state):
        self._is_warned = bool(state)
        self.emitDataChanged()

    @property
    def name(self):
        return self.node.name

    @name.setter
    def name(self, name):
        self._old_name = self.node.name
        if name != self._old_name:
            self.model().rename_item(self, name)
            self._check_name()

    def rename(self, new_name):
        # WARNING: only called to ensure update, actual renames must
        # go through the graph.
        self.model().data_ready.emit()

    @property
    def expr(self):
        return self.node.expr

    @expr.setter
    def expr(self, value):
        if isinstance(self._calc_item, QtGui.QStandardItem):
            # Update connected StandardItem.
            self._calc_item.setText(value)

        old_value = self.node.expr
        if value == old_value:
            return

        if self.model() is not None:
            self.model().change_item_expr(self, value)
            self.model().data_ready.emit()

    @property
    def duplicate(self):
        return self._duplicate

    @duplicate.setter
    def duplicate(self, value):
        self._duplicate = value

    @property
    def column_data(self):
        return self._column_data

    @column_data.setter
    def column_data(self, data):
        self._column_data = data
        self.emitDataChanged()

    @property
    def is_computing(self):
        return self._calc_item._is_computing

    @is_computing.setter
    def is_computing(self, state):
        self._calc_item.is_computing = state
        self.emitDataChanged()

    @property
    def is_pending(self):
        return self._is_pending

    @is_pending.setter
    def is_pending(self, state):
        self._is_pending = state

    @property
    def attributes(self):
        return self._attributes

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.index() == other.index()

    def __ne__(self, other):
        return self.index() != other.index()


def display_calculation(calc):
    if isinstance(calc, bytes):
        calc = str(calc.decode('utf8'))
    return calc


class DragItem(QtGui.QStandardItem):
    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return '\u205e'
        elif role == QtCore.Qt.ToolTipRole:
            return 'Grab with the first mouse button to drag!'
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        return super().data(role)


class CalculatorEnableItem(QtGui.QStandardItem):
    def __init__(self, model, main_item, enabled):
        super().__init__()
        self._main_item = main_item
        self._model = model
        self._emit = False

        self.setCheckable(True)
        self.setToolTip(
            "Uncheck this to create a temporary variable usable in the "
            "following calculations but excluded from the output.")
        if enabled and not self._main_item.enabled:
            self.setCheckState(QtCore.Qt.Checked)

        self._emit = True

    def setData(self, value, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.CheckStateRole:
            self._main_item.enabled = value == QtCore.Qt.Checked
            if self._emit:
                self._model.enabled_changed.emit()
        super().setData(value, role=role)


class CalculatorItemModel(QtGui.QStandardItemModel):
    data_ready = QtCore.Signal()
    item_dropped = QtCore.Signal(QtCore.QModelIndex)
    enabled_changed = QtCore.Signal()

    """
    Calculator Model.
    """
    def __init__(self, in_tables, data,
                 preview_calculator=None, parent=None,
                 empty_input=False):
        """
        Initialize :class:CalculatorModel

        Parameters
        ----------
        in_tables : table.FileList
        data : tuple
        preview_calculator : function or None
        parent : None or QtGui.QObject
        """

        def input_columns_and_types(in_items):
            res = collections.defaultdict(set)
            parent_name = 'arg'

            def inner(in_data):
                names = in_data.names('calc')
                types = in_data.types('calc')

                for cname, dtype in zip(names, types):
                    name = parent_name + cname
                    res[name].add(dtype)

            for in_item in in_items:
                inner(in_item)

            return [(k, list(sorted(v))) for k, v in sorted(
                res.items(), key=lambda s: s[0].lower())]

        super().__init__(parent=parent)
        self._in_tables = in_tables
        self._graph = CalculationGraph([])

        self.empty_input = empty_input
        self._input_columns_and_types = []
        self._preview_queue = []

        if not self._in_tables:
            self._in_tables = table.FileList()

        if len(self._in_tables) > 0:
            table_file = self._in_tables[0]
        else:
            table_file = table.File()
        self._preview_worker = CalculatorModelPreviewWorker(table_file)

        self.calc_timer = QtCore.QTimer()
        self.calc_timer.setInterval(1000)  # 1s timeout before calc runs
        self.calc_timer.setSingleShot(True)

        self.calc_timer.timeout.connect(self._compute_items)

        if self._in_tables:
            if isinstance(self._in_tables[0], sygeneric):
                self.empty_input = True
            else:
                self._input_columns_and_types = input_columns_and_types(
                    self._in_tables)
        self.set_data(data)

        self._preview_worker.preview_ready.connect(self._update_item)
        self._start_preview()

    def set_data(self, data):
        def trim_name(name):
            if name.startswith('res.col(') and name.endswith(')'):
                name = name[8:-1]
            if name.startswith('${') and name.endswith('}'):
                name = name[2:-1]
            return name

        for _ in range(self.rowCount()):
            # TODO: Delay preview updates?
            self.remove_item(0)

        calc_list, calc_attrs = data
        calc_attrs_dict = dict(calc_attrs)
        for i, item in enumerate(calc_list):
            name, calculation, enabled = parse_calc(item)
            name = trim_name(name)
            # TODO: Delay preview updates?
            model_item = self.add_item(name, calculation, bool(enabled))
            item_attrs = calc_attrs_dict.get(i, [])
            if item_attrs:
                model_item.attributes[:] = item_attrs

    def cleanup_preview_worker(self):
        try:
            self._preview_worker.preview_ready.disconnect(self._update_item)
            self._preview_worker.stop()
        except RuntimeError:
            pass

    def flags(self, index):
        if index.isValid():
            flags = QtCore.Qt.NoItemFlags
            if index.column() != 3:
                flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
                if index.column() == 2:
                    flags |= QtCore.Qt.ItemIsUserCheckable
            return flags
        else:
            return super().flags(index)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ['text/plain']

    def dropMimeData(self, mime_data, action, row, column, parent):
        return False

    @property
    def input_tables(self):
        return self._in_tables

    @property
    def first_input_table(self):
        return self._in_tables[0]

    @property
    def column_names(self):
        return [self.item(r).name for r in range(self.rowCount())]

    @property
    def available_columns(self):
        all_columns = sorted(self.input_columns + self.column_names,
                             key=lambda s: s.lower())
        return all_columns

    @property
    def input_columns_and_types(self):
        return self._input_columns_and_types

    @property
    def input_columns(self):
        return [i[0] for i in self.input_columns_and_types]

    def items(self):
        return (self.item(row) for row in range(self.rowCount()))

    def get_item_by_name(self, name):
        items = self.findItems(name, flags=QtCore.Qt.MatchExactly, columns=0)
        if items:
            return items[0]

    def build_item(self, name='', calculation='', enabled=True):
        calculation_item = CalculatorCalculationItem(calculation)
        name_item = CalculatorModelItem(name, calculation, calculation_item)
        enabled_item = CalculatorEnableItem(self, name_item, enabled)
        drag_item = DragItem()
        name_item.enabled = enabled
        return name_item, calculation_item, enabled_item, drag_item

    def add_item(self, name=None, calculation=None, enabled=True):
        """Add a column to the model and the preview table."""
        if name is None:
            name = 'New Column {}'.format(self.rowCount())
        if calculation is None:
            calculation = ''
        item_row = self.build_item(name, calculation, enabled)
        item = item_row[0]
        node = item.node
        self._before_add_item_set_duplicate(item)
        self.appendRow(item_row)
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.add_calc(node)

        if self.rowCount() < 2:
            self.setHeaderData(0, QtCore.Qt.Horizontal, 'Column name')
            self.setHeaderData(1, QtCore.Qt.Horizontal, 'Calculation')
            self.setHeaderData(2, QtCore.Qt.Horizontal, 'On')
            self.setHeaderData(3, QtCore.Qt.Horizontal, '')

        return item_row[0]

    def _insert_item(self, name='', calculation='', row=0):
        item_row = self.build_item(name, calculation)
        item = item_row[0]
        node = item.node
        self._before_add_item_set_duplicate(item)
        self.insertRow(row, item_row)
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.add_calc(node)
        return item_row[0]

    def copy_item(self, row):
        item = self.item(row, 0)

        def get_copy_name(base_name, all_names):
            numbers = []
            match = copy_name_regex.match(base_name)
            if match:
                base_name = match.group(1)
                numbers.append(int(match.group(2)))
            else:
                base_name = f'{base_name} Copy'

            names = []
            numbers = []

            for name in all_names:
                match = copy_name_regex.match(name)
                if match:
                    if match.group(1) == base_name:
                        numbers.append(int(match.group(2)))
            i = 0
            n = 0

            for n in sorted(numbers):
                if i != n:
                    break
                i += 1
            return f'{base_name} {i}'

        copy_name = get_copy_name(
            item.name, [item_.name for item_ in self.items()])
        new_item = self._insert_item(
            copy_name, item.expr, row + 1)
        new_item.attributes[:] = item.attributes
        self._recompute_item(new_item)

    def remove_item(self, row):
        """Remove a column from the model."""

        item = self.item(row, 0)
        if item is None:
            # List is empty
            return

        self.removeRow(row)
        node = item.node
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.remove_calc(node)
            self._preview_worker.remove_column(node.name)
        else:
            self._after_remove_item_set_duplicate(item)

        self.data_ready.emit()

    def rename_item(self, item, new_name):
        node = item.node
        old_name = node.name

        items_with_old_name = [
            i for i in self.items() if i.name == old_name]
        items_with_new_name = [
            i for i in self.items() if i.name == new_name]

        items_with_old_name.remove(item)
        n_old_name = len(items_with_old_name)
        n_new_name = len(items_with_new_name)

        if n_new_name >= 1:
            self._set_item_duplicate(item, True)
            self._graph.rename_calc(
                node, new_name, add_if_missing=False)

            for i in items_with_new_name:
                self._set_item_duplicate(i, True)
                # Force update.
                i.rename(new_name)
        else:
            if item.duplicate:
                item.duplicate = False

            if node not in self._graph:
                self._graph.rename_calc(
                    node, new_name, add_if_missing=False)
                with self._invalidate_affected(node):
                    self._graph.add_calc(node)
            else:
                with self._invalidate_affected(node):
                    try:
                        self._graph.rename_calc(node, new_name)
                    except Exception:
                        pass
            self._preview_worker.remove_column(old_name)

        # Force update.
        item.rename(new_name)
        if n_old_name == 1:
            self._set_item_duplicate(items_with_old_name[0], False)

    def change_item_expr(self, item, new_expr):
        node = item.node
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.change_calc_expr(node, new_expr)
        else:
            node.expr = new_expr

    def _set_item_duplicate(self, item, value):
        item.duplicate = value
        node = item.node

        if node in self._graph:
            if value:
                with self._invalidate_affected(node):
                    self._graph.remove_calc(node)
        else:
            if not value:
                with self._invalidate_affected(node):
                    self._graph.add_calc(node)

    def _before_add_item_set_duplicate(self, item):
        name = item.name
        items_with_same_name = [i for i in self.items() if name == i.name]
        if items_with_same_name:
            for i in items_with_same_name:
                self._set_item_duplicate(i, True)
            item.duplicate = True

    def _after_remove_item_set_duplicate(self, item):
        name = item.name
        items_with_same_name = [i for i in self.items() if name == i.name]
        if len(items_with_same_name) == 1:
            for i in items_with_same_name:
                self._set_item_duplicate(i, False)
            item.duplicate = False

    @contextlib.contextmanager
    def _invalidate_affected(self, node):
        try:
            nodes = set(self._graph.ancestor_calcs(node))
        except Exception:
            nodes = set()
        yield
        nodes.add(node)
        try:
            nodes.update(self._graph.ancestor_calcs(node))
        except Exception:
            pass

        nodes = {n for n in nodes if n in self._graph}
        self._queue_nodes(nodes)

    def _queue_nodes(self, nodes):
        item_map = {}
        for item in self.items():
            item_map[item.node] = item

        for node in nodes:
            item = item_map.get(node)
            if item:
                item.is_pending = True

        self._preview_graph = CalculationGraph.from_graph(self._graph)
        self._preview_queue.insert(0, {node: Calc.from_calc(node)
                                       for node in nodes})
        self.calc_timer.start()

    def _start_preview(self):
        self._preview_queue[:] = []
        self._queue_nodes(set(n.node for n in self.items()))

    def _recompute_item(self, item):
        if item.valid:
            self._queue_nodes([item.node])

    def _compute_items(self):
        item_map = {}
        for item in self.items():
            item_map[item.node] = item

        old_to_new_node_map = {}

        preview_graph = CalculationGraph.from_graph(self._preview_graph)

        for group in self._preview_queue:
            for old_calc, new_calc in group.items():
                item = item_map.get(old_calc)
                if item:
                    item.is_pending = False

                if old_calc not in old_to_new_node_map:
                    try:
                        preview_graph.remove_calc(old_calc)
                        preview_graph.add_calc(new_calc)
                    except Exception:
                        pass
                    else:
                        old_to_new_node_map[old_calc] = new_calc

        new_to_old_node_map = dict(zip(old_to_new_node_map.values(),
                                       old_to_new_node_map.keys()))
        node_set = set(new_to_old_node_map.keys())
        for node in list(node_set):
            node_set.update(preview_graph.descendant_calcs(node))
        cycles = preview_graph.nodes_in_calc_cycles()
        normal_nodes = node_set.difference(cycles)

        if normal_nodes:
            exec_order = preview_graph.topological_sort(
                normal_nodes, nodes_in_cycles=cycles)
            for new_node in exec_order:
                old_node = node
                if new_node in new_to_old_node_map:
                    old_node = new_to_old_node_map[new_node]
                self._preview_worker.calculate((old_node, new_node))
                item = item_map.get(old_node)
                if item:
                    item.is_computing = True

        self._preview_queue[:] = []

    def _update_item(self, items):

        calc, data, error_lines = items
        item = None
        for i in self.items():
            if i.node is calc:
                item = i
                break

        if item is None:
            return

        is_warned = False
        message = ''
        item.is_computing = False
        # check if the data can be stored in a sytable

        if error_lines:
            if calc.expr:
                is_warned = True
        try:
            dummy_output_table = table.File()
            dummy_output_table.set_column_from_array(item.name, data)
            item.column_data = data

            if error_lines:
                if error_lines[0] not in ['Empty', 'Invalid']:
                    message = 'Calculating {}: {}'.format(
                        item.name, error_lines[0])
            elif is_warned:
                message = data[0]
            else:
                message = ''
        except Exception as e:
            if data is not None:
                message = '{}'.format(e)
                is_warned = True

        item.message = message
        item.warned = is_warned
        item.emitDataChanged()
        self.data_ready.emit()

    def validate(self):

        def check_item_messages():
            """Return first message of items."""
            for item in items:
                if item.message:
                    return item.message
            return ''

        def check_column_length():
            """Return True if all selected columns have the same length."""
            ok = True
            enabled = [item for item in items
                       if item.enabled and not (item.is_computing or
                                                item.is_pending)]
            col_lens = np.array([len(i.column_data) for i in enabled])
            if len(col_lens):
                ok = np.all((col_lens - col_lens[0]) == 0)
            return ok

        def check_valid_names():
            """Return True if all column names are valid."""
            col_names_valid = [i.valid for i in items if i.node.is_empty]
            return np.all(col_names_valid)

        def check_calculation():
            """Return True if all column names are valid."""
            return [i for i in items if not i.node.is_empty and not i.valid]

        def check_empty_calculations():
            return [i for i in items if i.node.is_empty]

        def check_preview_warnings():
            """Return True if all calculations have finished."""
            calculations_warned = [i.warned
                                   for i in items]
            return np.all(calculations_warned)

        def check_duplicate():
            return [i for i in items if i.duplicate]

        def check_cycles():
            return self._graph.nodes_in_calc_cycles()

        def check_forbidden_names():
            return [i for i in items if i._forbidden_name]

        items = list(self.items())
        item_message = check_item_messages()
        valid = all([i.valid and not i.duplicate and not i._forbidden_name for i in items])
        cycles = check_cycles()

        if cycles:
            self_cycles = list(self._graph.nodes_in_self_cycles())
            if self_cycles:
                return False, 'Cyclic dependencies to itself in: {}'.format(
                    ', '.join(sorted(
                        n.name for n in self._graph.nodes_in_self_cycles())))
            else:
                return (
                    False,
                    'Cyclic dependencies in the following groups: {}'.format(
                        ', '.join('{{{}}}'.format(
                            ', '.join(sorted(n.name for n in g)))
                                  for g in self._graph.nodes_in_cycles())))

        if valid:
            if check_preview_warnings():
                item_map = {}
                for item in self.items():
                    item_map[item.node] = item
                    # Ensure the first message.
                    for node in self._graph.topological_sort(
                            item_map.keys()):
                        if item_message:
                            item_message = item_map[node].message
                            break
                return True, item_message
            elif self.empty_input:
                return True, 'No input data available'
            elif item_message:
                return True, item_message
            elif not check_column_length():
                return (False, 'The calculated columns do not have the same '
                        'length')
            return True, ''
        else:
            if check_calculation():
                return False, check_calculation()[0].node.exception
            elif check_forbidden_names():
                forbidden_s = ', '.join(sorted(set(
                    i.node.name for i in check_forbidden_names())))
                return False, 'Forbidden calculation names: {}'.format(
                    forbidden_s)
            elif check_duplicate():
                duplicate_s = ', '.join(sorted(set(
                    i.node.name for i in check_duplicate())))
                return False, 'Duplicate calculation names: {}'.format(
                    duplicate_s)
            elif check_empty_calculations():
                return True, ''
            return False, 'Unknown Error'

    def get_data(self):
        var = '{}'
        calc_list = [
            (var + ' {} {} {}{}').format(
                item.name, FUNCTION_SPLIT, item.expr, ENABLED_SPLIT,
                item.enabled) for item in self.items()]

        calc_attrs_dict = [(i, item.attributes)
            for i, item in enumerate(self.items())
            if item.attributes]

        return calc_list, calc_attrs_dict


class CalculatorMasterThread(preview.MasterThread):

    def __init__(self, state, output_signal, **kwargs):
        self._output_signal = output_signal
        self._state = state
        super().__init__(**kwargs)

    def _worker_function(self, org_calc, pre_calc):
        state = self._state
        arg = state['arg']
        res = state['res']
        err = state['err']

        name = pre_calc.name
        deps = pre_calc.deps
        clean = pre_calc.clean_expr
        empty = pre_calc.is_empty
        valid = pre_calc.valid

        res[name] = None
        error = set(deps).intersection(err)
        missing = set(deps).difference(res)
        error.update(missing)
        col = np.array([])
        error_lines = []
        if not valid:
            err.add(name)
            if empty:
                error_lines = ['Empty']
            else:
                error_lines = ['Invalid']
            col = np.array(error_lines)
        elif error:
            err.add(name)
            missing_s = ', '.join(sorted(error))
            col = np.array(['Missing deps: {}'.format(missing_s)])
            error_lines = ['Missing dependencies of {}: {}'.format(
                name, missing_s)]
        else:
            col = None
            try:
                col = python_calculator(
                    clean, {'res': res, 'arg': arg})
                res[name] = col
                try:
                    err.remove(name)
                except Exception:
                    pass
            except exceptions.SyUserCodeError as e:
                error_lines = e.brief_help_text.splitlines()
                col = np.array([error_lines[-1]])
                err.add(name)
            except preview.CancelThread:
                raise
            except:  # NOQA
                # For example if user code is a SyntaxError.
                e = sys.exc_info()[1]
                error_lines = traceback.format_exception_only(type(e), e)
                col = np.array([error_lines[-1]])
                err.add(name)

        self._output_signal.emit([
            org_calc, col, error_lines])


class CalculatorModelPreviewWorker(QtCore.QObject):
    preview_ready = QtCore.Signal(list)

    def __init__(self, arg):
        super().__init__()
        self._res = ResTable()
        state = {'arg': arg,
                 'res': self._res,
                 'err': set()}
        self._thread = CalculatorMasterThread(
            state, self.preview_ready, daemon=True)
        self._thread.start()
        self._calcs = {}

    def calculate(self, calc):
        org_calc, pre_calc = calc
        old_calc_id = self._calcs.pop(pre_calc.name, None)
        if old_calc_id is not None:
            self._thread.cancel_job(old_calc_id)

        new_calc_id = self._thread.create_job(org_calc, pre_calc)
        self._calcs[pre_calc.name] = new_calc_id

    def remove_column(self, col):
        # TODO: fix race conditions, by making this a job.
        try:
            del self._res[col]
        except KeyError:
            pass

    def stop(self):
        self._thread.stop()
