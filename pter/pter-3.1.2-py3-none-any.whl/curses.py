import logging
import os
import sys
import datetime
import string
import webbrowser
import curses
import curses.panel
import traceback
import tempfile
import subprocess
import shlex
import shutil

from pytodotxt import TodoTxt, Task

from cursedspace import Application, Panel, ScrollPanel, InputLine, ShellContext, Completion

from pter import common
from pter import utils
from pter import configuration
from pter.searcher import Searcher
from pter.key import Key
from pter.tr import tr


SHORT_NAMES = {'quit': 'Quit',
               'cancel': 'Cancel',
               'select-item': 'Select',
               'next-item': 'Next item',
               'prev-item': 'Previous item',
               'page-up': 'One page up',
               'page-down': 'One page down',
               'search': 'Search',
               'open-url': 'Open URL',
               'load-template': 'Load task template',
               'save-template': 'Save task as template',
               'load-search': 'Load search',
               'save-search': 'Save search',
               'search-context': 'Search for context of this task',
               'search-project': 'Search for project of this task',
               'first-item': 'First item',
               'last-item': 'Last item',
               'edit-task': 'Edit task',
               'create-task': 'New task',
               'jump-to': 'Jump to item',
               'toggle-hidden': 'Set/unset hidden',
               'toggle-done': 'Set/unset done',
               'toggle-tracking': 'Start/stop tracking',
               'show-help': 'Help',
               'open-manual': 'Read the manual',
               'go-left': 'Go one character to the left',
               'go-right': 'Go one character to the right',
               'go-bol': 'Go to start of line',
               'go-eol': 'Go to end of line',
               'del-left': 'Delete to the left',
               'del-right': 'Delete to the right',
               'del-to-bol': 'Delete to start of line',
               'submit-input': 'Apply changes',
               'select-file': 'Select file',
               'delegate': 'Delegate task',
               'delete': 'Delete task',
               'refresh-screen': 'Refresh screen',
               'reload-tasks': 'Reload todo files',
               'comp-next': 'Next completion option',
               'comp-prev': 'Previous completion option',
               'comp-use': 'Use selected completion option',
               'comp-close': 'Close the completion list',
               }


class Color:
    def __init__(self, fg, bg=None):
        self.fg = fg
        self.bg = bg

    def pair(self):
        return [self.fg, self.bg]

    def __eq__(self, other):
        return self.fg == other.fg and self.bg == other.bg


class TaskLineGroup:
    def __init__(self):
        self.elements = []

    def append(self, *args, **kwargs):
        self.elements.append(TaskLineElement(*args, **kwargs))


class TaskLine:
    def __init__(self, task, source):
        self.elements = {}
        self.task = task
        self.source = source
        self._due = None

    def add(self, kind, *args, **kwargs):
        self.elements[kind] = TaskLineElement(*args, **kwargs)
        self.elements[kind].name = kind

    @property
    def due(self):
        due = self.task.attr_due
        if self._due is None and len(due) > 0:
            try:
                self._due = datetime.datetime.strptime(due[0], Task.DATE_FMT).date()
            except ValueError:
                self._due = None
        return self._due

    @property
    def is_overdue(self):
        return not self.task.is_completed and \
               self.due is not None and \
               self.due < datetime.date.today()

    @property
    def is_due_tomorrow(self):
        return not self.task.is_completed and \
               self.due is not None and \
               self.due == datetime.date.today() + datetime.timedelta(days=1)

    @property
    def is_due_today(self):
        return not self.task.is_completed and \
               self.due is not None and \
               self.due == datetime.date.today()


class TaskLineDescription(TaskLineGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = common.TF_DESCRIPTION

    @property
    def space_around(self):
        return True


class TaskLineElement:
    def __init__(self, content, color=None, space_around=False, name=None):
        self.content = content
        self.color = color
        self.space_around = space_around
        self.name = name


class TaskLineSelectionIcon(TaskLineElement):
    def __init__(self, content):
        super().__init__(content, space_around=False)
        self.name = common.TF_SELECTION


class StatusBar(Panel):
    def __init__(self, app):
        super().__init__(app, (1, 1))
        self.text = ""
        self.color = None
        self.expire = datetime.datetime.max
        self.blank_after = max(1, app.conf.number(common.SETTING_GROUP_GENERAL,
                                                  common.SETTING_INFO_TIMEOUT,
                                                  common.DEFAULT_INFO_TIMEOUT))

    def set_text(self, text, color=None):
        self.text = text
        self.color = color or common.SETTING_COL_NORMAL
        self.expire = datetime.datetime.now() + datetime.timedelta(seconds=self.blank_after)
        self.paint()

    def is_expired(self):
        return len(self.text) > 0 and datetime.datetime.now() >= self.expire

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)

        if self.is_expired():
            self.text = ''
            self.color = common.SETTING_COL_NORMAL

        attr = self.app.color(common.SETTING_COL_NORMAL)
        try:
            self.win.addstr(0, 0, " "*self.dim[1], attr)
        except curses.error:
            pass
        if len(self.text) > 0:
            self.win.addstr(0, 0, self.text[:self.dim[1]], self.app.color(self.color))
        self.win.noutrefresh()


class HelpBar(Panel):
    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)

        mapping = self.app.key_mapping
        actions = ['show-help', 'quit', 'edit-task',
                   'create-task', 'search', 'load-search', 'save-search',
                   'toggle-done', 'jump-to', 'next-item', 'prev-item']

        if len(self.app.focus) == 0:
            pass
        elif isinstance(self.app.focus[-1], HelpScreen):
            actions = ['quit', 'cancel', 'refresh-screen']
        elif isinstance(self.app.focus[-1], Selector):
            actions = ['cancel', 'select-item']
        elif isinstance(self.app.focus[-1], TaskCreator):
            actions = ['cancel', 'submit-input']
            if len(self.app.sources) > 1:
                actions += ['select-file']
            mapping = self.app.editor_key_mapping
        elif isinstance(self.app.focus[-1], TaskEditor):
            actions = ['cancel', 'submit-input']
            mapping = self.app.editor_key_mapping

        try:
            self.win.addstr(0, 0, " "*self.dim[1])
        except curses.error:
            pass

        x = 1
        for action in actions:
            label = SHORT_NAMES.get(action, None)
            if label is None:
                continue
            label = tr(label) + " "

            keys = [k for k, v in mapping.items() if v == action]
            if len(keys) == 0:
                continue

            if keys[0] in Key.SPECIAL:
                keytext = f" {tr(Key.SPECIAL[keys[0]])} "
            else:
                keytext = f" {tr(keys[0])} "
            if x + len(keytext) + len(label) >= self.dim[1]:
                break

            self.win.addstr(0, x, keytext, self.app.color(common.SETTING_COL_HELP_KEY))
            x += len(keytext)
            self.win.addstr(0, x, label, self.app.color(common.SETTING_COL_HELP_TEXT))
            x += len(label) + 1
        self.win.noutrefresh()


class RemappedScrollPanel(ScrollPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SCROLL_NEXT = [key for key, value in self.app.key_mapping.items() if value == 'next-item']
        self.SCROLL_PREVIOUS = [key for key, value in self.app.key_mapping.items() if value == 'prev-item']
        self.SCROLL_NEXT_PAGE = [key for key, value in self.app.key_mapping.items() if value == 'page-down']
        self.SCROLL_PREVIOUS_PAGE = [key for key, value in self.app.key_mapping.items() if value == 'page-up']
        self.SCROLL_TO_START = [key for key, value in self.app.key_mapping.items() if value == 'first-item']
        self.SCROLL_TO_END = [key for key, value in self.app.key_mapping.items() if value == 'last-item']

        self.SCROLL_MARGIN = self.app.scroll_margin


class TaskList(RemappedScrollPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = []
        self.max_widths = {}
        self.cursor = 0
        self.SCROLL_MARGIN = self.app.scroll_margin

    def rebuild_items(self):
        self.items = []
        self.max_widths = {}

        today = datetime.date.today()

        self.update_max_width(common.TF_DONE, max(len(self.app.done_marker[0]), len(self.app.done_marker[1])))
        self.update_max_width(common.TF_SELECTION, self.app.selection_indicator)
        self.update_max_width(common.TF_TRACKING, self.app.tracking_marker)
        self.update_max_width(common.TF_DUE, max([len(m) for m in self.app.due_marker]))

        for nr, pair in enumerate(self.tasks):
            task, _ = pair
            line = TaskLine(task, task.todotxt)

            # Selection indicator
            if len(self.app.selection_indicator) > 0:
                line.elements[common.TF_SELECTION] = TaskLineSelectionIcon(self.app.selection_indicator)

            # Item number
            text = str(nr+1)
            line.add(common.TF_NUMBER, text)
            self.update_max_width(common.TF_NUMBER, text)

            # Done marker
            done_marker = self.app.done_marker[1 if task.is_completed else 0]
            line.add(common.TF_DONE, done_marker)

            # Age
            if task.creation_date is not None:
                text = str((datetime.date.today() - task.creation_date).days)
                line.add(common.TF_AGE, text)
                self.update_max_width(common.TF_AGE, text)

            # Creation date
            if task.creation_date is not None:
                text = self.app.date_as_str(task.creation_date, common.TF_CREATED)
                line.add(common.TF_CREATED, text)
                self.update_max_width(common.TF_CREATED, text)

            # Completion date
            if task.completion_date is not None:
                text = self.app.date_as_str(task.completion_date, common.TF_COMPLETED)
                line.add(common.TF_COMPLETED, text)
                self.update_max_width(common.TF_COMPLETED, text)

            # Tracking
            if task.attributes.get(common.ATTR_TRACKING, None) is not None:
                line.add(common.TF_TRACKING, self.app.tracking_marker)

            # Due marker
            if line.due is not None:
                duedays = str((line.due - today).days)
                line.add(common.TF_DUEDAYS, duedays)
                self.update_max_width(common.TF_DUEDAYS, duedays)

                if not task.is_completed:
                    if line.due < today:
                        line.add(common.TF_DUE,
                                 self.app.due_marker[0],
                                 common.SETTING_COL_OVERDUE)
                    elif line.due == today:
                        line.add(common.TF_DUE,
                                 self.app.due_marker[1],
                                 common.SETTING_COL_DUE_TODAY)
                    elif line.due == today + datetime.timedelta(days=1):
                        line.add(common.TF_DUE,
                                 self.app.due_marker[2],
                                 common.SETTING_COL_DUE_TOMORROW)

            # Priority marker
            if task.priority is not None:
                pri = task.priority.upper()
                attrs = None
                if pri == 'A':
                    attrs = common.SETTING_COL_PRI_A
                elif pri == 'B':
                    attrs = common.SETTING_COL_PRI_B
                elif pri == 'C':
                    attrs = common.SETTING_COL_PRI_C
                line.add(common.TF_PRIORITY, f"{pri}", attrs)
                self.update_max_width(common.TF_PRIORITY, '(A)')

            # Description
            description = TaskLineDescription()
            if task.description is not None:
                for word in task.description.split(' '):
                    if len(word) == 0:
                        continue

                    attr = None

                    if word.startswith('@') and len(word) > 1:
                        attr = common.SETTING_COL_CONTEXT
                    elif word.startswith('+') and len(word) > 1:
                        attr = common.SETTING_COL_PROJECT
                    elif ':' in word:
                        key, value = word.split(':', 1)
                        if 'hl:' + key in self.app.colors:
                            attr = 'hl:' + key
                        if key in [common.ATTR_T, common.ATTR_DUE]:
                            word = key + ':' + self.app.date_as_str(value, key)
                        if key == common.ATTR_PRI:
                            attr = None
                            value = value.upper()
                            if value == 'A':
                                attr = common.SETTING_COL_PRI_A
                            elif value == 'B':
                                attr = common.SETTING_COL_PRI_B
                            elif value == 'C':
                                attr = common.SETTING_COL_PRI_C
                    description.append(word, attr, space_around=True)
            line.elements[common.TF_DESCRIPTION] = description
            self.update_max_width(common.TF_DESCRIPTION,
                                  ' '.join([e.content for e in description.elements]))

            self.items.append(line)
        self.cursor = min(self.cursor, len(self.items)-1)

    def update_max_width(self, name, textlen):
        if name not in self.max_widths:
            self.max_widths[name] = 0
        if isinstance(textlen, str):
            textlen = len(textlen)
        for tf in self.app.task_format:
            if not isinstance(tf, tuple):
                continue
            tname, _, left, right = tf
            if tname == name:
                textlen += 0 if left is None else len(left)
                textlen += 0 if right is None else len(right)
        self.max_widths[name] = max(textlen, self.max_widths[name])

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)

    def do_paint_item(self, y, x, maxwidth, is_selected, taskline):
        is_tracked = len(taskline.task.attr_tracking) > 0

        baseattrs = common.SETTING_COL_NORMAL
        if taskline.is_overdue:
            baseattrs = common.SETTING_COL_OVERDUE
        elif taskline.is_due_tomorrow:
            baseattrs = common.SETTING_COL_DUE_TOMORROW
        elif taskline.is_due_today:
            baseattrs = common.SETTING_COL_DUE_TODAY
        if is_tracked:
            baseattrs = common.SETTING_COL_TRACKING

        def print_element(y, x, maxwidth, element, align, extra):
            cut_off = False
            if isinstance(element, TaskLineSelectionIcon) and not is_selected:
                elem = ''
            elif isinstance(element, TaskLineGroup):
                return print_group(y, x, maxwidth, element, align, extra)
            elif isinstance(element, str):
                element = TaskLineElement(element)
                elem = element.content
            else:
                elem = element.content

            if align is not None:
                width = self.max_widths.get(element.name, 0)
                if extra is not None and extra[0] is not None:
                    width -= len(extra[0])
                if extra is not None and extra[1] is not None:
                    width -= len(extra[1])
                width = max(0, width)
                elem = f"{elem:{align}{width}}"
            elif len(elem) == 0:
                return ''

            if extra_left is not None:
                elem = extra_left + elem

            if extra_right is not None:
                elem = elem + extra_right

            elemlen = len(elem)
            if elemlen > maxwidth:
                cut_off = True
                elem = elem[:maxwidth]

            try:
                self.win.addstr(y, x, elem, self.app.color(element.color, is_selected, baseattrs))
            except curses.error:
                pass

            if cut_off:
                attrs = common.SETTING_COL_OVERFLOW
                try:
                    self.win.addstr(y, x+maxwidth-len(self.app.overflow_marker[1]),
                                    self.app.overflow_marker[1],
                                    self.app.color(attrs, is_selected, baseattrs))
                except curses.error:
                    pass
            return elem

        def print_group(y, x, maxwidth, group, align, extra):
            line = ''

            if extra is not None and extra[0] is not None:
                self.win.addstr(y, x + len(line), extra[0], self.app.color(baseattrs, is_selected))
                line = extra[0]

            if align is not None and align.endswith('>'):
                group_width = len(' '.join([e.content for e in group.elements]))
                spacing_width = min(maxwidth - len(line),
                                    self.max_widths[group.name] - group_width)
                spacing = align[0] * spacing_width
                try:
                    self.win.addstr(y, x + len(line), spacing, self.app.color(baseattrs, is_selected))
                except curses.error:
                    pass
                line += spacing

            cut_off = False
            for elnr, element in enumerate(group.elements):
                word = ''

                if elnr > 0 and (element.space_around or group.elements[elnr-1].space_around):
                    if len(line) + 1 >= maxwidth:
                        cut_off = True
                    else:
                        self.win.addstr(y, x + len(line), " ",
                                        self.app.color(baseattrs, is_selected))
                        line += " "

                cut_off = cut_off or len(line) >= maxwidth

                if not cut_off:
                    if isinstance(element, TaskLineGroup):
                        word = print_group(y, x + len(line),
                                           maxwidth-len(line),
                                           element, None, None)
                    else:
                        word = print_element(y, x + len(line),
                                             maxwidth-len(line),
                                             element, None, None)
                    line += word

                if cut_off or len(line) >= maxwidth:
                    break

            if not cut_off and align is not None and align.endswith('<'):
                if len(line) < self.max_widths[group.name]:
                    spacing = align[0] * min(maxwidth-len(line),
                                             self.max_widths[group.name]-len(line))
                    self.win.addstr(y, x + len(line),
                                    spacing,
                                    self.app.color(baseattrs, is_selected))
                    line += spacing

            if not cut_off and extra is not None and extra[1] is not None and len(line) + 1 < maxwidth:
                self.win.addstr(y, x + len(line), extra[1], self.app.color(baseattrs, is_selected))
            return line

        self.win.move(y, x)
        self.win.clrtoeol()
        self.win.noutrefresh()

        for token in self.app.task_format:
            align = None
            extra = None
            if isinstance(token, tuple):
                token, align, extra_left, extra_right = token
                extra = (extra_left, extra_right)
                token = taskline.elements.get(token, TaskLineElement('', name=token))
            elif isinstance(token, str):
                token = TaskLineElement(token)
            else:
                raise TypeError()

            x += len(print_element(y, x, maxwidth-x, token, align, extra))

            if x >= maxwidth:
                break

        if x < maxwidth:
            try:
                self.win.addstr(y, x, ' '*(maxwidth-x), self.app.color(baseattrs, is_selected))
            except curses.error:
                pass

    def jump_to(self, item):
        if item in self.items:
            self.cursor = self.items.index(item)

        elif isinstance(item, int):
            if item < 0 or item >= len(self.items):
                return False
            self.cursor = item

        elif isinstance(item, (TaskLine, Task)):
            if isinstance(item, TaskLine):
                task = str(item.source.filename) + "\n" + str(item.task)
            elif isinstance(item, Task):
                task = str(item.todotxt.filename) + "\n" + str(item)
            else:
                return False

            matching = [idx for idx, t in enumerate(self.items)
                        if str(t.source.filename) + "\n" + str(t.task) == task]

            if len(matching) == 0:
                return False
            self.cursor = matching[0]

        else:
            return False

        self.scroll()
        return True


class RemappedInputLine(InputLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_changed = False

    def focus(self):
        y, x = super().focus()
        if not self.cursor_changed:
            self.cursor_changed = True
            self.app.show_cursor(True)
        return y, x

    def on_submit(self):
        pass

    def on_cancel(self):
        pass

    def on_change(self):
        self.update_completion()

    def on_timeout(self):
        return False

    def handle_key(self, key):
        fnc = self.app.editor_key_mapping.get(str(key), None)

        handled = True
        must_repaint = False
        text_before = self.text
        current_word = None
        if self.completion is not None:
            current_word = self.current_word()

        if key == Key.TIMEOUT:
            must_repaint = self.on_timeout()
        elif self.completion is not None and self.completion.handle_key(key):
            handled = True
        elif fnc == 'cancel':
            self.on_cancel()
        elif fnc == 'submit-input':
            self.on_submit()
        elif fnc == 'del-left' and self.cursor > 0:
            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
            self.cursor -= 1
            must_repaint = True
        elif fnc == 'del-right':
            self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
            must_repaint = True
        elif fnc == 'del-to-bol':
            self.text = self.text[self.cursor:]
            self.cursor = 0
            must_repaint = True
        elif fnc == 'go-left':
            self.cursor = max(0, self.cursor-1)
            must_repaint = self.scroll()
        elif fnc == 'go-right':
            self.cursor = min(len(self.text), self.cursor+1)
            must_repaint = self.scroll()
        elif fnc == 'go-bol':
            self.cursor = 0
            must_repaint = self.scroll()
        elif fnc == 'go-eol':
            self.cursor = len(self.text)
            must_repaint = self.scroll()
        elif len(str(key)) == 1:
            self.text = self.text[:self.cursor] + str(key) + self.text[self.cursor:]
            self.cursor += 1
            must_repaint = True
        else:
            handled = False

        if self.completion is not None and self.current_word() != current_word:
            self.completion.close()

        if text_before != self.text:
            self.on_change()

        if must_repaint:
            self.paint()

        return handled


class ContextCompletion(Completion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.KEYS_NEXT_ALTERNATIVE = [key for key, value in self.app.completion_key_mapping.items()
                                      if value == 'comp-next']
        self.KEYS_PREVIOUS_ALTERNATIVE = [key for key, value in self.app.completion_key_mapping.items()
                                          if value == 'comp-prev']
        self.KEYS_SELECT_ALTERNATIVE = [key for key, value in self.app.completion_key_mapping.items()
                                        if value == 'comp-use']
        self.KEYS_CANCEL_SUGGESTIONS = [key for key, value in self.app.completion_key_mapping.items()
                                        if value == 'comp-close']

    def close(self):
        retval = super().close()
        if retval:
            self.app.paint(True)
        return retval

    def update(self, y, x):
        span = self.inputline.current_word()

        if span is None:
            self.close()
            return

        word = self.inputline.text[span[0]:self.inputline.cursor]
        if word.startswith('@'):
            options = {context
                       for context in sum([list(source.contexts) for source in self.app.sources], start=[])
                       if context.startswith(word)}
        elif word.startswith('+'):
            options = {project
                       for project in sum([list(source.projects) for source in self.app.sources], start=[])
                       if project.startswith(word)}
        else:
            return

        if len(options) == 0 or (len(options) == 1 and word in options):
            self.close()
            return

        options = list(options)
        options.sort()
        self.set_alternatives(options, (y, x))
        self.app.paint()


class SearchBar(RemappedInputLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_text = self.text
        if self.app.use_completion:
            self.completion = ContextCompletion(self)

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        if clear:
            self.win.erase()
        self.scroll()

        attr = 0
        if len(self.text) == 0 and (len(self.app.focus) == 0 or self.app.focus[-1] is not self):
            visible_text = tr('(no search active)')
            attr = self.app.color(common.SETTING_COL_INACTIVE)
        else:
            visible_text = self.text[self.offset:]

        visible_text = visible_text[:self.dim[1]]
        try:
            self.win.addstr(0, 0, " "*self.dim[1])
        except curses.error:
            pass
        self.win.addstr(0, 0, visible_text, attr)
        self.win.noutrefresh()

        if self.completion is not None:
            self.completion.paint(clear)

    def on_change(self):
        self.update_completion()
        self.app.search.text = self.text
        self.app.search.parse()
        self.app.apply_search()
        self.app.tasks.paint(True)
        if self.app.focus[-1] is self:
            self.focus()

    def on_submit(self):
        self.previous_text = self.text
        self.unfocus()

    def on_cancel(self):
        self.text = self.previous_text
        self.unfocus()

    def unfocus(self):
        self.cursor_changed = False
        self.app.show_cursor(False)
        self.app.focus.pop(-1)
        self.scroll()
        self.app.paint()


class UserInput(Panel):
    def __init__(self, parent, on_accept, on_cancel=None, title='', text=''):
        super().__init__(parent.app)
        self.parent = parent
        self.title = title
        self.on_accept = on_accept
        self.custom_on_cancel = on_cancel
        self.editor = RemappedInputLine(self.app, 1, (1, 1))
        self.border = Panel.BORDER_ALL
        self.editor.text = text
        self.editor.cursor = len(self.editor.text)
        self.editor.on_cancel = self.on_cancel
        self.editor.on_submit = self.on_submit
        self.autoresize()

    def destroy(self):
        super().destroy()
        self.app.focus.pop(-1)
        self.app.paint(True)

    def handle_key(self, key):
        return self.editor.handle_key(key)

    def focus(self):
        if self.app.focus[-1] is self:
            y, x = self.editor.focus()
            self.win.move(y + 1, x + 1)
            self.win.noutrefresh()

    def autoresize(self):
        maxheight, maxwidth = self.app.size()
        width = 2*maxwidth//3
        if width < 22:
            width = maxwidth
        self.resize(3, width)
        y = maxheight//2 - 2
        x = (maxwidth - width)//2
        self.move(y, x)
        self.editor.resize(width-2)
        self.editor.move(y+1, x+1)

    def paint(self, clear=None):
        super().paint(clear)
        label = tr(self.title)
        if self.editor.read_only:
            label += ' ' + tr("(read only)")
        add_title(self, tr(self.title))
        self.win.noutrefresh()
        self.editor.paint(clear)
        self.editor.focus()

    def on_cancel(self):
        if self.custom_on_cancel is not None:
            self.custom_on_cancel()
        self.app.show_cursor(False)
        self.destroy()

    def on_submit(self):
        self.on_accept(self.editor.text)
        self.app.show_cursor(False)
        self.destroy()


class TaskEditor(UserInput):
    def __init__(self, parent, task):
        super().__init__(parent, None, None, 'Edit Task', '' if task is None else str(task.task))
        self.task = task
        self.on_accept = self.save_changes
        self.on_cancel = lambda: self.app.show_cursor(False)
        if self.app.use_completion:
            self.editor.completion = ContextCompletion(self.editor)

    def save_changes(self, text):
        self.app.show_cursor(False)
        if self.has_changes() and not self.editor.read_only:
            text = self.processed_text
            self.app.modify_task(self.task, lambda t: t.parse(text))

    @property
    def processed_text(self):
        return utils.dehumanize_dates(utils.auto_task_id(self.app.sources, self.editor.text))

    def has_changes(self):
        return str(self.task.task) != self.processed_text


class TaskCreator(TaskEditor):
    def __init__(self, parent):
        super().__init__(parent, None)
        self.title = 'New task'

        add_creation_date = self.app.conf.bool(common.SETTING_GROUP_GENERAL, common.SETTING_ADD_CREATED)
        create_from_search = self.app.conf.bool(common.SETTING_GROUP_GENERAL, common.SETTING_CREATE_FROM_SEARCH)
        self.auto_id = self.app.conf.bool(common.SETTING_GROUP_GENERAL, common.SETTING_AUTO_ID)

        initial = []
        if add_creation_date:
            initial.append(datetime.datetime.now().strftime(Task.DATE_FMT))
        if create_from_search:
            initial.append(utils.create_from_search(self.app.search))
        if self.app.selected_template is not None:
            initial.append(self.app.selected_template)

        initial = ' '.join([part for part in initial if len(part) > 0])
        if len(initial) > 0 and not initial.endswith(' '):
            initial += ' '
        self.editor.text = initial
        self.editor.cursor = len(initial)
        self.editor.scroll()

        self.task = Task(initial, todotxt=self.app.sources[0])

    def handle_key(self, key):
        fnc = self.app.editor_key_mapping.get(str(key), None)

        if fnc == 'select-file' and len(self.app.sources) > 1:
            self.app.show_cursor(False)
            self.app.focus.append(SourceSelector(self,
                                                 self.app.sources,
                                                 self.change_source,
                                                 lambda: self.app.show_cursor(True)))
            self.app.paint(True)
            return True

        return super().handle_key(key)

    def change_source(self, source):
        self.task.todotxt = source
        self.app.show_cursor(True)
        self.paint(True)

    def save_changes(self, text):
        self.app.show_cursor(False)
        if self.has_changes() and not self.editor.read_only:
            text = self.processed_text
            if self.auto_id and not any([word.startswith('id:') for word in text.split(' ')]):
                text += ' id:#'
                text = utils.auto_task_id(self.app.sources, text)

            self.task.parse(text)

            source = self.task.todotxt
            # reload if necessary
            if source.refresh():
                source.parse()

            # append the new task and save
            source.tasks.append(self.task)
            source.save(safe=self.app.safe_save)

            # update book keeping
            source.update_from_task(self.task)
            self.task.linenr = len(source.tasks)

            self.app.search.update_sources(self.app.sources)
            self.app.update_tasks()
            self.app.tasks.jump_to(self.task)

    def paint(self, clear=False):
        super().paint(clear)

        if len(self.app.sources) > 1:
            label = self.task.todotxt.displayname
            self.win.addstr(2, self.dim[1]-len(label)-3, f"┤{label}├")
            self.win.noutrefresh()

    def has_changes(self):
        return str(self.task) != self.processed_text


class Selector(RemappedScrollPanel):
    def __init__(self, parent, items, on_select, on_cancel=None, title='', numbered=False):
        super().__init__(parent.app)
        self.parent = parent
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.items = items
        self.title = title
        self.numbered = numbered
        self.autoresize()

    def paint(self, clear=False):
        super().paint(clear)
        if len(self.title) > 0:
            add_title(self, tr(self.title))
            self.win.noutrefresh()

    def autoresize(self):
        self.border = Panel.BORDER_ALL
        if hasattr(self.parent, 'autoresize'):
            self.parent.autoresize()
        maxheight, maxwidth = self.app.size()
        labelwidth = max([len(self.make_label(item)) for item in self.items]) \
                   + len(self.indicator(True)) \
                   + len(str(len(self.items))) + 3
        w = min(maxwidth, labelwidth)
        h = min(maxheight-2, len(self.items)+2)
        self.resize(h, w)
        self.move((maxheight-h)//2, (maxwidth-w)//2)

    def handle_key(self, key):
        strkey = str(key)
        fnc = self.app.key_mapping.get(strkey, None)

        if fnc == 'cancel':
            self.destroy()
            if self.on_cancel is not None:
                self.on_cancel()
            return True

        elif fnc == 'select-item':
            item = self.selected_item
            self.destroy()
            self.on_select(item)
            return True

        elif fnc == 'jump-to':
            self.app.focus.append(JumpToIndexReader(self.app, ''))
            self.app.paint(True)
            return True

        elif len(strkey) == 1 and strkey in string.digits:
            self.app.focus.append(JumpToIndexReader(self.app, strkey))
            self.app.paint(True)
            return True

        return super().handle_key(key)

    def number_prefix(self, item):
        if not self.numbered:
            return ""

        idx = self.items.index(item)
        nrwidth = len(str(len(self.items)+1))
        return f"{idx+1: >{nrwidth}} "

    def indicator(self, is_selected):
        if self.app.use_colors:
            return ""
        pointer = self.app.selection_indicator + " "
        if not is_selected:
            pointer = " "*len(pointer)
        return pointer

    def make_label(self, item):
        return str(item)

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        attrs = self.app.color(common.SETTING_COL_NORMAL, is_selected)

        label = self.indicator(is_selected) + self.number_prefix(item) + self.make_label(item)

        self.win.addstr(y, x, label[:maxwidth], attrs)
    
    def destroy(self):
        super().destroy()
        self.app.focus.pop(-1)
        self.app.paint(True)


class SourceSelector(Selector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Select source'

    def make_label(self, item):
        return item.displayname


class HelpScreen(RemappedScrollPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        nav_fncs = ['next-item', 'prev-item', 'page-up', 'page-down',
                    'first-item', 'last-item', 'jump-to']
        edt_fncs = ['toggle-hidden', 'toggle-done', 'edit-task', 'create-task',
                    'toggle-tracking', 'delegate', 'save-template', 'load-template', 'delete-task']
        search_fncs = ['search', 'load-search', 'save-search', 'search-context', 'search-project']
        meta_fncs = ['show-help', 'open-manual', 'quit', 'cancel', 'refresh-screen',
                     'reload-tasks']
        other_fncs = ['open-url']

        lines = [(tr('TASK LIST'), ''), ('', ''), (tr('Program'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(meta_fncs, self.app.key_mapping)]
        lines += [('', ''), (tr('Navigation'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(nav_fncs, self.app.key_mapping)]
        lines += [('', ''), (tr('Search'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(search_fncs, self.app.key_mapping)]
        lines += [('', ''), (tr('Change Tasks'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(edt_fncs, self.app.key_mapping)]
        lines += [('', ''), (tr('Other'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(other_fncs, self.app.key_mapping)]

        edt_nav_fncs = ['go-left', 'go-right', 'go-bol', 'go-eol']
        edt_edt_fncs = ['del-left', 'del-right', 'del-to-bol']
        edt_meta_fncs = ['cancel', 'submit-input']
        edt_comp_fncs = ['comp-next', 'comp-prev', 'comp-use', 'comp-close']
        lines += [('', ''), ('', ''), (tr('TASK EDITING'), ''), ('', ''), (tr('General'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(edt_meta_fncs, self.app.editor_key_mapping)]
        lines += [('', ''), (tr('Navigation'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(edt_nav_fncs, self.app.editor_key_mapping)]
        lines += [('', ''), (tr('Deletion'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(edt_edt_fncs, self.app.editor_key_mapping)]
        lines += [('', ''), (tr('Completion'), '')]
        lines += [(name, key) for name, key in self.collect_name_fnc(edt_comp_fncs, self.app.completion_key_mapping)]

        self.maxnamelen = max([len(n) for n, _ in lines])

        self.items = lines
        self.border = Panel.BORDER_ALL
        self.SCROLL_MARGIN = 1000

    def resize(self, *args):
        super().resize(*args)
        self.scroll()

    def scroll(self):
        self.cursor = max((self.list_height-1)//2, self.cursor)
        super().scroll()

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        attrs = common.SETTING_COL_NORMAL
        if item[1] == '':
            attrs = common.SETTING_COL_CONTEXT
        self.win.addstr(y, x, item[0] + " "*(self.maxnamelen-len(item[0])+3) + item[1], self.app.color(attrs))
        self.win.noutrefresh()

    def collect_name_fnc(self, fncs, mapping):
        for name, fnc in sorted([(v, k) for k, v in SHORT_NAMES.items() if k in fncs]):
            for key in [k for k, v in mapping.items() if v == fnc]:
                yield name, key

    def handle_key(self, key):
        fnc = self.app.key_mapping.get(str(key), None)

        if fnc in ['quit', 'cancel']:
            self.destroy()
            self.app.focus.pop(-1)
            self.app.paint(True)
            return True

        return super().handle_key(key)


class JumpToIndexReader(RemappedInputLine):
    def __init__(self, app, init):
        super().__init__(app, 1, (1,1))
        self.parent = app.focus[-1]
        assert self.parent is not self

        self.prefix = tr("Jump to:") + " "
        self.text = init
        self.cursor = len(self.text)
        self.autoresize()
        self.scroll()

    def autoresize(self):
        height, width = self.app.size()
        self.move(height-2, 0)
        self.resize(width-1)

    def on_submit(self):
        try:
            index = int(self.text)-1
        except ValueError:
            index = None

        if index is not None:
            self.parent.jump_to(index)
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def destroy(self):
        super().destroy()
        self.app.show_cursor(False)
        self.app.focus.pop(-1)
        self.app.status_bar.paint(True)
        self.app.focus[-1].paint(True)


class CursesApplication(Application):
    def __init__(self, sources, conf):
        super().__init__()
        self.quit = False
        self.sources = sources
        self.conf = conf
        self.colors = {}
        self.color_cache = {}
        self.all_tasks = []

        # sorting and searching
        self.sort_order = utils.build_sort_order(common.DEFAULT_SORT_ORDER)
        self.sort_order_txt = common.DEFAULT_SORT_ORDER
        self.search = Searcher('',
                               self.conf.bool(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_SEARCH_CASE_SENSITIVE),
                               self.conf.get(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_DEFAULT_THRESHOLD),
                               self.conf.bool(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_HIDE_SEQUENTIAL))
        self.search.update_sources(self.sources)

        # task display
        self.task_format = utils.parse_task_format(conf.get(common.SETTING_GROUP_GENERAL,
                                                            common.SETTING_TASK_FORMAT,
                                                            common.DEFAULT_TASK_FORMAT))
        self.done_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                   common.SETTING_ICON_NOT_DONE)),
                            utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                   common.SETTING_ICON_DONE)))
        self.overflow_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                       common.SETTING_ICON_OVERFLOW_LEFT)),
                                utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                       common.SETTING_ICON_OVERFLOW_RIGHT)))
        self.due_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_OVERDUE)),
                           utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_DUE_TODAY)),
                           utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_DUE_TOMORROW)))
        self.tracking_marker = utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                      common.SETTING_ICON_TRACKING))
        self.human_friendly_dates = conf.list(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_HUMAN_DATES)

        # colors and UI markers
        self.use_colors = conf.bool(common.SETTING_GROUP_GENERAL,
                                    common.SETTING_USE_COLORS)
        self.selection_indicator = utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                          common.SETTING_ICON_SELECTION))

        # delegation configuration
        self.delegation_marker = self.conf.get(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_DELEG_MARKER).strip()
        self.delegation_action = self.conf.get(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_DELEG_ACTION).lower()
        self.delegate_to = self.conf.get(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_DELEG_TO).lower().strip()
        if self.delegation_action not in common.DELEGATE_ACTIONS:
            logging.error(f"Configuration option 'delegate-option' ('{self.delegation_action}') is invalid.")
            self.delegation_action = common.DELEGATE_ACTION_NONE

        # behaviour
        self.clear_contexts = [context
                               for context in conf.list(common.SETTING_GROUP_GENERAL, common.SETTING_CLEAR_CONTEXT)
                               if len(context) > 0]
        self.reuse_recurring = conf.bool(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_REUSE_RECURRING, 'n')
        self.scroll_margin = conf.number(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_SCROLL_MARGIN)
        self.safe_save = conf.bool(common.SETTING_GROUP_GENERAL,
                                   common.SETTING_SAFE_SAVE, 'y')
        self.use_completion = conf.bool(common.SETTING_GROUP_GENERAL,
                                        common.SETTING_USE_COMPLETION, 'y')
        self.trash_file = conf.path(common.SETTING_GROUP_GENERAL,
                                    common.SETTING_TRASHFILE,
                                    common.DEFAULT_TRASHFILE);
        self.delete_is = conf.get(common.SETTING_GROUP_GENERAL,
                                  common.SETTING_DELETE_IS,
                                  common.DELETE_OPTION_DISABLED)
        if self.delete_is not in common.DELETE_OPTIONS:
            logging.error(f"Configuration option 'delete-is' ('{self.delete_is}') is invalid.")
            self.delete_is = common.DELETE_OPTION_DISABLED
        self.last_perm_delete = datetime.datetime.now()
        self.perm_delete_timeout = datetime.timedelta(milliseconds=500)

        # ensure paths to trash file
        if self.delete_is == common.DELETE_OPTION_TRASH:
            try:
                self.trash_file.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logging.error(f"Could not create path to trash file '{self.trash_file.parent}': {exc}")
                self.delete_is = common.DELETE_OPTION_DISABLED

        # ensure the trash file can be written
        if self.delete_is == common.DELETE_OPTION_TRASH:
            try:
                with open(self.trash_file, 'a', encoding='utf-8'):
                    logging.debug(f"Using trash file {self.trash_file}")
            except OSError as exc:
                logging.error(f"Could not open trash file '{self.trash_file}': {exc}")
                self.delete_is = common.DELETE_OPTION_DISABLED

        # external editor
        self.external_editor = self.conf.get(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_EXT_EDITOR)

        # protocols accepted to open with open-url
        self.protos = conf.list(common.SETTING_GROUP_GENERAL,
                                common.SETTING_PROTOCOLS)

        self.selected_template = None

        # keys, mappings, and functions
        self.key_mapping = {
            'q': 'quit',
            '^C': 'cancel',
            '<escape>': 'cancel',
            '<down>': 'next-item',
            '<up>': 'prev-item',
            '<pgup>': 'page-up',
            '<pgdn>': 'page-down',
            '<home>': 'first-item',
            '<end>': 'last-item',
            'j': 'next-item',
            'k': 'prev-item',
            '<return>': 'select-item',
            'h': 'toggle-hidden',
            'd': 'toggle-done',
            'e': 'edit-task',
            'E': 'edit-external',
            'n': 'create-task',
            ':': 'jump-to',
            '/': 'search',
            'c': 'search-context',
            'p': 'search-project',
            't': 'toggle-tracking',
            '^L': 'refresh-screen',
            '^R': 'reload-tasks',
            'u': 'open-url',
            '>': 'delegate',
            'L': 'load-template',
            'S': 'save-template',
            'l': 'load-search',
            's': 'save-search',
            '?': 'show-help',
            'm': 'open-manual',
            }
        self.editor_key_mapping = {
            '^C': 'cancel',
            '<escape>': 'cancel',
            '<left>': 'go-left',
            '<right>': 'go-right',
            '^U': 'del-to-bol',
            '<backspace>': 'del-left',
            '<del>': 'del-right',
            '<home>': 'go-bol',
            '<end>': 'go-eol',
            '<f6>': 'select-file',
            '<return>': 'submit-input',
            }
        self.completion_key_mapping = {
                '^C': 'comp-close',
                Key.ESCAPE: 'comp-close',
                Key.DOWN: 'comp-next',
                Key.TAB: 'comp-next',
                '^N': 'comp-next',
                Key.UP: 'comp-prev',
                '^P': 'comp-prev',
                Key.RETURN: 'comp-use',
            }
        self.functions = {
            'quit': self.do_quit,
            'nop': lambda: True,
            'refresh-screen': self.do_refresh_screen,
            'reload-tasks': self.do_reload_tasks,
            'search': self.do_start_search,
            'search-context': self.do_search_context,
            'search-project': self.do_search_project,
            'load-template': self.do_load_template,
            'save-template': self.do_save_template,
            'load-search': self.do_load_search,
            'save-search': self.do_save_search,
            'edit-task': self.do_edit_task,
            'edit-external': self.do_edit_task_external,
            'create-task': self.do_create_task,
            'jump-to': self.do_jump_to,
            'open-url': self.do_open_url,
            'toggle-tracking': self.do_toggle_tracking,
            'toggle-done': self.do_toggle_done,
            'toggle-hidden': self.do_toggle_hidden,
            'show-help': self.do_show_help,
            'delegate': self.do_delegate,
            'open-manual': utils.open_manual,
            'delete-task': self.do_delete,
            }

        self.search_bar = None
        self.status_bar = None
        self.help_bar = None
        self.tasks = None
        self.focus = []

        self.load_key_configuration()

    def main(self):
        # initialise colors
        if curses.has_colors() and self.use_colors:
            curses.use_default_colors()
            self.update_color_pairs()
        elif len(self.selection_indicator) == 0:
            self.selection_indicator = '>'

        self.tasks = TaskList(self)
        self.search_bar = SearchBar(self, 1, (0, 0))
        self.status_bar = StatusBar(self)
        self.help_bar = HelpBar(self)

        self.show_cursor(False)

        self.resize()
        self.update_tasks()
        self.paint()
        curses.doupdate()

        # general timeout is 1s
        self.screen.timeout(1000)
        then = datetime.datetime.now()

        self.set_term_title("pter")
        self.info('Welcome to pter')
        self.focus = [self.tasks]

        while not self.quit:
            source_changed = False
            must_repaint = False

            # detect changes of the sources
            for source in self.sources:
                if source.refresh():
                    logging.debug(f"Source {source} changed")
                    source.parse()
                    source_changed = True
                    
                    for panel in self.focus:
                        if not isinstance(panel, TaskEditor) or isinstance(panel, TaskCreator):
                            continue

                        if panel.task.source is source:
                            # beware! the currently edited task comes from this source
                            # let's see if we can still find it. if not? it has changed!
                            matching = [t for t in source.tasks if str(t) == str(panel.task.task)]
                            if len(matching) == 0:
                                self.error(tr("The task has changed in the background! Please copy your changes to clipboard and start over."))
                                panel.editor.read_only = True

            # detect the passing of midnight
            now = datetime.datetime.now()
            past_midnight = then.day != now.day
            then = now

            if source_changed or past_midnight:
                must_repaint = self.update_tasks()

            if must_repaint:
                logging.debug("Must repaint")
                self.paint(True)
            elif self.status_bar.is_expired() and not isinstance(self.focus[-1], JumpToIndexReader):
                logging.debug("Refreshing status bar")
                self.status_bar.paint()
            if len(self.focus) > 0:
                self.focus[-1].focus()

            curses.doupdate()

            key = Key.read(self.screen)

            if key == Key.RESIZE:
                self.resize()
                self.paint(True)
            elif self.focus[-1] is self.search_bar:
                self.search_bar.handle_key(key)
            elif isinstance(self.focus[-1], (HelpScreen, UserInput, RemappedInputLine, Selector)):
                self.focus[-1].handle_key(key)
            elif not key.special and str(key) in string.digits:
                self.do_jump_to(str(key))
            elif str(key) in self.key_mapping and self.key_mapping[str(key)] in self.functions:
                # clear status bar
                if len(self.status_bar.text) > 0:
                    self.info('')

                self.functions[self.key_mapping[str(key)]]()
            elif len(self.focus) > 0 and self.focus[-1].handle_key(key):
                # clear status bar
                if len(self.status_bar.text) > 0:
                    self.info('')

    def paint(self, clear=False):
        if clear:
            self.screen.erase()
        self.screen.noutrefresh()

        if len(self.focus) > 0 and isinstance(self.focus[-1], HelpScreen):
            self.focus[-1].paint(clear)
            self.help_bar.paint()
            return

        attr = self.color(common.SETTING_COL_NORMAL)
        try:
            self.screen.addstr(1, 0, "─"*self.size()[1], attr)
        except curses.error:
            pass
        self.screen.noutrefresh()

        self.tasks.paint()
        self.search_bar.paint()
        self.status_bar.paint()
        self.help_bar.paint()
        for panel in self.focus:
            if panel not in [self.tasks, self.search_bar]:
                panel.paint()

    def resize(self):
        height, width = self.size()

        if len(self.focus) > 0 and isinstance(self.focus[-1], HelpScreen):
            self.focus[-1].resize(height-1, width)
            self.focus[-1].move(0, 0)
        for panel in self.focus:
            if hasattr(panel, 'autoresize'):
                panel.autoresize()

        self.tasks.resize(height - 4, width)
        self.tasks.move(2, 0)
        self.search_bar.resize(width)
        self.status_bar.resize(1, width)
        self.status_bar.move(height-2, 0)
        self.help_bar.resize(1, width)
        self.help_bar.move(height-1, 0)

    def apply_search(self):
        current = self.tasks.selected_item
        self.tasks.tasks = [(task, source) for task, source in self.all_tasks
                                           if self.search.match(task)]
        self.update_sorting()
        self.tasks.rebuild_items()
        self.tasks.jump_to(current)
        self.tasks.scroll()

    def update_sorting(self, apply=True):
        new_sort_order = common.DEFAULT_SORT_ORDER
        for part in self.search.text.split(' '):
            if part.startswith('sort:'):
                new_sort_order = part.split(':', 1)[1]
                break
        if self.sort_order_txt != new_sort_order:
            self.sort_order_txt = new_sort_order
            self.sort_order = utils.build_sort_order(new_sort_order)
        if apply:
            self.tasks.tasks.sort(key=lambda t: utils.sort_fnc(t, self.sort_order))

    def update_tasks(self):
        current = self.tasks.selected_item
        self.all_tasks = []
        for source in self.sources:
            self.all_tasks += [(task, source) for task in source.tasks]

        self.apply_search()
        self.tasks.jump_to(current)
        return True

    def update_color_pairs(self):
        self.colors = {common.SETTING_COL_NORMAL: [Color(7, -1), Color(0, 7)],
                       common.SETTING_COL_INACTIVE: [Color(8), None],
                       common.SETTING_COL_ERROR: [Color(1), None],
                       common.SETTING_COL_PRI_A: [Color(1), None],
                       common.SETTING_COL_PRI_B: [Color(3), None],
                       common.SETTING_COL_PRI_C: [Color(6), None],
                       common.SETTING_COL_CONTEXT: [Color(4), None],
                       common.SETTING_COL_PROJECT: [Color(2), None],
                       common.SETTING_COL_HELP_TEXT: [Color(11, 8), None],
                       common.SETTING_COL_HELP_KEY: [Color(2, 8), None],
                       common.SETTING_COL_OVERFLOW: [Color(11), None],
                       common.SETTING_COL_OVERDUE: [Color(7, 1), Color(1, 7)],
                       common.SETTING_COL_DUE_TODAY: [Color(4), None],
                       common.SETTING_COL_DUE_TOMORROW: [Color(6), None],
                       common.SETTING_COL_TRACKING: [Color(7, 2), Color(2, 7)],
                       }
        if curses.has_colors() and self.use_colors:
            for colorname in self.conf[common.SETTING_GROUP_COLORS]:
                colpair = self.conf.color_pair(common.SETTING_GROUP_COLORS, colorname)

                if colpair is None:
                    continue
                fg, bg = colpair
                pairidx = 0

                if colorname.startswith('sel-'):
                    colorname = colorname[4:]
                    pairidx = 1

                if colorname not in self.colors:
                    logging.error(f"Invalid color name {colorname}.")
                    continue

                self.colors[colorname][pairidx] = Color(fg, bg)

            # register the color pairs
            for colorname in self.colors.keys():
                self.color(colorname, 0)
                self.color(colorname, 1)

            for key in self.conf[common.SETTING_GROUP_HIGHLIGHT]:
                hlcol = Color(*self.conf.color_pair(common.SETTING_GROUP_HIGHLIGHT, key))

                variant = 0
                if key.startswith('sel-'):
                    variant = 1
                    key = key[4:]

                if len(key.strip()) == 0:
                    continue

                if 'hl:' + key not in self.colors:
                    self.colors['hl:' + key] = [None, None]

                self.colors['hl:' + key][variant] = hlcol

                # and initialize the color
                self.color('hl:' + key, variant)

    def color(self, colorname, variant=0, default=None):
        """Return a color pair number for use with curses attributes
        variant can be 0/False (for normal) or 1/True (for selected text)
        If the color pair does not exist yet, it is registered, if possible."""

        if colorname is None:
            colorname = default or common.SETTING_COL_NORMAL

        if not self.use_colors or colorname not in self.colors:
            return 0

        if variant is True:
            variant = 1
        if variant is False:
            variant = 0
        if default is None:
            default = common.SETTING_COL_NORMAL

        colors = self.colors[colorname]
        if variant >= len(colors):
            logging.error(f"Programmer's error: color variant {variant} is invalid ({self.colors}).")
            raise ValueError(variant)

        color = colors[variant]
        if color is None:
            if variant > 0 and colors[0] is not None:
                color = colors[0].pair()
            else:
                color = self.colors[default][variant].pair()
        else:
            color = color.pair()

        default_variant = self.colors[default][variant]
        if default_variant is None and variant > 0:
            default_variant = self.colors[default][0]
        if default_variant is None:
            default_variant = self.colors[common.SETTING_COL_NORMAL][variant]

        if color[0] is None:
            color[0] = default_variant.fg
        if color[1] is None:
            color[1] = default_variant.bg
            if color[1] is None and self.colors[default][0] is not None:
                color[1] = self.colors[default][0].bg
            if color[1] is None:
                color[1] = self.colors[common.SETTING_COL_NORMAL][variant].bg

        color = (color[0], color[1])

        if color in self.color_cache:
            return curses.color_pair(self.color_cache[color])

        next_id = len(self.color_cache) + 1
        if next_id >= curses.COLOR_PAIRS:
            # sucks, we ran out of numbers
            logging.error(f"Too many color pairs defined. This terminal only supports {curses.COLOR_PAIRS} color pairs.")
            return 0

        try:
            curses.init_pair(next_id, *color)
            self.color_cache[color] = next_id
        except curses.error:
            self.color_cache[color] = 0
            return 0
        return next_id

    def load_key_configuration(self):
        logging.debug("Loading key configuration")
        for item in self.conf[common.SETTING_GROUP_KEYS]:
            target = None
            fnc = self.conf.get(common.SETTING_GROUP_KEYS, item, None)
            for mapping in [self.key_mapping, self.editor_key_mapping, self.completion_key_mapping]:
                if fnc in mapping.values():
                    target = mapping
            if target is None:
                if fnc in self.functions:
                    target = self.key_mapping
                else:
                    logging.warning(f"Cannot bind {item} to {fnc}: no such function")
                    continue

            logging.debug(f"Trying to map {item} to {fnc}")

            if len(item) == 1:
                target[item] = fnc
            elif len(item) == 2 and item[0] == '^':
                target[item.upper()] = fnc
            elif item in Key.SPECIAL:
                target[item] = fnc
            else:
                logging.error(f"Invalid key name '{item}' in configuration")

        to_exit = [k for k, fnc in self.key_mapping.items() if fnc == 'quit']
        if len(to_exit) == 0:
            logging.fatal("No key defined to exit pter.")
            raise RuntimeError("No key to exit")

    def info(self, text):
        self.status_bar.set_text(text)
        self.status_bar.paint(True)

    def error(self, text):
        self.status_bar.set_text(text, common.SETTING_COL_ERROR)
        self.status_bar.paint(True)

    def date_as_str(self, text, hint=''):
        if common.TF_ALL in self.human_friendly_dates or hint in self.human_friendly_dates:
            return utils.human_friendly_date(text)
        if not isinstance(text, str):
            return text.strftime(Task.DATE_FMT)
        return text

    def resolve_editor(self):
        candidates = [self.external_editor] \
                   + [os.getenv(name) for name in ['VISUAL', 'EDITOR']] \
                   + ['nano']
        for value in candidates:
            if value is None or len(value.strip()) == 0:
                continue
            editor = shutil.which(value)
            if editor is not None:
                return shlex.split(editor)

        return None

    def modify_task(self, taskline, fnc):
        """Try to minimize the chance that this task was changed in the background
        and apply fnc to it."""
        assert isinstance(taskline, TaskLine)
        task = utils.ensure_up_to_date(taskline.task)
        if task is not None:
            fnc(task)
            taskline.source.save(safe=self.safe_save)
            taskline.source.update_contexts_and_projects()
            self.search.update_sources(self.sources)
            self.update_tasks()
            self.tasks.jump_to(task)
            return True, task
        self.update_tasks()
        self.error(tr("Not changed: task was modified in the background"))
        return False, None

    def do_quit(self):
        self.quit = True

    def do_reload_tasks(self):
        self.update_tasks()

    def do_start_search(self):
        self.focus.append(self.search_bar)
        self.search_bar.previous_text = self.search_bar.text
        self.search_bar.cursor = len(self.search_bar.text)
        self.focus[-1].paint()

    def do_load_template(self):
        templates = utils.parse_templates()
        if len(templates) == 0:
            self.info(tr("There are no templates"))
            return

        none = tr("None")
        names = [none] + [name for name in sorted(templates.keys())]
        self.focus.append(Selector(self.tasks,
                                   names,
                                   lambda t: self.set_template(templates, none, t),
                                   title='Load Template',
                                   numbered=True))
        self.paint(True)

    def set_template(self, templates, none, template):
        if template == none:
            self.selected_template = None
        else:
            self.selected_template = templates.get(template, None)

    def do_save_template(self):
        if self.tasks.selected_item is None:
            self.error(tr("No task selected to create a template from"))
            return

        self.focus.append(UserInput(self.tasks,
                                    self._do_save_template,
                                    lambda: self.app.show_cursor(False),
                                    "Save Template"))
        self.paint(True)

    def _do_save_template(self, name):
        self.show_cursor(False)

        if len(name.strip()) == 0:
            self.error(tr("Not a valid name for a template"))
            return

        task = self.tasks.selected_item
        if task is None:
            self.error(tr("No task selected to create a template from"))
            return

        # create a copy of the selected task and remove creation date,
        # completion date and completion marker
        task = Task(str(task.task))
        task.is_completed = False
        task.creation_date = None
        task.completion_date = None

        templates = utils.parse_templates()
        templates[name] = str(task)
        utils.save_templates(templates)

    def do_load_search(self):
        searches = utils.parse_searches()
        if len(searches) == 0:
            self.info(tr("There are not named searches"))
            return

        names = [name for name in sorted(searches.keys())]
        self.focus.append(Selector(self.tasks,
                                   names,
                                   lambda s: self.set_named_search(searches, s),
                                   title='Load Search',
                                   numbered=True))
        self.paint(True)

    def set_named_search(self, searches, search):
        text = searches.get(search, None)
        if text is None:
            return
        self.set_search(text)

    def set_search(self, text):
        self.search.text = text
        self.search_bar.text = text
        self.search_bar.scroll()
        self.search.parse()
        self.apply_search()
        self.search_bar.paint(True)
        self.tasks.paint(True)

    def do_save_search(self):
        self.focus.append(UserInput(self.tasks,
                                    self._do_save_search,
                                    lambda: self.app.show_cursor(False),
                                    "Save Search"))
        self.paint(True)

    def _do_save_search(self, name):
        self.show_cursor(False)

        if len(name.strip()) == 0:
            self.error(tr("Not a valid name for a named search"))
            return

        searches = utils.parse_searches()
        searches[name] = self.search.text
        utils.save_searches(searches)

    def do_edit_task(self):
        if self.tasks.selected_item is None:
            self.error(tr("No task selected"))
            return
        self.focus.append(TaskEditor(self.tasks, self.tasks.selected_item))
        self.paint()

    def do_edit_task_external(self):
        task = self.tasks.selected_item
        if task is None:
            self.error(tr("No task selected"))
            return

        editor = self.resolve_editor()
        if editor is None:
            self.error(tr("Could not determine your external text editor"))
            return

        with tempfile.NamedTemporaryFile("w+t", encoding="utf-8", suffix='.txt') as fh:
            fh.write(str(task.task))
            fh.flush()
            with ShellContext(self.screen, True):
                subprocess.run(editor + [fh.name])

            # only actually apply changes when editing the 'extra' tags
            fh.flush()
            fh.seek(0)
            tasktext = fh.read()

        tasktext = utils.dehumanize_dates(utils.auto_task_id(self.sources, tasktext))
        if tasktext != str(task.task):
            self.modify_task(task, lambda t: t.parse(tasktext))

        self.paint(True)

    def do_create_task(self):
        self.focus.append(TaskCreator(self.tasks))
        self.paint()

    def do_jump_to(self, init=''):
        logging.debug(f"do_jump_to")
        if len(self.focus) == 0:
            return
        if not hasattr(self.focus[-1], 'jump_to'):
            logging.debug(f"{self.focus[-1]} does not have a 'jump_to' function")
            return
        
        self.focus.append(JumpToIndexReader(self, init))
        self.paint(True)

    def do_open_url(self):
        task = self.tasks.selected_item
        if task is None:
            self.info(tr("Nothing selected"))
            return

        task = task.task

        urls = []
        if task.description is not None:
            for match in common.URL_RE.finditer(task.description):
                if match.group(1) not in self.protos:
                    continue
                urls.append(match.group(0))

        urls = [url[1:-1] if url.startswith('<') and url.endswith('>') else url
                for url in urls if len(url) > 0]

        if len(urls) == 0:
            self.info(tr("No URLs found"))
            return

        if len(urls) > 1:
            self.focus.append(Selector(self.tasks,
                                       urls,
                                       lambda u: webbrowser.open(u),
                                       title="Open URL",
                                       numbered=True))
            self.paint(True)
        else:
            webbrowser.open(urls[0])

    def do_toggle_tracking(self):
        if self.tasks.selected_item is None:
            return
        success, task = self.modify_task(self.tasks.selected_item,
                                         lambda t: utils.toggle_tracking(t))
        if success:
            self.tasks.jump_to(task)
            self.tasks.paint_item(self.tasks.selected_item)

    def do_toggle_done(self):
        if self.tasks.selected_item is None:
            return
        success, _ = self.modify_task(self.tasks.selected_item,
                                      lambda t: utils.toggle_done(t, self.clear_contexts, self.reuse_recurring, self.safe_save))
        if success:
            self.tasks.paint(True)

    def do_toggle_hidden(self):
        if self.tasks.selected_item is None:
            return
        success, _ = self.modify_task(self.tasks.selected_item,
                                      lambda t: utils.toggle_hidden(t))
        if success:
            self.tasks.paint(True)

    def do_show_help(self):
        self.focus.append(HelpScreen(self))
        height, width = self.size()
        self.focus[-1].resize(height-1, width)
        self.focus[-1].move(0, 0)
        self.paint(True)

    def do_delegate(self):
        task = self.tasks.selected_item
        if task is None:
            return

        if len(self.delegation_marker) == 0:
            self.error(tr("No delegation marker defined"))
            return

        if self.delegation_marker in str(task.task).split(' '):
            self.do_delegation_action(task.task)
            return

        success, task = self.modify_task(task,
                                         lambda t: utils.delegate_task(t, self.delegation_marker))
        if success:
            self.do_delegation_action(task)
            self.tasks.jump_to(task)
            self.tasks.paint_item(self.tasks.selected_item)

    def do_delegation_action(self, task):
        utils.execute_delegate_action(task,
                                      self.delegate_to,
                                      self.delegation_marker,
                                      self.delegation_action)

    def do_refresh_screen(self):
        self.paint(True)

    def do_search_context(self):
        task = self.tasks.selected_item
        if task is None:
            return

        task = task.task
        contexts = [context for context in task.contexts
                    if context not in self.search.contexts]

        if len(contexts) == 0:
            return

        contexts.sort()
        if len(contexts) == 1:
            self.add_to_search('@'+contexts[0])
        else:
            self.focus.append(Selector(self.tasks,
                                       contexts,
                                       lambda c: self.add_to_search('@'+c),
                                       title="Select Context",
                                       numbered=True))
            self.paint(True)

    def do_delete(self):
        taskline = self.tasks.selected_item
        if taskline is None:
            return

        def _do_delete(t):
            t.todotxt.tasks.remove(t)

        can_perm_delete = self.last_perm_delete + self.perm_delete_timeout < datetime.datetime.now()

        if self.delete_is == common.DELETE_OPTION_DISABLED:
            return

        elif self.delete_is == common.DELETE_OPTION_PERMANENT and can_perm_delete:
            success, _ = self.modify_task(taskline, _do_delete)
            if success:
                self.last_perm_delete = datetime.datetime.now()
                self.info(tr("Task deleted"))
                self.tasks.paint(True)

        elif self.delete_is == common.DELETE_OPTION_TRASH:
            # first save the task in the trash
            trashfile = TodoTxt(self.trash_file)
            trashfile.parse()
            trashfile.tasks.append(taskline.task)
            trashfile.save()

            # attempt to delete the task
            success, _ = self.modify_task(taskline, _do_delete)
            if success:
                self.info(tr("Task moved to trash"))
                self.tasks.paint(True)
            else:
                # deletion was not okay, remove the task again from the trash
                trashfile.tasks.pop()
                trashfile.save()

    def add_to_search(self, text):
        if len(self.search.text) > 0:
            text = ' ' + text
        self.set_search(self.search.text + text)

    def do_search_project(self):
        task = self.tasks.selected_item
        if task is None:
            return

        task = task.task
        projects = [project for project in task.projects
                    if project not in self.search.projects]

        if len(projects) == 0:
            return

        projects.sort()
        if len(projects) == 1:
            self.add_to_search('+'+projects[0])
        else:
            self.focus.append(Selector(self.tasks,
                                       projects,
                                       lambda p: self.add_to_search('+'+p),
                                       title="Select Project",
                                       numbered=True))
            self.paint(True)


def add_title(panel, title, attr=0):
    assert isinstance(panel, Panel)
    _, w = panel.dim
    if (panel.border & Panel.BORDER_TOP) == 0:
        # no top border, no title
        return
    if (panel.border & Panel.BORDER_RIGHT) > 0:
        w -= 1
    if (panel.border & Panel.BORDER_LEFT) > 0:
        w -= 1

    w -= 2  # the indicators left and right
    label = title[:min(w, len(title))]
    if label != title:
        label = label[:-1] + '…'

    panel.win.addstr(0, 1, f"┤{label}├", attr)


def run_cursesui(args):
    logging.basicConfig(format="[%(levelname)s] %(message)s", filename=args.log_file)
    logging.getLogger().setLevel(args.log_level.upper())

    success = 0
    sources = utils.open_sources(args)
    
    if len(sources) == 0:
        success = -1
        print(tr("To start pter you must provide at least one todo.txt file. See --help for more information."),
              file=sys.stderr)
    else:
        search = Searcher('', False)
        search.update_sources(sources)

        window = CursesApplication(sources, configuration.get_config(args))
        exception = None

        try:
            window.run()
        except Exception as exc:
            callstack = ''.join(traceback.format_tb(exc.__traceback__))
            logging.fatal(f"Pter crashed with exception: {exc}\n{callstack}")
            exception = exc
            success = -3

        if args.log_level.lower() == 'debug' and exception is not None:
            raise exception

    return success

