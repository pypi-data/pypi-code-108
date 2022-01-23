"""gui.py  -- GUI system

select(win)  -- select a window
  "win"  -- the tkinter name ("tkname") for a toplevel (ex: ".settings")
"""

import tkinter as tk

from liontk.symbols import *

import liontk.tcltalk as tcltalk
from liontk.tcltalk import quote, encase, peek, poke, tclexec, mkcmd


# Global Variables

g = {NEXTID: 1}

root = None  # MUST be assigned AFTER tcltalk is setup


def nextid():
    """Return NEXTID, auto-increment."""
    g[NEXTID] += 1
    return g[NEXTID]-1


# Global Variables -- Scheduled Tasks (nullary functions; run once)

tasks = []


# Functions -- Setup routine

def setup():
    """
    Establish basic global GUI settings assumed by liontk.
    Must be called AFTER tcltalk.setup().
    Must be called ONCE, and ONLY once.
    """
    global root
    tclexec("wm withdraw .")  # close initial tk window
    tclexec("option add *tearOff 0")  # turn off tear-off menus
#   mkcmd("wm_delete_window", wm_delete_window)
    mkcmd("mainloop_tasks", mainloop_tasks)
    root = tcltalk.root
    


def closing_check():
    """Shut-down (internal; not to be called externally.)
    
    The GUI system shuts down automatically when the last window is closed.
    
    This routine MUST NOT be called by the consumer of this API.
    
    This routine ASSUMES that:
    * there is no longer any scheduled timer
    * there are no longer any top level windows
    
    TODO:
    
    There is presently NO WAY for the consumer of the API to shut down
    the system; Only the user can instigate that, by shutting all
    windows.  This said, sys.exit() should work just fine.  And a way
    to do it a "proper" way would be to close each top-level window,
    by calling wm_delete_window after cueing each top level window.
    YES, a function should be created that does this.
    
    """
    if not toplevels():
        root.destroy()
        return True
    else:
        return False


# Functions -- Tk main loop control

def loop():
    """Setup complete; Run main loop."""
    schedule()
    root.mainloop()


def after_idle():
    """Call mainloop_tasks() RIGHT AWAY, don't fuss for 100ms"""
    cancel()
    tclexec("after idle mainloop_tasks")


def schedule():
    """Schedule mainloop task, 100 ms into the future."""
    tclexec("set afterhandle [after 100 mainloop_tasks]")


def cancel():
    """Cancel the next scheduled mainloop task."""
    tclexec("after cancel $afterhandle")
    tclexec("unset afterhandle")


def mainloop_tasks():
    while tasks:
        fn = tasks.pop()
        fn()
    if not closing_check():
        schedule()  # schedule next run


# Functions -- main entry & debug

def debug():
    cancel()
    breakpoint()
    schedule()


# Focus & Cue-ing

def cue(tkname=None):
    """Set tk's $w to tkname or currently focused window.
    
    Very importantly: tkname may contain substitutions, allowing for
    indirect referencing of window names.  For example, "$top.foo" can
    be used to point to a window on a top level identified by tcl
    variable "top".  (see: cue_top, for example)
    
    This is commonly used in the tcl_code executed to customize a
    newly created window.
    """
    if tkname is None:
        tkname = focused()
    else:
        tkname = tcltalk.subst(tkname)
    poke("w", tkname)

def cue_top():
    """Sets tk's $top to toplevel for $w."""
    poke("top", top())

def cur():
    return peek("w")

def exists():
    """Return True if the cue'd window still exists."""
    return tclexec("winfo exists $w") == '1'

def top():
    """Returns the toplevel for $w."""
    return tclexec("winfo toplevel $w")

def name():
    """Returns the name of $w, alone, without parents"""
    return tclexec("winfo name $w")

def wtype():
    """Returns the "window type" of $w.
    
    Important notes:
    * "window type" is not a tk concept;
      rather, Tk refers to a window's "class";
      see "winfo class" for more on this context
    * "window type" is made up by me, and consists of a matching symbol;
      presently (2021-10-09), I support here the symbols:
        ENTRY, TEXT, and LISTBOX
    * if a matching symbol is not found, returns the window class, per Tk
    * HOWEVER: you should not use the window class --
      instead, I want you to extend symbols.py with a symbol to correspond
      with the window class, and that will be known as the window's "type"
    * because type is already used and essential to Python,
      I call the window type "wtype"
    """
    x = tclexec("winfo class $w")
    if x == "TEntry":
        return ENTRY
    elif x == "Text":
        return TEXT
    elif x == "Listbox":
        return LISTBOX
    elif x == "TLabel":
        return LABEL
    else:
        return x

def children():
    """Return the path names of the children of $w, as a list"""
    return tclexec("winfo children $w").split()


def destroy():
    """Destroy the cue'd window."""
    tclexec("destroy $w")


def text_get():
    """Return text from the cue'd window."""
    wt = wtype()
    if wt == ENTRY:
        return tclexec("$w get")
    elif wt == TEXT:
        return tclexec("$w get 1.0 end")
    else:
        raise ValueError("$w type not recognized")

def text_set(s):
    """Set text into the cue'd window."""
    wt = wtype()
    if wt == ENTRY:
        poke("tmp", s)
        tclexec("$w delete 0 end")
        tclexec("$w insert 0 $tmp")
    elif wt == TEXT:
        poke("tmp", s)
        tclexec("$w delete 1.0 end")
        tclexec("$w insert 1.0 $tmp")
    elif wt == LABEL:
        poke("tmp", s)
        tclexec("$w configure -text $tmp")
    else:
        raise ValueError("$w type not recognized")

def text_ro():
    """Make text in the cue'd window read-only."""
    wt = wtype()
    if wt == ENTRY:
        tclexec("$w configure -state readonly")  # can select, but not write
    elif wt == TEXT:
        tclexec("$w configure -state disabled")  # "readonly" doesn't exist for text
    else:
        raise ValueError("$w type not recognized")

def text_rw():
    """Make text in the cue'd window read-write."""
    wt = wtype()
    if wt == ENTRY:
        tclexec("$w configure -state normal")
    elif wt == TEXT:
        tclexec("$w configure -state normal")
    else:
        raise ValueError("$w type not recognized")

def text_see_end():
    """Put the end into view."""
    wt = wtype()
    if wt == TEXT:
        tclexec("$w see end")
    else:
        raise ValueError("$w type not recognized for text_see_end()")


def list_clear():
    tclexec("$w delete 0 end")

def list_add(s):
    poke("tmp", s)
    tclexec("$w insert end $tmp")

def list_set(L):
    list_clear()
    for x in L:
        list_add(x)

def list_selected():
    return tclexec("$w get [$w curselection]")
    

def focused():
    """Return tkname of current Tk focused window.
    
    WARNING: While debugging, if the toplevel is no longer focused,
             you're going to get an empty string back, which,
             technically speaking, is correct.
    """
    return tclexec("focus")


# Top-Level Management

def lift():
    """Raise the cue'd window to the top level."""
    tclexec("focus $w")
    tclexec("raise [winfo toplevel $w]")

def title(ttl):
    """Reset the title of the cue'd window's toplevel."""
    poke("tmp", ttl)
    tclexec("wm title [winfo toplevel $w] $tmp")

def toplevels():
    return tclexec("winfo children .").split()

def toplevel_unique(tkname):
    """Create or lift a unique toplevel.
    
    If it was NOT already created,
      - the window is created,
XXX   - it is hooked up for WM_DELETE_WINDOW (so it'll close)
      - returns True (meaning: a NEW window)

    If it was already there, though,
      - returns False (meaning: a PRE-EXISTING window)

    In both cases,
      - $w points to the toplevel
      - $top points to the toplevel
      - the toplevel window is lifted to the top
    
    NOTE: Formerly, this function titled the window.
          That activity is now left to the caller.
    """
    cue(tkname)
    makeit = not exists()
    if makeit:
        tclexec("toplevel $w")
#       tclexec("wm protocol $w WM_DELETE_WINDOW wm_delete_window")
    lift()
    cue_top()
    return makeit

def toplevel_recurring(tkname_prefix):
    """Create a new top-level, and set $top to, and return, its tkname."""
    tkname = tkname_prefix + str(nextid())
    cue(tkname)
    tclexec("toplevel $w")
#   tclexec("wm protocol $w WM_DELETE_WINDOW wm_delete_window")
    lift()
    cue_top()
    return tkname


