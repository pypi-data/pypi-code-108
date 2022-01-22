#!/usr/bin/env python3
"""
Module WX.APP -- Python wxWidgets Application Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI application objects.
"""

from abc import ABCMeta
import functools
import string

import wx
import wx.adv
import wx.dataview
import wx.grid
from wx.lib.evtmgr import eventManager
from wx.lib.newevent import NewEvent

from plib.ui.defs import *
from plib.ui.base.app import (
    PMessageBoxBase, PFileDialogBase, PAboutDialogBase,
    PTopWindowBase, PApplicationBase
)


# Style constant for edit controls that are scrolling

ec_scroll_style = wx.VSCROLL | wx.HSCROLL | wx.TE_DONTWRAP

# FIXME: These are only good for buttons and menus, and the toolbar ones
# in wx.ArtProvider don't match all the ids! WTF!@#$%^&*()
# FIXME: Even the menu ones don't all work properly
stock_ids = {
    ACTION_FILE_NEW: wx.ID_NEW,
    ACTION_FILE_OPEN: wx.ID_OPEN,
    ACTION_FILE_SAVE: wx.ID_SAVE,
    ACTION_FILE_SAVEAS: wx.ID_SAVEAS,
    ACTION_FILE_CLOSE: wx.ID_CLOSE,
    #ACTION_EDIT: wx.ID_EDIT,
    ACTION_EDIT_UNDO: wx.ID_UNDO,
    ACTION_EDIT_REDO: wx.ID_REDO,
    ACTION_EDIT_CUT: wx.ID_CUT,
    ACTION_EDIT_COPY: wx.ID_COPY,
    ACTION_EDIT_PASTE: wx.ID_PASTE,
    ACTION_EDIT_DELETE: wx.ID_DELETE,
    #ACTION_EDIT_SELECTALL: wx.ID_SELECTALL,
    #ACTION_REFRESH: wx.ID_REFRESH,
    #ACTION_ADD: wx.ID_ADD,
    #ACTION_REMOVE: wx.ID_REMOVE,
    #ACTION_APPLY: wx.ID_APPLY,
    #ACTION_OK: wx.ID_OK,
    #ACTION_CANCEL: wx.ID_CANCEL,
    #ACTION_PREFS: wx.ID_PREFERENCES,
    ACTION_ABOUT: wx.ID_ABOUT,
    ACTION_EXIT: wx.ID_EXIT
}

align_map = {
    ALIGN_LEFT: wx.ALIGN_LEFT,
    ALIGN_CENTER: wx.ALIGN_CENTER_HORIZONTAL,
    ALIGN_RIGHT: wx.ALIGN_RIGHT,
}

icon_map = {
    MBOX_INFO: wx.ICON_INFORMATION,
    MBOX_WARN: wx.ICON_EXCLAMATION,
    MBOX_ERROR: wx.ICON_ERROR,
    MBOX_QUERY: wx.ICON_QUESTION
}

font_families = {
    wx.FONTFAMILY_ROMAN: ["Times New Roman"],
    wx.FONTFAMILY_SWISS: ["Arial", "Verdana"],
    wx.FONTFAMILY_MODERN: ["Courier New"]
}

color_map = {
    COLOR_BLACK: wx.BLACK,  # wx.Colour(0, 0, 0)
    COLOR_DARKRED: wx.Colour(63, 0, 0),
    COLOR_RED: wx.RED,  # wx.Colour(127, 0, 0)
    COLOR_DARKGREEN: wx.Colour(0, 63, 0),
    COLOR_GREEN: wx.GREEN,  # wx.Colour(0, 127, 0)
    COLOR_LIGHTGREEN: wx.Colour(0, 255, 0),
    COLOR_DARKBLUE: wx.Colour(0, 0, 63),
    COLOR_BLUE: wx.BLUE,  # wx.Colour(0, 0, 127)
    COLOR_LIGHTBLUE: wx.Colour(0, 0, 255),
    COLOR_YELLOW: wx.YELLOW,  # wx.Colour(255, 255, 0)
    COLOR_MAGENTA: wx.Colour(255, 0, 255),
    COLOR_CYAN: wx.CYAN,  # wx.Colour(0, 255, 255)
    COLOR_DARKGRAY: wx.Colour(63, 63, 63),
    COLOR_GRAY: wx.Colour(127, 127, 127),
    COLOR_LIGHTGRAY: wx.LIGHT_GREY,  # wx.Colour(191, 191, 191)
    COLOR_WHITE: wx.WHITE,  # wx.Colour(255, 255, 255)
}

# Wx doesn't provide any standard shortcuts, so we have to
# roll our own; this is our best guess at what is common to
# the various possible platforms

accel_map = {
    ACTION_FILE_NEW: "Ctrl+N",
    ACTION_FILE_OPEN: "Ctrl+O",
    ACTION_FILE_SAVE: "Ctrl+S",
    ACTION_FILE_SAVEAS: "Ctrl+Shift+S",
    ACTION_FILE_CLOSE: "Ctrl+W",
    ACTION_EDIT_UNDO: "Ctrl+Z",
    ACTION_EDIT_REDO: "Ctrl+Shift+Z",
    ACTION_EDIT_CUT: "Ctrl+X",
    ACTION_EDIT_COPY: "Ctrl+C",
    ACTION_EDIT_PASTE: "Ctrl+V",
    ACTION_EDIT_DELETE: "Ctrl+D",
    ACTION_EDIT_SELECTALL: "Ctrl+A",
    ACTION_EDIT_SELECTNONE: "Ctrl+Shift+A",
    #ACTION_EDIT_OVERWRITE: "Ins",  # this already seems to be built in to wx
    #ACTION_EDIT_CLEAR: ,
    #ACTION_VIEW: ,
    #ACTION_EDIT: ,
    #ACTION_OK: ,
    #ACTION_CANCEL: ,
    ACTION_REFRESH: "F5",
    #ACTION_ADD: ,
    #ACTION_REMOVE: ,
    #ACTION_APPLY: ,
    #ACTION_COMMIT: ,
    #ACTION_ROLLBACK: ,
    #ACTION_PREFS: ,
    ACTION_ABOUT: "Alt+B",
    ACTION_ABOUT_TOOLKIT: "Alt+T",
    ACTION_EXIT: "Ctrl+Q",
}

keycode_map = {
    "F5": wx.WXK_F5,
}

control_key_map = {
    "Ctrl": wx.ACCEL_CTRL,
    "Shift": wx.ACCEL_SHIFT,
    "Alt": wx.ACCEL_ALT
}


def parse_accel(s,
                sep="+", cmap=control_key_map,
                norm=wx.ACCEL_NORMAL):
    
    if isinstance(s, wx.KeyCode):
        return s
    keys = s.split(sep)
    key = keys[-1]
    keycode = keycode_map.get(key)
    if not keycode:
        keycode = ord(key)
    flags = norm
    for c in keys[:-1]:
        flags |= cmap[c]
    return (flags, keycode)


# Define our own custom events
QueryCloseEvent, EVT_QUERYCLOSE = NewEvent()
ClosingEvent, EVT_CLOSING = NewEvent()
ShownEvent, EVT_SHOWN = NewEvent()
HiddenEvent, EVT_HIDDEN = NewEvent()
CellSelectedEvent, EVT_CELL_SELECTED = NewEvent()
CellChangedEvent, EVT_CELL_CHANGED = NewEvent()
TextModChangedEvent, EVT_TEXT_MOD_CHANGED = NewEvent()
TextStateChangedEvent, EVT_TEXT_STATE_CHANGED = NewEvent()

custom_map = {
    SIGNAL_CELLSELECTED: CellSelectedEvent,
    SIGNAL_CELLCHANGED: CellChangedEvent,
    SIGNAL_TEXTMODCHANGED: TextModChangedEvent,
    SIGNAL_TEXTSTATECHANGED: TextStateChangedEvent,
    SIGNAL_QUERYCLOSE: QueryCloseEvent,
    SIGNAL_CLOSING: ClosingEvent,
    SIGNAL_SHOWN: ShownEvent,
    SIGNAL_HIDDEN: HiddenEvent
}

event_map = {
    SIGNAL_ACTIVATED: wx.EVT_MENU,
    SIGNAL_CLICKED: wx.EVT_BUTTON,
    SIGNAL_TOGGLED: wx.EVT_CHECKBOX,
    SIGNAL_SELECTED: wx.EVT_COMBOBOX,
    SIGNAL_FOCUS_IN: wx.EVT_SET_FOCUS,
    SIGNAL_FOCUS_OUT: wx.EVT_KILL_FOCUS,
    SIGNAL_LISTBOXSELECTED: wx.EVT_LISTBOX,
    SIGNAL_LISTVIEWSELECTED: wx.dataview.EVT_TREELIST_SELECTION_CHANGED,
    SIGNAL_CELLSELECTED: EVT_CELL_SELECTED,
    SIGNAL_TABLECELLSELECTED: wx.grid.EVT_GRID_SELECT_CELL,
    SIGNAL_TABLECELLEDITING: wx.grid.EVT_GRID_EDITOR_SHOWN,
    SIGNAL_TABLECELLEDITDONE: wx.grid.EVT_GRID_CELL_CHANGING,
    SIGNAL_CELLCHANGED: EVT_CELL_CHANGED,
    SIGNAL_TABLECHANGED: wx.grid.EVT_GRID_CELL_CHANGED,
    SIGNAL_TEXTCHANGED: wx.EVT_TEXT,
    SIGNAL_TEXTMODCHANGED: EVT_TEXT_MOD_CHANGED,
    SIGNAL_TEXTSTATECHANGED: EVT_TEXT_STATE_CHANGED,
    SIGNAL_EDITCHANGED: wx.EVT_TEXT,
    SIGNAL_ENTER: wx.EVT_TEXT_ENTER,
    SIGNAL_TABSELECTED: wx.EVT_NOTEBOOK_PAGE_CHANGED,
    SIGNAL_QUERYCLOSE: EVT_QUERYCLOSE,
    SIGNAL_CLOSING: EVT_CLOSING,
    SIGNAL_SIZEEVENT: wx.EVT_SIZE,
    SIGNAL_SHOWEVENT: wx.EVT_SHOW,
    SIGNAL_MINIMIZEEVENT: wx.EVT_ICONIZE,
    SIGNAL_SHOWN: EVT_SHOWN,
    SIGNAL_HIDDEN: EVT_HIDDEN,
    SIGNAL_CLOSEEVENT: wx.EVT_CLOSE,
    SIGNAL_BEFOREQUIT: wx.EVT_WINDOW_DESTROY
}

# 'Wrapper' functions for certain events to repackage parameters

def wx_plain_wrapper(self, target):
    def wrapper(event):
        target()
    return wrapper


def wx_toggled_wrapper(self, target):
    def wrapper(event):
        target(self.GetValue())
    return wrapper


def wx_selected_wrapper(self, target):
    def wrapper(event):
        target(self.GetSelection())
    return wrapper


def wx_listviewselected_wrapper(self, target):
    def wrapper(event):
        # wx doesn't use the "list of lists" model so we have to use our current item method
        target(self.current_item())
    return wrapper


def wx_listboxselected_wrapper(self, target):
    def wrapper(event):
        target(self[self.GetSelection()])
    return wrapper


def wx_cellselected_wrapper(self, target):
    def wrapper(event):
        target(event.CurrentRow, event.CurrentCol, event.PreviousRow, event.PreviousCol)
    return wrapper


def wx_cellchanged_wrapper(self, target):
    def wrapper(event):
        target(event.Row, event.Col)
    return wrapper


def wx_textmodchanged_wrapper(self, target):
    def wrapper(event):
        target(self.IsModified())
    return wrapper


def wx_editchanged_wrapper(self, target):
    def wrapper(event):
        target(self.GetValue())
    return wrapper


def wx_tabselected_wrapper(self, target):
    def wrapper(event):
        target(event.GetSelection())
    return wrapper


wrapper_map = {
    SIGNAL_ACTIVATED: wx_plain_wrapper,
    SIGNAL_CLICKED: wx_plain_wrapper,
    SIGNAL_TOGGLED: wx_toggled_wrapper,
    SIGNAL_SELECTED: wx_selected_wrapper,
    SIGNAL_FOCUS_IN: wx_plain_wrapper,
    SIGNAL_FOCUS_OUT: wx_plain_wrapper,
    SIGNAL_LISTVIEWSELECTED: wx_listviewselected_wrapper,
    SIGNAL_LISTBOXSELECTED: wx_listboxselected_wrapper,
    SIGNAL_CELLSELECTED: wx_cellselected_wrapper,
    SIGNAL_CELLCHANGED: wx_cellchanged_wrapper,
    SIGNAL_TEXTCHANGED: wx_plain_wrapper,
    SIGNAL_TEXTMODCHANGED: wx_textmodchanged_wrapper,
    SIGNAL_TEXTSTATECHANGED: wx_plain_wrapper,
    SIGNAL_EDITCHANGED: wx_editchanged_wrapper,
    SIGNAL_ENTER: wx_plain_wrapper,
    SIGNAL_TABSELECTED: wx_tabselected_wrapper,
    SIGNAL_QUERYCLOSE: wx_plain_wrapper,
    SIGNAL_CLOSING: wx_plain_wrapper,
    SIGNAL_SHOWN: wx_plain_wrapper,
    SIGNAL_HIDDEN: wx_plain_wrapper
}

# This event is for manual do_notify, since we can't instantiate wx.Event itself

NotifyEvent, _EVT_NOTIFY = NewEvent()


class PWxSignal(object):
    """Mixin class to abstract notification functionality in wxWidgets.
    """
    
    _forward = None
    
    def wx_register_event(self, event, handler):
        # Do the following instead of self.Bind(event, handler)
        # so that multiple handlers can receive a single event
        eventManager.Register(handler, event, self)
    
    def wrap_target(self, signal, target):
        target = super(PWxSignal, self).wrap_target(signal, target)
        if signal in wrapper_map:
            return wrapper_map[signal](self, target)
        return target
    
    def connect_target(self, signal, target):
        if signal in event_map:
            event = event_map[signal]
            self.wx_register_event(event, target)
    
    def do_notify(self, signal, *args):
        # FIXME: any way to pass on args in wx?
        if signal in custom_map:
            event = custom_map[signal]()
        else:
            assert signal in event_map
            # This is a kludge because wx doesn't allow you to instantiate wx.Event
            # and then set a type, and it doesn't give an easy way to instantiate
            # all the necessary specific event types
            event = NotifyEvent()
            event.SetEventType(event_map[signal]._getEvtType())
        if event is not None:
            if self._forward:
                forward_event, fields = self._forward
                event.SetId(forward_event.GetId())
                event.SetEventObject(forward_event.GetEventObject())
                for attr, value in (fields or ()):
                    setattr(event, attr, value)
                self._forward = None
            else:
                if hasattr(self, 'id'):
                    event.SetId(self.id)
                elif hasattr(self, '_id'):
                    event.SetId(self._id)
                elif hasattr(self, 'GetId'):
                    event.SetId(self.GetId())
                event.SetEventObject(self)
            self.AddPendingEvent(event)
    
    def forward_event(self, signal, event, fields, *args):
        # Ugly hack to allow data to be transferred to custom events
        # that are "translations" of built-in ones
        self._forward = (event, fields)
        self.do_notify(signal, *args)


def scaled_bitmap(image, factor):
    if factor is not None:
        image = image.Scale(image.GetWidth() * factor,
                            image.GetHeight() * factor)
    return wx.Bitmap(image)


class PWxActionMixin(object):
    
    def load_icon_from_data(self, data):
        import io
        stream = io.BytesIO(data)
        return wx.Image(stream)
    
    def load_icon_from_file(self, filename):
        return wx.Image(filename)
    
    def get_accel_str(self, key):
        return accel_map.get(key)


font_weights = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_BOLD]
font_styles = [wx.FONTSTYLE_NORMAL, wx.FONTSTYLE_ITALIC]


class PWxWidget(PWxSignal):
    """Mixin class to provide basic wx widget methods.
    """
    
    fn_enable_get = 'IsEnabled'
    fn_enable_set = 'Enable'
    
    _depth_test_str = string.ascii_letters + string.digits
    _depth_scale_factor = 1.3
    
    def update_widget(self):
        self.Refresh()
    
    def preferred_width(self):
        return self.GetSize().GetWidth()
    
    def preferred_height(self):
        return self.GetSize().GetHeight()
    
    get_width = preferred_width
    
    get_height = preferred_height
    
    def set_size(self, width, height):
        self.SetSize(width, height)
    
    def get_left(self):
        return self.GetPosition().x
    
    def get_top(self):
        return self.GetPosition().y
    
    def set_position(self, left, top):
        self.SetPosition(wx.Point(left, top))
    
    def set_min_size(self, width, height):
        self.SetMinSize((width, height))
    
    def _mapped_color(self, color):
        if isinstance(color, wx.Colour):
            return color
        return color_map[color]
    
    def set_foreground_color(self, color):
        self.SetForegroundColour(self._mapped_color(color))
    
    def set_background_color(self, color):
        self.SetBackgroundColour(self._mapped_color(color))
    
    def get_font_name(self):
        return self.GetFont().GetFaceName()
    
    def get_font_size(self):
        return self.GetFont().GetPointSize()
    
    def get_font_bold(self):
        return (self.GetFont().GetWeight() == font_weights[1])
    
    def get_font_italic(self):
        return (self.GetFont().GetStyle() == font_styles[1])
    
    def wx_font_object(self, font_name, font_size, bold, italic):
        font_family = wx.FONTFAMILY_DEFAULT
        for family, names in font_families.items():
            if font_name in names:
                font_family = family
                break
        font_style = font_styles[int(italic)]
        font_weight = font_weights[int(bold)]
        font = wx.Font(font_size, font_family, font_style, font_weight)
        font.SetFaceName(font_name)
        return font
    
    def set_font_object(self, font_name, font_size, bold, italic):
        font = self.wx_font_object(font_name, font_size, bold, italic)
        if hasattr(self, '_depth_w'):
            # Hack to make list view column auto-sizing work correctly
            # on font change
            old_extent = self.GetTextExtent(self._depth_test_str)[0]
            new_extent = self.GetFullTextExtent(self._depth_test_str, font)[0]
            self._depth_w = int(
                self._depth_w * self._depth_scale_factor * new_extent /
                old_extent)
        self.SetFont(font)
        if hasattr(self, 'SetDefaultCellFont'):
            self.SetDefaultCellFont(font)  # takes care of the table widget
        if hasattr(self, 'AutoSizeCols'):
            self.AutoSizeCols()  # this takes care of the list view widget
    
    def set_focus(self):
        self.SetFocus()


# Ugly hack to fix metaclass conflict for sequence widgets

WxMeta = type(wx.Object)


class PWxSequenceMeta(WxMeta, ABCMeta):
    
    def __init__(cls, name, bases, attrs):
        WxMeta.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)


class PWxSequenceWidget(PWxWidget, metaclass=PWxSequenceMeta):
    
    # Ugly hack because the wx event manager needs widget instances
    # to be hashable; note that this is breaking the Python guideline
    # that mutable objects should not be hashable, but we have no
    # choice, and the hash value itself won't change if the widget
    # is mutated
    
    def __hash__(self):
        return hash(id(self))


default_map = {
    wx.ID_CANCEL: wx.CANCEL_DEFAULT,
    wx.ID_NO: wx.NO_DEFAULT,
    wx.ID_OK: wx.OK_DEFAULT,
    wx.ID_YES: wx.YES_DEFAULT,
}


class PWxMessageBox(PMessageBoxBase):
    """Customized wxWidgets message box.
    """
    
    question_map = {
        ANSWER_YES: wx.ID_YES,
        ANSWER_NO: wx.ID_NO,
        ANSWER_CANCEL: wx.ID_CANCEL,
        ANSWER_OK: wx.ID_OK
    }
    
    def message_box(self, type, caption, text, default,
                    button1, button2=None, button3=None):
        
        style = icon_map[type]
        buttons = [button1, button2, button3]
        if (wx.ID_YES in buttons) or (wx.ID_NO in buttons):
            style = style | wx.YES_NO
        if wx.ID_OK in buttons:
            style = style | wx.OK
        if wx.ID_CANCEL in buttons:
            style = style | wx.CANCEL
        default_style = default_map.get(default)
        if default_style:
            style |= default_style
        dlg = wx.MessageDialog(self.parent, text, caption, style)
        # TODO: Hack to fix strange button ordering for Yes/No/Cancel
        #b_cancel = dlg.FindWindowById(wx.ID_CANCEL)
        #b_no = dlg.FindWindowById(wx.ID_NO)
        #print(b_cancel, b_no)
        #if (b_cancel is not None) and (b_no is not None):
        #    b_yes = dlg.FindWindowById(wx.ID_YES)
        #    if b_yes:
        #        b_no.MoveAfterInTabOrder(b_yes)
        #    b_cancel.MoveAfterInTabOrder(b_no)
        result = dlg.ShowModal()
        dlg.Destroy()
        return result


class PWxFileDialog(PFileDialogBase):
    
    def choose_directory(self, curdir):
        dlg = wx.DirDialog(self.parent, defaultPath=curdir)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            retval = dlg.GetPath()
        else:
            retval = ""
        dlg.Destroy()
        return retval
    
    def wx_filedialog(self, msg, path, filter, style):
        if filter == "":
            filter = "*"
        dlg = wx.FileDialog(self.parent, msg, path, "", filter, style)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            retval = dlg.GetPath()
        else:
            retval = ""
        dlg.Destroy()
        return retval
    
    def _translate_filter_item(self, caption, ext_str):
        return "{0} ({1})|{1}".format(caption, ext_str)
    
    ext_sep = ";"
    filter_sep = "|"
    
    def _open_filename(self, path, filter, selected_filter):
        # TODO: how to use selected_filter?
        return self.wx_filedialog("Select file to open", path, filter,
                                  wx.FD_OPEN)
    
    def _save_filename(self, path, filter, selected_filter):
        # TODO: how to use selected_filter?
        return self.wx_filedialog("Select file to save", path, filter,
                                  wx.FD_SAVE)


def wx_icon_from_file(filename):
    # Kludgy but gets the job done on all platforms
    return wx.Icon(filename)


class PWxAboutDialog(PAboutDialogBase):
    
    attr_map = {
        'name': "SetName",
        'version': "SetVersion",
        'description': "SetDescription",
        'copyright': "SetCopyright",
        'license': "SetLicense",
        'developer': "AddDeveloper",
        'website': "SetWebSite",
    }
    
    info = None
    
    def display_func(self, parent, caption, body):
        # In case Wx-required about box fields are not present
        parent.app.message_box.info(caption, body)
    
    def display(self):
        data = self.parent.app.about_data
        if any(attr not in data for attr in self.attr_map):
            PAboutDialogBase.display(self)
        else:
            if self.info is None:
                self.info = info = wx.adv.AboutDialogInfo()
                for attr, fname in self.attr_map.items():
                    method = getattr(info, fname)
                    method(data[attr])
                iconfile = self.parent.app.main_iconfile
                if iconfile:
                    info.SetIcon(wx_icon_from_file(iconfile))
            else:
                info = self.info
            wx.adv.AboutBox(info, self.parent)


class PTopWindow(PWxWidget, wx.Frame, PTopWindowBase):
    """Customized wxWidgets top window class.
    """
    
    def __init__(self, manager):
        wx.Frame.__init__(self, None)
        PTopWindowBase.__init__(self, manager)
        
        # 'automagic' connections
        self.setup_notify(SIGNAL_CLOSEEVENT, self.OnCloseWindow)
        self.setup_notify(SIGNAL_SHOWEVENT, self.OnShowEvent)
        self.setup_notify(SIGNAL_MINIMIZEEVENT, self.OnIconizeEvent)
    
    def show_init(self):
        PTopWindowBase.show_init(self)
        self.Show(True)
    
    def set_caption(self, caption):
        self.SetTitle(caption)
    
    def get_desktop_rect(self, primary=True):
        r = wx.Display().GetClientArea()
        return (r.GetX(), r.GetY(), r.GetWidth(), r.GetHeight())
    
    def set_client_area_size(self, width, height):
        self.SetClientSize(width, height)
    
    def size_maximize(self):
        self.Maximize(True)
    
    def get_frame_size(self):
        pass  # centering is done differently in wx, see next method
    
    def center(self):
        self.CenterOnScreen()
    
    def do_exit(self):
        self.Close()
    
    def set_iconfile(self, iconfile):
        self.SetIcon(wx_icon_from_file(iconfile))
    
    def get_current_geometry(self):
        left, top = self.GetPosition()
        width, height = self.GetSizeTuple()
        return left, top, width, height
    
    def SignalShown(self, event, shown):
        # 'automagic' method for SIGNAL_SHOWEVENT
        if shown:
            self.forward_event(SIGNAL_SHOWN, event, None)
        else:
            self.forward_event(SIGNAL_HIDDEN, event, None)
    
    def OnShowEvent(self, event):
        # 'automagic' method for SIGNAL_SHOWEVENT
        self.SignalShown(event, event.IsShown())
    
    def OnIconizeEvent(self, event):
        # 'automagic' method for SIGNAL_MINIMIZEEVENT
        self.SignalShown(event, not event.IsIconized())
    
    def OnCloseWindow(self, event):
        # 'automagic' method for SIGNAL_CLOSEEVENT
        self.forward_event(SIGNAL_QUERYCLOSE, event, None)  # a handler here can adjust state to be checked below
        self.ProcessPendingEvents()  # force the handler to run before we check
        
        if event.CanVeto() and not self.can_close():
            event.Veto()
        else:
            # Send the closing signal
            self.forward_event(SIGNAL_CLOSING, event, None)
            # Allow signal handlers to process before destroying
            self.DestroyLater()


class PApplication(PWxSignal, wx.App, PApplicationBase):
    """Customized wxWidgets application class.
    """
    
    about_dialog_class = PWxAboutDialog
    message_box_class = PWxMessageBox
    file_dialog_class = PWxFileDialog
    
    def __init__(self, arglist=[]):
        wx.App.__init__(self, arglist)
        PApplicationBase.__init__(self, arglist)
    
    def about_toolkit(self):
        # No built-in "About Wx" dialog
        self.message_box.info("About Wx", "WxPython {}".format(wx.version()))
    
    def OnInit(self):
        # wxWidgets wants you to initialize subwidgets here
        self.do_create()
        
        # required return value
        return True
    
    def OnExit(self):
        # 'automagic' method for SIGNAL_BEFOREQUIT
        self.before_quit()
        
        # required return value
        return super(PApplication, self).OnExit()
    
    def event_loop(self):
        self.MainLoop()
    
    def process_events(self):
        self.ProcessPendingEvents()
