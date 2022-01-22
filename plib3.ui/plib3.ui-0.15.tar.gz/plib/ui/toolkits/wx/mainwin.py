#!/usr/bin/env python3
"""
Module WX.MAINWIN -- Python wxWidgets Main Window Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI main window objects.
"""

import wx
from wx.lib.evtmgr import eventManager

from plib.ui.defs import *
from plib.ui.base.mainwin import PMenuBase, PToolBarBase, PStatusLabelBase, PStatusBarBase, PActionBase, PMainWindowBase

from .app import PWxSignal, PWxActionMixin, PWxWidget, PTopWindow, scaled_bitmap, stock_ids, parse_accel


class PWxPopup(wx.Menu):
    """Customized wxWidgets popup menu class.
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        astyle = 0
        wx.Menu.__init__(self, "", astyle)


class PWxMenu(PWxWidget, wx.MenuBar, PMenuBase):
    """Customized wxWidgets menu class.
    """
    
    popup_class = PWxPopup
    
    def __init__(self, main_window):
        astyle = 0
        wx.MenuBar.__init__(self, astyle)
        PMenuBase.__init__(self, main_window)
    
    def do_add_popup(self, title, popup):
        self.Append(popup, title)
    
    def add_popup_action(self, action, popup):
        # FIXME: the stock menu ids don't enable standard images
        if action._id > wx.ID_HIGHEST:
            item = wx.MenuItem(popup, action._id, action.menustr, action.statusbarstr)
        else:
            item = wx.MenuItem(popup, action._id)
        item.SetBitmap(scaled_bitmap(action.image, action.menufactor))
        accel = action.accelstr
        if accel is not None:
            flags, keycode = parse_accel(accel)
            item.SetAccel(wx.AcceleratorEntry(flags, keycode, cmd=action._id, item=item))
        popup.Append(item)


class PWxToolBar(PWxWidget, wx.ToolBar, PToolBarBase):
    """Customized wxWidgets toolbar class.
    """
    
    def __init__(self, main_window):
        astyle = 0
        if main_window.app.show_labels:
            astyle = astyle | wx.TB_TEXT
        wx.ToolBar.__init__(self, main_window, style=astyle)
        PToolBarBase.__init__(self, main_window)
    
    def add_action(self, action):
        s = action.toolbarstr if self.main_window.app.show_labels else ""
        img = scaled_bitmap(action.image, action.toolbarfactor)
        # FIXME: The stock toolbar ids don't enable standard captions, images,
        # tooltips, or status bar text
        toolid = action._id
        self.AddTool(toolid, s, img)
        self.SetToolShortHelp(toolid, action.toolbarstr)
        self.SetToolLongHelp(toolid, action.statusbarstr)
    
    def add_separator(self):
        self.AddSeparator()


class PStatusLabel(PStatusLabelBase):
    
    def init_status_label(self):
        self.actual_widget = self
        self.status_bar = self._parent
        self.field_index = -1
    
    fn_get_text = 'GetText'
    fn_set_text = 'SetText'
    
    def GetText(self):
        return self.status_bar.GetStatusText(self.field_index)
    
    def SetText(self, value):
        self.status_bar.SetStatusText(value, self.field_index)
        if self.status_bar._initialized:
            self.status_bar.SetStatusWidths(self.status_bar.label_widths)


status_label_styles = {
    PANEL_NONE: wx.SB_NORMAL,
    PANEL_BOX: wx.SB_NORMAL,  # TODO: is there any way to get a box border in wx?
    PANEL_RAISED: wx.SB_RAISED,
    PANEL_SUNKEN: wx.SB_SUNKEN,
}


class PWxStatusBar(PWxWidget, wx.StatusBar, PStatusBarBase):
    
    def __init__(self, main_window):
        self._initialized = False
        wx.StatusBar.__init__(self, main_window)
        PStatusBarBase.__init__(self, main_window)
    
    def add_widget(self, widget, expand=False, custom=True):
        self.labels.append(widget)
    
    char_width = 12  # TODO: is there a way to get this info from wx?
    
    @property
    def label_widths(self):
        return [-1] + [self.char_width * len(label.caption) for label in self.labels]
    
    @property
    def label_styles(self):
        label_styles = [PANEL_NONE] + [label._style for label in self.labels]
        return [status_label_styles[style] for style in label_styles]
    
    def create_widgets(self):
        self.labels = []
        super(PWxStatusBar, self).create_widgets()
        
        self.SetFieldsCount(1 + len(self.labels))
        self.SetStatusStyles(self.label_styles)
        for i, label in enumerate(self.labels):
            label.field_index = i + 1  # so GetText and SetText will access the right field
            label.caption = label._caption
        self.SetStatusWidths(self.label_widths)
        
        self._initialized = True  # so individual labels will trigger a width update if their caption changes
    
    def get_text(self):
        return self.GetStatusText(0)
    
    def set_text(self, value):
        self.SetStatusText(value, 0)


class PWxAction(PWxActionMixin, PWxSignal, PActionBase):
    """Customized wxWidgets action class.
    """
    
    def __init__(self, key, main_window):
        PActionBase.__init__(self, key, main_window)
        
        self.menufactor = 0.5
        if main_window.app.large_icons:
            self.toolbarfactor = None
        else:
            self.toolbarfactor = 0.6875
        self.menustr = self.get_menu_str(key)
        self.toolbarstr = self.get_toolbar_str(key)
        self.statusbarstr = self.get_statusbar_str(key)
        self.accelstr = self.get_accel_str(key)
        self._id = stock_ids.get(key, wx.ID_HIGHEST + key)
        self.image = self.get_icon(key)
    
    def wx_register_event(self, event, handler):
        # The usual eventManager.Register doesn't seem to work here; note
        # that this method means only a single handler can be tied to
        # action events (the latest one bound)
        self.main_window.Bind(event, handler, id=self._id)
    
    def enable(self, enabled):
        menu = self.main_window.menu
        toolbar = self.main_window.toolbar
        if menu is not None:
            menu.Enable(self._id, enabled)
        if toolbar is not None:
            toolbar.EnableTool(self._id, enabled)


class PMainWindow(PTopWindow, PMainWindowBase):
    """Customized wxWidgets main window class.
    """
    
    menu_class = PWxMenu
    toolbar_class = PWxToolBar
    statusbar_class = PWxStatusBar
    action_class = PWxAction
    
    action_signals = None
    
    def create_menu(self):
        menu = super(PMainWindow, self).create_menu()
        self.SetMenuBar(menu)
        return menu
    
    def create_toolbar(self):
        toolbar = super(PMainWindow, self).create_toolbar()
        self.SetToolBar(toolbar)
        return toolbar
    
    def create_statusbar(self):
        statusbar = super(PMainWindow, self).create_statusbar()
        self.SetStatusBar(statusbar)
        return statusbar
    
    def create_actions(self):
        actions = super(PMainWindow, self).create_actions()
        # Can't do this until after all actions are added
        if self.toolbar:
            self.toolbar.Realize()
        return actions
