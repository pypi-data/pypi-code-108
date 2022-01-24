

import re
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView

from kivy.core.window import Window
from kivy.animation import Animation
from kivy.properties import NumericProperty

from .colors import ColorBoxLayout


class MarqueeLabel(ScrollView):
    spacer_width = NumericProperty(None)

    def __init__(self, **kwargs):
        bgcolor = kwargs.pop('bgcolor')
        ScrollView.__init__(self, bar_width=0)

        self._layout = ColorBoxLayout(size_hint_x=None,
                                      bgcolor=bgcolor,
                                      orientation='horizontal')
        self._mainlabels = []
        self._lspacer = Widget(size_hint_x=None, width=Window.width)
        self._rspacer = Widget(size_hint_x=None, width=Window.width)
        self.add_widget(self._layout)

        text = kwargs.pop('text')
        self._label_params = kwargs
        self.text = text

    def update_widths(self):
        width = self._lspacer.width + \
                self._rspacer.width + \
                sum([x.width for x in self._mainlabels])
        self._layout.width = width
        self.width = width

    def _set_spacer_width(self, _, size):
        self._lspacer.width = size[0]
        self._rspacer.width = size[0]
        self.update_widths()

    def on_parent(self, _, parent):
        if parent:
            parent.bind(size=self._set_spacer_width)

    @property
    def text(self):
        return ' '.join([x.text for x in self._mainlabels])

    def _set_mainlabel_width(self, l, size):
        l.width = size[0]
        self.update_widths()

    @text.setter
    def text(self, value):
        self.remove_widget(self._layout)

        texts = split_string(value, 64)
        self._layout.clear_widgets()
        self._layout.add_widget(self._lspacer)

        self._mainlabels = []
        for t in texts:
            l = Label(text=t, size_hint_x=None,
                      text_size=(None, None), **self._label_params)
            self._layout.add_widget(l)
            l.bind(texture_size=self._set_mainlabel_width)
            l.texture_update()
            self._mainlabels.append(l)

        self._layout.add_widget(self._rspacer)
        self.add_widget(self._layout)
        self.update_widths()

    def start(self, loop=True):
        speed = 75
        scroll_distance = self._layout.width - self._lspacer.width
        duration = scroll_distance / speed
        # print("Scroll was", self.scroll_x)
        self.scroll_x = 0
        # print("Using duration", duration)
        self._animation = Animation(scroll_x=1, duration=duration)
        if loop:
            self._animation.bind(on_complete=self._check_complete)
            pass
        self._animation.start(self)

    def _check_complete(self, animation, instance):
        # print(instance.scroll_x)
        # print(self._mainlabels[-1].x + self._mainlabels[-1].width)
        if instance.scroll_x > 0.95:
            # print("Repeating")
            self._animation.unbind(on_scroll=self._check_complete)
            animation.stop(self)
            self.start()

    def stop(self):
        self._animation.unbind(on_scroll=self._check_complete)
        self._animation.stop(self)
        self.clear_widgets()


def split_string(text, limit):
    words = re.split('(\W)', text)
    if max(map(len, words)) > limit:
        raise ValueError("limit is too small")
    result = []
    cpart = ''
    for word in words:
        if len(word) > limit - len(cpart):
            result.append(cpart)
            cpart = word
        else:
            cpart += word
    if cpart:
        result.append(cpart)
    return result
