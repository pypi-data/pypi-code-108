

import os
import io
import sys
import time
from twisted import logger
from twisted.logger import formatEvent
from twisted.logger import LogLevel
from twisted.logger import LogLevelFilterPredicate
from twisted.logger import FilteringLogObserver
from twisted.logger import textFileLogObserver
from twisted.logger import STDLibLogObserver

from appdirs import user_log_dir
from datetime import datetime
from collections import deque
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.utils import get_hex_from_color
from .widgets.labels import ColorLabel

from .config import ConfigMixin
from .basemixin import BaseMixin
from .basemixin import BaseGuiMixin

import logging
logging.basicConfig(level=logging.DEBUG)


class NodeLoggingMixin(ConfigMixin, BaseMixin):
    _log = None

    def __init__(self, *args, **kwargs):
        super(NodeLoggingMixin, self).__init__(*args, **kwargs)
        self._log_file = None
        self.log_prune()
        self._log = logger.Logger(namespace=self._appname,
                                  source=self)
        self.reactor.callWhenRunning(self._start_logging)

    def _observers(self):
        if self.config.debug:
            level = LogLevel.debug
        else:
            level = LogLevel.info

        return [
            # STDLibLogObserver(),
            FilteringLogObserver(
                textFileLogObserver(sys.stdout),
                predicates=[LogLevelFilterPredicate(LogLevel.warn)]
            ),
            FilteringLogObserver(
                textFileLogObserver(io.open(self.log_file, 'a')),
                predicates=[LogLevelFilterPredicate(level)]
            ),

        ]

    def _start_logging(self):
        # TODO Mention that docs don't say reactor should be running
        # TODO Mention that docs are confusing about how extract works
        # TODO Find out about a functional print to console observer
        # TODO Mention problem with IOBase vs TextIOWrapper
        # TODO log_source is not set when logger instantiated in __init__
        logger.globalLogBeginner.beginLoggingTo(self._observers())
        self.log.info("Logging to {logfile}", logfile=self.log_file)

    @property
    def log(self):
        return self._log

    @property
    def log_file(self):
        if not self._log_file:
            self._log_file = os.path.join(
                self.log_dir, 
                'runlog_{0}'.format(datetime.today().strftime('%d%m%y'))
            )
        return self._log_file

    def log_prune(self):
        for fname in self.log_files:
            fpath = os.path.join(self.log_dir, fname)
            mtime = os.path.getmtime(fpath)
            if time.time() - mtime > (7 * 24 * 60 * 60):
                os.remove(fpath)

    @property
    def log_files(self):
        return self._log_files()

    def _log_files(self):
        for filename in os.listdir(self.log_dir):
            if os.path.isfile(os.path.join(self.log_dir, filename)):
                yield filename

    @property
    def log_dir(self):
        os.makedirs(user_log_dir(self._appname), exist_ok=True)
        return user_log_dir(self._appname)


class LoggingGuiMixin(ConfigMixin, BaseGuiMixin):
    def __init__(self, *args, **kwargs):
        self._gui_log = None
        self._gui_log_end = None
        self._gui_log_layout = None
        self._gui_log_scroll = None
        self._gui_log_lines = deque([], maxlen=100)
        super(LoggingGuiMixin, self).__init__(*args, **kwargs)

    def _observers(self):
        rv = NodeLoggingMixin._observers(self)
        if self.config.gui_log_display:
            rv.extend([self.gui_log_observer])
        return rv

    _level_ignore_map = {
        'trace': [],
        'debug': ['trace'],
        'info': ['trace', 'debug'],
        'warning': ['trace', 'debug', 'info'],
        'error': ['trace', 'debug', 'info', 'error'],
    }

    def gui_log_observer(self, event):
        ll = event['log_level'].name
        if ll in self._level_ignore_map[self.config.gui_log_level]:
            return
        msg = "[font=RobotoMono-Regular][{0:^8}][/font] {1} {2}".format(
            ll.upper(),
            datetime.fromtimestamp(event['log_time']).strftime("%d%m %H:%M:%S"),
            formatEvent(event)
        )
        color = None
        if ll == 'warn':
            color = [1, 1, 0, 1]
        elif ll == 'error':
            color = [1, 0, 0, 1]
        elif ll == 'critical':
            color = [1, 0, 0, 1]
        if color:
            color = get_hex_from_color(color)
            msg = '[color={0}]{1}[/color]'.format(color, msg)

        self._gui_log_lines.append(msg)
        self._gui_log.text = '\n'.join(self._gui_log_lines)

    @property
    def gui_log(self):
        if not self._gui_log:
            self._gui_log_scroll = ScrollView(
                size_hint=(None, None), bar_pos_y='right',
                bar_color=[1, 1, 1, 1], effect_cls=ScrollEffect,
                do_scroll_x=False, do_scroll_y=True)

            def _set_log_size(_, size):
                width = min(max(700, size[0] * 0.3), size[0])
                height = size[1] * 0.6
                self._gui_log_scroll.size = width, height
            self.gui_root.bind(size=_set_log_size)

            self._gui_log_layout = BoxLayout(orientation='vertical',
                                             size_hint=(1, None))

            self._gui_log = ColorLabel(
                size_hint=(1, 1), padding=(8, 8), bgcolor=[0, 0, 0, 0.2],
                halign='left', valign='top', markup=True, font_size='12sp',
            )

            self._gui_log_end = Label(size_hint=(1, None), height=1)

            def _set_label_height(_, size):
                if size[1] > Window.height * 0.3:
                    self._gui_log.height = size[1]
                else:
                    self._gui_log.height = Window.height * 0.3
            self._gui_log.bind(texture_size=_set_label_height)

            def _set_layout_height(_, size):
                if size[1] > Window.height * 0.3:
                    self._gui_log_layout.height = size[1]
                else:
                    self._gui_log_layout.height = Window.height * 0.3
                self._gui_log_scroll.scroll_to(self._gui_log_end)
            self._gui_log.bind(texture_size=_set_layout_height)

            def _set_text_width(_, size):
                self._gui_log.text_size = size[0], None
            self._gui_log.bind(size=_set_text_width)

            self._gui_log_layout.add_widget(self._gui_log)
            self._gui_log_layout.add_widget(self._gui_log_end)
            self._gui_log_scroll.add_widget(self._gui_log_layout)
            self.gui_debug_stack.add_widget(self._gui_log_scroll)
        return self._gui_log

    def gui_setup(self):
        super(LoggingGuiMixin, self).gui_setup()
        if not self.config.gui_log_display:
            return
        _ = self.gui_log
