import urwid
from urwid.numedit import FloatEdit

from .debug import log

## Ref from https://github.com/rbistolfi/urwid-combobox
class ComboBox(urwid.PopUpLauncher):
    signals = ["change"]

    class MenuItem(urwid.Button):
        signals = urwid.Button.signals
        signals += ["click", "quit"]
        button_left = urwid.Text("")
        button_right = urwid.Text("")
        def keypress(self, size, key):
            command = urwid.command_map[key]
            if command == "activate":
                self._emit("click", True)
            elif command == "menu":
                self._emit("quit")
            super().keypress(size, key)
            return key

    class ComboBoxMenu(urwid.WidgetWrap):
        signals = ["close"]

        def __init__(self, items):
            self.items = []
            self._nav_search_key = None
            self._nav_iter = iter([])
            for i in items:
                self.append(i)
            self.walker = urwid.Pile([urwid.AttrWrap(_, "combo", 'focus') for _ in self.items])
            super().__init__(urwid.AttrWrap(urwid.Filler(self.walker), "combo", 'focus'))

        def keypress(self, size, key):
            if self._nav_search_key != key.lower():
                self._nav_search_key = key.lower()
                nav_candidates = []
                for entry in self.walker.contents:
                    if entry[0].get_label().lower().startswith(key.lower()):
                        nav_candidates.append(self.walker.contents.index(entry))
                self._nav_iter = iter(sorted(nav_candidates))
            try:
                nf = next(self._nav_iter)
                self.walker.set_focus(self.walker.contents[nf][0])
            except StopIteration:
                return super().keypress(size, key)
            return super().keypress(size, key)

        def append(self, item):
            r = ComboBox.MenuItem(str(item))
            self.items.append(r)

        def get_item(self, index):
            return self.items[index].get_label()

        def get_selection(self):
            for index, item in enumerate(self.items):
                if item.state is True:
                    return index

    class DropDownButton(urwid.Button):
        button_left = urwid.Text("▿")
        button_right = urwid.Text("")

    def __init__(self, items, default=0, on_state_change=None):
        self.menu = ComboBox.ComboBoxMenu(items)
        self.on_state_change = on_state_change
        #self.menu.items[default].set_state(True)
        #logger.print(type(self.menu.items[default]))
        self.menu.walker.focus_position = default
        self._button = ComboBox.DropDownButton(self.menu.get_item(default))
        super().__init__(self._button)
        urwid.connect_signal(self.original_widget, 'click', lambda b: self.open_pop_up())
        for i in self.menu.items:
            urwid.connect_signal(i, 'click', self.item_changed)
            urwid.connect_signal(i, 'quit', self.quit_menu)

    def create_pop_up(self):
        return self.menu

    def render(self, size, focus=False):
        self._size = size
        return super().render(size, focus)

    def get_pop_up_parameters(self):
        return {'left':0, 'top':0, 'overlay_width': self._size[0],
                'overlay_height': len(self.menu.items)}

    def item_changed(self, item, state=True):
        selection = item.get_label()
        state = selection != self._button.get_label()
        if state:
            self._button.set_label(selection)
            self._emit("change", selection)
        if self.on_state_change:
            self.on_state_change(self, item, state)
        self.close_pop_up()

    def quit_menu(self, widget):
        self.close_pop_up()

    def get_selection(self):
        return self.menu.get_selection()

class FlatButton(urwid.Button):
    def __init__(self, caption, callback):
        super(FlatButton, self).__init__(caption)
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.SelectableIcon(caption)

class HeaderButton(urwid.Button):
    button_left = urwid.Text(">")
    button_right = urwid.Text("")

class Widget:
    @staticmethod
    def _wrap_widget(widget, label=None, annotation=None):
        if annotation is not None and label is not None:
            widget = urwid.Padding(widget, left=2, right=2, min_width=20)
            if isinstance(label, int):
                items = [('pack', urwid.AttrWrap(urwid.Text(f'[{label}]: {annotation}'), 'label')), ('weight', 1, widget)]
            else:
                items = [('pack', urwid.AttrWrap(urwid.Text(f'{label}: {annotation}'), 'label')), ('weight', 1, widget)]
            return urwid.Padding(
                urwid.Pile(items),              
                left=2, right=2, min_width=20
            )
        elif label is not None:
            if isinstance(label, int):
                items = [('pack', urwid.AttrWrap(urwid.Text(f'[{label}]:'), 'label')), ('weight', 1, widget)]
            else:
                items = [('pack', urwid.AttrWrap(urwid.Text(f'{label}:'), 'label')), ('weight', 1, widget)]
            return urwid.Padding(
                urwid.Columns(items, dividechars=1, min_width=20),                 
                left=2, right=2, min_width=20
            )
        else:
            return urwid.Padding(
                urwid.Columns([('weight', 1, widget)], dividechars=1, min_width=20),                 
                left=2, right=2, min_width=20
            )
    @staticmethod
    def unwrap_widget(widget):
        target_type = [urwid.Text, urwid.Edit, urwid.IntEdit, FloatEdit, ComboBox, urwid.Button, FlatButton, HeaderButton, urwid.Divider]
        while not type(widget) in target_type:
            widget_type = type(widget)
            if widget_type == urwid.AttrWrap:
                widget = widget.original_widget
            elif widget_type == urwid.Padding:
                widget = widget.original_widget
            elif widget_type in [urwid.Columns, urwid.Pile]:
                widget = widget.widget_list[-1]
        return widget

    @staticmethod
    def hash(widget):
        return hash(Widget.unwrap_widget(widget))

    @staticmethod
    def divider(char=" ", top=0, bottom=0):
        return urwid.Divider(char, top, bottom)
    @staticmethod
    def text(text=" ", colorscheme='body'):
        return Widget._wrap_widget(urwid.AttrWrap(urwid.Text(text), colorscheme))
    class Edit:
        @staticmethod
        def text(label=None, default="", multiline=False, colorschemes=('edit', 'focus')):
            if not multiline:
                #widget = ('weight', 9, urwid.AttrWrap(urwid.Edit(edit_text=default, multiline=False), *colorschemes))
                widget = urwid.AttrWrap(urwid.Edit(edit_text=default, multiline=False), *colorschemes)
                return Widget._wrap_widget(widget, label)
            else:
                widget = urwid.AttrWrap(urwid.Edit(edit_text=default, multiline=True), *colorschemes)
                return Widget._wrap_widget(widget, label, annotation='|')
        @staticmethod
        def integer(label=None, default=0, colorschemes=('edit', 'focus')):
            widget = urwid.AttrWrap(urwid.IntEdit(default=default), *colorschemes)
            return Widget._wrap_widget(widget, label)
        @staticmethod
        def number(label=None, default=.0, colorschemes=('edit', 'focus')):
            widget = urwid.AttrWrap(FloatEdit(default=str(default)), *colorschemes)
            return Widget._wrap_widget(widget, label)

    def dropdown(label=None, items=[], default=0, on_state_change=None, colorschemes=('edit', 'focus')):
        widget = urwid.AttrWrap(ComboBox(items, default, on_state_change), *colorschemes)
        return Widget._wrap_widget(widget, label)

    def button(label=None, text="", callback=None, colorschemes=('edit', 'focus'), comment=None):
        if comment:
            widget = urwid.AttrWrap(
                urwid.Columns([
                    ('weight', 1, FlatButton(text, callback)),
                    #('pack', urwid.AttrWrap(urwid.Text(f'# {comment}', align=urwid.RIGHT), 'description'))
                    ('pack', urwid.Text(f'# {comment}', align=urwid.RIGHT))
                ], dividechars=1, min_width=20), 
            *colorschemes)
        else:
            widget = urwid.AttrWrap(FlatButton(text, callback), *colorschemes)
        return Widget._wrap_widget(widget, label, annotation='')

    def group(label=None):
        widget = urwid.ListBox()
        return Widget._wrap_widget(widget, label, annotation='')
