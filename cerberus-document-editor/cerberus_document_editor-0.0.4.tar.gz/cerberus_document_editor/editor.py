import sys
import time
import threading
import urwid
import json
from interrupt_handler import InterruptHandler

from .debug import log

DEFAULT_PALETTE=[
    ('header','white,bold', 'black', 'bold'),
    ('footer','white,bold', 'black', 'bold'),
    ('body','white', 'dark gray', ''),
    ('label','white,bold', 'dark gray', 'bold'),
    ('description','yellow,bold', 'dark gray'),
    ('edit', 'white', 'dark gray'),
    ('combo', 'light gray', 'black'),
    ('focus', 'black', 'white', 'bold'),
    ('stat', 'dark red,bold', 'dark gray'),
    ('indicator', 'black', 'light red', 'bold'),
    ('keymap_enable',   'white,bold',       'black'),
    ('keymap_disable',  'dark gray,bold',   'black'),
]

# Main Editor
# -- Page Stack (with Header)
# -- Show Top Page
# -- Serialize (JSON from Page)
class MainWindow:
    def __init__(self, name, palette=DEFAULT_PALETTE, pagestack=True):
        self.name = name
        self.stack = []
        self.palette = palette
        self.__pagestack = pagestack
        self.__modified = False
        self.__header_pagestack = urwid.Columns([], dividechars=1)
        self.__header = urwid.Pile([self.__header_title])  
        self.__footer_keymap = urwid.Columns([], dividechars=4)
        self.__footer = urwid.Pile([self.__footer_keymap])
        self.__body = urwid.AttrWrap(
            urwid.Filler(
                urwid.Padding(
                    urwid.Text(f":: {name} ::")
                    , "center"
                ), "middle"
            ), "body"
        )
        self.__view = urwid.Frame(
            urwid.AttrWrap(self.__body, 'body'),
            header=urwid.AttrWrap(self.__header, 'header'),
            footer=urwid.AttrWrap(self.__footer, 'footer')
        )

    @property
    def __header_title(self):
        title = f"{self.name.strip(' .').upper()}" 
        if len(self.stack) > 0:
            page = self.stack[0]
            title += f" - {page.name}"
        if self.__modified: title += " *"
        return urwid.Text(title, 'center')

    @property
    def __header_pagestack_contents(self):
        contents = [
            (urwid.Text('> ' + name), ('pack', 0, False)) if i > 0 else \
            (urwid.Text(name), ('pack', 0, False)) \
            for i, name, _ in [(i, f"[{_.name}]" if isinstance(_.name, int) else f"{_.name}", _) for i, _ in enumerate(self.stack)]
        ]
        return contents

    @property
    def __footer_keymap_contents(self):
        if len(self.stack) > 0:
            page = self.stack[-1]
            keymap = {'ctrl x': {'description': 'Exit', 'enabled': not page.is_modal}}
            keymap.update([(k, {'description': v.description, 'enabled': v.enabled}) for k, v in page.keymap.items()])
            contents = [(f"{'+'.join([_.title() for _ in k.split()])}: {v['description']}", v['enabled']) for k, v in keymap.items()]
            return [(urwid.AttrWrap(urwid.Text(_[0], 'center'), 'keymap_enable' if _[1] else 'keymap_disable'), ('pack', 0, False)) for _ in contents]
        return []

    def set_pagestack(self, enable=None):
        enable = enable or self.__pagestack
        self.__pagestack = enable
        if enable:
            self.__header = urwid.Pile([self.__header_title, self.__header_pagestack])  
        else:
            self.__header = urwid.Pile([self.__header_title])  
        self.__view.set_header(urwid.AttrWrap(self.__header, 'header'))
        
    def set_indicator(self, message=None):
        if message:
            self.__footer = urwid.Pile([urwid.AttrWrap(urwid.Text(message, wrap='ellipsis'), "indicator"), self.__footer_keymap])
            self.indicate_tick = time.time()
        elif len(self.__footer.widget_list) > 1:
            if self.indicate_tick + 0.01 > time.time():
                return # Block frequently undrawing command.
            self.__footer = urwid.Pile([self.__footer_keymap])
        else:
            return  # Not changed
        #self.loop.set_alarm_in(0, lambda ctx, user_data: self.__view.set_footer(urwid.AttrWrap(self.__footer, 'footer')))
        self.add_job(self.__view.set_footer, (urwid.AttrWrap(self.__footer, 'footer'),))

    def add_job(self, job, args=(), delay=0):
        if not hasattr(self, 'loop'):
            def pending_job(job, args, delay):
                while not hasattr(self, 'loop'): time.sleep(0.001)
                self.add_job(job, args, delay)
            threading.Thread(target=pending_job, args=(job, args, delay), daemon=True).start()
        else:
            self.loop.set_alarm_in(delay, lambda ctx, user_data: job(*args))

    def push(self, page):
        page.hwnd = self
        self.stack.append(page)
        self.redraw()

    def pop(self):
        if len(self.stack) > 1:
            page = self.stack.pop()
            self.stack[-1].on_page_result(page)
        self.redraw()

    def modified(self):
        self.__modified = True
        self.set_pagestack()

    @property
    def front_page(self):
        return json.loads(str(self.stack[0]))

    def redraw(self):
        if len(self.stack) > 0:
            page = self.stack[-1]
            page.on_update()
            self.__header_pagestack.contents = self.__header_pagestack_contents
            self.__footer_keymap.contents = self.__footer_keymap_contents
            self.set_pagestack()
            self.__body.w = page.on_draw()

    def input_handler(self, k):
        if len(self.stack):
            page = self.stack[-1]
            keymap = page.keymap
            if k in keymap:
                keymap[k].callback(page)
            elif k in ['ctrl x'] and not page.is_modal:
                if not self.__modified or not self.stack[-1].on_close():
                    self.destroy()
        else:
            self.destroy()

    def destroy(self, save_exit=True):
        while len(self.stack) > 1:
            self.stack[-1].close()
        self.save_exit = save_exit
        raise urwid.ExitMainLoop()

    def run(self, start_page):
        self.push(start_page)
        with InterruptHandler(lambda: True):
            self.loop = urwid.MainLoop(self.__view, self.palette,
                unhandled_input=self.input_handler, pop_ups=True)
            while True:
                try:
                    self.loop.run()
                    break
                except AssertionError as e:
                    if "rows, render mismatch" in e.args:
                        print('Assert in Loop', file=sys.stderr)
                    else:
                        raise e
                except Exception as e:
                    raise e
        if getattr(self, 'save_exit'):
            return self.front_page
