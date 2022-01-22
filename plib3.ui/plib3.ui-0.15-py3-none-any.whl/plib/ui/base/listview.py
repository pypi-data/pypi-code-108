#!/usr/bin/env python3
"""
Module LISTVIEW -- UI Tree/List View Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import functools
import types

from plib.stdlib.coll import SortMixin

from plib.ui.defs import *
from plib.ui.base import helpers

from .app import PWidgetBase


class PListViewItemCols(helpers._PTreeHelperItemCols):
    """Exposes columns of a list view item as a sequence.
    """
    
    def _get_listviewitem(self):
        return self._helperitem
    
    listviewitem = property(_get_listviewitem)
    
    def _get_data(self, index):
        return self.listviewitem._get_col(index)
    
    def _set_data(self, index, value):
        self.listviewitem._set_col(index, value)


class PListViewHelperItem(helpers._PTreeHelperItem):
    # Common base class for items
    
    colsclass = PListViewItemCols
    
    def __init__(self, parent, index, data=None):
        self._parent = parent
        self._depth = 0
        self._listview = self._listview_from_parent(parent)
        helpers._PTreeHelperItem.__init__(self, parent, index, data)
    
    def _listview_from_parent(self, p):
        while not isinstance(p, PListViewMixin):
            p = p._parent
            self._depth += 1
        return p
    
    def _get_listview(self):
        return self._listview
    
    listview = property(_get_listview)
    
    def colcount(self):
        return self.listview.colcount()
    
    def _get_col(self, col):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_col(self, col, value):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def indexes(self):
        parent = self._parent
        return parent.indexes() + (parent.index_of(self),)
    
    def current_item(self):
        item = self.listview.current_item()
        return item if item._value() in self else None
    
    def set_current_item(self, item):
        if item._value() in self:
            self.listview.set_current_item(item)


class ExpandMixin(object):
    # Mixin to handle common code for auto-expanding tree view
    
    def expand_all(self):
        for item in self.all_items():
            item.expand_all()


class PTreeViewItemBase(ExpandMixin, PListViewHelperItem):
    """Tree view item that looks like a sequence of 2-tuples.
    
    Each 2-tuple in the sequence is of the form
    (column-values, [list of child items]). The column-values
    is a list of strings; if the list view has only one column,
    the list has a single element.
    """
    
    def expand(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def expand_all(self):
        self.expand()
        ExpandMixin.expand_all(self)


class PListViewItemBase(PListViewHelperItem):
    """List view item that looks like a sequence of strings (columns)
    """
    
    def _value(self):
        cols, _ = PTreeViewItemBase._value(self)
        return cols


class PListViewLabelsBase(helpers._PHelperColLabels):
    
    def _get_listview(self):
        return self._helper
    
    listview = property(_get_listview)


class PListViewMixin(helpers._PTreeHelper):
    """Mixin class for PTreeViewBase and PListViewBase.
    
    Implements common behaviors.
    
    Includes convenience methods to handle common special cases.
    """
    
    signals = (
        SIGNAL_LISTVIEWSELECTED,
    )
    
    def __init__(self, parent, labels=None, data=None, header_font=None):
        # Some UI toolkits define a clear method but it
        # doesn't work reliably, so we insist on using
        # ours (note that we have to create the bound
        # method by hand)
        self.clear = types.MethodType(
            helpers._PTreeHelper.clear, self)
        self._parent = parent
        helpers._PTreeHelper.__init__(self, labels, data, header_font=header_font)
    
    def colcount(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def from_flat(self, items):
        """Canonicalize list of multi-column items with no children.
        """
        return ((item, []) for item in items)
    
    def from_list(self, items):
        """Canonicalize list of single-column items with no children.
        """
        return (([item], []) for item in items)
    
    def extend_flat(self, items):
        """Adds list of multi-column items to list.
        
        Assumes no children, but multiple columns.
        """
        self.extend(self.from_flat(items))
    
    def extend_list(self, items):
        """Adds list of strings to list.
        
        Assumes a single column list box with no children.
        """
        self.extend(self.from_list(items))


class PTreeViewBase(PWidgetBase, ExpandMixin, PListViewMixin):
    """Tree view that looks like a tree of list view items.
    """
    
    def __init__(self, manager, parent, labels=None, data=None, auto_expand=False,
                 font=None, header_font=None):
        
        PListViewMixin.__init__(self, parent, labels, data, header_font=header_font)
        PWidgetBase.__init__(self, manager, parent, font=font)
        if auto_expand:
            # Have to do this here because all children must already be added
            self.expand_all()
    
    def indexes(self):
        return ()
    
    def current_indexes(self):
        return self.current_item().indexes()
    
    def wrap_target(self, signal, target):
        if signal == SIGNAL_LISTVIEWSELECTED:
            @functools.wraps(target)
            def _wrapper(item):
                target(item.cols, item.children)
            return _wrapper
        return target


class PListViewBase(PWidgetBase, PListViewMixin):
    """List view that looks like a list of multi-column items.
    """
    
    def __init__(self, manager, parent, labels=None, data=None,
                 font=None, header_font=None):
        
        if data:
            data = self.from_flat(data)  # list views cannot have children for their items
        PListViewMixin.__init__(self, parent, labels, data, header_font=header_font)
        PWidgetBase.__init__(self, manager, parent, font=font)
    
    def wrap_target(self, signal, target):
        if signal == SIGNAL_LISTVIEWSELECTED:
            @functools.wraps(target)
            def _wrapper(item):
                target(item.cols)
            return _wrapper
        return target


class ListSortMixin(SortMixin):
    """Customized mixin class for sorted list view/list box.
    """
    
    # List view/list box keys are handled in a special way; we interpret
    # the key parameter as the function to apply to each column separately,
    # so we have to adjust it before using it
    
    def _init_key(self, key):
        # Construct key function that applies given key to each list column;
        # assume that our constructed function will be called on each item
        # in a sequence of (cols, children) tuples
        return (
            (lambda x: tuple(x[0])) if key is None else
            (lambda x: tuple(key(c) for c in x[0]))
        )


class ListItemSortMixin(ListSortMixin):
    """Customized mixin class for sorted list view/list box item.
    """
    
    def __init__(self, parent, index, data=None):
        # The data is a tuple (cols, children), we have to separate it
        # out so the inherited constructor initializes the cols but we
        # initialize the children
        if data is not None:
            cols, children = data
            data = (cols, [])
        else:
            children = None
        super(ListItemSortMixin, self).__init__(parent, index, data)
        self._init_seq(children, self.listview.key)


class PSortedListViewItemBase(ListItemSortMixin, PListViewItemBase):
    """Sorted list view item.
    """
    pass


class PSortedListViewBase(ListSortMixin, PListViewBase):
    """Customized mixin class for sorted list view.
    """
    
    def __init__(self, manager, parent, labels=None, data=None, key=None,
                 font=None, header_font=None):
        
        PListViewBase.__init__(self, manager, parent, labels=labels,
                               font=font, header_font=header_font)  # don't pass data here
        if data:
            data = self.from_flat(data)  # list views cannot have children for their items
        self._init_seq(data, key)  # sort items and add them here
