#!/usr/bin/env python3

import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

import warnings
warnings.filterwarnings("ignore", "g_object_unref")


DESKTOP_COORDINATES = 0
WINDOW_COORDINATES = 1


class Registry:
    def __init__(self):
        self.main_loop = GLib.MainLoop()
        self._set_registry()


    def __call__(self):
        return self


    def _set_registry(self):
        self.event_listeners = dict()


    def get_desktop(self, numbered_desktop):
        return Atspi.get_desktop(numbered_desktop)


class Config:
    def __init__(self):
        self.search_cutoff = 10


config = Config()

# Make listeners and events later.



# Find all satisfying descendants
# -------------------------------------------------------------------------------------------------
def find_all_descendants(accessible_node, predicate):
    match_list = []
    _find_all_descendants(accessible_node, predicate, match_list)
    return match_list


def _find_all_descendants(accessible_node, predicate, match_list):
    for accessible_child in accessible_node:
        try:
            if predicate(accessible_child):
                match_list.append(accessible_child)
        except Exception as error:
            print(f"Debug log to be deleted: {error}")
        _find_all_descendants(accessible_child, predicate, match_list)
# -------------------------------------------------------------------------------------------------


# Find a single satisfying descendant
# -------------------------------------------------------------------------------------------------
def find_descendant(accesible_node, predicate, depth_first=True):
    if depth_first:
        success_match =_find_descendant_depth_first(accesible_node, predicate)
    else: # breadth_first
        success_match =_find_descendant_breadth_first(accesible_node, predicate)

    return success_match


def _find_descendant_depth_first(accesible_node, predicate):
    try:
        if predicate(accesible_node):
            return accesible_node
    except Exception:
        pass

    for accesible_child in accesible_node:
        try:
            success_match = _find_descendant_depth_first(accesible_child, predicate)
        except Exception:
            success_match = None

        if success_match is not None:
            return success_match


def _find_descendant_breadth_first(accesible_node, predicate):
    for accesible_child in accesible_node:
        try:
            if predicate(accesible_node):
                return accesible_node
        except Exception:
            pass

    for accesible_child in accesible_node:
        try:
            success_match = _find_descendant_depth_first(accesible_child, predicate)
        except Exception:
            success_match = None

        if success_match is not None:
            return success_match
# -------------------------------------------------------------------------------------------------


# Generating events
# -------------------------------------------------------------------------------------------------
def verify_coordinates(x, y):
    if x < 0 or y < 0:
        raise ValueError(f"Attempting to generate mouse event at negative coordinates ({x},{y}) ")


def click(x, y, mouse_button=1, check=True):
    if check:
        verify_coordinates(x, y)

    print(f"Making a click at: ({x}, {y})")
    Atspi.generate_mouse_event(x, y, f"b{mouse_button}c")


def double_click(x, y, mouse_button=1, check=True):
    if check:
        verify_coordinates(x, y)

    Atspi.generate_mouse_event(x, y, f"b{mouse_button}d")


def point(x, y, check=True):
    if check:
        verify_coordinates(x, y)

    Atspi.generate_mouse_event(x, y, f"abs")


def press(x, y, mouse_button=1, check=True):
    if check:
        verify_coordinates(x, y)

    Atspi.generate_mouse_event(x, y, f"b{mouse_button}p")


def release(x, y, mouse_button=1, check=True):
    if check:
        verify_coordinates(x, y)

    Atspi.generate_mouse_event(x, y, f"b{mouse_button}r")

# -------------------------------------------------------------------------------------------------


class Node(object):

# Setting Atspi.Action properties
# -------------------------------------------------------------------------------------------------
    def do_action(self, index):
        """
        Invoke the action indicated by index.
        """

        atspi_action = self.get_action_iface()
        return atspi_action.do_action(index)


    def get_action_description(self, index):
        """
        Get the description of ‘i-th’ action invocable on an object implementing Atspi.Action.
        """

        atspi_action = self.get_action_iface()
        return atspi_action.get_action_description(index)


    def get_action_name(self, index):
        """
        Get the name of the ‘i-th’ action invocable on an object implementing Atspi.Action.
        """

        atspi_action = self.get_action_iface()
        return atspi_action.get_action_name(index)


    def get_key_binding(self, index):
        """
        Get the keybindings for the i-th action invocable on an object implementing Atspi.Action,
        if any are defined.
        """

        atspi_action = self.get_action_iface()
        return atspi_action.get_key_binding(index)


    def get_number_of_actions(self):
        """
        Get the number of actions invokable on an Atspi.Action implementor.
        """

        atspi_action = self.get_action_iface()
        return atspi_action.get_n_actions()


    @property
    def actions(self):
        """
        Get human readable format for all existing actions on Atspi.Action.
        """

        #Atspi.Accessible

        readable_actions = {}

        try:
            atspi_action = self.get_action_iface()
            for action_index in range(self.get_number_of_actions()):

                action_name = atspi_action.get_action_name(action_index)
                action_key_binding = atspi_action.get_key_binding(action_index)
                action_description = atspi_action.get_action_description(action_index)

                readable_actions[action_name] = [
                    action_index,
                    action_key_binding,
                    action_description
                ]
        except Exception as error:
            print(f"Error encountered: \n{error}")
        finally:
            return readable_actions


    def do_action_named(self, action_name):
        """
        Perform the action with the specified name. For a list of actions
        supported by this instance, check the 'actions' property.
        """

        atspi_action = self.get_action_iface()

        named_actions = self.actions
        if action_name in named_actions:
            return atspi_action.do_action(named_actions[action_name][0])

        raise Exception(f"Action {action_name} is not supported on this node.")
# -------------------------------------------------------------------------------------------------


# Setting Atspi.Component properties
# -------------------------------------------------------------------------------------------------
    @property
    def position(self):
        """
        Gets the minimum x and y coordinates of the specified Atspi.Component. The returned
        values are meaningful only if the Component has both STATE_VISIBLE and STATE_SHOWING.
        """
        if not self.get_component_iface():
            return None
        atspi_point = self.get_component_iface().get_position(DESKTOP_COORDINATES)
        return (atspi_point.x, atspi_point.y)


    @property
    def size(self):
        """
        Gets the size of the specified Atspi.Component. The returned values are meaningful only if
        the Component has both STATE_VISIBLE and STATE_SHOWING.
        """
        if not self.get_component_iface():
            return None
        atspi_point = self.get_component_iface().get_size()
        return (atspi_point.x, atspi_point.y)


    @property
    def extents(self):
        """
        Gets the size of the specified Atspi.Component. The returned values are meaningful only if
        the Component has both STATE_VISIBLE and STATE_SHOWING.
        """
        if not self.get_component_iface():
            return None
        atspi_rect =  self.get_component_iface().get_extents(DESKTOP_COORDINATES)
        return [atspi_rect.x, atspi_rect.y, atspi_rect.w, atspi_rect.h]


    def contains(self, x, y):
        """
        Queries whether a given Atspi.Component contains a particular point.
        """
        if not self.get_component_iface():
            return None
        return self.get_component_iface().contains(x, y, DESKTOP_COORDINATES)


    def get_accessible_at_point(self, x, y):
        """
        Queries whether a given Atspi.Component contains a particular point.
        """
        if not self.get_component_iface():
            return None
        return self.get_component_iface().get_accessible_at_point(x, y, DESKTOP_COORDINATES)


    def grab_focus(self):
        """
        Attempts to set the keyboard input focus to the specified Atspi.Component.
        """
        if not self.get_component_iface():
            return None
        return self.get_component_iface().grab_focus()
# -------------------------------------------------------------------------------------------------


# Setting up clicking and other related functions
# -------------------------------------------------------------------------------------------------
    @property
    def center(self):
        """
        Returns a center of an Node.
        """

        center_x = self.position[0] + int(self.size[0]/2)
        center_y = self.position[1] + int(self.size[1]/2)
        return [center_x, center_y]


    def click(self, mouse_button=1):
        """
        Generates a click over the AtspiAccesible node.
        """

        click(self.center[0], self.center[1], mouse_button)
# -------------------------------------------------------------------------------------------------


# Setting Atspi.StateSet properties
# -------------------------------------------------------------------------------------------------

    def child(self, name=None, role_name=None, description=None):
        predicate = lambda x: x.name==name and x.role_name==role_name and x.description==description
        return find_descendant(self, predicate)


    def findChild(self, predicate):

        result = None

        for _ in range(config.search_cutoff):
            result = find_descendant(self, predicate)

            if result:
                break

        return result


    def findChildren(self, predicate):
        return find_all_descendants(self, predicate)
# -------------------------------------------------------------------------------------------------


# Setting Atspi.StateSet properties
# -------------------------------------------------------------------------------------------------
    @property
    def focusable(self):
        """
        Indicates this object can accept keyboard focus, which means all events resulting from typing
        on the keyboard will normally be passed to it when it has focus.
        """

        return self.get_state_set().contains(Atspi.StateType.FOCUSABLE)


    @property
    def focused(self):
        """
        Indicates this object currently has the keyboard focus.
        """

        return self.get_state_set().contains(Atspi.StateType.FOCUSED)


    @property
    def pressed(self):
        """
        Indicates this object is currently pressed.
        """

        return self.get_state_set().contains(Atspi.StateType.PRESSED)


    @property
    def resizable(self):
        """
        Indicates the size of this object’s size is not fixed.
        """

        return self.get_state_set().contains(Atspi.StateType.RESIZABLE)


    @property
    def sensitive(self):
        """
        Indicates this object is sensitive, e.g. to user interaction.
        """

        return self.get_state_set().contains(Atspi.StateType.SENSITIVE)


    @property
    def showing(self):
        """
        Indicates this object, the object’s parent, the object’s parent’s parent, and so on, are all
        ‘shown’ to the end-user, i.e. subject to “exposure” if blocking or obscuring objects do not
        interpose between this object and the top of the window stack.
        """

        return self.get_state_set().contains(Atspi.StateType.SHOWING)


    @property
    def visible(self):
        """
        Indicates this object is visible, e.g. has been explicitly marked for exposure to the user.
        """

        return self.get_state_set().contains(Atspi.StateType.VISIBLE)


    @property
    def checked(self):
        """
        Indicates this object is currently checked.
        """

        return self.get_state_set().contains(Atspi.StateType.CHECKED)


    @property
    def checkable(self):
        """
        Indicates this object has the potential to be checked, such as a checkbox or toggle-able
        table cell.
        """

        return self.get_state_set().contains(Atspi.StateType.CHECKABLE)


    @property
    def read_only(self):
        """
        Indicates that an object which is ENABLED and SENSITIVE has a value which can be read, but
        not modified, by the user.
        """

        return self.get_state_set().contains(Atspi.StateType.READ_ONLY)


    @property
    def collapsed(self):
        """
        Indicates this object is collapsed.
        """

        return self.get_state_set().contains(Atspi.StateType.COLLAPSED)


    @property
    def editable(self):
        """
        Indicates the user can change the contents of this object.
        """

        return self.get_state_set().contains(Atspi.StateType.EDITABLE)
# -------------------------------------------------------------------------------------------------


# Setting Atspi.Selection properties
# -------------------------------------------------------------------------------------------------
    def clear_selection(self):
        """
        Clears the current selection, removing all selected children from the specified
        Atspi.Selection implementor’s selection list.
        """

        return self.get_selection_iface().clear_selection()


    def deselect_child(self, child_at_index):
        """
        Deselects a specific child of an Atspi.Selection. Note that child_at_index is the index of
        the child in the parent container.
        """

        return self.get_selection_iface().deselect_child(child_at_index)


    def deselect_selected_child(self, child_at_index):
        """
        Removes a child from the selected children list of an Atspi.Selection. Note that child_index is
        the index in the selected-children list, not the index in the parent container.
        """

        return self.get_selection_iface().deselect_selected_child(child_at_index)


    def get_n_selected_children(self):
        """
        Gets the number of children of an Atspi.Selection implementor which are currently selected.
        """

        return self.get_selection_iface().get_n_selected_children()


    def get_selected_child(self, child_index):
        """
        Gets the i-th selected Atspi.Accessible child of an Atspi.Selection.
        """

        return self.get_selection_iface().get_selected_child(child_index)


    def is_child_selected(self, child_index):
        """
        Determines whether a particular child of an Atspi.Selection implementor is currently
        selected.
        """

        return self.get_selection_iface().is_child_selected(child_index)


    def select_all(self):
        """
        Attempts to select all of the children of an Atspi.Selection implementor. Not all
        Atspi.Selection implementors support this operation.
        """

        return self.get_selection_iface().select_all()


    def select_child(self, child_index):
        """
        Adds a child to the selected children list of an Atspi.Selection. For Atspi.Selection
        implementors that only allow single selections, this may replace the (single) current
        selection.
        """

        return self.get_selection_iface().select_child(child_index)
# -------------------------------------------------------------------------------------------------



# Setting Atspi.TableCell properties
# -------------------------------------------------------------------------------------------------
    def get_column_header_cells(self):
        """
        Returns the column headers as an array of cell accessibles.
        """

        return self.get_table_cell().get_column_header_cells()

    def get_column_index(self):
        """
        Returns the column headers as an array of cell accessibles.
        """

        return self.get_table_cell().get_column_index()

    def get_column_span(self):
        """
        Returns the number of columns occupied by this cell accessible. The returned values are
        meaningful only if the table cell has both STATE_VISIBLE and STATE_SHOWING.
        """

        return self.get_table_cell().get_column_span()

    def get_position(self):
        """
        Retrieves the tabular position of this cell.
        """

        return self.get_table_cell().get_position()

    def get_row_column_span(self):
        """
        Gets the row and column indexes and extents of this cell accessible. The returned values
        are meaningful only if the table cell has both STATE_VISIBLE and STATE_SHOWING.
        """

        return self.get_table_cell().get_row_column_span()

    def get_row_header_cells(self):
        """
        Returns the row headers as an array of cell accessibles.
        """

        return self.get_table_cell().get_row_header_cells()

    def get_row_span(self):
        """
        Returns the number of rows occupied by this cell accessible. The returned values are
        meaningful only if the table cell has both STATE_VISIBLE and STATE_SHOWING.
        """

        return self.get_table_cell().get_row_span()

    def get_table(self):
        """
        Returns a reference to the accessible of the containing table.
        """

        return self.get_table_cell().get_table()
# -------------------------------------------------------------------------------------------------



# Setting Atspi.Table properties
# -------------------------------------------------------------------------------------------------
    def add_column_selection(self, column):
        """
        Selects the specified column, adding it to the current column selection. Not all tables
        support column selection.
        """

        return self.get_table_iface().add_column_selection(column)

    def add_row_selection(self, row):
        """
        Selects the specified row, adding it to the current row selection. Not all tables support
        row selection.
        """

        return self.get_table_iface().add_row_selection(row)

    def get_accessible_at(self, row, column):
        """
        Gets the table cell at the specified row and column indices.
        """

        return self.get_table_iface().get_accessible_at(row, column)

    def get_caption(self):
        """
        Gets an accessible representation of the caption for an Atspi.Table.
        """

        return self.get_table_iface().get_caption()

    def get_column_at_index(self, index):
        """
        Gets the table column index occupied by the child at a particular child index.
        """

        return self.get_table_iface().get_column_at_index(index)

    def get_column_description(self, column):
        """
        Gets a text description of a particular table column. This differs from
        Atspi.Table.get_column_header, which returns an #Accessible.
        """

        return self.get_table_iface().get_column_description(column)

    def get_column_extent_at(self, row, column):
        """
        Gets the number of columns spanned by the table cell at the specific row and column (some
        tables can have cells which span multiple rows and/or columns). The returned values are
        meaningful only if the Table has both STATE_VISIBLE and STATE_SHOWING.
        """

        return self.get_table_iface().get_column_extent_at(row, column)

    def get_column_header(self, column):
        """
        Gets the header associated with a table column, if available. This differs from
        Atspi.Table.get_column_description, which returns a string.
        """

        return self.get_table_iface().get_column_header(column)

    def get_index_at(self, row, column):
        """
        Gets the header associated with a table column, if available. This differs from
        Atspi.Table.get_column_description, which returns a string.
        """

        return self.get_table_iface().get_index_at(row, column)

    def get_n_columns(self):
        """
        Gets the number of columns in an Atspi.Table, exclusive of any columns that are
        programmatically hidden, but inclusive of columns that may be outside of the current
        scrolling window or viewport.
        """

        return self.get_table_iface().get_n_columns()

    def get_n_rows(self):
        """
        Gets the number of rows in an Atspi.Table, exclusive of any rows that are programmatically
        hidden, but inclusive of rows that may be outside of the current scrolling window or viewport.
        """

        return self.get_table_iface().get_n_columns()

    def get_n_selected_columns(self):
        """
        Queries a table to find out how many columns are currently selected. Not all tables support
        column selection
        """

        return self.get_table_iface().get_n_selected_columns()

    def get_n_selected_rows(self):
        """
        Queries a table to find out how many rows are currently selected. Not all tables support
        rows selection
        """

        return self.get_table_iface().get_n_selected_rows()


    def get_row_at_index(self, index):
        """
        Gets the table row index occupied by the child at a particular 1-D child index.
        See Atspi.Table.get_index_at, Atspi.Table.get_column_at_index
        """

        return self.get_table_iface().get_row_at_index(index)

    def get_row_column_extents_at_index(self, index):
        """
        Given a child index, determines the row and column indices and extents, and whether the cell
        is currently selected.
        """

        return self.get_table_iface().get_row_column_extents_at_index(index)

    def get_row_description(self, row):
        """
        Gets a text description of a particular table row. This differs from Atspi.Table.get_row_header,
        which returns an Atspi.Accessible.
        """

        return self.get_table_iface().get_row_description(row)

    def get_row_extent_at(self, row, column):
        """
        Gets the number of rows spanned by the table cell at the specific row and column. (some
        tables can have cells which span multiple rows and/or columns). The returned values are
        meaningful only if the Table has both STATE_VISIBLE and STATE_SHOWING.
        """

        return self.get_table_iface().get_row_extent_at(row, column)

    def get_row_header(self, row):
        """
        Gets the header associated with a table row, if available. This differs from
        Atspi.Table.get_row_description, which returns a string.
        """

        return self.get_table_iface().get_row_header(row)

    def get_selected_columns(self):
        """
        Queries a table for a list of indices of columns which are currently selected.
        """

        return self.get_table_iface().get_selected_columns()

    def get_selected_rows(self):
        """
        Queries a table for a list of indices of rows which are currently selected.
        """

        return self.get_table_iface().get_selected_rows()

    def get_summary(self):
        """
        Gets an accessible object which summarizes the contents of an Atspi.Table.
        """

        return self.get_table_iface().get_summary()

    def is_column_selected(self, column):
        """
        Determines whether specified table column is selected. Not all tables support column
        selection.
        """

        return self.get_table_iface().is_column_selected(column)

    def is_row_selected(self, row):
        """
        Determines whether a table row is selected. Not all tables support row selection.
        """

        return self.get_table_iface().is_row_selected(row)

    def is_selected(self, row, column):
        """
        Determines whether the cell at a specific row and column is selected.
        """

        return self.get_table_iface().is_selected(row, column)

    def remove_column_selection(self, column):
        """
        Determines whether the cell at a specific row and column is selected.
        """

        return self.get_table_iface().remove_column_selection(column)

    def remove_row_selection(self, row):
        """
        Determines whether the cell at a specific row and column is selected.
        """

        return self.get_table_iface().remove_row_selection(row)
# -------------------------------------------------------------------------------------------------



# Setting Atspi.Text properties
# -------------------------------------------------------------------------------------------------
    def get_text(self):
        """
        Gets a range of text from an Atspi.Text object. The number of bytes in the returned string
        may exceed either end_offset or start_offset, since UTF-8 is a variable-width encoding.
        """

        return self.get_text_iface().get_text(0, -1)
# -------------------------------------------------------------------------------------------------



# Setting Atspi.Value properties
# -------------------------------------------------------------------------------------------------
    @property
    def value(self):
        """
        Gets the current value for an Atspi.Value
        """

        return self.get_value_iface().get_current_value()


    @value.setter
    def value(self, new_value):
        """
        Gets the current value for an Atspi.Value
        """

        return self.get_value_iface().set_current_value(new_value)


    @property
    def min_value(self):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        return self.get_value_iface().get_minimum_value()


    @property
    def max_value(self):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        return self.get_value_iface().get_maximum_value()


    @property
    def min_value_increment(self):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        return self.get_value_iface().get_minimum_increment()
# -------------------------------------------------------------------------------------------------

    @property
    def index_in_parent(self):
        for index, child in enumerate(self.get_parent().children):
            if child.get_parent().get_child_at_index(index) == self:
                return index

    @property
    def last_child(self):
        return not self.get_parent() or \
            self.index_in_parent is None or \
            self.index_in_parent == self.get_parent().get_child_count() - 1


    del Atspi.Accessible.children

    @property
    def children(self):

        children_list = []

        for index in range(self.get_child_count()):
            child = self.get_child_at_index(index)
            if child:
                children_list.append(child)

        return children_list


    def __len__(self):
        return self.get_child_count()


    def __getitem__(self, index):
        length = len(self)
        if index < 0:
            index = index + length
        if index < 0 or index >= length:
            raise IndexError
        return self.get_child_at_index(index)


    def __bool__(self):
        return True


    def __nonzero__(self):
        return True


    def __str__(self):
        try:
            return f"[name:{self.name} | role_name:{self.role_name} | description:{self.description}]"
        except Exception as error:
            return f"[Exception encountered]: {error}"


    @property
    def name(self):
        self.set_cache_mask(Atspi.Cache(4))
        return self.get_name()


    @property
    def role_name(self):
        return self.get_role_name()


    @property
    def description(self):
        return self.get_description()


    del Atspi.Accessible.parent
    @property
    def parent(self):
        return self.get_parent()


    def _tree_branching(self, parent_prefix, was_parent_last, node, current, cutoff):
        if current == cutoff:
            return

        prefix_spacer = "     "
        prefix_extend = "  │  "
        suffix_branch = "  ├──"
        suffix_last =   "  └──"

        new_prefix = parent_prefix
        new_suffix = ""

        if node != self:
            if node.last_child:
                new_suffix = suffix_last
            else:
                new_suffix = suffix_branch

        if node != self and node.parent != self:
            if was_parent_last:
                current_prefix = prefix_spacer
            else:
                current_prefix = prefix_extend
            new_prefix += current_prefix


        node_data = "".join((
            f"[{node.name} -",
            f" {node.role_name} -",
            f" {node.description}]"
        ))

        print(f"{new_prefix+new_suffix} {node_data}")

        for child in node.children:
            self._tree_branching(new_prefix,
                                 was_parent_last=node.last_child,
                                 node=child,
                                 current=current+1,
                                 cutoff=cutoff)


    def tree(self, cutoff=None):
        return self._tree_branching(parent_prefix="",
                                    was_parent_last=False,
                                    node=self,
                                    current=0,
                                    cutoff=cutoff)


class Root(Node):

    def applications(self):
        return self.findChildren(lambda x: x.role_name == "application")


    def application(self, application_name, retry=True):
        return self.findChild(lambda x: x.name == application_name and x.role_name == "application" and x.description=="get4-demo")


Atspi.Accessible.__bases__ = (Root, Node,) + Atspi.Accessible.__bases__


# Required for GLib.MainLoop()
registry = Registry()
root = registry.get_desktop(0)
