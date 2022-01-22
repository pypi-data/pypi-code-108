#!/usr/bin/env python3
"""
Module HELPERS -- UI Widget Helper Classes
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines "helper" classes that implement the basic functionality
to make widgets look like Python containers. The two basic
container structures supported are:

- A "row" structure: the top-level container is a sequence of rows,
  and each row is in turn a sequence of columns. The top-level
  container is fully mutable (new rows can be inserted/appended,
  and existing rows can be deleted), but each row is of fixed length
  (columns cannot be added or deleted).

- A "tree" structure: the top-level container is a mutable list of items,
  where each item is a 2-sequence: the first member is a fixed-length
  sequence of columns, and the second member is a list of sub-items,
  which has the same structure recursively.
"""

from plib.stdlib.coll import abstractlist, basesequence, normalize

from plib.ui.defs import *
from plib.ui.common import font_args


class PHeaderLabel(object):
    """Encapsulates a header label for classes that use the helpers below.
    """
    
    def __init__(self, text, width=WIDTH_CONTENTS, align=ALIGN_LEFT, readonly=False):
        self.text = text
        self.width = width  # positive int, or WIDTH_CONTENTS or WIDTH_STRETCH
        self.align = align
        self.readonly = readonly
    
    def __str__(self):
        return self.text


class _PHelperData(object):
    # Abstract base class for helper items that update displayed
    # text from data.
    
    def __init__(self, data=None):
        if data is not None:
            self._update(data)
    
    def _update(self, data):
        """Derived classes must implement to populate widget from data.
        """
        raise NotImplementedError


class _PHelperItem(_PHelperData):
    # Abstract mixin class for helper items. See the PHelper docstring
    # below for more details.
    
    def __init__(self, index, data=None):
        self._i = index
        _PHelperData.__init__(self, data)
    
    def _value(self):
        """Derived classes must implement to get widget data.
        """
        raise NotImplementedError


class _PColsMixin(basesequence):
    # Mixin class to expose multiple columns of a single row
    # or node in a multi-column widget as a sequence. Designed to
    # be a mixin or helper for a _PHelperItem subclass. Assumes
    # that data is a sequence of strings.
    
    _updating = False
    
    def _update(self, data):
        self._updating = True
        self._len = len(data)
        for index, item in enumerate(data):
            self[index] = item
        self._updating = False
    
    def _indexlen(self):
        return self._len


class _PHelperColLabels(_PColsMixin, _PHelperData):
    # Encapsulates the column labels of a multi-column widget
    # with _PHelper.
    
    def __init__(self, helper, labels=None):
        self._helper = helper
        # Allow each label to be either a string (title only), or a tuple of arguments
        # (to allow width, alignment, and readonly args to be given)
        labels = [PHeaderLabel(*((args,) if isinstance(args, str) else args)) for args in labels]
        _PHelperData.__init__(self, labels)
    
    def _get_data(self, index):
        return self._get_label(index)
    
    def _set_data(self, index, value):
        self._set_label(index, str(value))
        self._set_width(index, value.width)
        self._set_align(index, value.align)
        self._set_readonly(index, value.readonly)
    
    def _get_label(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_label(self, index, label):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_width(self, index, width):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_align(self, index, align):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_readonly(self, index, readonly):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class _PHelper(abstractlist):
    """Make a widget look like a list of child items.
    
    Abstract class to provide common methods to make a widget look
    like a list of 'child' items. Each 'child' item should be a mixin
    of a _PHelperItem (see above) and either a child widget (such as a
    PListViewItem child of a PListView) or an object that manages a
    portion of the parent widget (such as a PTableRow for managing a
    single row of a PTable).
    
    Note that the basic method of implementation for this class is to
    override key list methods to provide "hooks" for side effects to
    occur when items are added or deleted. The "hook" methods must then
    be overridden in derived/mixin classes to implement the specific
    side effects desired (such as adding/deleting items from a list
    view or rows from a table).
    
    Note also that most of the sequence emulation methods work with the
    actual 'values', not the helper items. To access the helper items,
    use the items attribute (which is a standard dict mapping index
    values to the helper items).
    """
    
    labels_class = None
    
    def __init__(self, labels=None, data=None, header_font=None):
        if header_font is not None:
            # Do this before adding data
            if isinstance(header_font, str):
                header_font = (header_font,)  # font name only is allowed
            self.set_header_font(*header_font)
        if (labels is not None) and (self.labels_class is not None):
            self.labels = self.labels_class(self, labels)
        else:
            self.labels = []
        abstractlist.__init__(self, data)
    
    def __len__(self):
        return self.item_count()
    
    def _indexlen(self):
        return self.item_count()
    
    def item_count(self):
        """Return the number of items.
        
        Derived classes must override to implement.
        """
        raise NotImplementedError
    
    def item_at(self, index):
        """Return the item at the given index.
        
        Derived classes must override to implement.
        """
        raise NotImplementedError
    
    def index_of(self, item):
        """Return the index of the item.
        
        Derived classes must override to implement.
        """
        raise NotImplementedError
    
    def all_items(self):
        for index in range(self.item_count()):
            yield self.item_at(index)
    
    def set_header_font(self, font_name=None, font_size=None,
                        bold=None, italic=None):
        
        self.set_header_font_object(*font_args(
            self,
            font_name,
            font_size,
            bold,
            italic
        ))
    
    def set_header_font_object(self, font_name, font_size, bold, italic):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _newitem(self, index, value):
        # Derived classes can override to change the signature of
        # the item class or substitute another callable that returns
        # an item instance.
        return self.item_class(self, index, value)
    
    def _get(self, index):
        # Return the value of the helper item at index. Note that we assume
        # each item stored in the items dict is a _PHelperItem or derived from it.
        return self.item_at(index)._value()
    
    def _set(self, index, value):
        # Update helper item at index with new value. Note that this method
        # should never be called with an index out of range (meaning that the
        # index will always be in the items dict); adding a new item should
        # always be done using the _add method.
        self.item_at(index)._update(value)
    
    def _add_item(self, index, item):
        # Add new item at index
        raise NotImplementedError
    
    def _add(self, index, value):
        # Insert or append a helper item wrapped around value.
        item = self._newitem(index, value)
        self._add_item(index, item)
    
    def _del_item(self, index, item):
        # Delete item at index
        raise NotImplementedError
    
    def _del(self, index):
        # Delete the helper item at index.
        item = self.item_at(index)
        self._del_item(index, item)
    
    # Note: we subclass abstractlist instead of baselist because we don't
    # want to support slicing
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return self._get(normalize(self.__len__(), index))
        else:
            raise TypeError("List index must be an int.")
    
    def __setitem__(self, index, value):
        if isinstance(index, int):
            self._set(normalize(self.__len__(), index), value)
        else:
            raise TypeError("List index must be an int.")
    
    def __delitem__(self, index):
        if isinstance(index, int):
            self._del(normalize(self.__len__(), index))
        else:
            raise TypeError("List index must be an int.")
    
    def insert(self, index, value):
        if isinstance(index, int):
            self._add(normalize(self.__len__(), index, noraise=True), value)
        else:
            raise TypeError("List index must be an int.")


class _PRowHelperItem(_PColsMixin, _PHelperItem):
    """Helper item that exposes a sequence of columns.
    
    Intended to map to a row in a multi-column widget which does *not*
    have nested tree functionality, such as a table.
    """
    
    def __init__(self, helper, index, data=None):
        self._helper = helper
        _PHelperItem.__init__(self, index, data)
    
    def _value(self):
        # This item already appears as a sequence of column values
        return self


class _PRowHelper(_PHelper):
    """Helper class for list or table-type widgets.
     
    Assumes that each row has a helper item, but no nested tree structure.
    """
    
    def __init__(self, labels=None, data=None, header_font=None):
        self._rowlist = []  # these widgets won't store rows so we have to
        _PHelper.__init__(self, labels, data, header_font=header_font)
    
    def item_count(self):
        result = self.rowcount()
        assert result == len(self._rowlist)
        return result
    
    def index_of(self, item):
        return self._rowlist.index(item)
    
    def item_at(self, index):
        return self._rowlist[index]
    
    def _add(self, index, value):
        self._insert_row(index)
        _PHelper._add(self, index, value)
    
    def _add_item(self, index, item):
        self._rowlist.insert(index, item)
    
    def _del(self, index):
        _PHelper._del(self, index)
        self._remove_row(index)
    
    def _del_item(self, index):
        del self._rowlist[index]
    
    def _insert_row(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _remove_row(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def rowcount(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def current_row(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def current_item(self):
        r = self.current_row()
        if r < 0:
            return None
        else:
            return self.item_at(r)


class _PTreeHelper(_PHelper):
    """Helper class for tree-type widgets.
    
    Provides methods to easily manage a tree with this object as root.
    """
    
    def current_item(self):
        """Return the currently selected helper item.
        
        Derived classes must override to implement.
        """
        raise NotImplementedError
    
    def set_current_item(self, item):
        """Set the currently selected helper item.
        
        Derived classes must override to implement.
        """
        raise NotImplementedError
    
    def current_index(self):
        item = self.current_item()
        if item is not None:
            return self.index_of(item)
        return None
    
    def set_current_index(self, index):
        self.set_current_item(self.item_at(index))


class _PTreeHelperItemCols(_PColsMixin, _PHelperData):
    """Expose columns of a tree view node as a sequence.
    """
    
    def __init__(self, helperitem, data=None):
        self._helperitem = helperitem
        _PHelperData.__init__(self, data)


class _PTreeHelperItem(_PHelperItem, _PTreeHelper):
    """Tree helper item that is also the root of its own subtree.
    
    Helper item that appears as its own nested sequence of
    helper items, intended to map to a tree-style widget such
    as a list view item. The data parameter must be a 2-tuple,
    with the first item being this item's strings (may be more
    than one because of columns), and the second item being a
    sequence of child data 2-tuples. The sequence of column
    strings is also exposed as the cols attribute.
    """
    
    colsclass = None
    
    def __init__(self, parent, index, data=None):
        self._parent = parent
        if data is not None:
            cols, children = data
        else:
            cols = children = None
        if not hasattr(self.__class__, 'item_class'):
            self.__class__.item_class = self.__class__
        if (self.colsclass is not None) and not hasattr(self, 'cols'):
            self.cols = self.colsclass(self, cols)
        self.children = children
        _PHelperItem.__init__(self, index)  # data must be None (it's in cols)
        _PTreeHelper.__init__(self, None, children)  # labels must be None
    
    def _value(self):
        # The item should appear as a sequence of 2-tuples
        return (self.cols, self.children)
