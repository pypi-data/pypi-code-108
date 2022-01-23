print('Loading tk functions...')

from omfit_classes.utils_base import *
from omfit_classes.utils_base import _streams

from utils_widgets import *
from utils_widgets import _defaultFont

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog

from idlelib.redirector import WidgetRedirector
from idlelib.percolator import Percolator
from idlelib.colorizer import ColorDelegator
from idlelib.search import SearchDialog


def get_entry_fieldbackground():
    fbg = ttk.Style().lookup('TEntry', 'fieldbackground')
    if fbg == '':
        fbg = 'white'
    return fbg


# ----------------
# ttk GUI subclasses
# ---------------
_Combobox = ttk.Combobox


class Combobox(_Combobox):
    """
    Monkey patch of ttk combobox to dynamically update its dropdown menu.
    The issue is ttk uses a tk Listbox that doesn't conform to the ttk theme for its dropdown (not cool ttk).
    This patch is modified from https://stackoverflow.com/questions/43086378/how-to-modify-ttk-combobox-fonts
    """

    def __init__(self, *args, **kwargs):
        #   initialisation of the combobox entry
        _Combobox.__init__(self, *args, **kwargs)
        #   "initialisation" of the combobox popdown
        self._handle_popdown_font()

    def _handle_popdown_font(self):
        """Handle popdown font
        Note: https://github.com/nomad-software/tcltk/blob/master/dist/library/ttk/combobox.tcl#L270
        """
        try:
            #   grab (create a new one or get existing) popdown
            popdown = self.tk.eval('ttk::combobox::PopdownWindow %s' % self)
            #   configure popdown font
            self.tk.call('%s.f.l' % popdown, 'configure', '-font', self['font'])
        except tk.TclError as _err:  # fails for old iris no_conda python, needed for old xarray unpickling
            pass

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget. Overridden!

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """
        #   default configure behavior
        result = self._configure('configure', cnf, kw)
        #   if font was configured - configure font for popdown as well
        if 'font' in kw or (cnf is not None and 'font' in cnf):
            self._handle_popdown_font()
        return result

    #   keep overridden shortcut
    config = configure


# ttk.Combobox = Combobox

# ----------------
# Tk GUI subclasses
# Note: all these classes are added to the `tk` Python module
# ---------------
# Tk supports two kinds of selection: CLIPBOARD and PRIMARY.
# Both selection buffers are capable of handling arbitrary data, but they default to simple ASCII text strings.
# When making a selection, standard Tk widgets (such as Text and Entry) select PRIMARY and highlight the selection.
# The widgets copy the selection to CLIPBOARD as well. This means that pasting text in Tk works in either of two ways:
#
# * Using the middle button, which copies the PRIMARY selection
#
# * Using the keyboard character `Control-v`, which copies the CLIPBOARD selection
#
# Tk widgets bind <<Copy>>, <<Cut>>, and <<Paste>> virtual events to class methods that manipulate the CLIPBOARD selection.
# The MainWindow generates virtual <<Copy>>, <<Cut>>, and <<Paste>> events when it sees the characters Control-c, Control-x, and Control-v, respectively.
# Venerable Unix applications tend to use PRIMARY, where you select text with mouse button 1 and paste with mouse button 3.


def _clipboard_get(self, selection=None, type=None):
    """
    :param selection: name of the selection (default 'PRIMARY', alternatively 'CLIPBOARD')

    :param type: type of the selection (default 'STRING', alternatively 'UTF8-SRTRING', 'FILE_NAME')
    """
    if type is None:
        type = os.environ.get('OMFIT_CLIPBOARD_TYPE', 'STRING')
    if selection is None:
        selection = os.environ.get('OMFIT_CLIPBOARD_SELECTION', 'PRIMARY')
    try:
        return self.clipboard_get(selection=selection, type=type)
    except tk.TclError:
        return self.clipboard_get(type=type)


def omfit_sel_handle(offset, length, selection=None, type=None):
    """
    This function must return the contents of the selection.
    The function will be called with the arguments OFFSET and LENGTH which allows the chunking of very long selections.
    The following keyword parameters can be provided: selection - name of the selection (default PRIMARY), type - type of the selection (e.g. STRING, FILE_NAME).

    :param offset: allows the chunking of very long selections

    :param length: allows the chunking of very long selections

    :param selection: name of the selection (default set by $OMFIT_CLIPBOARD_SELECTION)

    :param type: type of the selection (default set by $OMFIT_CLIPBOARD_TYPE)

    :return: clipboard selection
    """
    return _clipboard_get(OMFITaux['rootGUI'], selection, type)[int(offset) : int(offset) + int(length)]


tk.omfit_sel_handle = omfit_sel_handle


def _paste(self):
    # get the clipboard data, and replace all newlines with the literal string "\n"; also handle carriage returns.
    try:
        clipboard = _clipboard_get(self)
    except tk.TclError:
        return
    clipboard = clipboard.replace('\r\n', '\n')
    clipboard = clipboard.replace('\r', '\n')
    clipboard = clipboard.replace("\n", "\\n")

    # delete the selected text, if any
    try:
        start = self.index("sel.first")
        end = self.index("sel.last")
        self.delete(start, end)
    except tk.TclError:
        # nothing was selected, so paste doesn't need
        # to delete anything
        pass


_Toplevel = tk.Toplevel


class Toplevel(_Toplevel):
    """
    Patch tk.Toplevel to get windows with ttk themed backgrounds.
    """

    def __init__(self, *args, **kw):
        kw.setdefault('background', kw.pop('bg', ttk.Style().lookup('TFrame', 'background')))
        kw.setdefault('highlightbackground', ttk.Style().lookup('TFrame', 'background'))
        _Toplevel.__init__(self, *args, **kw)


tk.Toplevel = Toplevel

_Canvas = tk.Canvas


class Canvas(_Canvas):
    """
    Patch tk.Canvas to get windows with ttk themed backgrounds.
    """

    def __init__(self, *args, **kw):
        kw.setdefault('background', kw.pop('bg', ttk.Style().lookup('TFrame', 'background')))
        kw.setdefault('highlightbackground', ttk.Style().lookup('TFrame', 'background'))
        _Canvas.__init__(self, *args, **kw)


tk.Canvas = Canvas

_Menu = tk.Menu


class Menu(_Menu):
    """
    Patch tk.Menu to get windows with ttk themed backgrounds.
    """

    def __init__(self, *args, **kw):
        kw.setdefault('background', kw.pop('bg', ttk.Style().lookup('TFrame', 'background')))
        fg = kw.pop('fg', ttk.Style().lookup('TLabel', 'foreground'))
        if fg:  # robust to no specific color
            kw.setdefault('foreground', fg)
        kw.setdefault('font', OMFITfont('normal', 0))
        _Menu.__init__(self, *args, **kw)


tk.Menu = Menu

_Listbox = tk.Listbox


class Listbox(_Listbox):
    """
    Patch tk.Listbox to get windows with ttk themed backgrounds.
    """

    def __init__(self, *args, **kw):

        kw.setdefault('background', kw.pop('bg', get_entry_fieldbackground()))
        fg = kw.pop('fg', ttk.Style().lookup('TEntry', 'foreground'))
        if fg:  # robust to no specific color
            kw.setdefault('foreground', fg)
        kw.setdefault('font', OMFITfont('normal', 0))
        _Listbox.__init__(self, *args, **kw)


tk.Listbox = Listbox

_Entry = tk.Entry


class Entry(_Entry):
    def __init__(self, *args, **kw):
        _Entry.__init__(self, *args, **kw)
        self.bind(f'<{ctrlCmd()}-v>', lambda *args, **kw: _paste(self))
        self.bind(f'<{ctrlCmd()}-A>', self.select_all)

        self.changes = [""]
        self.steps = int()
        self.bind(f'<{ctrlCmd()}-z>', self.undo)
        self.bind(f'<{ctrlCmd()}-Z>', self.redo)
        self.bind('<Key>', self.add_changes)

    def select_all(self, event):
        '''Set selection on the whole text'''
        self.selection_range(0, tk.END)

    def undo(self, event=None):
        if self.steps != 0:
            self.steps -= 1
            self.delete(0, tk.END)
            self.insert(tk.END, self.changes[self.steps])

    def redo(self, event=None):
        if self.steps < len(self.changes):
            self.delete(0, tk.END)
            self.insert(tk.END, self.changes[self.steps])
            self.steps += 1

    def add_changes(self, event=None):
        if self.get() != self.changes[-1]:
            self.changes.append(self.get())
            self.steps += 1


tk.Entry = Entry

_Text = tk.Text


class Text(_Text):
    def __init__(self, *args, **kw):
        kw.setdefault('undo', tk.TRUE)
        kw.setdefault('maxundo', -1)
        kw.setdefault('background', kw.pop('bg', get_entry_fieldbackground()))
        fg = kw.pop('fg', ttk.Style().lookup('TEntry', 'foreground'))
        if fg:  # robust to no specific color
            kw.setdefault('foreground', fg)
        kw.setdefault('highlightbackground', ttk.Style().lookup('TFrame', 'background'))
        kw.setdefault('font', OMFITfont('normal', 0))
        _Text.__init__(self, *args, **kw)
        self.bind(f'<{ctrlCmd()}-v>', lambda *args, **kw: _paste(self))
        self.bind(f'<{ctrlCmd()}-A>', self.select_all)

    def select_all(self, event):
        self.tag_add(tk.SEL, "1.0", tk.END)
        # self.mark_set(tk.INSERT, "1.0")
        # self.see(tk.INSERT)
        return 'break'


tk.Text = Text


class _OneLineText(tk.Text):
    def __init__(self, master, **kw):
        percolator = kw.pop('percolator', False)

        kw.setdefault('background', kw.pop('bg', get_entry_fieldbackground()))
        kw.setdefault('highlightbackground', ttk.Style().lookup('TFrame', 'background'))
        tk.Text.__init__(self, master, **kw)

        self.config(height=1, undo=tk.TRUE, maxundo=-1, wrap='none')
        self.config(font=OMFITfont())

        tmp = [item for item in self.bindtags()]
        tmp.insert(2, 'post-class-bindings' + str(id(self)))
        tmp.insert(0, 'pre-class-bindings' + str(id(self)))
        self.bindtags(tuple(tmp))

        self.denyEnter()

        # highlight
        self.prc = Percolator(self)
        # CONDA aqua variant of tk on mac has 100% cpu when using the ColorDelegator here
        # Use `conda install -c smithsp tk=8.6.10=h1de35cc_2` if you encounter this issue
        self.flt = ColorDelegator()
        if percolator:
            self.set_highlight(True)

    def set_highlight(self, set=True):
        try:
            if set:
                self.prc.insertfilter(self.flt)
            else:
                self.prc.removefilter(self.flt)
        except Exception:
            pass

    def allowEnter(self):
        self.unbind_class('pre-class-bindings' + str(id(self)), "<Tab>")
        self.unbind_class('pre-class-bindings' + str(id(self)), "<Shift-Tab>")
        self.unbind_class('pre-class-bindings' + str(id(self)), "<ISO_Left_Tab>")
        self.unbind_class('post-class-bindings' + str(id(self)), "<Key>")

    def denyEnter(self):
        self.bind_class('pre-class-bindings' + str(id(self)), '<Tab>', lambda event=None: self.__denyTab__(None, action='next'))
        self.bind_class('pre-class-bindings' + str(id(self)), '<Shift-Tab>', lambda event=None: self.__denyTab__(None, action='prev'))
        try:
            self.bind_class(
                'pre-class-bindings' + str(id(self)), '<ISO_Left_Tab>', lambda event=None: self.__denyTab__(None, action='prev')
            )
        except tk.TclError:
            pass
        self.bind_class('post-class-bindings' + str(id(self)), '<Key>', self.__denyEnter__)

    def __denyTab__(self, event=None, action='next'):
        try:
            if action == 'next':
                self.tk_focusNext().focus()
            else:
                self.tk_focusPrev().focus()
            return 'break'
        except Exception:
            pass

    def __denyEnter__(self, event=None):
        if self.get("%s-1c" % tk.INSERT, "%s" % tk.INSERT) == '\n':
            self.delete("%s-1c" % tk.INSERT, "%s" % tk.INSERT)

    def set(self, string):
        self.delete(1.0, tk.END)
        return super().insert(1.0, str(string))

    def get(self, start=None, end=None):
        if start is None:
            start = 1.0
        if end is None:
            end = 'end -1 chars'
        return str(super().get(start, end))

    def icursor(self, index):
        self.see(index)


tk.OneLineText = _OneLineText


class _ReadOnlyEntry(tk.Entry):
    """
    Adapted from
    http://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
    """

    def __init__(self, *args, **kw):
        initial_text = kw.pop('initial_text', '')
        tk.Entry.__init__(self, *args, **kw)
        self.insert(0, initial_text)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")


tk.ReadOnlyEntry = _ReadOnlyEntry


class _ReadOnlyText(tk.Text):
    """
    From http://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
    (originally from http://tkinter.unpythonic.net/wiki/ReadOnlyText)
    """

    def __init__(self, *args, **kw):
        initial_text = kw.pop('initial_text', '')
        tk.Text.__init__(self, *args, **kw)
        self.insert('1.0', initial_text)
        self.redirector = WidgetRedirector(self)
        self._ReadOnlyInsert = self.insert
        self._ReadOnlyDelete = self.delete
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

    def set(self, string):
        self.insert = self.redirector.register("insert", self._ReadOnlyInsert)
        self.delete = self.redirector.register("delete", self._ReadOnlyDelete)
        try:
            self.delete(1.0, tk.END)
            return self.insert(1.0, str(string))
        finally:
            self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
            self.delete = self.redirector.register("delete", lambda *args, **kw: "break")


tk.ReadOnlyText = _ReadOnlyText


class _ScrolledText(tk.Text):
    """
    >> top=tk.Tk()
    >> tmp=_ScrolledText(top)
    >> tmp.pack()
    """

    def __init__(self, master=None, wrapButton='char', **kw):
        percolator = kw.pop('percolator', False)

        self.frame = ttk.Frame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.vbar = ttk.Scrollbar(self.frame)
        self.hbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)

        kw.update({'yscrollcommand': self.vbar.set})
        kw.update({'xscrollcommand': self.hbar.set})
        kw.setdefault('background', kw.pop('bg', get_entry_fieldbackground()))
        kw.setdefault('highlightbackground', ttk.Style().lookup('TFrame', 'background'))
        tk.Text.__init__(self, self.frame, **kw)
        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview

        # wrapping
        if wrapButton:

            def toggleWrap(event=None):
                if self.configure('wrap')[4].lower() != 'none':
                    self.configure(wrap='none')
                else:
                    self.configure(wrap=wrapButton)

            self.wrap = ttk.Button(self.frame, text='w', command=toggleWrap, style='flat.TButton')
            self.wrap.grid(row=1, column=1, sticky='nsew', rowspan=2)
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.hbar.grid(row=2, column=0, sticky='ew')
        self.grid(row=0, column=0, sticky='nswe', rowspan=2)

        self.configure(wrap=kw.get('wrap', 'none'))

        # Copy geometry methods of self.frame without overriding Text methods -- hack!
        text_meths = list(vars(tk.Text).keys())
        methods = list(vars(tk.Pack).keys()) + list(vars(tk.Grid).keys()) + list(vars(tk.Place).keys())
        methods = set(methods).difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

        # highlight
        self.prc = Percolator(self)
        # CONDA aqua variant of tk on mac has 100% cpu when using the ColorDelegator here
        # Use `conda install -c smithsp tk=8.6.10=h1de35cc_2` if you encounter this issue
        self.flt = ColorDelegator()
        if percolator:
            self.set_highlight(True)

        self.bind(f'<{ctrlCmd()}-c>', self._selown)
        self.bind(f'<{ctrlCmd()}-x>', self._selown)
        self.bind(f'<{ctrlCmd()}-f>', lambda event=None: self.search())
        self.bind('<F3>', lambda event=None: self.search_again_forward())
        self.bind('<Shift-F3>', lambda event=None: self.search_again_backward())

    def __str__(self):
        return str(self.frame)

    def set_highlight(self, set=True):
        try:
            if set:
                self.prc.insertfilter(self.flt)
            else:
                self.prc.removefilter(self.flt)
        except Exception:
            pass

    def configure(self, *args, **kw):
        if 'wrap' in kw:
            if kw['wrap'].lower() != 'none':
                self.hbar.grid_remove()
            else:
                self.hbar.grid()

        return super().configure(*args, **kw)

    def clear(self, what=None):
        if what is not None:
            while len(self.tag_ranges(what)):
                self.delete(self.tag_ranges(what)[-2], self.tag_ranges(what)[-1])
        else:
            self.delete('0.0', 'end')
        self.update_idletasks()

    def set(self, string):
        self.delete(1.0, tk.END)
        return super().insert(1.0, string)

    def get(self, start=None, end=None):
        if start is None:
            start = 1.0
        if end is None:
            end = 'end -1 chars'
        return super().get(start, end)

    def icursor(self, index):
        self.see(index)

    def _selown(self, event=None):
        self.selection_own()

    def search(self):
        self.tag_add(tk.SEL, "1.0", tk.END)
        from idlelib import searchengine

        engine = searchengine.get(self._root())
        if not hasattr(engine, "_searchdialog"):
            engine._searchdialog = SearchDialog(self._root(), engine)
        s = engine._searchdialog
        try:
            s.open(self)
            s.top.grab_release()
        except tk.TclError:
            pass
        s.top.wm_transient(self._root())
        self.tag_remove(tk.SEL, "1.0", tk.END)
        return 'break'

    def search_again_forward(self):
        engine = SearchDialog.SearchEngine.get(self._root())
        engine.backvar.set(False)
        SearchDialog.find_again(self)
        return 'break'

    def search_again_backward(self):
        engine = SearchDialog.SearchEngine.get(self._root())
        engine.backvar.set(True)
        SearchDialog.find_again(self)
        return 'break'


tk.ScrolledText = _ScrolledText


class _ScrolledReadOnlyText(_ReadOnlyText):
    def __init__(self, master=None, initial_text='', **kw):
        self.frame = ttk.Frame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.hbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hbar.grid(row=1, column=0, sticky='ew')

        kw.update({'yscrollcommand': self.vbar.set})
        kw.update({'xscrollcommand': self.hbar.set})
        _ReadOnlyText.__init__(self, self.frame, initial_text=initial_text, **kw)
        self.grid(row=0, column=0, sticky='nswe')
        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = list(vars(_ReadOnlyText).keys())
        methods = list(vars(tk.Pack).keys()) + list(vars(tk.Grid).keys()) + list(vars(tk.Place).keys())
        methods = set(methods).difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

        self.configure(wrap=self.configure('wrap')[4])


tk.ScrolledReadOnlyText = _ScrolledReadOnlyText


class _Treeview(ttk.Treeview):
    """
    Subclass of ttk.Treeview which is used in OMFIT
    provides some keybindings and defines tags (for colors and actions) for different OMFITobjects
    """

    def __init__(self, master, scrollup=None, **kw):
        self.frame = ttk.Frame(master)

        ttk.Treeview.__init__(self, self.frame, **kw)
        self.frame.bind_class("Treeview", "<space>", lambda event: None)
        self.frame.bind_class("Treeview", "<Return>", lambda event: None)
        self.frame.bind_class("Treeview", f'<{ctrlCmd()}-Left>', lambda event: None)
        self.frame.bind_class("Treeview", f'<{ctrlCmd()}-Right>', lambda event: None)
        self.frame.bind_class("Treeview", f'<{ctrlCmd()}-Up>', lambda event: None)
        self.frame.bind_class("Treeview", f'<{ctrlCmd()}-Down>', lambda event: None)
        self.frame.bind_class("Treeview", "<Prior>", lambda event: None)
        self.frame.bind_class("Treeview", "<Next>", lambda event: None)
        self.frame.bind_class("Treeview", "<Home>", lambda event: None)
        self.frame.bind_class("Treeview", "<End>", lambda event: None)
        self.frame.bind_class(f'<{ctrlCmd()}-Escape>', lambda event: None)
        self.frame.bind_class(f'<{ctrlCmd()}-Return>', lambda event: None)
        self.frame.bind_class('<Shift-Return>', lambda event: None)
        self.frame.bind_class("Treeview", "<Double-1>", lambda event: None)
        self.frame.bind_class("Treeview", "<Double-2>", lambda event: None)
        self.frame.bind_class("Treeview", "<Double-3>", lambda event: None)
        self.treeViewSelection = ()
        self.bind("<<TreeviewSelect>>", self.viewSelectionChange)

        tmp = [item for item in self.bindtags()]
        tmp.insert(2, 'post-class-bindings')
        tmp.insert(0, 'pre-class-bindings')
        self.bindtags(tuple(tmp))

        self.hScroll = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.vScroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        self.vScroll.grid(row=0, column=0, sticky='ns')
        self.grid(row=0, column=1, sticky='nswe')
        self.hScroll.grid(row=1, column=1, sticky='we')
        self.scrollup = scrollup
        self.configure(xscrollcommand=self.hScroll.set, yscrollcommand=self._scrollup)
        self.vScroll.config(command=self.yview)
        self.hScroll.config(command=self.xview)

        self.single_tags = []
        self.tags()

    def viewSelectionChange(self, event=None):
        for node in self.treeViewSelection:
            if self.exists(node):
                priorTags = self.item(node)["tags"]
                if len(priorTags) and priorTags[-1] == 'selected':
                    self.item(node, tags=tuple(priorTags[:-1]))
        self.treeViewSelection = self.selection()
        for node in self.treeViewSelection:
            priorTags = self.item(node)["tags"]
            if priorTags:
                self.item(node, tags=tuple(list(priorTags) + ['selected']))

    def _scrollup(self, *args, **kw):
        if self.scrollup is not None:
            self.scrollup(self)
        self.vScroll.set(*args, **kw)

    def tags(self):
        # deduce if the theme is dark
        fg = ttk.Style().lookup('.', 'foreground')
        if not len(fg):
            fg = 'BLACK'
        dark_theme = False
        if fg.startswith('#'):
            if (eval('0x' + fg[1:3]) / 255.0 + eval('0x' + fg[3:5]) / 255.0 + eval('0x' + fg[5:7]) / 255.0) / 3.0 > 0.5:
                dark_theme = True
        elif fg.lower() in list(map(lambda x: str(x).lower(), ['white', 'systemModelessDialogActiveText'])):
            dark_theme = True
        printd('Tree detected ' + ['light', 'dark'][dark_theme] + ' theme (fg=%s)' % fg)

        self.single_tags[:] = []
        # note to self: tags that appear first win over tags appearing later
        self.tag_configure('selected', background='#4B6886', foreground='white')

        self.tag_configure('other', background='PaleGreen2')

        self.tag_configure('OMFITmodule', background='gray25', foreground='white')
        self.tag_configure('MainSettings', background='gray40', foreground='white')
        self.tag_configure('OMFITtmp', background='gray40', foreground='white')
        self.tag_configure('OMFITnamespace', background='gray40', foreground='white')
        self.tag_configure('shotBookmarks', background='gray40', foreground='white')

        self.tag_configure('queryMatchFileContent', background='DarkOliveGreen3')
        self.tag_configure('queryMatchContent', background='DarkOliveGreen1')
        self.tag_configure('queryMatch', background='DarkOliveGreen2')

        self.tag_configure('modifyOriginal_readOnly', background='#ffb295', foreground='grey20')
        self.tag_configure('readOnly', background='#ffea87', foreground='grey20')
        self.tag_configure('modifyOriginal', background='#fcffb7', foreground='grey20')

        self.tag_configure('dynaLoad', font=OMFITfont(slant='italic'))

        self.tag_configure('MDSactive', foreground='indianRed1')

        if dark_theme:
            self.tag_configure('OMFITtree', foreground='dodgerblue')
            self.tag_configure('OMFITcollection', foreground='dodgerblue')
        else:
            self.tag_configure('OMFITtree', foreground='mediumblue')
            self.tag_configure('OMFITcollection', foreground='mediumblue', background='azure')

        self.tag_configure('OMFITgeqdsk', foreground='darkorange')
        self.tag_configure('OMFITaeqdsk', foreground='darkorange')
        self.tag_configure('OMFITmeqdsk', foreground='darkorange')
        self.tag_configure('OMFITseqdsk', foreground='darkorange')
        if dark_theme:
            self.tag_configure('OMFITsettings', foreground='maroon3')
            self.tag_configure('OMFITnamelist', foreground='maroon3')
            self.tag_configure('NamelistFile', foreground='maroon3')
            self.tag_configure('NamelistName', foreground='maroon1')
            self.tag_configure('SettingsName', foreground='maroon1')
        else:
            self.tag_configure('OMFITsettings', foreground='maroon4')
            self.tag_configure('OMFITnamelist', foreground='maroon4')
            self.tag_configure('NamelistFile', foreground='maroon4')
            self.tag_configure('NamelistName', foreground='maroon2')
            self.tag_configure('SettingsName', foreground='maroon2')
        self.tag_configure('OMFITnc', foreground='darkgreen')
        self.tag_configure('OMFITncDataset', foreground='darkgreen')
        self.tag_configure('OMFITGPECnc', foreground='chartreuse2')
        self.tag_configure('OMFITGPECbin', foreground='chartreuse3')
        self.tag_configure('OMFITGPECascii', foreground='chartreuse4')
        self.tag_configure('list', foreground='forestgreen')
        self.tag_configure('tuple', foreground='limegreen')
        self.tag_configure('ndarray', foreground='chartreuse4')
        self.tag_configure('DataArray', foreground='DarkOliveGreen4')
        self.tag_configure('Dataset', foreground='dark green')
        self.tag_configure('OMFITdataset', foreground='dark green')
        self.tag_configure('OMFITncDataset', foreground='dark green')
        self.tag_configure('OMFITprofiles', foreground='dark green')
        self.tag_configure('DataFrame', foreground='dark green')
        self.tag_configure('OMFITlazyLoad', foreground='gray30')
        self.tag_configure('Series', foreground='forestgreen')
        self.tag_configure('int', foreground='gold4')
        self.tag_configure('int32', foreground='gold4')
        self.tag_configure('bool', foreground='cyan4')
        self.tag_configure('float', foreground='red2')
        self.tag_configure('float32', foreground='red2')
        self.tag_configure('float64', foreground='red2')
        self.tag_configure('complex', foreground='SlateBlue4')
        self.tag_configure('instancemethod', foreground='sienna4')
        self.tag_configure('method', foreground='sienna4')
        self.tag_configure('function', foreground='sienna4')
        self.tag_configure('builtin_function_or_method', foreground='sienna4')
        self.tag_configure('method-wrapper', foreground='sienna4')
        if dark_theme:
            self.tag_configure('str', foreground='deep sky blue')
        else:
            self.tag_configure('str', foreground='dodgerblue')
        self.tag_configure('OMFITini', foreground='dark slate blue')
        self.tag_configure('OMFITerror', background='indianRed1')
        self.tag_configure('OMFITexpression', font=OMFITfont(weight='bold'))
        self.tag_configure('OMFITiterableExpression', font=OMFITfont(weight='bold'))

        from extras.graphics.colors import tk_colors

        for k in tk_colors:
            self.tag_configure('FG_' + re.sub(' ', '_', k), foreground=k)
            self.tag_configure('BG_' + re.sub(' ', '_', k), background=k)
        self.tag_configure('FG_', foreground='black')
        self.tag_configure('BG_', background='white')

    def force_selection(self, event=None):
        # focus and selection are two different things
        # focus is what makes things happen, whereas selection is the highligting
        # the purpose of force_selection is to make the two coincide

        if event is not None:
            if isinstance(event, str):
                focus = event
            else:
                focus = self.identify_row(event.y)
        else:
            focus = self.focus()

        # this logic is here because different versions of TK require different string escaping
        # and here we try to automatically detect which one is which
        try:
            self.selection_set(tkStringEncode(focus))
        except tk.TclError as _excp:
            try:
                os.environ['OMFIT_ESCAPE_TK_SPACES'] = str(abs(int(os.environ.get('OMFIT_ESCAPE_TK_SPACES', '1')) - 1))
                self.selection_set(tkStringEncode(focus))
            except tk.TclError:
                os.environ['OMFIT_ESCAPE_TK_SPACES'] = str(abs(int(os.environ.get('OMFIT_ESCAPE_TK_SPACES', '1')) - 1))
                raise _excp

        if not len(focus):
            self.selection_clear()

        self.focus(focus)
        self.see(focus)

        self.update_idletasks()

        return focus


tk.Treeview = _Treeview

_last_email_to = {}


class _email_widget(tk.Toplevel):
    r"""
    A widget for sending an email.

    :param parent: parent tkInter widget

    :param fromm: email of the submitter

    :param to: email of the receiver (string of comma separated addresses)

    :param subject: subject of the email

    :param message: email message

    :param attachments: list of path to files

    :param prompt: label to be displayed

    :param lock_from: do not allow editing of from field

    :param lock_to: do not allow editing of to field

    :param lock_subject: do not allow editing of subject field

    :param title: title to display in the email window

    :param use_last_email_to: re-use the same email addresses as the last email that was sent

    :param quiet: print confirmation message on send

    :param \**kw: keywords passed to tkInter frame containing this widget

    Example usage from within OMFIT:

    eml = tk.email_widget(parent=OMFITaux['rootGUI'])
    eml.wait_window(eml)
    """

    def __init__(
        self,
        parent,
        fromm='',
        to='',
        cc='',
        subject='',
        message='',
        attachments=[],
        prompt=None,
        lock_from=False,
        lock_to=False,
        lock_cc=False,
        lock_subject=False,
        title='Send email',
        use_last_email_to=False,
        quiet=False,
        **kw,
    ):
        tk.Toplevel.__init__(self, parent, **kw)
        self.withdraw()
        self.transient(parent)
        self.wm_title(title)

        self.use_last_email_to = use_last_email_to
        self.quiet = quiet
        self.sent = False

        # handle Nones
        if not isinstance(fromm, str):
            fromm = ''
        if isinstance(to, list):
            to = ','.join(map(str, to))
        if not isinstance(to, str):
            to = ''
        if not isinstance(cc, str):
            cc = ''
        if not isinstance(subject, str):
            subject = ''
        if not isinstance(message, str):
            message = ''
        if not isinstance(attachments, list):
            attachments = list(map(str, list(attachments)))

        # re-use last to addresses
        if use_last_email_to and use_last_email_to in _last_email_to:
            to = _last_email_to[use_last_email_to]

        # from
        row = 0
        ttk.Label(self, text='From:').grid(row=row, column=0, sticky=tk.W)
        if lock_from:
            _from = _ReadOnlyEntry(self, initial_text=fromm)
        else:
            _from = tk.Entry(self)
            _from.insert(0, fromm)
        _from.grid(row=row, column=1, sticky=tk.E + tk.W)
        self._from = _from

        # to
        row += 1
        ttk.Label(self, text='To:').grid(row=row, sticky=tk.W)
        if isinstance(to, (list, tuple)):
            to = ','.join(to)
        if lock_to:
            _to = _ReadOnlyEntry(self, initial_text=to)
        else:
            _to = tk.Entry(self)
            _to.insert(0, to)
        _to.grid(row=row, column=1, sticky=tk.E + tk.W)
        self._to = _to

        # cc
        row += 1
        ttk.Label(self, text='CC:').grid(row=row, sticky=tk.W)
        if isinstance(cc, (list, tuple)):
            cc = ','.join(cc)
        if lock_cc:
            _cc = _ReadOnlyEntry(self, initial_text=cc)
        else:
            _cc = tk.Entry(self)
            _cc.insert(0, cc)
        _cc.grid(row=row, column=1, sticky=tk.E + tk.W)
        self._cc = _cc
        # subject
        row += 1
        ttk.Label(self, text='Subject:').grid(row=row, sticky=tk.W)
        if lock_subject:
            _subject = _ReadOnlyEntry(self, initial_text=subject)
        else:
            _subject = tk.Entry(self)
            _subject.insert(0, subject)
        _subject.grid(row=row, column=1, sticky=tk.E + tk.W)
        self._subject = _subject

        # attachments
        self._attachments = []
        for k, attachment in enumerate(attachments):
            if not os.path.exists(attachment):
                printe(attachment + ' does not exist')
                continue
            row += 1
            ttk.Label(self, text='Attachment [%d]:' % (k + 1)).grid(row=row, sticky=tk.W)
            _attachment = _ReadOnlyEntry(self, initial_text=os.path.split(attachment)[1])
            _attachment.grid(row=row, column=1, sticky=tk.E + tk.W)
            self._attachments.append(attachment)

        # send button
        bt = ttk.Button(self, text='Send email', command=self.send_email)
        bt.grid(row=0, column=2, rowspan=row + 1, sticky=tk.E + tk.W + tk.N + tk.S)

        # message
        row += 2
        if prompt:
            ttk.Label(self, text=prompt, justify=tk.LEFT).grid(row=row, columnspan=2, sticky=tk.W)
        st = _ScrolledText(self, wrap='word')
        st.insert(1.0, message)
        row += 1
        st.grid(row=row, columnspan=3, sticky=tk.E + tk.W + tk.N + tk.S)
        self.st = st

        self.grid_columnconfigure(1, weight=1)

        tk_center(self, parent)
        self.deiconify()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def send_email(self):
        from utils import send_email

        if not self.validate_inputs():
            return

        send_email(
            to=encode_ascii_ignore(self._to.get()),
            cc=encode_ascii_ignore(self._cc.get()),
            fromm=encode_ascii_ignore(self._from.get()),
            subject=encode_ascii_ignore(self._subject.get()),
            message=encode_ascii_ignore(self.st.get()),
            attachments=self._attachments,
        )

        self.sent = True
        if not self.quiet:
            printi('Email sent to: ' + encode_ascii_ignore(self._to.get()))

        # store what emails were used
        if self.use_last_email_to:
            _last_email_to[self.use_last_email_to] = encode_ascii_ignore(self._to.get())

        self.destroy()

    def validate_inputs(self):
        _from = self._from.get().strip()
        _to = self._to.get().strip()
        _cc = self._cc.get().strip()
        _subject = self._subject.get().strip()
        _message = self.st.get('1.0', tk.END).strip()

        valid = True
        for field in ['From', 'To', 'Subject', 'Message']:
            if not eval('_' + field.lower()):
                dialog(
                    title='Invalid `' + field + '` Field', message='The `' + field + '` field cannot be blank', icon='error', answers=['Ok']
                )
                valid = False
                break
        for field in ['From', 'To', 'CC']:
            if eval('_' + field.lower()) and not is_email(eval('_' + field.lower())):
                dialog(
                    title='Invalid `' + field + '` Field',
                    message='The `' + field + '` field must be a valid email address',
                    icon='error',
                    answers=['Ok'],
                )
                valid = False
                break

        return valid


tk.email_widget = _email_widget


class _ConsoleTextGUI(_ScrolledText):
    '''A Tkinter Text widget that provides a scrolling display of console stderr and stdout.'''

    class Redirector(object):
        '''A class for redirecting stdout and stderr to this Text widget'''

        def __init__(self, text_area, tag='STDOUT'):
            self.text_area = text_area
            self.tag = tag

        def write(self, string):
            self.text_area.write(string, self.tag)

        def __getattr__(self, attr):
            return getattr(self.text_area, attr)

    def __init__(
        self,
        parent=None,
        name='OMFIT command box',
        cnf={},
        mirror=False,
        OMFITcwd=None,
        OMFITpythonTask=None,
        OMFITpythonGUI=None,
        OMFITx=None,
        **kw,
    ):
        '''See the __init__ for Tkinter.Text for most of this stuff.'''
        _ScrolledText.__init__(self, parent, wrapButton=False)
        self.config(undo=tk.TRUE, maxundo=-1)
        self.config(font=OMFITfont(_defaultFont.get('weight2', ''), _defaultFont.get('size2', 0), 'Courier'))
        self.config(*cnf, **kw)
        self.config(state=tk.NORMAL)
        self.mirror = mirror

        # store these infos, necessary for execution
        self.OMFITcwd = OMFITcwd
        self.OMFITpythonTask = OMFITpythonTask
        self.OMFITpythonGUI = OMFITpythonGUI
        self.OMFITx = OMFITx

        # execution namespace
        self.namespace = None
        self.name = name

        # behaviour
        self.started = False
        self.follow = True
        self.show = True
        self.clearTextOnExecution = False

        # buffered writing
        self.buffer = ''
        self.last_tag = None
        self.write_alarm = 0
        self.lag = 10  # ms time
        self.block = 100  # ms time
        self.time_last_write = 0

        # tags & streams
        for k in _streams.tags:
            self.tag_configure(k, foreground=_streams.tags[k][0])

        # history
        self.history = []
        self.histPtr = -1

        # override default bindings
        for k in [f'<{ctrlCmd()}-Return>', '<Tab>', '<Shift-Tab>', '<ISO_Left_Tab>', f'<{ctrlCmd()}-f>']:
            try:
                self.bind_class('Text', k, 'break')
            except tk.TclError:
                pass

        self.q = streams_q

        # bindings
        self.bind('<<retrigger_tab_popup>>', self._process_tab)

    def isatty(self):
        return False

    def execute(self, event=None, f9f=False):
        if not f9f:
            tmp = self.get('1.0', 'end')
        else:
            try:
                tmp = self.selection_get()
            except Exception:
                tmp = self.get("insert linestart", "insert lineend")

        # find leftmost significant character
        exe = tmp.split('\n')
        for k, line in enumerate(exe):
            chtmp = len(re.sub(r'^(\s*).*', r'\1', line))
            if k == 0:
                spaces = chtmp
            if len(line) - chtmp:
                spaces = min(spaces, chtmp)

        # remove spaces from all other lines
        exe = [line[spaces:] for line in exe]
        exe = '\n'.join(exe)

        if not f9f:
            if not len(self.history) or tmp != self.history[-1]:
                self.history.append(tmp)
                self.histPtr = len(self.history)
            if self.clearTextOnExecution:
                self.clear()

        def GlobLoc_tk():
            filename = self.OMFITcwd + os.sep + self.name
            with open(filename, 'wb') as f:
                f.write(exe.encode('utf-8'))

            # Automatically determine if this is a GUI script
            # by checking if OMFITx. functions relevant to GUI
            # are used in it.
            tmp = '\n'.join([line.split('#')[0] for line in exe.split('\n')])
            match_GUI = False
            for item in list(map(lambda x: x.__name__, OMFITaux['OMFITxGUI_functions'])):
                if 'OMFITx.' + item in tmp:
                    match_GUI = True
                    break

            if match_GUI:
                py = self.OMFITpythonGUI(filename, modifyOriginal=True)
            else:
                py = self.OMFITpythonTask(filename, modifyOriginal=True)

            if not f9f:
                # make a backup copy of the script
                py.modifyOriginal = False
                py._create_backup_copy()
                py.modifyOriginal = True

            return py.run(_relLoc=self.namespace, _OMFITscriptsDict=False, _OMFITconsoleDict=True, noGUI=None)

        def do_exec_delay(*args, **kwargs):
            try:
                self.OMFITx.manage_user_errors(GlobLoc_tk)
            finally:
                self.event_generate("<<update_treeGUI>>")
                if os.path.exists(self.OMFITcwd):
                    os.chdir(self.OMFITcwd)

        self.after(1, do_exec_delay)

        return "break"

    def _histUP(self, event=None):
        self.delete('1.0', 'end')
        if self.tag_ranges('HIST'):
            self.delete(self.tag_ranges('HIST')[0], self.tag_ranges('HIST')[1])
        if self.histPtr >= 0:
            self.histPtr -= 1
        if self.histPtr >= 0 and self.histPtr <= (len(self.history) - 1):
            self.insert('insert', self.history[self.histPtr].strip('\n'), 'HIST')
        self.see('insert')

    def _histDOWN(self, event=None):
        self.delete('1.0', 'end')
        if self.tag_ranges('HIST'):
            self.delete(self.tag_ranges('HIST')[0], self.tag_ranges('HIST')[1])
        if self.histPtr <= (len(self.history) - 1):
            self.histPtr += 1
        if self.histPtr >= 0 and self.histPtr <= (len(self.history) - 1):
            self.insert('insert', self.history[self.histPtr].strip('\n'), 'HIST')
        self.see('insert')

    def start(self, use_queue=False):
        if self.started:
            return

        if use_queue:
            for k in _streams.tags:
                _streams[k] = qRedirector(k)
            sys.stdout = _streams['STDOUT']
            sys.stderr = _streams['STDERR']
            self._readq()
        else:
            for k in _streams.tags:
                _streams[k] = self.Redirector(self, k)
            sys.stdout = _streams['STDOUT']
            sys.stderr = _streams['STDERR']

        self.started = True

    def stop(self):
        if not self.started:
            return

        _streams.setDefaults()
        sys.stdout = _streams['STDOUT']
        sys.stderr = _streams['STDERR']

        if self.write_alarm:
            self.after_cancel(self.write_alarm)
            self.write_alarm = None

        self.started = False

    def interactive(self):
        self.set_highlight(True)
        global_event_bindings.add('COMMAND BOX: execute line or selection', self, '<F9>', lambda event=None: self.execute(None, f9f=True))
        global_event_bindings.add('COMMAND BOX: execute', self, f'<{ctrlCmd()}-Return>', self.execute)
        global_event_bindings.add('COMMAND BOX: move history up', self, f'<{ctrlCmd()}-u>', self._histUP)
        global_event_bindings.add('COMMAND BOX: move history down', self, f'<{ctrlCmd()}-d>', self._histDOWN)
        global_event_bindings.add('COMMAND BOX: tab', self, '<Tab>', self._process_tab)
        global_event_bindings.add('COMMAND BOX: un-tab', self, '<Shift-Tab>', self._del_tab)
        global_event_bindings.add('COMMAND BOX: un-tab (alternative)', self, '<ISO_Left_Tab>', self._del_tab)
        global_event_bindings.add('COMMAND BOX: API reference', self, f'<{ctrlCmd()}-h>', lambda event=None: help())

    def _readq(self, event=None):
        if self.write_alarm:
            self.after_cancel(self.write_alarm)
            self.write_alarm = None

        text = None
        k = 0
        while not self.q.empty() or (time.time() - self.time_last_write) > (self.block / 1000.0):
            if not self.q.empty():
                text, tag = self.q.get(block=False, timeout=0)
                if k == 0 or tag == self.last_tag:
                    self.buffer += text.decode('utf-8', errors='ignore')
                    self.last_tag = tag
                    k += 1
                else:  # change of tag
                    k = None
                    break
            else:
                break

        if self.buffer:
            self._write(self.buffer, self.last_tag)
            self.buffer = ''

        self.time_last_write = time.time()
        if k is None:  # change of tag
            self._write(text, tag)
            self.last_tag = tag
            self.write_alarm = self.after(0, self._readq)
        else:
            self.write_alarm = self.after(self.lag, self._readq)

    def write(self, val=None, tag='STDOUT'):
        # note: setting val=None forces a flush of the buffer
        if self.write_alarm:
            self.after_cancel(self.write_alarm)
            self.write_alarm = None
        if val is None or self.last_tag != tag or (time.time() - self.time_last_write) > (self.block / 1000.0):
            if len(self.buffer):
                self._write(self.buffer, self.last_tag)
                self.buffer = ''
            self.time_last_write = time.time()
        if val is not None:
            self.last_tag = tag
            try:
                self.buffer += val.decode('utf-8', errors='ignore')
            except Exception:
                self.buffer += str(val).encode('utf-8').decode('utf-8', errors='ignore')
        self.write_alarm = self.after(self.lag, self.write)

    def _write(self, val, tag='STDOUT'):
        if tag in ['PROGRAM_OUT', 'PROGRAM_ERR']:
            val = re.sub('\r\n', '\n', val)

        # handle return lines
        cr_sections = val.split('\r')
        if len(cr_sections) > 3:
            cr_sections = [cr_sections[0]] + [x for x in cr_sections[1:-1] if '\n' in x] + [cr_sections[-1]]

        for k, cr_section in enumerate(cr_sections):
            self.insert('end', cr_section, tag)
            if not self.follow:
                self.delete('1.0', 'end - 1000000 lines')
            else:
                self.delete('1.0', 'end - 100000 lines')
                self.see('end-1c linestart')
            if (k + 1) < len(cr_sections):
                self.delete("end-1c linestart", "end")
                self.insert('end', '\n', tag)
        if self.mirror and tag not in ['DEBUG']:
            sys.__stdout__.write(val)
        self.update_idletasks()

    def _make_popup_menu_jedi(self, event):
        def do_scriptpopup(event):
            # Determine the pixel location of the typing cursor
            x0 = self.winfo_rootx()
            dx = self.winfo_width()
            y0 = self.winfo_rooty()
            dy = self.winfo_height()

            where_am_i = self.index(tk.INSERT)
            found = False
            for r in range(0, dx, 5):
                for c in range(0, dy, 5):
                    where = self.index(f'@{r},{c}')
                    if str(where) == str(where_am_i):
                        found = True
                        break
                if found:
                    break

            scriptpopup.post(x0 + r, y0 + c)
            scriptpopup.focus_set()
            return 'break'

        scriptpopup = tk.Menu(tearoff=0)
        names = []
        names_params = []
        completions = []
        completions_params = []
        for c in self.tab_comp:
            name = c.name
            if c.complete and c.complete[-1] == '(':
                name += '('
            if '=' in name:
                names_params.append(name)
                completions_params.append(c.complete)
            else:
                names.append(name)
                completions.append(c.complete)

        for name, completion in list(zip(names_params + names, completions_params + completions))[:15]:

            def complete_i(i=completion):
                scriptpopup.unpost()
                self.insert("insert", i)
                self.focus()
                return 'break'

            scriptpopup.add_command(label=name, command=complete_i)

        def popup_process_event(event=None):
            if event.char == '??':
                return 'break'

            if event.keysym == 'BackSpace':
                scriptpopup.unpost()
                self.delete('insert-1c', 'insert')
                self.focus()
                self.after(1, lambda: self.event_generate("<<retrigger_tab_popup>>"))
                return 'break'

            if event.keysym == 'Escape':
                scriptpopup.unpost()
                self.focus()
                return 'break'
            if not event.char:
                return
            import string

            if event.char not in string.ascii_letters + string.digits + r'!@#$%^&*()-_=+[{]}\|;:\'",<.>/?`~\]':
                return

            self.insert("insert", event.char)
            scriptpopup.unpost()
            self.focus()
            if event.char:
                self.after(1, lambda: self.event_generate("<<retrigger_tab_popup>>"))
            return 'break'

        def focus_out(event):
            scriptpopup.unpost()
            self.focus()
            return 'break'

        scriptpopup.bind('<Key>', popup_process_event)
        scriptpopup.bind("<FocusOut>", focus_out)

        do_scriptpopup(event)
        return 'break'

    def _process_tab(self, event):
        prefix = self.get("insert linestart", "insert")

        # At beginning of line or some text selected
        if not prefix.strip() or self.tag_ranges(tk.SEL):
            return self._insert_tab(event)

        # try to import jedi
        try:
            import jedi

            if compare_version(jedi.__version__, '0.16.0') < 0:
                # warnings.warn('jedi package is old (<0.16.0)')
                # warnings.warn('Use `pip install jedi --upgrade` to rectify the situation')
                return 'break'
        except ImportError:
            # warnings.warn('jedi package not installed: No autocompletion available')
            # warnings.warn('Use `pip install jedi` to rectify the situation')
            return 'break'
        else:
            import jedi.settings

            jedi.settings.case_insensitive_completion = False
            jedi.settings.add_bracket_after_function = True

        # tab-complete based on the text in the command-box and the following namespaces
        import omfit_classes.omfit_python

        script = jedi.Interpreter(
            self.get(),
            [
                self.namespace,  # namespace of the command box (where root, rootName, and dependencies are defined...)
                omfit_classes.omfit_python.OMFITconsoleDict,  # namespace with variables defined in the command box
                omfit_classes.omfit_python.__dict__,
            ],
        )  # namespace with all functions/classes available to the user

        # actual tab-complete at this line/char position
        line, char = map(int, self.index("insert").split('.'))
        self.tab_comp = script.complete(line, char)

        # no options --> do nothing
        if not len(self.tab_comp):
            pass
        # only one option --> complete
        elif len(self.tab_comp) == 1:
            self.insert("insert", self.tab_comp[0].complete)
        # multiple option --> show popup
        else:
            self._make_popup_menu_jedi(event)

        return 'break'

    def _insert_tab(self, event):
        # insert 4 spaces instead of a tab
        if self.tag_ranges(tk.SEL):
            first = 'sel.first linestart'
            last = 'sel.last lineend'
            ind1 = self.index(first).split('.')[0]
            ind2 = self.index(last).split('.')[0]
            for l in range(int(ind1), int(ind2) + 1):
                self.insert('%s.0' % l, '    ')
            self.tag_add('sel', '%s.0' % ind1, '%s lineend' % ind2)
        else:
            tmp = self.get("insert linestart", "insert lineend")
            self.insert("insert linestart", " " * (4 - int(np.mod(len(tmp) - len(tmp.lstrip(' ')), 4))))
        return 'break'

    def _del_tab(self, event):
        # delete 4 spaces instead of a tab
        if self.tag_ranges(tk.SEL):
            first = 'sel.first linestart'
            last = 'sel.last lineend'
            ind1 = self.index(first).split('.')[0]
            ind2 = self.index(last).split('.')[0]
            tmp = self.get(first, last)
            self.replace(first, last, re.sub(r'^\s{1,4}', '', tmp, flags=re.MULTILINE))
            self.tag_remove(tk.SEL, '1.0', tk.END)
            self.tag_add('sel', '%s.0 linestart' % ind1, '%s.0 lineend' % ind2)
        else:
            tmp = self.get("insert linestart", "insert lineend")
            for k in range(4 - int(np.mod(-len(tmp) + len(tmp.lstrip(' ')), 4))):
                if self.get("insert linestart", "insert linestart +1c") == ' ':
                    self.delete("insert linestart", "insert linestart +1c")
        return 'break'

    def flush(self):
        pass

    def close(self):
        self.flush()


tk.ConsoleTextGUI = _ConsoleTextGUI


def __nonzero__(*args, **kw):
    return True


tk.Misc.__nonzero__ = __nonzero__


class TtkScale(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        ttk.Frame.__init__(self, master)
        self.columnconfigure(0, weight=1)
        self.tickinterval = kwargs.pop('tickinterval', 1)
        digits = kwargs.pop('digits', None)
        if np.any(map(is_float, [kwargs['to'], kwargs['from_'], self.tickinterval])):
            self.digits = 3
        else:
            self.digits = 0
        if digits is not None:
            self.digits = digits

        if 'command' in kwargs:
            # add self.display_value to the command
            fct = kwargs['command']

            def cmd(value):
                value = self.display_value(value)
                fct(value)

            kwargs['command'] = cmd
        else:
            kwargs['command'] = self.display_value

        self.scale = ttk.Scale(self, **kwargs)

        # get slider length
        style = ttk.Style(self)
        style_name = kwargs.get('style', '%s.TScale' % (str(self.scale.cget('orient')).capitalize()))
        self.sliderlength = style.lookup(style_name, 'sliderlength', default=30)

        self.extent = float(kwargs['to'] - kwargs['from_'])
        self.start = kwargs['from_']
        ttk.Label(self, text=' ').grid(row=0)
        self.label = ttk.Label(self, text='0')
        self.label.place(in_=self.scale, bordermode='outside', x=0, y=0, anchor='s')
        self.display_value(self.scale.get())

        self.scale.grid(row=1, sticky='ew')

        # ticks
        if self.tickinterval:
            ttk.Label(self, text=' ').grid(row=2)
            self.ticks = []
            self.ticklabels = []
            nb_interv = int(round(self.extent / float(self.tickinterval)))
            formatter = '{:.' + str(self.digits) + 'f}'
            for i in range(max([nb_interv + 1, 2])):
                if i == 0:
                    tick = kwargs['from_']
                elif i >= nb_interv:
                    tick = kwargs['to']
                else:
                    tick = kwargs['from_'] + i * self.tickinterval
                self.ticks.append(tick)
                self.ticklabels.append(ttk.Label(self, text=formatter.format(tick)))
                self.ticklabels[i].place(in_=self.scale, bordermode='outside', x=0, rely=1, anchor='n')
            self.place_ticks()

        self.scale.bind('<Configure>', self.on_configure)

    def convert_to_pixels(self, value):
        try:
            return ((value - self.start) / self.extent) * (self.scale.winfo_width() - self.sliderlength) + self.sliderlength // 2
        except Exception:
            return

    def display_value(self, value):
        # position (in pixel) of the center of the slider
        x = self.convert_to_pixels(float(value))
        # pay attention to the borders
        half_width = self.label.winfo_width() // 2
        if x + half_width > self.scale.winfo_width():
            x = self.scale.winfo_width() - half_width
        elif x - half_width < 0:
            x = half_width
        self.label.place_configure(x=x)
        formatter = '{:.' + str(self.digits) + 'f}'
        self.label.configure(text=formatter.format(float(value)))
        return formatter.format(float(value))

    def place_ticks(self):
        # first tick
        tick = self.ticks[0]
        label = self.ticklabels[0]
        x = self.convert_to_pixels(tick)
        half_width = label.winfo_width() // 2
        if x - half_width < 0:
            x = half_width
        label.place_configure(x=x)
        # ticks in the middle
        for tick, label in zip(self.ticks[1:-1], self.ticklabels[1:-1]):
            x = self.convert_to_pixels(tick)
            label.place_configure(x=x)
        # last tick
        tick = self.ticks[-1]
        label = self.ticklabels[-1]
        x = self.convert_to_pixels(tick)
        half_width = label.winfo_width() // 2
        if x + half_width > self.scale.winfo_width():
            x = self.scale.winfo_width() - half_width
        label.place_configure(x=x)

    def on_configure(self, event):
        """Redisplay the ticks and the label so that they adapt to the new size of the scale."""
        self.display_value(self.scale.get())
        self.place_ticks()


def help(*args, **kw):
    # define help here to avoid GUI to lock
    pass


# ----------------
# screen geometry
# ---------------
def _winfo_screen(reset=False):
    """
    This function detects and returns the screen width and height.
    This is necessary because XQuartz under OSX does not update the screen size when the monitors configuration changes.

    :param reset: forces the detection of the screen size on OSX (useful when the screen size changes for example because a external monitor is plugged to a laptop)

    :return: tuple with screen width and screen height
    """
    if platform.system() == 'Darwin':
        if reset:
            _winfo_screen_cache[:] = []

        if not len(_winfo_screen_cache):
            # find screensize using xrandr
            # (the problem is that XQuartz does not find the right screen size when
            # the screen configuration changes on the fly eg. adding/removing screen)
            s = subprocess.Popen(
                [distutils.spawn.find_executable('xrandr')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            std_out, std_err = list(map(b2s, s.communicate()))
            for line in std_out.split('\n'):
                if '*' in line:
                    geometry = re.sub(r'.* ([0-9]+\s*x\s*[0-9]+) .*', r'\1', line)
                    _winfo_screen_cache[:] = list(map(int, geometry.split('x')))
                    break
        return _winfo_screen_cache[0], _winfo_screen_cache[1]

    else:
        return OMFITaux['rootGUI'].winfo_screenwidth(), OMFITaux['rootGUI'].winfo_screenheight()


if platform.system() == 'Darwin':
    _winfo_screen_cache = []

    def _winfo_screenwidth(*args, **kw):
        # returns the width of the screen
        return _winfo_screen()[0]

    def _winfo_screenheight(*args, **kw):
        # returns the height of the screen
        return _winfo_screen()[1]

    tk.Misc.winfo_screenwidth = _winfo_screenwidth
    tk.Misc.winfo_screenheight = _winfo_screenheight

# ---------------
# intercept tk variable generation and substitute with alternative
# non-tk dependent class if OMFIT session without Tk is started
# ---------------
_globaTkVars = {}


class _dummyTkVarClass(object):
    def __init__(self, default):
        self.value = default

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def __del__(self):
        return

    def __getattr__(self, attr):
        raise Exception('this is not a full replacement for tk variables')


_orig_tkBooleanVar = tk.BooleanVar


def _tkBooleanVar(name=None, **kw):
    if OMFITaux['rootGUI'] is not None:
        return _orig_tkBooleanVar(name=name, **kw)
    elif name is None:
        return _dummyTkVarClass(False)
    else:
        return _globaTkVars.setdefault(name, _dummyTkVarClass(False))


_orig_tkStringVar = tk.StringVar


def _tkStringVar(name=None, **kw):
    if OMFITaux['rootGUI'] is not None:
        return _orig_tkStringVar(name=name, **kw)
    elif name is None:
        return _dummyTkVarClass('')
    else:
        return _globaTkVars.setdefault(name, _dummyTkVarClass(''))


tk.BooleanVar = _tkBooleanVar
tk.StringVar = _tkStringVar
