#!c:/Python24/python
"""
    printwindow.py                   Nat Goodspeed
    Copyright (C) 2005               Nat Goodspeed

This module defines a class that you can use to open a temporary output window
into which to dump transient progress output, such as the voluminous output
from a C++ compilation. It doesn't deal with user input AT ALL; it merely
opens a scrolling Tkinter window. Because it's a "file-like object," you can
write() to it and even assign it to sys.stdout if you're so minded, which
means it will display all your 'print' output.

NRG 06/24/05
"""

from contextlib import contextmanager
try:
    # Python 3
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    # Python 2
    import Tkinter as tk
    from ScrolledText import ScrolledText
import os
from pyng.tk import get_root
import sys
# Tricky way to discover the name of the importing script!
import __main__

class PrintPanel(ScrolledText):
    """Make a ScrolledText widget that acts like a "file-like object". In
    particular, you can 'print' to an object of this class.
    """
    def __init__(self, *args, **kwds):
        # Don't allow any user interaction. Since the app isn't going to
        # respond to the mouse or keyboard in any way, it would only confuse
        # the user if we allowed him/her to edit the window contents.
        ScrolledText.__init__(self, state=tk.DISABLED, *args, **kwds)

    def get(self):
        """
        support retrieving text content as well
        """
        return ScrolledText.get(self, 1.0, tk.END)

    def write(self, text):
        # Because this widget is normally disabled, we have to re-enable it --
        # briefly -- if we want to add text to it.
        with self._enable():
            self._write(text)

    def _write(self, text):
        # Actually insert text into the Text widget
        self.insert(tk.END, text)

    @contextmanager
    def _enable(self):
        self.config(state=tk.NORMAL)
        try:
            yield
        finally:
            self.config(state=tk.DISABLED)
            # Force scrolling to the bottom of the window so that we can watch new
            # output arriving.
            self.see(tk.END)
            # We're not yet in mainloop(), because we don't call that until the
            # mainline script is done. Therefore we have to forcibly update the
            # display after every time we print more output.
            self.flush()

    def writelines(self, sequence):
        for line in sequence:
            self.write(line)

    def flush(self):
        self.master.update()

    def clear(self):
        with self._enable():
            self.delete(1.0, tk.END)

class ProgressPanel(PrintPanel):
    """
    This PrintPanel subclass adds support for '\r' overwriting the current
    line, as for old-skool TTY-type progress bars.
    """
    # The optimal approach, we suppose, would be to monitor BOTH '\n' and
    # '\r', and not send any text between the most recent '\n' and the most
    # recent '\r' we have in hand. But since (due to leaky abstraction) we can
    # get the Tkinter.Text widget to track the start of the current line:
    # https://www.daniweb.com/programming/software-development/threads/343340/tkinter-text-and-r
    # then we won't worry about '\n' at all. We'll just keep shoving text at
    # Text until we hit '\r', do the erase-current-line thing and carry on.

    # One potentially worrisome case would be a text source that ENDS each
    # progress line with '\r', pausing there until it produces the next line.
    # Our naive initial implementation would immediately erase the current
    # line; the user would see nothing but an empty line until the progress
    # bar is complete and '\n' is finally produced. But we'll worry about that
    # case when we hit it.
    def _write(self, data):
        # We override _write() so that base-class write() takes care of the
        # boilerplate of enabling, disabling, flushing and keeping the tail end
        # of the buffer visible.

        lines = data.split('\r')
        # Code below takes the form:
        # - write everything but the last chunk
        # - write the last chunk
        # But if data is in fact empty, lines is empty, and there is no last
        # chunk.
        if lines:
            # For every chunk of data EXCEPT what follows the last '\r'
            for line in lines[:-1]:
                PrintPanel._write(self, line)
                # leaky abstraction -- direct Text to erase the current line
                self.delete(tk.INSERT + ' linestart', tk.INSERT + ' lineend')
            # and for the last chunk...
            PrintPanel._write(self, lines[-1])

class PrintWindow(tk.Toplevel):
    def __init__(self, title=None, panel=PrintPanel, master=None):
        tk.Toplevel.__init__(self, master=master or get_root())
        # Change our title from the default 'tk' to the name of the main script.
        try:
            title = title or os.path.splitext(os.path.basename(__main__.__file__))[0]
        except AttributeError:
            # Interactively, __main__ has no __file__.
            pass
        else:
            # got a plausible title, set it
            self.title(title)

        # Our window has just one control, a PrintPanel.
        self.text = panel(master=self)
        self.text.pack()

        # display the window right away
        self.update_idletasks()

    def get(self):
        return self.text.get()

    # Forward file-like calls to our PrintPanel
    def write(self, *args, **kwds): return self.text.write(*args, **kwds)
    def writelines(self, *args, **kwds): return self.text.writelines(*args, **kwds)
    def flush(self, *args, **kwds): return self.text.flush(*args, **kwds)
    def clear(self, *args, **kwds): return self.text.clear(*args, **kwds)
