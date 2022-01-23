print('Loading widgets utility functions...')

from omfit_classes.utils_base import *
from omfit_classes.utils_math import array_info
from tkinter import Tk as tk
from tkinter import ttk
import tkinter.font as tkFont
import numpy as np
import pandas
import xarray
import collections
from uncertainties.unumpy import nominal_values, std_devs

# -------------
# Tk utils
# -------------
rightClick = 'Button-3'
middleClick = 'Button-2'
rightClickIndex = 3
middleClickIndex = 2

hide_ptrn = re.compile(r'^__.*__$')


def treeText(inv, strApex=False, n=-1, escape=True):
    """
    Returns the string that is shown in the OMFITtree for the input object `inv`

    :param inv: input object

    :param strApex: should the string be returned with apexes

    :param n: maximum string length

    :param escape: escape backslash characters

    :return: string representation of object `inv`
    """
    if isinstance(inv, str):
        if strApex:
            return short_str(repr(inv), n, escape)
        elif isinstance(inv, str):
            return short_str(repr(inv)[1:-1], n, escape)

    elif isinstance(inv, list):

        def listType(x):
            lst = []
            for k in x[:10]:
                if isinstance(k, str):
                    kr = repr(k)
                    if len(kr) > 12:
                        k = kr[:11] + '..'
                elif hasattr(k, '__iter__'):
                    kr = '<%s>' % k.__class__.__name__
                elif isinstance(k, (int, np.integer, float, np.float, complex, np.complex)):
                    kr = repr(k)
                else:
                    kr = '<object>'
                lst.append(kr)
            if len(x) > 10:
                lst.append('...')
            return lst

        return short_str('[%s]' % ', '.join(listType(inv)), n, escape)

    elif is_float(inv):
        return format(inv, '3.8g')

    elif isinstance(inv, np.ndarray):
        return array_info(inv)

    elif pandas is not None and isinstance(inv, pandas.DataFrame):
        ncol = len(inv.columns)
        if ncol > 5:
            return ', '.join(k for k in inv.columns[:5]) + '...'
        else:
            return ', '.join(k for k in inv.columns)

    elif pandas is not None and isinstance(inv, pandas.Series):
        return (', '.join(l for l in str(inv.describe()).split('\n')[:2] if '%' not in l)).replace('\n', '')

    elif xarray is not None and isinstance(inv, xarray.DataArray):
        return ', '.join('%s: %s' % (k, v) for k, v in zip(inv.dims, inv.shape))

    elif xarray is not None and isinstance(inv, xarray.Dataset):
        return ', '.join(['%s: %s' % (k, inv.dims[k]) for k in inv.dims])

    elif isinstance(inv, (dict, collections.MutableMapping)):
        if hasattr(inv, 'dynaLoad') and inv.dynaLoad:
            return '--{\t?\t}--'

        vshow = [k for k in inv if not isinstance(k, str) or not re.match(hide_ptrn, k)]
        vhide = [k for k in inv if isinstance(k, str) and re.match(hide_ptrn, k)]
        values = '--{\t'
        if vshow:
            values += '%d' % len(vshow)
        if vshow and vhide:
            values += ' '
        if vhide:
            values += '(%d)' % len(vhide)
        values += '\t}--'

        for k in ['modifyOriginal', 'readOnly']:
            if hasattr(inv, k) and getattr(inv, k):
                values += ' ' + k + ' '

        return values

    elif inspect.isroutine(inv):
        if inv.__doc__ is not None:
            tmp = inv.__doc__.strip().split('\n')
            tmp = [line for line in map(lambda x: x.strip(), tmp) if line and not line.startswith(':') and not line.startswith('>')]
            if tmp:
                return short_str(' | '.join(tmp), n, escape)
        try:
            return short_str('(' + function_arguments(inv, [], True).replace('\n', '').replace('self,', '') + ')', n, escape)
        except TypeError:
            return short_str('built-in method', n, escape)

    else:
        return short_str(repr(inv), n, escape)


def ctrlCmd():
    return 'Control'
    # return 'Command'


def short_str(inv, n=-1, escape=True, snip='[...]'):
    """
    :param inv: input string

    :param n: maximum length of the string (negative is unlimited)

    :param escape: escape backslash characters

    :param snip: string to replace the central part of the input string

    :return: new string
    """
    l = len(inv)
    s = len(snip)
    if not l:
        inv = "\'\'"
    elif l > n and n > s + 1:
        nn = (n - s) / 2.0
        a = int(round(nn))
        b = int(nn)
        inv = inv[:a] + snip + inv[-b:]
    if escape:
        inv = re.sub(r'\\', r'\\\\', inv)
    return inv


def tkStringEncode(inv):
    r"""
    Tk requires ' ', '\', '{' and '}' characters to be escaped
    Use of this function dependes on the system and the behaviour can be
    set on a system-by-system basis using the OMFIT_ESCAPE_TK_SPACES environmental variable

    :param inv: input string

    :return: escaped string
    """
    if int(os.environ.get('OMFIT_ESCAPE_TK_SPACES', '1')) and len(inv):
        inv = re.sub(r'([ \\\{\}])', r'\\\1', treeText(inv, strApex=False, n=-1, escape=False))
    return inv


_defaultFont = {}


def OMFITfont(weight='', size=0, family='', slant=''):
    """
    The first time that OMFITfont is called, the system defaults are gathered

    :param weight: 'normal' or 'bold'

    :param size: positive or negative number relative to the tkinter default

    :param family: family font

    :return: tk font object to be used in tkinter calls
    """

    font = {'family': 'Helvetica', 'size': 11, 'weight': 'normal', 'slant': 'roman'}

    # save default font if not done yet
    if not len(_defaultFont):
        ttk_style = ttk.Style()
        # generate font
        f = tkFont.Font(font=ttk_style.lookup('TLabel', 'font'))
        _defaultFont.update(f.metrics())

    # make sure the default font has all the categories
    for key, val in list(font.items()):
        _defaultFont.setdefault(key, val)
    if not _defaultFont['family']:  # bad things happen if this somehow gets set to ''
        _defaultFont['family'] = 'Helvetica'
    if _defaultFont['size'] < 6:  # bad things happen if this somehow gets set to 0
        _defaultFont['size'] = 6
    # modifications to default font
    font = {}
    font['size'] = abs(_defaultFont['size']) + size
    if weight:
        font['weight'] = weight
    elif _defaultFont['weight']:
        font['weight'] = _defaultFont['weight']
    if slant:
        font['slant'] = slant
    elif _defaultFont['slant']:
        font['slant'] = _defaultFont['slant']
    if family:
        font['family'] = family
    elif _defaultFont['family']:
        font['family'] = _defaultFont['family']

    return (font['family'], font['size'], font['weight'], font['slant'])


def tk_center(win, parent=None, width=None, height=None, xoff=None, yoff=None, allow_negative=False):
    """
    Function used to center a tkInter GUI

    Note: by using this function tk does not manage the GUI geometry
    which is beneficial when switching between desktop on some window
    managers, which would otherwise re-center all windows to the desktop.

    :param win: window to be centered

    :param parent: window with respect to be centered (center with respect to screen if `None`)

    :width: set this window width

    :height: set this window height

    :param xoff: x offset in pixels

    :param yoff: y offset in pixels

    :param allow_negative: whether window can be off the left/upper part of the screen
    """
    win.update_idletasks()

    if parent is None:
        utils_tk._winfo_screen(reset=True)
        swidth, sheight, x0, y0 = screen_geometry()
    else:
        swidth, sheight, x0, y0 = _parse_tk_geometry(TKtopGUI(parent).geometry())

    if xoff is None:
        xoff = 0
    if yoff is None:
        yoff = 0

    _width = width
    if width is None:
        _width = win.winfo_reqwidth()

    _height = height
    if height is None:
        _height = win.winfo_reqheight()

    x = (swidth - _width) // 2 + x0 + xoff
    y = (sheight - _height) // 2 + y0 + yoff

    if not allow_negative:
        x = np.max([xoff, x])
        y = np.max([yoff, y])

    if width or height:
        win.geometry('%dx%d+%d+%d' % (_width, _height, x, y))
    else:
        win.geometry('+%d+%d' % (x, y))


# ----------------
# extra Tk widgets
# ---------------
class HelpTip(object):
    def __init__(self, widget=None, move=False):
        self.widget = widget
        self.tipwindow = None
        self.mode = 0
        self.location = None
        self.text = None

    def showtip(self, text, location=None, mode=None, move=True, strip=False):
        "Display text in helptip window"
        self.hidetip()
        if location is not None:
            self.location = location
        if mode is not None:
            self.mode = mode
        if text:
            if strip:
                text = text.strip()
            self.text = text

            if isinstance(text, list):
                text = '\n'.join(text)
            text = wrap(text, 100)

            self.tipwindow = tk.Toplevel(self.widget)
            self.tipwindow.withdraw()
            color = "#ffffe0"

            if self.mode == 1:
                # editor mode
                self.tipwindow.wm_transient(self.widget)
                wmax = np.max([max(np.array([len(line) for line in text.split('\n')])), 50])
                hmax = 11
                self.tipwindow.wm_title('Tip')
                self.widget.winfo_containing(self.widget.winfo_pointerx(), self.widget.winfo_pointery()).unbind("<Leave>")
                self.widget.bind_all("<Escape>", self.hidetip)
                self.widget.unbind_all("<F4>")
            else:
                # view mode
                if platform.system() != 'Darwin':
                    self.tipwindow.wm_overrideredirect(1)
                wmax = np.max(np.array([len(line) for line in text.split('\n')]))
                hmax = np.min([text.count('\n') + 1, 11])
                if hmax > 10 and move:
                    ttk.Label(self.tipwindow, text='Press F4 to detach', font=OMFITfont('bold', -1)).pack()
                    self.widget.winfo_containing(self.widget.winfo_pointerx(), self.widget.winfo_pointery()).bind("<Leave>", self.hidetip)
                self.widget.unbind_all("<Escape>")
                if not move:
                    self.widget.bind_all("<F4>", self.changeMode)

            frm = ttk.Frame(self.tipwindow, relief=tk.SOLID, borderwidth=1)
            frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
            label = tk.Text(frm, width=wmax, height=hmax, undo=tk.TRUE, maxundo=-1, wrap='word')
            label.config(borderwidth=0, font=OMFITfont('normal', 0, 'Courier'))
            label.insert(1.0, text)
            label.delete('end -1 chars', 'end')
            label.grid(column=0, row=0, sticky='nsew')
            sb = ttk.Scrollbar(frm, command=label.yview, orient='vertical')
            if hmax > 10:
                sb.grid(column=1, row=0, sticky='ns')

            if self.mode == 1 and self.location:
                label.insert(1.0, '')
                label.focus_set()

                def onButton(event=None):
                    self.text = label.get(1.0, tk.END)
                    exec((self.location + '=' + repr(self.text)), globals(), locals())
                    self.changeMode()
                    return "break"

                bt = ttk.Button(frm, text='Update variables description <{ctrlCmd()}-Return>', command=onButton)
                bt.grid(column=0, row=1, sticky='nsew')
                label.bind(f'<{ctrlCmd()}-Return>', onButton)
            else:
                label.config(state=tk.DISABLED)

            label['yscrollcommand'] = sb.set
            frm.columnconfigure(0, weight=1)
            frm.rowconfigure(0, weight=1)

            if not move:
                x = self.widget.winfo_pointerx()
                y = self.widget.winfo_pointery()
                self.tipwindow.update_idletasks()

                # place window smack in the middle of the cursor
                self.x = int(x - self.tipwindow.winfo_reqwidth() / 2.0)
                self.y = int(y - self.tipwindow.winfo_reqheight() / 2.0)

                # move window off the edges
                if (self.x + self.tipwindow.winfo_reqwidth()) > screen_geometry()[0]:
                    self.x = self.x - self.tipwindow.winfo_reqwidth()
                if (self.y + self.tipwindow.winfo_reqheight()) > screen_geometry()[1]:
                    self.y = self.y - self.tipwindow.winfo_reqheight()
                if self.x < 0:
                    self.x = 0
                if self.y < 0:
                    self.y = 0
                self.tipwindow.wm_geometry("+%d+%d" % (self.x, self.y))
                self.tipwindow.update_idletasks()

                # place cursor smack in the middle of the window
                x = int(self.x + self.tipwindow.winfo_reqwidth() / 2.0)
                y = int(self.y + self.tipwindow.winfo_reqheight() / 2.0)
                self.tipwindow.event_generate('<Motion>', warp=True, x=x, y=y)
                self.tipwindow.update_idletasks()

                self.tipwindow.deiconify()
                self.tipwindow.bind("<Leave>", self.hidetip)

            else:
                self.movetip()
                self.tipwindow.deiconify()

    def hidetip(self, event=None):
        try:
            self.mode = 0
            self.tipwindow.destroy()
            self.tipwindow = None
        except Exception:
            pass

    def movetip(self, event=None):
        try:
            if self.tipwindow is not None:
                if event is None:
                    x = self.widget.winfo_pointerx()
                    y = self.widget.winfo_pointery()
                else:
                    x = event.x_root
                    y = event.y_root
                self.tipwindow.update_idletasks()
                self.x = x + 10
                self.y = y + 12
                if self.x > screen_geometry()[0] - (self.tipwindow.winfo_reqwidth() + 10):
                    self.x = self.x - self.tipwindow.winfo_reqwidth() - 20
                if self.y > screen_geometry()[1] - (self.tipwindow.winfo_reqheight() + 12):
                    self.y = self.y - self.tipwindow.winfo_reqheight() - 24
                self.tipwindow.wm_geometry("+%d+%d" % (self.x, self.y))
                if self.mode == 0:
                    self.tipwindow.after(25, self.movetip)
        except Exception as _excp:
            warnings.warn(repr(_excp))

    def changeMode(self, event=None):
        self.showtip(self.text, mode=np.mod(self.mode + 1, 2))


helpTip = HelpTip()


class ToolTip(object):
    """
    Tooltip recipe from
    http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387
    """

    @staticmethod
    def createToolTip(widget, text):
        toolTip = ToolTip(widget)

        def enter(event):
            toolTip.showtip(text)

        def leave(event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + self.widget.winfo_rooty()
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def dialog(message='Are You Sure?', answers=['Yes', 'No'], icon='question', title=None, parent=None, options=None, entries=None, **kw):
    """
    Display a dialog box and wait for user input

    Note:

    * The first answer is highlighted (for users to quickly respond with `<Return>`)

    * The last answer is returned for when users press `<Escape>` or close the dialog

    :param message: the text to be written in the label

    :param answers: list of possible answers

    :param icon: "question", "info", "warning", "error"

    :param title: title of the frame

    :param parent: tkinter window to which the dialog will be set as transient

    :param options: dictionary of True/False options that are displayed as checkbuttons in the dialog

    :param entries: dictionary of string options that are displayed as entries in the dialog

    :return: return the answer chosen by the user (a dictionary if options keyword was passed)
    """

    class _Dialog(object):
        def __init__(self, top, message='Are You Sure?', answers=['Yes', 'No'], icon='question', title=None, options=None, entries=None):
            self.top = top
            self.result = None
            self.options_var = {}
            self.entries_var = {}
            top = ttk.Frame(self.top)
            top.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, fill=tk.X, expand=tk.YES, padx=0, pady=0)
            if icon in ["question", "info", "warning", "error"]:
                if title is None:
                    title = icon
                OMFITsrc = str(os.path.abspath(os.path.dirname(__file__)))
                img = tk.PhotoImage(file=os.path.join(OMFITsrc, 'extras', 'graphics', icon + ".gif"))
                icon_canvas = tk.Canvas(frm, width=64, height=64)
                icon_canvas.copy_image = img
                icon_canvas.create_image(32, 32, image=icon_canvas.copy_image)
                icon_canvas.pack(side=tk.LEFT, fill=tk.NONE, expand=tk.NO)

            ttk.Label(frm, text=message, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

            if options is not None:
                for item in list(options.keys()):
                    frm = ttk.Frame(top)
                    frm.pack(side=tk.TOP, fill=tk.X, expand=tk.YES, padx=0, pady=0)
                    self.options_var[item] = var = tk.BooleanVar()
                    tmp = ttk.Checkbutton(frm, variable=var, text=item)
                    tmp.var = var
                    tmp.pack(side=tk.LEFT, padx=5, pady=2)
                    var.set(options[item])

            if entries is not None:
                for item in list(entries.keys()):
                    frm = ttk.Frame(top)
                    frm.pack(side=tk.TOP, fill=tk.X, expand=tk.YES, padx=5, pady=2)
                    self.entries_var[item] = var = tk.StringVar()
                    ttk.Label(frm, text=item + ' ').pack(side=tk.LEFT)
                    tmp = ttk.Entry(frm, textvariable=var)
                    tmp.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
                    var.set(entries[item])

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, fill=tk.X, expand=tk.YES, padx=0, pady=0)
            for ii, answer in enumerate(answers):
                tmp = ttk.Button(frm, text=answer, command=lambda answer=answer: self.ok(answer))
                tmp.bind('<Return>', lambda event: event.widget.invoke())
                tmp.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
                if ii == 0:
                    tmp.focus()
            self.top.bind('<Escape>', lambda event=None, answer=answers[-1]: self.ok(answer))
            self.top.protocol("WM_DELETE_WINDOW", lambda event=None, answer=answers[-1]: self.ok(answer))

            if title is None:
                title = 'message'
            self.top.wm_title(title[0].upper() + title[1:])

        def ok(self, x=None):
            if not len(self.options_var) and not len(self.entries_var):
                self.result = x
            else:
                self.result = [x]
                kw = {}
                for item in list(self.options_var.keys()):
                    kw[item] = bool(self.options_var[item].get())
                for item in list(self.entries_var.keys()):
                    kw[item] = self.entries_var[item].get()
                self.result.append(kw)
            self.top.destroy()

    if parent is None:
        parent = OMFITaux['rootGUI']
    try:
        frm_top = tk.Toplevel(parent)
    except Exception:
        parent = OMFITaux['rootGUI']
        frm_top = tk.Toplevel(parent)
    frm_top.withdraw()
    frm_top.transient(parent)
    d = _Dialog(frm_top, message=message, answers=answers, icon=icon, title=title, options=options, entries=entries)
    frm_top.resizable(False, False)
    tk_center(frm_top, parent)
    frm_top.deiconify()
    try:
        frm_top.grab_set()
    except tk.TclError:
        pass
    frm_top.update_idletasks()
    frm_top.wait_window(d.top)
    return d.result


def pickTreeLocation(startLocation=None, title='Pick tree location ...', warnExists=True, parent=None):
    """
    Function which opens a blocking GUI to ask user to pick a tree location

    :param startLocation: starting location

    :param title: title to show in the window

    :param warnExists: warn user if tree location is already in use

    :param parent: tkinter window to which the dialog will be set as transient

    :return: the location picked by the user
    """

    def onEscape(event=None):
        top.destroy()

    if parent is None:
        parent = OMFITaux['rootGUI']
    top = tk.Toplevel(parent)
    top.withdraw()
    top.transient(parent)
    frm = ttk.Frame(top)
    frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx=5, pady=5)
    frm.grid_columnconfigure(1, weight=1)
    top.wm_title(title)
    outcome = [None]

    def onReturn(event=None):
        v2 = newLocation.get()
        try:
            eval(v2)
            if warnExists and 'No' == dialog(
                title='Location already exists', message='Proceed anyways?', answers=['Yes', 'No'], parent=top
            ):
                return
        except Exception:
            pass
        top.destroy()
        outcome[0] = v2

    ttk.Label(frm, text='To: ').grid(row=1, sticky=tk.E)
    newLocation = tk.OneLineText(frm, width=50, percolator=True)
    if startLocation is None:
        newLocation.set(OMFITaux['GUI'].focusRoot)
    else:
        newLocation.set(startLocation)
    tk_center(top, parent)
    e1 = newLocation
    e1.grid(row=1, column=1, sticky=tk.E + tk.W, columnspan=2)
    e1.focus_set()
    top.bind('<Return>', onReturn)
    top.bind('<KP_Enter>', onReturn)
    top.bind('<Escape>', onEscape)
    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.update_idletasks()
    top.deiconify()
    top.wait_window(top)
    return outcome[0]


stored_passwords = {}


def password_gui(title='Password', parent=None, key=None):
    """
    Present a password dialog box

    :param title: The title for the dialog box

    :param parent: The GUI parent

    :param key: A key for caching the password in this session
    """
    if key and key in stored_passwords:
        return stored_passwords[key]

    def onEscape(event=None):
        top.destroy()

    if parent is None:
        parent = OMFITaux['rootGUI']

    import tkinter as tk
    from tkinter import ttk

    top = tk.Toplevel(parent)
    top.withdraw()
    top.transient(parent)
    frm = ttk.Frame(top)
    frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx=5, pady=5)
    frm.grid_columnconfigure(1, weight=1)
    top.wm_title(title)
    outcome = [None]

    def onReturn(event=None):
        outcome[0] = pass_phrase.get()
        top.destroy()

    ttk.Label(frm, text='Pass_phrase').grid(row=1, sticky=tk.E)
    pass_phrase = tk.Entry(frm, width=50, show='*')
    tk_center(top, parent)
    pass_phrase.grid(row=1, column=1, sticky=tk.E + tk.W, columnspan=2)
    pass_phrase.focus_set()
    top.bind('<Return>', onReturn)
    top.bind('<KP_Enter>', onReturn)
    top.bind('<Escape>', onEscape)
    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.update_idletasks()
    top.deiconify()
    top.wait_window(top)
    if key:
        stored_passwords[key] = outcome[0]
    return outcome[0]


# ----------------
# Tk events
# ---------------
class eventBindings(object):
    def __init__(self):
        self.descs = []
        self.widgets = []
        self.events = []
        self.callbacks = []
        self.tags = []
        self.default_desc_event = {}

    def add(self, description, widget, event, callback, tag=None):
        if '_' in description:
            raise ValueError('The saving/restoring of key bindings cannot handle _ in the description')

        # set event bindings for more than one widget
        if description in self.descs:
            ind = self.descs.index(description)
            if tag:
                widget.tag_bind(tag + '_action', self.events[ind], callback)
            else:
                try:
                    widget.bind(self.events[ind], callback)
                except tk.TclError:
                    if 'ISO' in event:
                        pass
                    else:
                        raise
            self.widgets[ind].append(widget)
            return

        # bind
        if tag:
            widget.tag_bind(tag + '_action', event, callback)
            if platform.system() == 'Darwin' and 'Control' in event:
                widget.tag_bind(tag + '_action', re.sub('Control', 'Command', event), callback)
        else:
            try:
                widget.bind(event, callback)
            except tk.TclError:
                if 'ISO' in event:
                    pass
                else:
                    raise
            if platform.system() == 'Darwin' and 'Control' in event:
                widget.bind(re.sub('Control', 'Command', event), callback)

        # add to list
        self.descs.append(description)
        self.widgets.append([widget])
        self.events.append(event)
        self.callbacks.append(callback)
        if tag:
            self.tags.append(tag + '_action')
        else:
            self.tags.append(tag)
        self.default_desc_event[description.replace(' ', '_')] = event

    def remove_widget(self, widget):
        for wi in range(len(self.widgets)):
            if widget in self.widgets[wi]:
                self.widgets[wi].remove(widget)

    def set(self, description, event):
        try:
            ind = self.descs.index(description)
        except ValueError:
            raise ValueError('Unable to set %s because it is not yet bound to a widget' % description)
        if event == self.events[ind]:
            return
        for w in list(self.widgets[ind]):
            try:
                if self.tags[ind]:
                    w.tk.call(w._w, 'tag', 'bind', self.tags[ind], self.events[ind], '')
                    # Doesn't exist -> w.tag_unbind(self.tags[ind],self.events[ind])
                else:
                    w.unbind(self.events[ind])
            except tk.TclError as _excp:
                if 'bad window path name' in str(_excp) or "application has been destroyed" in str(_excp):
                    self.remove_widget(w)
                    continue
            if self.tags[ind]:
                w.tag_bind(self.tags[ind], event, self.callbacks[ind])
            else:
                w.bind(event, self.callbacks[ind])
            self.events[ind] = event

    def get(self, description):
        for di, d in enumerate(self.descs):
            if d == description:
                return self.events[di]

    def print_event_in_bindings(self, w, event, ind):
        bindings = set()
        for cls in w.bindtags():
            bindings |= set(w.bind_class(cls))  # s |= t means: update set s, adding elements from t
        bindings = [s.replace('Key-', '') for s in list(bindings)]
        printi(event in bindings, self.events[ind] in bindings)

    def printAll(self):
        from utils import printi

        for di, d in enumerate(self.descs):
            printi('%s: %s' % (d, self.events[di]))  # ,self.callbacks[di],self.widgets[di]


global_event_bindings = eventBindings()

# ----------------
# import tk elements
# ---------------
from utils_tk import *
import utils_tk

# ----------------
# screen geometry
# ---------------
def _parse_tk_geometry(geom):
    """
    Function that parses string returned by tk geometry()

    :param geom: string in the format width, height, x, y `400x300+30+55`

    :return: tuple with 4 integers for width, height, x, y
    """
    geometry = []
    geometry.append(int(re.sub(r'([0-9]*)x([0-9]*)\+([\-0-9]*)\+([\-0-9]*)', r'\1', geom)))
    geometry.append(int(re.sub(r'([0-9]*)x([0-9]*)\+([\-0-9]*)\+([\-0-9]*)', r'\2', geom)))
    geometry.append(int(re.sub(r'([0-9]*)x([0-9]*)\+([\-0-9]*)\+([\-0-9]*)', r'\3', geom)))
    geometry.append(int(re.sub(r'([0-9]*)x([0-9]*)\+([\-0-9]*)\+([\-0-9]*)', r'\4', geom)))
    return geometry


_screen_geometry = []


def screen_geometry():
    """
    Function returns the screen geometry

    :return: tuple with 4 integers for width, height, x, y
    """
    if not len(_screen_geometry):
        t = tk.Tk()  # new window
        t.withdraw()

        t.attributes("-alpha", 0)
        try:
            t.state('zoomed')
        except Exception:
            t.attributes('-fullscreen', True)
        t.update_idletasks()
        geom = _parse_tk_geometry(t.geometry())
        geom[0] = t.winfo_reqwidth()
        geom[1] = t.winfo_reqheight()

        _screen_geometry.extend(geom)

        screen = [t.winfo_screenwidth(), t.winfo_screenheight()]
        _screen_geometry[0] = screen[0] - _screen_geometry[2]
        _screen_geometry[1] = screen[1] - _screen_geometry[3]

        t.destroy()

    return _screen_geometry


_displays = [0]


def wmctrl():
    """
    This function is useful when plugging in a new display in OSX and the OMFIT window disappear
    To fix the issue, go to the XQuartz application and select the OMFIT window from the menu `Window > OMFIT ...`
    Then press F8 a few times until the OMFIT GUI appears on one of the screens.
    """
    # screen sizes
    with open(os.devnull, 'w') as nul_f:
        child = subprocess.Popen([OMFITsrc + '/../bin/hmscreens', "-info"], stderr=nul_f, stdout=subprocess.PIPE)
    hms_out, std_err = map(b2s, child.communicate())

    # parse output of hmscreens
    screens = []
    for ks, s in enumerate(hms_out.strip().split('\n\n')):
        s = re.sub(r'\}', ']', re.sub(r'\{', '[', s))
        s = re.sub(r'([\w \(\)]+):(.*)\n*', r'"\1":"\2",', s)
        s = re.sub(r'\n', ',', s)
        screens.append(eval('{%s}' % s))
        for item in screens[-1]:
            try:
                screens[-1][item] = eval(screens[-1][item])
                if isinstance(screens[-1][item], list):
                    screens[-1][item] = np.array(screens[-1][item])
            except (TypeError, NameError):
                pass

    # loop through displays
    display = _displays[0] = np.mod(_displays[0] + 1, len(screens))

    # find geometry according to Tk inter
    minx = 0
    maxx = 0
    miny = 0
    maxy = 0
    for s in screens:
        minx = np.min([minx, s['Global Position'][0, 0]])
        miny = np.min([miny, s['Global Position'][0, 1]])
        maxx = np.max([maxx, s['Global Position'][1, 0]])
        maxy = np.max([maxy, s['Global Position'][1, 1]])

    # change window geometry accordingly
    g = [
        screens[display]['Size'][0],
        screens[display]['Size'][1] - 44 * int(screens[display]['Resolution(dpi)'][1] // 72),
        screens[display]['Global Position'][0, 0] - minx,
        screens[display]['Global Position'][1, 1] - maxy - 44 * int(screens[display]['Resolution(dpi)'][1] // 72),
    ]
    g = '%dx%d+%d+%d' % (g[0], g[1], g[2], g[3])
    OMFITaux['rootGUI'].geometry(g)
    printi('Switched to display #%d: %s' % (display, g))
    OMFITaux['rootGUI'].update_idletasks()


def TKtopGUI(item):
    """
    Function to reach the TopLevel tk from a GUI element

    :param item: tk GUI element

    :return: TopLevel tk GUI
    """
    while True:
        try:
            if item.master is None:
                break
            item = item.master
        except Exception:
            return item
    return item


if __name__ == '__main__':

    main = tk.Tk()
    password_gui(parent=main)
    main.mainloop()
