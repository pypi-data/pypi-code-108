#!/usr/bin/env python3
"""
Module APP -- UI Application Classes
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import sys
import os.path

from plib.stdlib.builtins import inverted
from plib.stdlib.classtools import Singleton
from plib.stdlib.decotools import cached_property

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.common import *
from plib.ui.widgets import setup_signal_handlers, get_toolkit_class, widget_from_spec


class PSignalBase(object):
    """Base class for objects that can send signals to notify other objects.
    """
    
    signals = None
    
    def wrap_target(self, signal, target):
        return target
    
    def connect_target(self, signal, target):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def setup_notify(self, signal, target):
        target = self.wrap_target(signal, target)
        self.connect_target(signal, target)
    
    def do_notify(self, signal, *args):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PActionMixin(object):
    """Mixin class for objects that behave like actions.
    """
    
    def get_icon_data(self, key):
        return action_icondata(key)
    
    def load_icon_from_data(self, data):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def load_icon_from_file(self, filename):
        # Most toolkit implementations will probably override this
        # since they provide direct loading of images from files,
        # but this default implementation is here if needed
        with open(filename, 'rb') as f:
            return self.load_icon_from_data(f.read())
    
    def get_icon(self, key):
        return self.load_icon_from_data(self.get_icon_data(key))
    
    def get_menu_str(self, key):
        return action_caption(key)
    
    def get_toolbar_str(self, key):
        return self.get_menu_str(key).replace('&', '').strip('.')
    
    def get_statusbar_str(self, key):
        return action_description(key)
    
    def get_accel_str(self, key):
        return None


class PWidgetBase(PSignalBase):
    """Base class for widgets.
    """
    
    fn_enable_get = None
    fn_enable_set = None
    
    signals = (
        SIGNAL_FOCUS_IN,
        SIGNAL_FOCUS_OUT,
    )
    
    def __init__(self, manager, parent, geometry=None, font=None):
        self.manager = manager
        self.parent = parent
        if geometry is not None:
            self.set_geometry(*geometry)
        if font is not None:
            if isinstance(font, str):
                font = (font,)  # font name only is allowed
            self.set_font(*font)
    
    def update_widget(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def preferred_width(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def preferred_height(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_width(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_height(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_size(self):
        return self.get_width(), self.get_height()
    
    def set_size(self, width, height):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_width(self, width):
        self.set_size(width, self.get_height())
    
    def set_height(self, height):
        self.set_size(self.get_width(), height)
    
    def set_client_area_size(self, width, height):
        # Factored out so toolkits can override if needed
        self.set_size(width, height)
    
    def get_left(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_top(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_position(self, left, top):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_min_size(self, width, height):
        """Derived classes must implement.
        """
        raise NotImplementedError
    
    def set_min_width(self, width):
        self.set_min_size(width, self.get_height())
    
    def set_min_height(self, height):
        self.set_min_size(self.get_width(), height)
    
    def set_geometry(self, left, top, width, height):
        """Set widget geometry.
        
        Also sets minimum size; this method is mainly intended to
        be called from the constructor based on parameters given
        in a widget spec.
        """
        if (width is not None) or (height is not None):
            self.set_size(
                width if width is not None else self.get_width(),
                height if height is not None else self.get_height()
            )
            if (width is not None) and (height is not None):
                self.set_min_size(width, height)
            else:
                if width is not None:
                    self.set_min_width(width)
                if height is not None:
                    self.set_min_height(height)
        if (left is not None) or (top is not None):
            self.set_position(
                left if left is not None else self.get_left(),
                top if top is not None else self.get_top()
            )
    
    def set_colors(self, fg=None, bg=None):
        if fg is not None:
            self.set_foreground_color(fg)
        if bg is not None:
            self.set_background_color(bg)
    
    def set_foreground_color(self, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_background_color(self, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_name(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_size(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_bold(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_italic(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_font_object(self, font_name, font_size, bold, italic):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_font(self, font_name=None,
                 font_size=None, bold=None, italic=None):
        
        self.set_font_object(*font_args(self,
                                        font_name,
                                        font_size,
                                        bold,
                                        italic))
    
    def get_enabled(self):
        return getattr(self, self.fn_enable_get)()
    
    def set_enabled(self, value):
        getattr(self, self.fn_enable_set)(value)
    
    enabled = property(get_enabled, set_enabled)
    
    def set_focus(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PDialogBase(Singleton):
    
    def _init(self, parent):
        self.parent = parent


class PMessageBoxMeta(type):
    """Metaclass to automatically set up message box classes.
    """
    
    def __init__(cls, name, bases, dict):
        # Add None to question map and set up answer map
        type.__init__(cls, name, bases, dict)
        question_map = getattr(cls, 'question_map')
        question_map.update({ANSWER_NONE: None})
        setattr(cls, 'question_map', question_map)
        answer_map = inverted(question_map)
        setattr(cls, 'answer_map', answer_map)


class PMessageBoxBase(PDialogBase, metaclass=PMessageBoxMeta):
    
    question_map = {}
    
    def message_box(self, type, caption, text, default,
                    button1, button2=None, button3=None):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def translate(self, type, caption, text,
                  button1, button2=ANSWER_NONE, button3=ANSWER_NONE):
        
        default = (
            button3 if button3 != ANSWER_NONE else
            button2 if button2 != ANSWER_NONE else
            button1
        )
        return self.answer_map[self.message_box(
            type, caption, text, self.question_map.get(default),
            self.question_map.get(button1),
            self.question_map.get(button2),
            self.question_map.get(button3))]
    
    def info(self, caption, text):
        """Information message box.
        """
        return self.translate(MBOX_INFO, caption, text,
                              ANSWER_OK)
    
    def warn(self, caption, text):
        """Warning message box.
        """
        return self.translate(MBOX_WARN, caption, text,
                              ANSWER_OK)
    
    def error(self, caption, text):
        """Error message box.
        """
        return self.translate(MBOX_ERROR, caption, text,
                              ANSWER_OK)
    
    def query2(self, caption, text):
        """OK/Cancel message box.
        """
        return self.translate(MBOX_QUERY, caption, text,
                              ANSWER_OK, ANSWER_CANCEL)
    
    def query3(self, caption, text):
        """Yes/No/Cancel message box.
        """
        return self.translate(MBOX_QUERY, caption, text,
                              ANSWER_YES, ANSWER_NO, ANSWER_CANCEL)


class PFileDialogBase(PDialogBase):
    
    def choose_directory(self, curdir):
        """Display select folder dialog and return chosen folder.
        """
        raise NotImplementedError
    
    def _translate_filter_item(self, caption, ext_str):
        """Translate filter item into toolkit format.
        """
        raise NotImplementedError
    
    ext_sep = None
    
    def _ext_str_from_list(self, ext_list):
        return self.ext_sep.join("*.{}".format(ext) for ext in ext_list)
    
    filter_sep = None
    
    def _translate_filter(self, filter):
        return self.filter_sep.join(
            self._translate_filter_item(caption, self._ext_str_from_list(ext_list))
            for caption, ext_list in filter
        )
    
    def _open_filename(self, path, filter, selected_filter):
        """Display select file dialog and return chosen filename for opening.
        """
        raise NotImplementedError
    
    def _save_filename(self, path, filter, selected_filter):
        """Display select file dialog and return chosen filename for saving.
        """
        raise NotImplementedError
    
    def open_filename(self, path, filter, selected_filter):
        return self._open_filename(path, self._translate_filter(filter), self._translate_filter_item(*selected_filter))
    
    def save_filename(self, path, filter, selected_filter):
        return self._save_filename(path, self._translate_filter(filter), self._translate_filter_item(*selected_filter))


class PAboutDialogBase(PDialogBase):
    """Base class for about dialogs.
    """
    
    plibstr = "Using PLIB.UI version {}".format(__version__)
    
    display_func = None
    
    def display(self):
        data = self.parent.app.about_data
        fmt = self.parent.app.about_format
        caption = "About {}".format(data.get('name', "Application"))
        aboutstr = fmt.format(**data)
        body = "{}\n\n{}".format(aboutstr, self.plibstr)
        self.display_func(self.parent, caption, body)


class PTopWindowBase(PWidgetBase):
    """Base class for 'top window' widgets.
    
    A top window is a 'plain' main application window; it has no
    frills like menus, toolbars, status bars, etc. built in.
    """
    
    signals = (
        SIGNAL_SHOWN,
        SIGNAL_QUERYCLOSE,
        SIGNAL_CLOSING,
        SIGNAL_HIDDEN,
    )
    
    def __init__(self, manager):
        PWidgetBase.__init__(self, manager, None)  # no parent
        self.shown = False
        self.client_widget = None
        
        setup_signal_handlers(self.app, self, 'app')
    
    @property
    def app(self):
        return self.manager  # these are always the same for a top window
    
    def before_client(self):
        """For subclasses, to allow initialization before client widget is created
        """
        pass
    
    def set_client_widget(self, client_widget):
        self.client_widget = client_widget
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_desktop_rect(self, primary=True):
        """Return 6-tuple (index, num_desktops, left, top, width, height) for desktop.
        """
        raise NotImplementedError
    
    def get_client_size(self):
        """Return tuple of (width, height) needed to wrap client.
        """
        c = self.client_widget
        return (c.preferred_width(), c.preferred_height())
    
    def size_to_client(self):
        self.set_client_area_size(*self.get_client_size())
    
    def size_maximize(self):
        """Size the window to be maximized.
        """
        raise NotImplementedError
    
    def size_to_screen(self, width_offset=0, height_offset=0):
        l, t, w, h = self.get_desktop_rect()
        self.set_size(w - width_offset, h - height_offset)
        self.set_position(l, t)
    
    def get_frame_size(self):
        """Return tuple of (width, height) for the window's frame size.
        """
        raise NotImplementedError
    
    def center(self):
        l, t, w, h = self.get_desktop_rect()
        x, y = self.get_frame_size()
        self.set_position(l + (w - x) / 2, t + (h - y) / 2)
    
    def init_placement(self, size, pos):
        if size == SIZE_CLIENTWRAP:
            self.size_to_client()
        elif size == SIZE_MAXIMIZED:
            self.size_maximize()
        elif size == SIZE_DESKTOP:
            self.size_to_screen()
        elif size == SIZE_OFFSET:
            self.size_to_screen(self.app.width_offset, self.app.height_offset)
        if (pos == MOVE_CENTER) and (size != SIZE_MAXIMIZED):
            self.center()
    
    def show_init(self):
        """Should always call from derived classes to ensure proper setup.
        """
        if not self.shown:
            # Do placement just before showing for first time
            self.init_placement(self.app.main_size, self.app.main_placement)
            self.shown = True
    
    def can_close(self):
        # To be called after SIGNAL_QUERYCLOSE is handled, so handlers
        # for that signal can adjust any state to be checked here
        return self.app.accept_close()
    
    def do_exit(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def exit(self):
        """Ensure client references are removed before exiting.
        """
        self.client_widget = None
        self.do_exit()
    
    def set_iconfile(self, iconfile):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_current_geometry(self):
        """Return the window's current geometry (including frame).
        """
        raise NotImplementedError


class PApplicationBase(PSignalBase):
    """Base class for GUI application.
    """
    
    signals = (
        # SIGNAL_BEFOREQUIT
    )
    
    about_dialog_class = None
    message_box_class = None
    file_dialog_class = None
    
    about_toolkit_func = None
    
    about_data = {}
    about_format = None
    
    main_title = "Application"
    main_iconfile = None
    main_size = SIZE_NONE
    main_placement = MOVE_NONE
    
    width_offset = height_offset = 160
    
    main_widget = None
    
    menu_actions = None
    toolbar_actions = None
    
    include_statusbar = True
    
    large_icons = False
    show_labels = False
    
    status_labels = None
    
    def __init__(self, arglist=[]):
        self.arglist = arglist
    
    def do_create(self):
        # Allow custom processing before any widgets are created
        self.before_create()
        
        self.main_window = self.create_main_widget()
        self.main_window.before_client()
        self.client_widget = self.create_client_widget()
        if self.main_iconfile:
            self.main_window.set_iconfile(self.main_iconfile)
        
        # This is factored out to allow custom signal setup by toolkits if needed
        self.setup_signals()
        
        # Allow custom processing after all widgets are created
        self.after_create()
    
    def setup_signals(self):
        # This does nothing unless the user has added custom signals to the app
        setup_signal_handlers(self, self, 'app')
    
    @property
    def use_mainwindow(self):
        return bool(self.menu_actions or self.toolbar_actions)
    
    @property
    def include_menu(self):
        return bool(self.menu_actions)
    
    @property
    def include_toolbar(self):
        return bool(self.toolbar_actions)
    
    def create_main_widget(self):
        """Create the main widget and return it.
        """
        
        args = (
            ('mainwin', 'PMainWindow') if self.use_mainwindow else
            ('app', 'PTopWindow')
        )
        main_klass = get_toolkit_class(*args)
        main_window = main_klass(self)
        main_window.set_caption(self.main_title)
        return main_window
    
    def create_client_widget(self):
        spec = self.main_widget
        if spec:
            main_window = self.main_window
            client_widget = widget_from_spec(self, main_window, *spec)
            main_window.set_client_widget(client_widget)
            return client_widget
        return None
    
    @cached_property
    def message_box(self):
        return self.message_box_class(self.main_window)
    
    @cached_property
    def file_dialog(self):
        return self.file_dialog_class(self.main_window)
    
    @cached_property
    def about_dialog(self):
        return self.about_dialog_class(self.main_window)
    
    def about(self):
        self.about_dialog.display()
    
    def about_toolkit(self):
        self.about_toolkit_func()
    
    def event_loop(self):
        """Placeholder for derived classes for main event loop.
        """
        raise NotImplementedError
    
    def run(self):
        """Show the main widget and run the main event loop.
        """
        
        self.main_window.show_init()
        self.event_loop()
        self.main_window = None
    
    def process_events(self):
        """Placeholder for derived classes to pump events outside main loop.
        """
        raise NotImplementedError
    
    def exit_app(self):
        self.main_window.exit()
    
    def before_create(self):
        """Placeholder for derived classes if needed.
        
        This method is called before any widgets are created or specs are evaluated.
        """
        pass
    
    def after_create(self):
        """Placeholder for derived classes if needed.
        
        This method can assume that all widgets are created and available.
        """
        pass
    
    def accept_close(self):
        """Return False if app should not close based on current state.
        """
        return True
    
    def before_quit(self):
        """Placeholder for derived classes if needed.
        
        Note that this method cannot assume that *any* objects other than
        the application itself are still available; things that need to be
        done with widgets still available should be done in the accept_close
        method above.
        """
        pass
