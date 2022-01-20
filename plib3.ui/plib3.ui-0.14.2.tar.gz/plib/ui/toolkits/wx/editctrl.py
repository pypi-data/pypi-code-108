#!/usr/bin/env python3
"""
Module WX.EDITCTRL -- Python wxWidgets Editing Widgets
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for edit controls.
"""

import wx
from wx.lib.evtmgr import eventManager

from plib.ui.defs import *
from plib.ui.base.editctrl import PEditBoxBase, PNumEditBoxBase, PEditControlBase

from .app import PWxWidget, ec_scroll_style


class PWxEditBase(PWxWidget, wx.TextCtrl):
    
    fn_get_text = 'GetValue'
    fn_set_text = 'SetValue'
    
    fn_get_readonly = 'NotEditable'
    fn_set_readonly = 'SetNotEditable'
    
    _align = False  # used by panel to determine placement
    
    def __init__(self, parent, expand):
        self._expand_horiz = expand
        wx.TextCtrl.__init__(self, parent, style=self._style)
    
    def setup_expand(self, expand):
        pass  # this is handled differently in wx, see constructor above
    
    def NotEditable(self):
        return not self.IsEditable()
    
    def SetNotEditable(self, value):
        self.SetEditable(not value)


class PEditBox(PWxEditBase, PEditBoxBase):
    
    _style = wx.TE_PROCESS_ENTER
    
    def __init__(self, manager, parent, text="",
                 geometry=None, expand=True):
        
        PWxEditBase.__init__(self, parent, expand)
        PEditBoxBase.__init__(self, manager, parent, text,
                              geometry=geometry, expand=expand)


# FIXME: Wx docs say this class should exist, but can't find it

class IntegerValidator(wx.Validator):
    
    def __init__(self, value=0):
        wx.Validator.__init__(self)
        self.value = value
    
    # FIXME: Wx docs say you're supposed to always implement Clone, but
    # doing that breaks the validator
    
    def IsValid(self, value):
        try:
            int(value)
        except (TypeError, ValueError):
            return False
        else:
            return True
    
    def OnTextEvent(self, event):
        text = self.GetWindow().GetValue()
        if not self.IsValid(text):
            self.GetWindow().ChangeValue(str(self.value))
            event.StopPropagation()
        else:
            self.value = int(text)
            event.Skip()
    
    def Validate(self, parent):
        return IsValid(parent.GetValue())
    
    def TransferFromWindow(self):
        self.value = int(self.GetWindow().GetValue())
    
    def TransferToWindow(self):
        self.GetWindow().SetValue(str(self.value))


class PNumEditBox(PWxEditBase, PNumEditBoxBase):
    
    _style = wx.TE_PROCESS_ENTER
    
    def __init__(self, manager, parent, value=0,
                 geometry=None, expand=True):
        
        PWxEditBase.__init__(self, parent, expand)
        self.val = val = IntegerValidator()
        self.SetValidator(val)
        val.SetWindow(self)  # FIXME: isn't Wx supposed to do this automatically in SetValidator?
        # Bypass the normal setup_notify mechanism because we don't want a wrapper
        eventManager.Register(val.OnTextEvent, wx.EVT_TEXT, self)
        PNumEditBoxBase.__init__(self, manager, parent, value,
                                 geometry=geometry, expand=expand)
    
    def set_value(self, value):
        super(PNumEditBox, self).set_value(value)
        self.val.value = value


class PEditControl(PWxEditBase, PEditControlBase):
    
    _style = wx.TE_MULTILINE | wx.TE_PROCESS_TAB
    
    _align = True  # used by panel to determine placement
    _expand = True
    
    def __init__(self, manager, parent, text="",
                 scrolling=False, font=None):
        
        if scrolling:
            self._style = self._style | ec_scroll_style
        PWxEditBase.__init__(self, parent, True)  # automatically expands
        PEditControlBase.__init__(self, manager, parent, text,
                                  scrolling=scrolling, font=font)
        
        self._overwrite_mode = False  # since wx does not have a built-in property for this
        self._modified = False  # since wx does not have a built-in text mod change event
        self._selection = False  # since wx does not have a built-in text state change event
        self._mpending = False  # since the EVT_CHAR handler gets called before the modification state is updated
        self._spending = False  # since the EVT_CHAR handler gets called before the selection changes
        # Bypass the normal setup_notify mechanism because we don't want a wrapper
        eventManager.Register(self.OnKeyEvent, wx.EVT_CHAR, self)
        eventManager.Register(self.OnIdleEvent, wx.EVT_IDLE, self)
    
    def OnKeyEvent(self, event):
        # Can't actually test for mod/selection change yet since the event has to be handled first
        self._mpending = True
        self._spending = True
        event.Skip()
    
    def OnIdleEvent(self, event):
        if self._mpending:
            # A key was pressed so check the modification state
            modified = self.IsModified()
            if modified != self._modified:
                self._modified = modified
                self.forward_event(SIGNAL_TEXTMODCHANGED, event, None)
            self._mpending = False
        # Wait until next idle event if both pending flags were set
        elif self._spending:
            # The super call above changed the selection state, so now we can test it
            selection = bool(self.GetStringSelection())
            if selection != self._selection:
                self._selection = selection
                self.forward_event(SIGNAL_TEXTSTATECHANGED, event, None)
            self._spending = False
        event.Skip()  # FIXME: this doesn't seem to be needed?
    
    # FIXME: no way to programmatically get or set overwrite mode in wx? Ins key works
    
    def GetOverwriteMode(self):
        return self._overwrite_mode
    
    def SetOverwriteMode(self, value):
        if value != self._overwrite_mode:
            # TODO: Fake an Ins key press
            pass
        self._overwrite_mode = value
    
    def setup_scrolling(self, scrolling):
        pass  # this must be done in the constructor in wxWidgets
    
    fn_get_overwrite = 'GetOverwriteMode'
    fn_set_overwrite = 'SetOverwriteMode'
    
    # FIXME: No undo facility in wx on non-Windows platforms
    
    def can_undo(self):
        return self.CanUndo()
    
    def can_redo(self):
        return self.CanRedo()
    
    def can_clip(self):
        return self.CanCut() or self.CanCopy()
    
    def can_paste(self):
        return self.CanPaste()
    
    def clear_edit(self):
        self.Clear()
    
    def undo_last(self):
        self.Undo()
    
    def redo_last(self):
        self.Redo()
    
    def select_all(self):
        self.SelectAll()
    
    def clear_selection(self):
        self.SelectNone()
    
    def delete_last_cut(self):
        pass  # wx handles this differently, see next method
    
    def delete_selected(self):
        self.Remove(*self.GetSelection())
    
    def copy_to_clipboard(self):
        self.Cut()
    
    def cut_to_clipboard(self):
        self.Copy()
    
    def paste_from_clipboard(self):
        self.Paste()
