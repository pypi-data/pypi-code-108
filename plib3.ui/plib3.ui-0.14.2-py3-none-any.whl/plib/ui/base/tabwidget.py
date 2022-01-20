#!/usr/bin/env python3
"""
Module TABWIDGET -- UI Tab Widget
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.stdlib.coll import baselist

from plib.ui.defs import *
from plib.ui.widgets import widget_from_spec

from .app import PWidgetBase


class PTabWidgetBase(PWidgetBase, baselist):
    """Tab widget as a Python list of 2-tuples (tab-title, widget).
    """
    
    signals = (
        SIGNAL_TABSELECTED,
    )
    
    def __init__(self, manager, parent, tabs=None):
        PWidgetBase.__init__(self, manager, parent)
        baselist.__init__(self)
        self.create_tabs(tabs)
    
    def create_tabs(self, tabs):
        """Create tabs from sequence.
        
        Assumes that the sequence contains tuples of (title, spec)
        for each tab.
        """
        self.extend((title, widget_from_spec(self.manager, self, *spec)) for title, spec in tabs)
    
    def append_and_focus(self, tab):
        """Add new tab and set focus to it.
        
        Assumes that tab is a (title, widget) tuple.
        """
        self.append(tab)
        self.set_current_index(len(self) - 1)
    
    def __len__(self):
        return self.tab_count()
    
    def _indexlen(self):
        return self.tab_count()
    
    def tab_count(self):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def get_tab_title(self, index):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def set_tab_title(self, index, title):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def tab_at(self, index):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def add_tab(self, index, title, widget):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def del_tab(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _get_data(self, index):
        return (self.get_tab_title(index), self.tab_at(index))
    
    def _set_data(self, index, value):
        # This gets a little complicated because we have to delete the
        # old tab at this index and insert a new one.
        self._del_data(index)
        self._add_data(index, value)
    
    def _add_data(self, index, value):
        self.add_tab(index, value[0], value[1])
    
    def _del_data(self, index):
        self.del_tab(index)
    
    def current_index(self):
        """Return the currently selected tab index.
        
        Derived classes must implement.
        """
        raise NotImplementedError
    
    def set_current_index(self, index):
        """Set the currently selected tab index.
        
        Derived classes must implement.
        """
        raise NotImplementedError
    
    def current_title(self):
        return self[self.current_index()][0]
    
    def current_widget(self):
        return self[self.current_index()][1]
