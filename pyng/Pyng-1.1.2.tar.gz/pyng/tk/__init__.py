#!/usr/bin/python
"""
    __init__.py                      Nat Goodspeed
    Copyright (C) 2017               Nat Goodspeed

NRG 2017-10-26
"""

from functools import partial
import os
import __main__                         # for filename of main script
import sys
try:
    # Python 3
    import tkinter as tk
except ImportError:
    # Python 2
    import Tkinter as tk

BULLET = '\N{BULLET}'           # works in Python 3
if len(BULLET) > 1:
    # In Python 2, the above assignment produces exactly those 10 characters
    BULLET = u"\u2022"          # U+2022 is "bullet"

try:
    WINDOW_TITLE = os.path.basename(__main__.__file__)
except AttributeError:
    WINDOW_TITLE = "pyng/tk"

# Once we obtain the root Tk instance, by whatever means, find it here.
_root = None

def get_root():
    """
    Find or create the top-level Tk instance. If one doesn't already exist (or
    we can't discover it), construct a plain Tk instance. A Tk application
    window implicitly created by get_root() is hidden.
    """
    # There Should Be Only One
    # https://effbot.org/tkinterbook/variable.htm#patterns
    # "The [Variable] constructor argument is only relevant if you're running
    # Tkinter with multiple Tk instances (which you shouldn't do, unless you
    # really know what you're doing)."
    # Suppose we're constructing a Toplevel subclass. If we let the (lazy)
    # user pass master=None, and there isn't already a Tk instance, tkinter
    # will create a useless empty visible Tk window. get_root() is intended to
    # solve this problem. But what if the user already hand-constructed a Tk
    # instance that's supposed to be the main application? We don't want to
    # instantiate another Tk!
    # As of 2020-04-23, and probably since well before that, tkinter (the
    # module formerly known as Tkinter) stores the first/default Tk instance
    # in _default_root. At least peek there.
    global _root
    # only need to initialize once
    if _root is None:
        # Conflate the cases of "_default_root hasn't yet been set" and
        # "there's no such attribute." In future, if tkinter stores its root
        # Tk instance elsewhere, the code below might end up creating a bogus
        # second Tk instance anyway. Sorry!
        _root = getattr(tk, '_default_root', None)
        # If the user already created a root Tk application window, and if
        # tkinter stored it where we expect, cool, our work is done. Otherwise...
        if not _root:
            _root = tk.Tk()
            # Don't show lame empty application window
            _root.withdraw()
    return _root

# Python 3.7 or later (ignored in earlier versions):
def __getattr__(name):
    # Treat 'root' as a lazy module attribute
    if name == 'root':
        return get_root()
    # __getattr__() is called when a name can't be found otherwise, so for an
    # unknown name its default behavior must always be to raise
    # AttributeError.
    raise AttributeError('module {} has no attribute {}'.format(__name__, name))

# TODO: This is more general than tk, but we don't yet have a suitable pyng
# module for it, and so far it's only used by tkvar.
class lazy_attr(object):
    """
    This oddly-named class is used to set a class descriptor that will lazily
    construct an instance attribute on each instance of that class -- but only
    if that attribute is referenced. This is useful, for instance, if the
    attribute might be expensive to compute. It can also be useful as an
    implementation detail for other descriptor classes, such as tkvar.

    Usage:

    class Foo(object):
        a = lazy_attr(int, 17)

    foo = Foo()
    vars(foo) => {}
    foo.a     => 17
    vars(foo) => {'a': 17}
    """
    def __init__(self, cls, *args, **kwds):
        self.cls  = cls
        self.args = args
        self.kwds = kwds

    # This hook was introduced in Python 3.6. Every descriptor defined on a
    # class gets a __set_name__() call with the class type and the attribute
    # name on completion of class definition.
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        # This method could have been written as:
        # return obj.__dict__.setdefault(self.name, self.cls(*self.args, **self.kwds))
        # It is not written that way only because one of the more obvious use
        # cases is to avoid constructing an unreferenced instance attribute.
        # The above would incur the cost of repeatedly constructing and
        # discarding self.cls instances!
        try:
            return obj.__dict__[self.name]
        except KeyError:
            value = self.cls(*self.args, **self.kwds)
            obj.__dict__[self.name] = value
            return value

    def __set__(self, obj, value):
        # This descriptor is meant to perform lazy instantiation. It is not
        # meant to forbid explicit assignment. If someone assigns, just do it.
        obj.__dict__[self.name] = value

class tkvar(object):
    """
    tkvar is a data descriptor to facilitate read/write access to class
    instance attributes of tkinter's BooleanVar, DoubleVar, IntVar, StringVar
    types. It works a bit like the built-in property() function, except that
    it's a bit clumsier: Python descriptors are only engaged when stored as
    class attributes, not as instance attributes.

    So the usage goes something like this:

    class MyWidget(base_class):
        def __init__(self, ...):
            base_class.__init__(...)
            # note use of self._message to access the StringVar itself
            self.display = tkinter.Message(..., textvariable=self._message, ...)

        # Although 'message' and 'status' are class attributes, these
        # definitions will lazily produce '_message' and '_status' StringVar
        # instance variables on each instance of MyWidget.
        message = tkvar(tkinter.StringVar)
        status  = tkvar(tkinter.StringVar)

    Given that class definition, given an instance 'w' of MyWidget,
    w.message         # calls w._message.get() and
    w.message = 'xxx' # calls w._message.set('xxx').
    """
    def __init__(self, varclass):
        self.varclass = varclass

    # This hook was introduced in Python 3.6. Every descriptor defined on a
    # class gets a __set_name__() call with the class type and the attribute
    # name on completion of class definition.
    def __set_name__(self, owner, name):
        # Now that we know our own class attribute name, create an associated
        # attribute to store the actual varclass instance.
        self.varname = '_' + name
        varattr = lazy_attr(self.varclass)
        setattr(owner, self.varname, varattr)
        # We assign this class attribute too late for it to get an implicit
        # __set_name__() call, so call it explicitly.
        varattr.__set_name__(owner, self.varname)

    def __get__(self, obj, owner=None):
        return getattr(obj, self.varname).get()

    def __set__(self, obj, value):
        return getattr(obj, self.varname).set(value)

# TODO: This, too, belongs in a more general pyng module. with_tkvars can be
# an alias for the general name.
def with_tkvars(cls):
    """
    Python 3.6 introduced the __set_name__() descriptor hook: that hook will
    be implicitly called with the attribute name for any descriptor stored as
    a class attribute.

    But for compatibility with Python < 3.6, we introduce this class decorator.
    It's a no-op in Python 3.6 and later. Usage:

    @with_tkvars
    class MyWidget(base_class):
        message = tkvar(tkinter.StringVar)
        status  = tkvar(tkinter.StringVar)
    """
    if sys.version_info[:2] < (3, 6):
        for name, attr in cls.__dict__.items():
            try:
                set_name = attr.__set_name__
            except AttributeError:
                # ignore any class attribute that doesn't need a
                # __set_name__() call
                pass
            else:
                set_name(cls, name)

    # don't forget to return the class we're decorating
    return cls

# from http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win):
    """generic center function for any Tkinter window"""
    # do this before retrieving any geometry to ensure accurate values
    win.update_idletasks()
    # width of client area
    width = win.winfo_width()
    # winfo_rootx() is client area's left x; winfo_x() is outer frame's left x
    frm_width = win.winfo_rootx() - win.winfo_x()
    # outer frame overall width is client width plus two frame widths
    win_width =  width + 2 * frm_width
    # height of client area
    height = win.winfo_height()
    # winfo_rooty() is client area's top y; winfo_y() is outer frame's top y
    # y is measured from top, therefore winfo_rooty() > winfo_y()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    # outer frame overall height = client height plus titlebar plus frame width
    win_height = height + titlebar_height + frm_width
    x = (win.winfo_screenwidth() - win_width) // 2
    y = (win.winfo_screenheight() - win_height) // 2
    win.geometry('%sx%s+%s+%s' % (width, height, x, y))
    ## if win.attributes('-alpha') == 0:
    ##     win.attributes('-alpha', 1.0)
    win.deiconify()
