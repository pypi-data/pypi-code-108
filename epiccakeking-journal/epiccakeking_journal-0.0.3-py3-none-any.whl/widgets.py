from gi.repository import Gtk, GLib

from epiccakeking_journal.utilities import templated


class SetManager(Gtk.Box):
    def __init__(self, initial_contents=None, callback=None):
        super().__init__(orientation=1)
        self.entry = Gtk.Entry(
            placeholder_text='Add a word'
        )
        self.entry.connect('activate', self.on_entry)
        self.append(self.entry)
        scroller = Gtk.ScrolledWindow(vexpand=True)
        self.list = Gtk.Box(orientation=1)
        scroller.set_child(self.list)
        self.append(scroller)
        self.callback=None
        if initial_contents:
            for i in initial_contents:
                self.add_entry(i)
        self.callback=callback

    def on_entry(self, *_):
        self.add_entry(self.entry.get_text())
        self.entry.set_text('')

    def add_entry(self, entry):
        sibling = None
        next_sibling = self.list.get_first_child()
        while next_sibling:
            if next_sibling.value > entry:
                break
            if next_sibling.value == entry:
                return
            sibling = next_sibling
            next_sibling = sibling.get_next_sibling()
        widget = Gtk.Box()
        widget.value = entry
        widget.append(Gtk.Label(label=entry, hexpand=True))
        button = Gtk.Button(icon_name='list-remove-symbolic')
        button.connect('clicked', lambda *_: self.list_remove(widget))
        widget.append(button)
        self.list.insert_child_after(widget, sibling)
        if self.callback:
            self.callback(self)

    def get_list(self):
        lst = []
        child = self.list.get_first_child()
        while child:
            lst.append(child.value)
            child = child.get_next_sibling()
        return lst

    def list_remove(self, widget):
        self.list.remove(widget)
        if self.callback:
            self.callback(self)


@templated
class SearchResult(Gtk.Button):
    __gtype_name__ = 'SearchResult'
    date_label = Gtk.Template.Child('date_label')
    preview = Gtk.Template.Child()

    def __init__(self, parent, date, line_number, text):
        super().__init__()
        self.parent = parent
        self.date = date
        self.connect('clicked', self.on_click)
        self.date_label.set_label(date.isoformat() + ': ')
        self.preview.set_label(text.rstrip())

    def on_click(self, *_):
        self.parent.change_day(self.date)


class WordCloud(Gtk.ScrolledWindow):
    MAX_WORDS = 50

    def __init__(self, frequency_data=None, press_callback=None):
        """
        :param frequency_data: Iterable yielding (word, count) tuples
        """
        super().__init__(vexpand=True)
        self.press_callback = press_callback
        if frequency_data is not None:
            self.load(frequency_data)

    def load(self, frequency_data):
        box = Gtk.TextView(wrap_mode=2, editable=False, cursor_visible=False)
        buffer = box.get_buffer()
        words = sorted(frequency_data, key=lambda x: x[1], reverse=True)
        words = words[:self.MAX_WORDS]
        if words:
            avg = sum(x[1] ** .5 for x in words) / len(words)
        else:
            avg = 1
        words.sort(key=lambda x: x[0])
        for word, count in words:
            button = Gtk.Button(css_classes=('cloud_button',))
            label = Gtk.Label(
                margin_end=2,
                margin_start=2,
                yalign=1,
            )
            label.set_markup(f'<span font_desc="{10 * count ** .5 // avg}">{GLib.markup_escape_text(word)}</span>')
            button.connect('clicked', self.make_button_func(word))
            button.set_child(label)
            box.add_child_at_anchor(button, buffer.create_child_anchor(buffer.get_end_iter()))
        self.set_child(box)

    @classmethod
    def from_string(cls, s):
        """Generate a word cloud from a string"""
        word_dict = {}
        for word in s.split():
            word_dict.setdefault(word, 0)
            word_dict[word] += 1
        return cls(word_dict.items())

    def on_button_press(self, *_):
        print(*_)
        return True

    def make_button_func(self, word):
        def f(*_):
            self.press_callback(word)
            return True

        return f


@templated
class JournalPage(Gtk.ScrolledWindow):
    __gtype_name__ = 'JournalPage'
    text_area = Gtk.Template.Child('text_area')

    def __init__(self, backend, date):
        super().__init__()
        self.backend = backend
        self.date = date
        self.buffer = self.text_area.get_buffer()
        self.tags = {
            'title': self.buffer.create_tag(
                'title',
                foreground='pink',
                font='Sans 20',
            ),
            'bullet': self.buffer.create_tag(
                'bullet',
                foreground='green',
            ),
            'code': self.buffer.create_tag(
                'code',
                font='Monospace',
            ),
            'rule': self.buffer.create_tag(
                'rule',
                foreground='green',
            ),
        }
        self.buffer.connect('changed', lambda *_: self.format())
        self.add_shortcut(Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string('<Control>space'),
            Gtk.CallbackAction.new(lambda *_: self.insert_line()),
        ))
        self.add_shortcut(Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string('<Control>H'),
            Gtk.CallbackAction.new(lambda *_: self.insert_header()),
        ))
        self.add_shortcut(Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string('<Control>M'),
            Gtk.CallbackAction.new(lambda *_: self.insert_code()),
        ))
        self.buffer.set_text(self.backend.get_day(self.date))

    def save(self):
        return self.backend.save_day(self.date, self.get_text())

    def get_text(self):
        return self.buffer.get_text(*self.buffer.get_bounds(), True)

    def focus(self):
        self.text_area.grab_focus()

    def format(self):
        self.buffer.remove_all_tags(*self.buffer.get_bounds())
        code = False
        for i in range(self.buffer.get_line_count()):
            start = self.buffer.get_iter_at_line(i)[1]
            end = start.copy()
            end.forward_to_line_end()
            text = self.buffer.get_text(start, end, True)
            if text == '```':
                code ^= True
                self.buffer.apply_tag(self.tags['code'], start, end)
            elif code:
                self.buffer.apply_tag(self.tags['code'], start, end)
            elif text.startswith('# '):
                self.buffer.apply_tag(self.tags['title'], start, end)
            elif text == '====================':
                self.buffer.apply_tag(self.tags['rule'], start, end)
            elif text.startswith('* '):
                bullet_end = start.copy()
                bullet_end.forward_char()
                self.buffer.apply_tag(self.tags['bullet'], start, bullet_end)

    def insert_line(self):
        self.buffer.insert_at_cursor('\n====================\n')

    def insert_header(self):
        iter = self.buffer.get_iter_at_offset(self.buffer.get_property('cursor-position'))
        iter.set_line_offset(0)
        iter2 = iter.copy()
        iter2.set_line_offset(2)
        if self.buffer.get_text(iter, iter2, True) == '# ':
            self.buffer.delete(iter, iter2)
        else:
            self.buffer.insert(iter, '# ')

    def insert_code(self):
        self.buffer.begin_user_action()
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            self.buffer.insert(bounds[0], '```\n' if bounds[0].starts_line() else '\n```\n')
            # Insertion invalidated the iters, so a new one is needed
            bounds = self.buffer.get_selection_bounds()
            self.buffer.insert(bounds[1], '\n```' if bounds[1].ends_line() else '\n```\n')
        else:
            self.buffer.insert_at_cursor('\n```\n')
            offset = self.buffer.get_property('cursor-position')
            self.buffer.insert_at_cursor('\n```\n')
            self.buffer.place_cursor(self.buffer.get_iter_at_offset(offset))
        self.format()
        self.buffer.end_user_action()
