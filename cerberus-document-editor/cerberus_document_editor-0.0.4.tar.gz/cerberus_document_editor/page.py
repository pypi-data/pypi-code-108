import urwid
import json
import time
from abc import ABCMeta, abstractmethod
from cerberus_kind.utils import parse_error

from .validator import Validator
from .widget import Widget, FlatButton
from .debug import log

# Page
# -- JSON Data
# -- JSON Schema
# -- Show Editor Widgets
class Page(metaclass=ABCMeta):
    def __init__(self, name, hwnd=None, modal=False):
        self.__name = name
        self.__hwnd = hwnd
        self.__modified = False
        self.__modal = modal
        self.__keymap = {}
        self.__data = {}
        self.__warning_info = {'high_priority': False, 'latest_time': 0.0}

    @property
    def name(self):
        return self.__name

    @property
    def hwnd(self):
        return self.__hwnd

    @hwnd.setter
    def hwnd(self, hwnd):
        self.__hwnd = hwnd
        if self.__modified:
            self.__hwnd.modified()

    @property
    def is_modified(self):
        return self.__modified
    
    def modified(self):
        self.__modified = True
        if self.__hwnd:
            self.__hwnd.modified()
    
    @property
    def keymap(self):
        return dict([(k, type('KeyMap', (), v)) for k, v in self.__keymap.items()])

    @property
    def json(self):
        return json.loads(json.dumps(self.__data))
    
    @json.setter
    def json(self, data):
        self.__data.update(data)

    @property
    def is_modal(self):
        return self.__modal

    def __repr__(self):
        return json.dumps(self.__data)

    def register_keymap(self, k, desc, callback, enabled=True):
        self.__keymap[k] = {
            'description': desc,
            'callback': callback,
            'enabled': enabled
        }
    
    def unregister_keymap(self, k):
        if k in self.__keymap:
            del self.__keymap[k]

    def set_keymap(self, k, enable=True):
        if k in self.__keymap:
            self.__keymap[k]['enabled'] = enable

    def next(self, page):
        self.__hwnd.push(page)

    def close(self):
        self.__hwnd.pop()

    def render(self):
        if hasattr(self, '_page_widget'):
            focus = self._page_widget.get_focus()
            self.__hwnd.redraw()
            self._page_widget.set_focus(min(len(self._page_widget.body)-1, focus[-1]))
        else:
            self.__hwnd.redraw()

    def warning(self, message=None, high_priority=False):
        current_tick = time.time()
        if self.__warning_info['high_priority']:
            if self.__warning_info['latest_time'] + 0.1 < current_tick:
                self.__warning_info['high_priority'] = False
        if high_priority or not self.__warning_info['high_priority']:
            self.hwnd.set_indicator(message)
            self.__warning_info['latest_time'] = current_tick
            self.__warning_info['high_priority'] = high_priority

    def on_change_focus(self):
        self.warning()

    @abstractmethod
    def on_page_result(self, page):
        ...

    @abstractmethod
    def on_update(self):
        ...

    @abstractmethod
    def on_draw(self):
        ...

    @abstractmethod
    def on_close(self):
        ...

class ListPage(Page):
    def __init__(self, name, sub_page=False):
        super().__init__(name)
        self.listbox_contents = []
        self.widget_map = {}
        if sub_page:
            self.register_keymap('ctrl left', 'Back', lambda page: page.close())
    
    def add_column_number(self, label, desc=None, value=0.):
        return self.add_item(Widget.Edit.number(label, value), desc)

    def add_column_integer(self, label, desc=None, value=0):
        return self.add_item(Widget.Edit.integer(label, value), desc)

    def add_column_str(self, label, desc=None, value=None, multiline=False):
        return self.add_item(Widget.Edit.text(label, value, multiline), desc)

    def add_column_object(self, label, desc=None, text='More...', callback=None):
        return self.add_item(Widget.button(label, text, callback or (lambda x: None)), desc)

    def add_column_dropdown(self, label, desc=None, items=[], default=None):
        return self.add_item(Widget.dropdown(label, items, items.index(default) if default is not None else 0), desc)

    def add_column_group(self, label, desc=None):
        return self.add_item(Widget.group(label), desc)
        
    def add_column(self, label, desc=None, dtype='string', **kwargs):
        #, value=None, callback=None, multiline=False):
        if dtype in ['boolean', 'binary', 'date', 'datetime', 'list', 'set']:
            # bool, (bytes, bytearray), datetime.date, datetime.datetime, Collections.abc.Squence, set
            ...
        else:
            widget = None
            if dtype == 'number':
                return self.add_column_number(label, desc, kwargs.get('value', 0.0))
            elif dtype == 'integer':   # int
                return self.add_column_integer(label, desc, kwargs.get('value', 0))
            elif dtype == 'string':    # str
                return self.add_column_str(label, desc, kwargs.get('value', 0), kwargs.get('multiline', False))
            elif dtype == 'dict':      # dict
                return self.add_column_object(label, desc, kwargs.get('text', 'More...'), kwargs.get('callback', None))
            elif dtype == 'dropdown':   # options
                return self.add_column_dropdown(label, desc, kwargs.get('items', []), kwargs.get('default', 0), kwargs.get('callback', None))

    def add_item(self, widget, desc=None):
        ignore_react_list = [
            urwid.Button, FlatButton
        ]
        #self.listbox_contents.append(Widget.divider())
        if desc: self.listbox_contents.append(Widget.text(f'# {desc}', colorscheme='description'))
        self.listbox_contents.append(widget)
        inner_widget = Widget.unwrap_widget(widget)
            
        if not type(inner_widget) in ignore_react_list:
            signal = urwid.connect_signal(inner_widget, 'change', self.on_change)
        return inner_widget
   
    def clear_items(self):
        self.listbox_contents = []

    def on_draw(self):
        if len(self.listbox_contents):
            walker = urwid.SimpleListWalker(self.listbox_contents)
            urwid.connect_signal(walker, 'modified', self.on_change_focus)
            self._page_widget = urwid.ListBox(walker)
            return self._page_widget
        else:
            return urwid.Filler(
                urwid.Padding(
                    urwid.Text("Empty items.", align=urwid.CENTER),
                    align=urwid.CENTER
                ), valign=urwid.MIDDLE
            )

    def get_focus_widget(self):
        if hasattr(self, '_page_widget'):
            _ = self._page_widget.get_focus_widgets()
            return _[-1]

    def next_focus(self):
         if hasattr(self, '_page_widget'):
            max_index = len(self._page_widget.body)-1
            pos = self._page_widget.get_focus()[-1]
            self._page_widget.set_focus(max(0, min(max_index, pos+1)))

    def prev_focus(self):
         if hasattr(self, '_page_widget'):
            max_index = len(self._page_widget.body)-1
            pos = self._page_widget.get_focus()[-1]
            self._page_widget.set_focus(max(0, min(max_index, pos-1)))

class PopupPage(Page):
    def __init__(self, name, ptype='prompt', return_key='popup', **kwargs):
        super().__init__(name, modal=True)
        self.listbox_contents = []
        self.ptype = ptype
        self.return_key = return_key
        self.block_close=False
        self.bg_frame = kwargs.get('background', urwid.SolidFill(u'\N{MEDIUM SHADE}'))

        self.add_item(Widget.text(name.upper(), colorscheme='label'))
        self.add_item(Widget.divider())
        if ptype == 'prompt':
            schema = kwargs.get('schema', None)
            self.validator = Validator(schema) if schema else None
            self.add_item(Widget.Edit.text())
            status_bar = Widget.text(colorscheme='stat')
            self.add_item(status_bar)
            self.status_bar = Widget.unwrap_widget(status_bar)
        elif ptype == 'select':
            self.items = kwargs.get('items', [])
            for item in self.items:
                if isinstance(item, dict):
                    key = item
                    desc = self.item.get(key)
                else:
                    key = item
                    desc = None
                if desc:
                    self.add_item(Widget.button(None, key, lambda x: self.on_select(x.label), colorschemes=('label', 'focus'), comment=desc))
                else:
                    self.add_item(Widget.button(None, key, lambda x: self.on_select(x.label), colorschemes=('label', 'focus')))
        else:
            raise RuntimeError(f'Not Supported type. [{ptype}]')

        self.register_keymap('esc', 'Cancel', lambda page: page.on_cancel())
        self.register_keymap('enter', 'Add', lambda page: page.on_apply())

    def add_item(self, widget, signal=None, callback=None):
        ignore_react_list = [
            urwid.Text, FlatButton, urwid.Divider
        ]
        self.listbox_contents.append(widget)
        inner_widget = Widget.unwrap_widget(widget)
        if not type(inner_widget) in ignore_react_list:
            signal = urwid.connect_signal(inner_widget, 'change', self.on_change)
        return inner_widget
   
    def clear_items(self):
        self.listbox_contents = []

    def on_draw(self):
        return urwid.Overlay(
            urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(self.listbox_contents))),
            self.bg_frame,
            align='center', width=('relative', 50), min_width=20,
            valign='middle', height=len(self.listbox_contents)+2, min_height=4
        )

    def on_page_result(self, page):
        self.render()

    def on_select(self, value):
        self.json = {self.return_key: value}
        self.close()

    def on_apply(self):
        if not self.block_close:
            self.close()
        else:
            self.status_bar.set_text("Item is not valid.")

    def on_cancel(self):
        self.json = {}
        self.close()

    def on_change(self, widget, new_value):
        if self.validator and not self.validator.validate({'value': new_value}):
            error = parse_error(self.validator.errors, with_path=True)
            self.status_bar.set_text(error)
            self.block_close=True
        else:
            self.json = {self.return_key: new_value}
            self.block_close=False
            self.status_bar.set_text("")

    def on_update(self):
        ...

    def on_close(self):
        ...
