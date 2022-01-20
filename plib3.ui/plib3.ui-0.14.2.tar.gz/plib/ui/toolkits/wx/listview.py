#!/usr/bin/env python3
"""
Module WX.LISTVIEW -- Python wxWidgets Tree/List View Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for the tree/list view widgets.
"""

import wx
import wx.dataview

from plib.ui.defs import *
from plib.ui.base.listview import (
    PTreeViewItemBase, PListViewLabelsBase,
    PListViewItemBase, PSortedListViewItemBase,
    PTreeViewBase, PListViewBase, PSortedListViewBase
)

from .app import PWxSequenceWidget, align_map


width_map = {
    WIDTH_CONTENTS: wx.COL_WIDTH_AUTOSIZE,
    WIDTH_STRETCH: wx.COL_WIDTH_DEFAULT,
}


class PWxListViewMixin(object):
    """Mixin class to help handle auto-sizing of columns.
    """
    
    def __init__(self):
        # Need this because the wx control doesn't use the "list of lists" model
        self._child_items = []
    
    def item_count(self):
        return len(self._child_items)
    
    def item_at(self, index):
        # FIXME: Why doesn't self._child_items[index] work?
        for i, it in enumerate(self._child_items):
            if i == index:
                return it
        return None
    
    def index_of(self, item):
        # FIXME: Why doesn't self._child_items.index(item) work?
        for i, it in enumerate(self._child_items):
            if it is item:
                return i
        return None
    
    def _add_item(self, index, item):
        # The ugly hack in the list view item _set_cols below will take care of
        # actually adding the item to the control
        if index == len(self._child_items):
            self._child_items.append(item)
        else:
            self._child_items.insert(index, item)
    
    def _del_item(self, index, item):
        del self._child_items[index]


class PWxListViewItemBase(PWxListViewMixin):
    
    def __init__(self, parent, index):
        PWxListViewMixin.__init__(self)
        if index == len(parent):
            before = None
        else:
            before = parent._items[index]
        # Ugly hack to postpone creating the wx tree item until _set_col below
        self._b = before
    
    def _del_item(self, index, item):
        PWxListViewMixin._del_item(index, item)
        self.listview.DeleteItem(item._id)
    
    def _get_col(self, col):
        return self.listview.GetItemText(self._id, col)
    
    def _set_col(self, col, value):
        value = str(value)  # just in case
        if (col == 0) and not hasattr(self, '_id'):
            if self._b is not None:
                self._id = self.listview.InsertItem(
                    self._parent._id, self._b._id, value)
            else:
                self._id = self.listview.AppendItem(
                    self._parent._id, value)
            # this trick is to allow the current_item method to work
            self.listview.SetItemData(self._id, self)
            # ugly hack to clear up the instance namespace
            del self._b
        else:
            self.listview.SetItemText(self._id, col, value)
    
    def expand(self):
        self.listview.Expand(self._id)
    
    def current_item(self):
        curr = self.listview.GetSelection()
        item = self.listview.GetItemData(curr)
        return item if item in self._child_items else None
    
    def set_current_item(self, item):
        if item in self._child_items:
            self.listview.SelectItem(item._id)


class PTreeViewItem(PWxListViewItemBase, PTreeViewItemBase):
    
    def __init__(self, parent, index, data=None):
        PWxListViewItemBase.__init__(self, parent, index)
        PTreeViewItemBase.__init__(self, parent, index, data)


class PListViewItem(PWxListViewItemBase, PListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        PWxListViewItemBase.__init__(self, parent, index)
        PListViewItemBase.__init__(self, parent, index, data)


class PSortedListViewItem(PWxListViewItemBase, PSortedListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        PWxListViewItemBase.__init__(self, parent, index)
        PSortedListViewItemBase.__init__(self, parent, index, data)


class PListViewLabels(PListViewLabelsBase):
    
    def __init__(self, helper, labels=None):
        self._add_indexes = {}
        PListViewLabelsBase.__init__(self, helper, labels)
        self.listview._id = self.listview.GetRootItem()
    
    def _set_label(self, index, label):
        if (index == self.listview.colcount()):
            # Ugly hack because we can't set the column alignment after it's added
            self._add_indexes[index] = [label]
        else:
            pass  # FIXME: how can we set the text of an already added column?
    
    def _set_width(self, index, width):
        entry = self._add_indexes.get(index)
        if entry:
            entry.append(width)
        else:
            self.listview.SetColumnWidth(index, width)
    
    def _set_align(self, index, align):
        entry = self._add_indexes.get(index)
        if entry:
            label, width = entry
            align = align_map[align]
            width = width_map.get(width, width)
            self.listview.AppendColumn(label, width, align)
            del self._add_indexes[index]
        else:
            pass  # FIXME: how can we set the alignment of an already added column?
    
    def _set_readonly(self, index, readonly):
        pass


class PWxListViewBase(PWxSequenceWidget, wx.dataview.TreeListCtrl, PWxListViewMixin):
    
    labels_class = PListViewLabels
    
    _depth_w = 30  # additional column width for each sub-level in tree
    
    _align = True  # used by panel to determine placement
    _expand = True
    
    def __init__(self, parent):
        PWxListViewMixin.__init__(self)
        
        # This will be seen by the autocols property from mixin class above
        self._autocols = {}
        wx.dataview.TreeListCtrl.__init__(self, parent,
                                          style=(wx.dataview.TL_SINGLE))
        
        # Need this because the wx control doesn't use the "list of lists" model
        self._child_items = []
    
    def _del_item(self, index, item):
        PWxListViewMixin._del_item(index, item)
        self.DeleteItem(item._id)
    
    def set_header_font_object(self, font_name, font_size, bold, italic):
        #self.GetHeaderWindow().SetFont(self._wx_font_object(
        #    font_name, font_size, bold, italic
        #))  # FIXME: how the fsck do we set the header font???
        pass
    
    def colcount(self):
        return self.GetColumnCount()
    
    def current_item(self):
        curr = self.GetSelection()
        item = self.GetItemData(curr)
        return item
    
    def current_index(self):
        item = self.current_item()
        if item in self._child_items:
            return self.index_of(item)
        return None
    
    def set_current_item(self, item):
        self.SelectItem(item._id)


class PTreeView(PWxListViewBase, PTreeViewBase):
    
    item_class = PTreeViewItem
    
    def __init__(self, manager, parent, labels=None, data=None, auto_expand=False,
                 font=None, header_font=None):
        
        PWxListViewBase.__init__(self, parent)
        PTreeViewBase.__init__(self, manager, parent, labels=labels, data=data, auto_expand=auto_expand,
                               font=font, header_font=header_font)


class PListView(PWxListViewBase, PListViewBase):
    
    item_class = PListViewItem
    
    def __init__(self, manager, parent, labels=None, data=None,
                 font=None, header_font=None):
        
        PWxListViewBase.__init__(self, parent)
        PListViewBase.__init__(self, manager, parent, labels=labels, data=data,
                               font=font, header_font=header_font)
        if labels is not None:
            self.Expand(self._id)


class PSortedListView(PWxListViewBase, PSortedListViewBase):
    
    item_class = PSortedListViewItem
    
    def __init__(self, manager, parent, labels=None, data=None, key=None,
                 font=None, header_font=None):
        
        PWxListViewBase.__init__(self, parent)
        PSortedListViewBase.__init__(self, manager, parent, labels=labels, data=data,
                                     key=key, font=font, header_font=header_font)
