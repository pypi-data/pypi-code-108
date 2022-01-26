#!/usr/bin/env python
"""\
@file   multistatus.py
@author Nat Goodspeed
@date   2020-03-19
@brief  Tk.Toplevel used to track multiple concurrent tasks.
"""

from future import standard_library
standard_library.install_aliases()
from contextlib import contextmanager
from pyng.tk import WINDOW_TITLE, get_root, tkvar, with_tkvars
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class Error(Exception):
    pass

# from http://effbot.org/zone/tkinter-autoscrollbar.htm
class AutoScrollbar(tk.Scrollbar):
    """
    Scrollbar that hides itself when not needed. Only works with grid.
    """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)

@with_tkvars
class Item(ttk.Frame):
    """
    Display label, message and progress bar for a given MultiStatus row key.

    +--------+---------------------------------------------------------------+
    + label  | Word-wrapped message text for this label                      |
    +        | [][][][][][][][][][]  (optional progress bar for this label)  |
    +--------+---------------------------------------------------------------+
    """
    def __init__(self, parent, row, label, message, total=None, start=0):
        """
        'parent' is the tkinter parent widget to contain this Frame subclass.

        'row' is the grid row within that parent widget.

        If 'label' has a string value, it will be displayed as the initial value.
        Thereafer assigning the 'label' attribute will update that field. But if
        'label' is initially passed as None, the label field will not be
        displayed, and subsequent assignments to the 'label' attribute will be
        ignored.

        'message' is displayed as the message field. Thereafter, assigning to
        the 'message' attribute will update that field.

        'total' is the total size of the progress bar. This is saved
        regardless of whether the progress bar is initially displayed or not.

        'start' is the initial value of the progress bar. If it is None, the
        progress bar is hidden; otherwise it must be a numeric value between 0
        and 'total', and the progress bar is displayed with that value.
        Thereafter, assigning to the 'current' attribute updates the progress
        bar: if you assign None, it hides the progress bar; otherwise the
        progress bar is displayed with the specified value. This intentionally
        diverges from the treatment of 'label'. It is expected that either
        every Item will display a label, or no Item will, and that the
        decision will be made when the MultiStatus is instantiated. By
        contrast, it is expected that some Items will display a progress bar
        while others will not, and that the set of Items displaying a progress
        bar will change at runtime.
        """
        ttk.Frame.__init__(self, master=parent)
        self.grid()
        self.label   = label
        self.message = message
        self.total   = total
        # Use a Message widget for its automatic text reflow:
        # http://effbot.org/tkinterbook/message.htm
        # Initial width is arbitrary; we just need to suppress Message's
        # default behavior of trying to preserve the specified aspect ratio.
        if label is not None:
            self.labelfld = tk.Message(master=self, textvariable=self._label, width=150)
            # The label field is in column 0. It spans 2 rows.
            self.labelfld.grid(row=0, column=0, rowspan=2, sticky='NSEW')
        self.messagefld  = tk.Message(master=self, textvariable=self._message, width=150)
        self.progressfld = ttk.Progressbar(master=self, orient='horizontal', length=150,
                                           mode='determinate', maximum=total)
        self.messagefld.grid(row=0, column=1, sticky='NSEW')
        self.progressfld.grid(row=1, column=1, sticky='NSEW')
        # The label field never stretches -- all stretching is done by the
        # message field and the progress bar.
        # https://mail.python.org/pipermail/python-list/2000-June/055758.html
        self.grid_columnconfigure(1, weight=1)
        # Empirically, *all three* of sticky='EW', configuring the column
        # weight and resetting the Message width on <Configure> are necessary
        # for a self-adjusting Message with proper text flow.
        # https://stackoverflow.com/a/8364895/5533635
        self.messagefld.bind("<Configure>",
                             lambda event: self.messagefld.config(width=event.width))

        # Because setting current affects our progress bar, defer this
        # assignment until we've defined the progress bar.
        self.current = start

    # implicitly called by assignment to current
    def set_current(self, current):
        # Since self.current is a property, use self.__dict__['current']
        # to reference the instance variable.
        self.__dict__['current'] = current
        if current is None:
            self.progressfld.grid_remove()
        else:
            self.progressfld.config(value=current)
            self.progressfld.grid()

    # implicitly called by referencing current
    def get_current(self):
        return self.__dict__['current']

    label   = tkvar(tk.StringVar)
    message = tkvar(tk.StringVar)
    # We need a property() to intercept setting to None as well as to numeric
    # values. You can set an IntVar to None, but that causes errors when you
    # try to get it.
    current = property(get_current, set_current)

    def set_color(self, color=''):
        """
        Change the background color for this entire Item, e.g. 'red' or
        'green'. Omit 'color' to revert to the default background color.
        """
        self['background'] = color

class MultiStatus(tk.Toplevel):
    """
    MultiStatus is an output-only scrolling Toplevel window whose content
    (within the scrolling Frame) is arranged more or less like this:

    +--------+---------------------------------------------------------------+
    + label0 | Word-wrapped message text for label0                          |
    +        | [][][][][][][][][][]  (optional progress bar for label0)      |
    +--------+---------------------------------------------------------------+
    + label1 | Word-wrapped message text for label1                          |
    +        | [][][][][][][][][][][][][]                                    |
    +--------+---------------------------------------------------------------+

    for as many rows as you care to provide, which is why the whole thing is
    wrapped in a scrolling Frame.

    The column displaying label0, label1 etc. may be suppressed.

    A progress bar may be displayed or suppressed for each row individually.

    Each row is associated with a unique dict key -- range(n) works. Each row
    may be individually updated by changing the label, message, color or
    progress bar for that key.
    """
    def __init__(self, title, labels=True, master=None):
        tk.Toplevel.__init__(self, master=master or get_root())
        self.title(title or WINDOW_TITLE)
        self.grid()

        # from http://effbot.org/zone/tkinter-autoscrollbar.htm
        vscrollbar = AutoScrollbar(self)
        vscrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)

        self.frame = ttk.Frame(master=self) #, yscrollcommand=vscrollbar.set)
        self.frame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        #vscrollbar.config(command=self.frame.yview)

        # make the frame expandable
        self.grid_rowconfigure(0, weight=1)

    def flush_display(self):
        self.update_idletasks()

    @contextmanager
    def atomic(self):
        """
        Within 'with ms.atomic():' block, make related changes without
        updating the display piecemeal. When you leave the block, display all
        the updates.
        """
        prev_flush = self.flush_display
        self.flush_display = lambda: None
        try:
            # execute body of 'with' block
            yield
            # Two things to note:
            # - At the end of the 'with' block, we call prev_flush(), not
            #   self.update_idletasks(). That handles the case of nested 'with
            #   atomic()' blocks. Only when we exit the last will we actually
            #   update.
            # - We call prev_flush() here, inside the try, rather than in the
            #   finally stanza. If the body of the 'with' statement blows up,
            #   we do want to restore self.flush_display(), but it might
            #   actually be bad to call it.
            prev_flush()
        finally:
            self.flush_display = prev_flush

def main():
    """
    Test code
    """
    from pyng.tk import get_root

    root = get_root()

    class SampleStatus(MultiStatus):
        def __init__(self, *args, **kwds):
            MultiStatus.__init__(self, *args, **kwds)
            self.item = Item(parent=self.frame, row=0, label='key', message='testing!',
                             total=100, start=33)
            self.grid()

    ss = SampleStatus(root, 'MultiStatus test')
    ss.flush_display()
    import time
    time.sleep(10)

if __name__ == "__main__":
    try:
        sys.exit(main(*sys.argv[1:]))
    except Error as err:
        sys.exit(str(err))
