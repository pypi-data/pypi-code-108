#!/usr/bin/env python3
"""
UI-SIGNALS.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A demo app that tests all of the available UI signals.
"""

import sys
import os

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.app import PApplication
from plib.ui.output import PTextOutput
from plib.ui.widgets import *


number_strings = ("One", "Two", "Three", "Four", "Five", "Six")


class UISignalTester(PApplication):
    
    about_data = {
        'name': "UISignalTester",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "UI Signal Test Demo",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net"
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    main_title = "UI Signal Tester"
    
    main_size = SIZE_CLIENTWRAP
    main_placement = MOVE_CENTER
    
    main_widget = frame(ALIGN_JUST, LAYOUT_HORIZONTAL, [
        tabwidget('panels', [
            ('Dialog', tab(ALIGN_JUST, LAYOUT_VERTICAL, [
                button('action', "Test Clicked"),
                checkbox('option', "Test Toggled"),
                sorted_combo('selection', (numstr.lower() for numstr in number_strings)),
                edit('text'),
                num_edit('num'),
                sorted_listbox('list', ("Item {}".format(numstr) for numstr in number_strings)),
                padding(),
            ])),
            ('Memo', memo('notes')),
            ('Tree', treeview('tree', [("Title", WIDTH_CONTENTS), ("Description", WIDTH_STRETCH)], (
                (("Item {}".format(numstr), "Tree item {}".format(numstr.lower())), tuple(
                    (("Sub-item {} {}".format(numstr, substr), "Tree sub-item {} {}".format(numstr, substr)), ())
                    for substr in number_strings[:3]
                ))
                for numstr in number_strings
            ), auto_expand=True)),
            ('List', sorted_listview('items', [("Title", WIDTH_CONTENTS), ("Description", WIDTH_STRETCH)], (
                ("Item {}".format(numstr), "List item {}".format(numstr.lower()))
                for numstr in number_strings
            ))),
            ('Table', table('cells', [("Title", WIDTH_CONTENTS), ("Description", WIDTH_STRETCH)], (
                ("Row {}".format(numstr), "Table row {}".format(numstr.lower()))
                for numstr in number_strings
            ))),
        ]),
        text('output'),
    ])
    
    def before_create(self):
        # We can't call output_message here because widgets aren't available yet
        print("before_create")
    
    def after_create(self):
        self.outputfile = PTextOutput(self.text_output)
        self.output_message("after_create")
    
    def output_message(self, message):
        print(message)
        self.outputfile.write("{}{}".format(message, os.linesep))
        self.outputfile.flush()
    
    def focus_in(self, widget_name):
        self.output_message("SIGNAL_FOCUS_IN {}".format(widget_name))
    
    def focus_out(self, widget_name):
        self.output_message("SIGNAL_FOCUS_OUT {}".format(widget_name))
    
    def on_text_focus_in(self):
        self.focus_in('edit_text')
    
    def on_text_focus_out(self):
        self.focus_out('edit_text')
    
    def on_notes_focus_in(self):
        self.focus_in('memo_notes')
    
    def on_notes_focus_out(self):
        self.focus_out('memo_notes')
    
    def on_panels_selected(self, index):
        assert self.tabwidget_panels.current_index() == index
        self.output_message("SIGNAL_TABSELECTED {} {}".format(
            index, self.tabwidget_panels[index][0])
        )
    
    def on_action_clicked(self):
        self.output_message("SIGNAL_CLICKED")
    
    def on_option_toggled(self, checked):
        assert checked == self.checkbox_option.checked
        self.output_message("SIGNAL_TOGGLED {}".format(('off', 'on')[checked]))
    
    def on_selection_selected(self, index):
        assert self.combo_selection.current_index() == index
        assert self.combo_selection.current_text() == self.combo_selection[index]
        self.output_message("SIGNAL_SELECTED {} {}".format(index, self.combo_selection.current_text()))
    
    def on_text_changed(self, text):
        assert text == self.edit_text.edit_text
        self.output_message("SIGNAL_EDITCHANGED {}".format(text))
    
    def on_text_enter(self):
        self.output_message("SIGNAL_ENTER")
    
    def on_num_changed(self, value):
        assert value == self.edit_num.edit_value
        self.output_message("SIGNAL_EDITCHANGED {}".format(value))
    
    def on_list_selected(self, item):
        assert item == self.listbox_list.current_text()
        assert item == self.listbox_list[self.listbox_list.current_index()]
        self.output_message("SIGNAL_LISTSELECTED {} {} {}".format(
            'listbox', self.listbox_list.current_index(), item
        ))
    
    def on_notes_changed(self):
        self.output_message("SIGNAL_TEXTCHANGED {}".format(self.memo_notes.edit_text))
    
    def on_notes_mod_changed(self, changed):
        self.output_message("SIGNAL_TEXTMODCHANGED {} {}".format(self.memo_notes.edit_text, changed))
    
    def on_notes_state_changed(self):
        self.output_message("SIGNAL_TEXTSTATECHANGED memo_notes")
    
    def on_tree_selected(self, cols, children):
        assert (cols, children) == (self.treeview_tree.current_item().cols, self.treeview_tree.current_item().children)
        self.output_message("SIGNAL_LISTSELECTED {} ({}) {} {} {}".format(
            'treeview', " ".join(str(i) for i in self.treeview_tree.current_indexes()), len(children), *cols
        ))
    
    def on_items_selected(self, cols):
        assert cols == self.listview_items.current_item().cols
        assert cols == self.listview_items[self.listview_items.current_index()]
        self.output_message("SIGNAL_LISTSELECTED {} {} {} {}".format(
            'listview', self.listview_items.current_index(), *cols
        ))
    
    def on_cells_selected(self, curr_row, curr_col, prev_row, prev_col):
        assert self.table_cells.current_row() == curr_row
        assert self.table_cells.current_col() == curr_col
        assert self.table_cells.current_cell() == self.table_cells[curr_row][curr_col]
        self.output_message("SIGNAL_CELLSELECTED ({}, {}) -> ({}, {}) {}".format(
            str(prev_row), str(prev_col), str(curr_row), str(curr_col), self.table_cells.current_cell())
        )
    
    def on_cells_changed(self, row, col):
        assert self.table_cells.current_row() == row
        assert self.table_cells.current_col() == col
        assert self.table_cells.current_cell() == self.table_cells[row][col]
        self.output_message("SIGNAL_CELLCHANGED {} {} {}".format(
            str(row), str(col), self.table_cells.current_cell())
        )
    
    queryclose_handled = False
    
    def on_app_queryclose(self):
        self.queryclose_handled = True
        self.output_message("SIGNAL_QUERYCLOSE")
    
    def accept_close(self):
        print("SIGNAL_QUERYCLOSE handled:", self.queryclose_handled)
        return self.queryclose_handled
    
    def on_app_closing(self):
        self.output_message("SIGNAL_CLOSING")
    
    def on_app_shown(self):
        self.output_message("SIGNAL_SHOWN")
    
    def on_app_hidden(self):
        self.output_message("SIGNAL_HIDDEN")
    
    def before_quit(self):
        # We can't call output_message here because widgets might not be available
        # any more
        print("before_quit")


if __name__ == "__main__":
    UISignalTester().run()
