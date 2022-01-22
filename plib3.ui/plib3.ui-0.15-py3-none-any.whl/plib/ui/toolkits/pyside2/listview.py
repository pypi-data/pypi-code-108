#!/usr/bin/env python3
"""
Module PYSIDE2.LISTVIEW -- Python PySide 2 Tree/List View Objects
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for the tree/list view widgets.
"""

from PySide2 import QtWidgets as qt

from plib.ui.base.listview import (
    PTreeViewItemBase, PListViewLabelsBase,
    PListViewItemBase, PSortedListViewItemBase,
    PTreeViewBase, PListViewBase, PSortedListViewBase
)

from .app import PQtSequence, PQtSequenceWidget, align_map
from .header import PQtHeaderBase, PQtHeaderWidget


class PQtListViewItemBase(PQtSequence, qt.QTreeWidgetItem):
    
    def item_count(self):
        return self.childCount()
    
    def item_at(self, index):
        return self.child(index)
    
    def index_of(self, item):
        return self.indexOfChild(item)
    
    def _add_item(self, index, item):
        if index == len(self):
            self.addChild(item)
        else:
            self.insertChild(index, item)
    
    def _del_item(self, index, item):
        self.takeChild(index)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
        # FIXME: it would be nice if this could be done once instead of
        # per item
        self.setTextAlignment(col,
                              self.listview.headerItem().textAlignment(col))


class PTreeViewItem(PQtListViewItemBase, PTreeViewItemBase):
    
    def __init__(self, parent, index, data=None):
        PQtListViewItemBase.__init__(self)
        PTreeViewItemBase.__init__(self, parent, index, data)
    
    def expand(self):
        self.setExpanded(True)


class PListViewItem(PQtListViewItemBase, PListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        PQtListViewItemBase.__init__(self)
        PListViewItemBase.__init__(self, parent, index, data)


class PSortedListViewItem(PQtListViewItemBase, PSortedListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        PQtListViewItemBase.__init__(self)
        PSortedListViewItemBase.__init__(self, parent, index, data)


class PListViewLabels(PQtHeaderBase, PListViewLabelsBase):
    
    def _set_labels_from_list(self, label_list):
        self.listview.setHeaderLabels(label_list)
    
    def _header_item(self, index):
        return self.listview.headerItem()
    
    def _header_view(self):
        return self.listview.header()
    
    def _set_align(self, index, align):
        item = self.listview.headerItem()
        item.setTextAlignment(index, align_map[align])
        # each item will align itself when added


class PQtListViewBase(PQtHeaderWidget, PQtSequenceWidget, qt.QTreeWidget):
    
    labels_class = PListViewLabels
    
    def __init__(self, parent):
        qt.QTreeWidget.__init__(self, parent)
        self.header().setStretchLastSection(False)
        self.setSortingEnabled(False)
        self.setRootIsDecorated(True)
    
    def item_count(self):
        return self.topLevelItemCount()
    
    def item_at(self, index):
        return self.topLevelItem(index)
    
    def index_of(self, item):
        return self.indexOfTopLevelItem(item)
    
    def _add_item(self, index, item):
        if index == len(self):
            self.addTopLevelItem(item)
        else:
            self.insertTopLevelItem(index, item)
    
    def _del_item(self, index, item):
        self.takeTopLevelItem(index)
    
    def header_object(self):
        return self.header()
    
    def colcount(self):
        return self.columnCount()
    
    def current_item(self):
        return self.currentItem()
    
    def set_current_item(self, item):
        self.setCurrentItem(item)


class PTreeView(PQtListViewBase, PTreeViewBase):
    
    item_class = PTreeViewItem
    
    def __init__(self, manager, parent, labels=None, data=None, auto_expand=False,
                 font=None, header_font=None):
        
        PQtListViewBase.__init__(self, parent)
        PTreeViewBase.__init__(self, manager, parent, labels=labels, data=data, auto_expand=auto_expand,
                               font=font, header_font=header_font)


class PListView(PQtListViewBase, PListViewBase):
    
    item_class = PListViewItem
    
    def __init__(self, manager, parent, labels=None, data=None,
                 font=None, header_font=None):
        
        PQtListViewBase.__init__(self, parent)
        PListViewBase.__init__(self, manager, parent, labels=labels, data=data,
                               font=font, header_font=header_font)


class PSortedListView(PQtListViewBase, PSortedListViewBase):
    
    item_class = PSortedListViewItem
    
    def __init__(self, manager, parent, labels=None, data=None, key=None,
                 font=None, header_font=None):
        
        PQtListViewBase.__init__(self, parent)
        PSortedListViewBase.__init__(self, manager, parent, labels=labels, data=data,
                                     key=key, font=font, header_font=header_font)
