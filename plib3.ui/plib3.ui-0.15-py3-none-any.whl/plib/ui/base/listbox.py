#!/usr/bin/env python3
"""
Module LISTBOX-- UI List Box Widget
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import functools

from plib.stdlib.coll import baselist, SortMixin

from plib.ui.defs import *

from .app import PWidgetBase


class PListBoxBase(PWidgetBase, baselist):
    """List box that looks like a list of strings.
    """
    
    signals = (
        SIGNAL_LISTBOXSELECTED,
    )
    
    default_itemheight = 30
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PWidgetBase.__init__(self, manager, parent,
                             geometry=geometry)
        baselist.__init__(self, items)
        self.complete_init(items, value)
    
    def complete_init(self, items, value):
        if items:
            self.set_min_height(self.minheight())
        if value:
            self.set_current_text(value)
    
    def item_height(self, index):
        return self.default_itemheight
    
    def minheight(self):
        return sum(self.item_height(index) for index in range(len(self)))
    
    def item_text(self, item):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def wrap_target(self, signal, target):
        if signal == SIGNAL_LISTBOXSELECTED:
            @functools.wraps(target)
            def _wrapper(item):
                target(self.item_text(item))
            return _wrapper
        return target
    
    def current_text(self):
        return self[self.current_index()]
    
    get_current_text = current_text
    
    def set_current_text(self, text):
        self.set_current_index(self.index(text))
    
    def current_index(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_current_index(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PSortedListBoxBase(SortMixin, PListBoxBase):
    """List box that automatically sorts its items.
    """
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None, key=None):
        
        PListBoxBase.__init__(self, manager, parent, geometry=geometry)  # don't pass items here
        self._init_seq(items, key)  # sort items and add them here
        self.complete_init(items, value)  # do this since the inherited constructor didn't see items or value
