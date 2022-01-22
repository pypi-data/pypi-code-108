#!/usr/bin/env python3
"""
Module COMBO -- UI Combo Box Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import collections

from plib.stdlib.builtins import inverted
from plib.stdlib.coll import baselist, SortMixin

from plib.ui.defs import *

from .app import PWidgetBase


class PComboBoxBase(PWidgetBase, baselist):
    """Combo box that looks like a list of strings.
    
    (Note: currently selection is limited to items added to the
    combo box programmatically; the user cannot edit in the edit
    control and add new items to the pick list.)
    """
    
    signals = (
        SIGNAL_SELECTED,
    )
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PWidgetBase.__init__(self, manager, parent,
                             geometry=geometry)
        baselist.__init__(self, items)
        self.complete_init(items, value)
    
    def complete_init(self, items, value):
        if value:
            self.set_current_text(value)
        elif items:
            self.set_current_index(0)
    
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


class PNumComboBoxBase(PComboBoxBase):
    """Combo box that maps strings to integer values.
    """
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        self.text_map = dict(items)  # value -> text
        self.value_map = inverted(self.text_map)  # text -> value
        str_items = [item[1] for item in items]
        PComboBoxBase.__init__(self, manager, parent, items=str_items,
                               geometry=geometry)
        if value:
            self.set_current_value(value)  # value will be an int
    
    def current_value(self):
        return self.value_map[self.current_text()]
    
    get_current_value = current_value
    
    def set_current_value(self, value):
        self.set_current_text(self.text_map[value])


class PSortedComboBoxBase(SortMixin, PComboBoxBase):
    """Combo box that automatically sorts its items.
    """
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None, key=None):
        
        PComboBoxBase.__init__(self, manager, parent, geometry=geometry)  # don't pass items here
        self._init_seq(items, key)  # sort items and add them here
        self.complete_init(items, value)  # have to do this after data is added
