#!c:/Python24/python
"""
    ProgressBar.py                   Nat Goodspeed
    Copyright (C) 2006               Nat Goodspeed

Present a ProgressBar class for use by a procedural console script. Such
scripts often kick off processing that runs for a long time, such as copying a
big file or generating tons of success messages. We want a non-GUI script to
be able to put up a temporary GUI progress-bar dialog for just that part of
its processing. Part of the point of this module is that our ProgressBar class
does "something reasonable" on any box:

- If wxPython is installed, use wxPython's ProgressDialog
- Otherwise, on a Mac, use EasyDialogs.ProgressBar
- On Linux, use zenity
- Fall back to a hand-drawn Tkinter progress bar
- Otherwise use a stream of self-overwriting messages on sys.stdout

Also support mixins to automatically supplement a ProgressBar's label messages
with information such as N of M items, percent complete, a running estimate of
time to completion and so forth.

NRG 06/22/06
NRG 2014-02-13 Refactor to use registry of factory functions, deferring
    pertinent imports until the first time we're asked to construct a progress
    bar since some errors don't manifest until then. Add Tkinter-based
    ProgressMeter implementation found on unpythonic.net. Add zenity-based
    implementation for Linux. EasyDialogs.ProgressBar seems hosed on OS X
    10.7.5; leaving in place for now.
NRG 2014-09-14 Migrate ProgressTimer and time display functions to timing
    module. Add Throttle mixin.
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import datetime
import time
from .timing import ProgressTimer, pickUnits, duration, format_time

# ****************************************************************************
#   TODO:
# - Figure out how to resize GUI windows to accommodate long text.
# - Allow extra kwd arguments for mixin constructors, e.g. timer start=.
# ****************************************************************************

class ProgressError(Exception):
    pass

# ****************************************************************************
#   Factory functions registry
# ****************************************************************************
class factory(object):
    """
    Usage:

    @factory("description")
    def make_a_particular_kind_of_progress_bar(mixins, ...):
        ...

    Register the decorated function as a progress bar factory function. The
    registered function will either raise an exception, or return a progress
    bar (class, instance) that should work in this environment.

    Any exception (from ImportError to our own ProgressError) indicates that
    that factory function is ill-suited to the current environment, and the
    next registered factory function is tried. The exception is silently
    discarded. This places a special burden on each factory function: it must
    be thoroughly debugged in its target environment, since any bug that
    raises an exception will cause it to be unconditionally rejected in every
    environment.

    Each factory function accepts as its first argument a tuple of mixin
    classes, plus any other args/kwds to pass through to the enriched
    implementation class. Each factory function must determine the vanilla
    implementation class for this environment and return
    make_impl_pair(mixins, vanilla, args, kwds).

    A successful factory function returns an instance as well as the class
    because in some environments, the only way to tell whether we can use a
    particular tactic is to actually create a progress bar of that kind, and
    we don't want to waste the effort. It also returns the vanilla
    implementation class so we can later reuse it with other sets of mixins.
    The instance's __class__ attribute tells us the synthesized subclass, but
    what we want to cache is the vanilla implementation class.
    """
    def __init__(self, desc):
        self.desc = desc

    def __call__(self, func):
        ProgressBar._factory_funcs.append((self.desc, func))
        # This is an unusually easy decorator because we're not trying to wrap
        # the decorated function, only register it.
        return func

def make_impl_pair(mixins, vanilla, args, kwds):
    """
    This is the prescribed way for any factory function to return. It accepts:

    - tuple of mixins to be added to the vanilla implementation class
    - the vanilla implementation class appropriate to this environment
    - positional args and keyword kwds to be passed through to the actual
      implementation class constructor.

    It:
    - synthesizes a subclass of that vanilla class with the specified mixins
    - instantiates the subclass
    - returns (vanilla class, subclass instance).

    However, attempting to instantiate the subclass might raise an exception,
    indicating that this vanilla implementation class is unsuitable to the
    current environment.
    """
    if not mixins:
        # If there are no mixins, the derived class IS the vanilla
        # implementation class.
        derived = vanilla
    else:
        # Make a derived class by prepending mixins to the vanilla
        # implementation class. But because mixins conventionally perform left
        # super() traversal, reverse them so mixin messages appear in the
        # order the user expects.
        bases = tuple(reversed(mixins)) + (vanilla,)
        # Generate a class name by glomming together all the other class
        # names.
        name = '_'.join(cls.__name__ for cls in bases)
        # Through the magic of the type() builtin, perform the equivalent of:
        # class name(*bases):
        #     pass
        derived = type(name, bases, {})

    # Instantiate that class with the passed-through args and kwds, and return
    # according to protocol. Note that instantiating the derived class may
    # raise an exception! That's okay, it's our indicator that the selected
    # vanilla implementation class isn't right for this environment, so our
    # caller will try another.
    return (vanilla, derived(*args, **kwds))

# ****************************************************************************
#   ProgressBar
# ****************************************************************************
# The tricky thing about our ProgressBar class is that we don't actually know
# yet how we're going to implement it. So we pick an implementation that works
# and use a Python-style pimpl idiom (forwarding __getattr__() method) to
# delegate to it.
class ProgressBar(object):
    # Depending on the environment, we may need to try a number of different
    # approaches before we find an implementation class on which we can rely.
    # Instead of maintaining a long list of if/elif -- or worse, an ever-more-
    # deeply nested chain of try/except blocks -- the @factory decorator registers
    # each (description, factory function) pair in this list. They are registered
    # in the order they're encountered: the first one that works, reading top to
    # bottom through this file, is the one we'll use.
    _factory_funcs = []

    # Once we've selected an implementation class, cache it here: we don't
    # need or want to run through the whole selection process for each
    # subsequent instance.
    _cached_class = None

    # When our consumer requests mixins, we synthesize an implementation class
    # containing those mixins. But we don't want to synthesize classes
    # redundantly. For each tuple of mixins, cache the synthesized class for
    # later use.
    _class_cache = {}

    def __init__(self, *args, **kwds):
        # We really, really want to let a ProgressBar consumer add mixins. We
        # define a few ourselves; it's a good way to intercept control at the
        # right times. But adding a mixin to THIS class doesn't do it, since
        # all the real work is done by the implementation object. Accept a
        # keyword-only argument specifying the required tuple of mixins.
        # classic implementation of keyword-only argument
        mixins = kwds.pop("mixins", ())

        # Do we already have an implementation class for this specific
        # mixins tuple? If so, use that.
        try:
            impl_class = ProgressBar._class_cache[mixins]
        except KeyError:
            # We do not already have an enriched implementation class for this
            # particular mixins tuple.
            if not ProgressBar._cached_class:
                # This is the first time through: not only do we not have a
                # specific implementation subclass for this mixins tuple, we
                # haven't even picked the right implementation class for this
                # environment. Do so. Sets _cached_class.
                self._impl = self._find_impl(mixins, *args, **kwds)
            else:
                # Although we don't yet have a specific implementation
                # subclass for this mixins tuple, we've already picked the
                # implementation class for this environment. Use
                # make_impl_pair() to synthesize an appropriate implementation
                # subclass and instantiate it. Extract just the implementation
                # instance from the returned tuple.
                self._impl = make_impl_pair(mixins, ProgressBar._cached_class, args, kwds)[1]

            # Remember this specific implementation subclass next time we get
            # called for this same mixins tuple.
            ProgressBar._class_cache[mixins] = self._impl.__class__

        else:
            # We HAVE already seen this same mixins tuple. Previously we used
            # impl_class as its implementation.
            self._impl =  impl_class(*args, **kwds)

    def __getattr__(self, attr):
        return getattr(self._impl, attr)

    def _find_impl(self, mixins, *args, **kwds):
        """
        This method iterates through the registered factory functions to find
        one that works.
        """
        for desc, func in ProgressBar._factory_funcs:
            try:
                vanilla, impl = func(mixins, *args, **kwds)
            except Exception as err:
                # Here would be a plausible place to print (desc,
                # err.__class__.__name__, err) if we suspect that there's an
                # exception we DON'T expect from one of our factory functions.
                ## print "%s implementation raised %s: %s" % \
                ##       (desc, err.__class__.__name__, err)
                ## import traceback
                ## traceback.print_exc()
                continue
            # Ha, this func works in this environment! Cache vanilla class for
            # later.
            ## print "%s implementation selected" % desc
            ProgressBar._cached_class = vanilla
            # and return our implementation instance
            return impl

        # oh oh, NONE of our registered factory functions works!
        ProgressBar._cached_class = ProgressBar.NoImpl
        # This raises the right exception
        ProgressBar.NoImpl()

    class NoImpl(object):
        """
        Bogus class used to cache failure: if we've been through the whole
        list once without finding anything that works, save this as the
        implementation class so that (regardless of mixins!) attempting to
        initialize it again later will raise the same exception.
        """
        def __init__(self, *args, **kwds):
            raise ProgressError("No available ProgressBar implementation "
                                "in this environment -- tried " +
                                ", ".join(desc for desc, func in ProgressBar._factory_funcs))

# ****************************************************************************
#   Implementation base class
# ****************************************************************************
# Define an interface like EasyDialogs.ProgressBar, deferring to virtual
# methods the problem of actually displaying anything.
class ProgressBarImplBase(object):
    """Define the ProgressBar interface -- since we have a number of different
    implementations. This interface is derived from, but slightly extends, the
    EasyDialogs.ProgressBar interface.
    """
    # Typical subclass calls our __init__() after initializing whatever
    # graphical progress bar it supports. In an environment that doesn't
    # support that particular UI framework, that initialization can raise,
    # bypassing our __init__(). But later __del__() will call cleanup(), which
    # references self.live -- normally set by bypassed __init__()! Set a
    # default 'live' value for instances that never get that far.
    live = False

    def __init__(self, title, maxval, label):
        self.titletext = title
        self.labeltext = label
##         print title
        self.set(0, maxval)
        # Because we define __del__(), we might have an implicit call to
        # cleanup() after an explicit call. Some implementations object to
        # multiple cleanup() calls. Prevent that.
        self.live = True

    # A subclass capable of displaying a new title string should override this
    # method
    def title(self, newstr=""):
        self.titletext = newstr

    def label(self, newstr=""):
        self.labeltext = newstr

    def _get_display_label(self):
        """do NOT override this method, override get_display_list() instead!"""
        return ''.join(self.get_display_list())

    def get_display_list(self):
        """
        Mixins override this method to implicitly supplement the label text
        set by label(). The return is a list so we can efficiently add items
        to that list; then _get_display_label() glues it all into a single
        string at the last moment.

        Conventionally, each mixin class will return something like:

        return super(MyMixin, self).get_display_list() + \
               [', new text %s' % stuff]

        The chain of super() calls is what eventually traverses the whole tree
        of mixins. Of course, any given mixin can bypass that call and return
        only ['my value'].
        """
        return [self.labeltext]

    def inc(self, amt=1):
        self.set(self.curval + amt)

    def set(self, value, max=None):
        if max is not None:
            self.maxval = max

        if value < 0:
            value = 0
        elif value > self.maxval:
            value = self.maxval
        self.curval = value

        self.display()

    def __del__(self):
        self.cleanup()

    # Override this to display each progress increment.
    def display(self):
        pass

    # Don't override the public cleanup() method...
    def cleanup(self):
        if self.live:
            self.live = False
            self._cleanup()

    # Override this to make the progress display go away.
    def _cleanup(self):
        pass

# ****************************************************************************
#   Mixins
# ****************************************************************************
class Throttle(object):
    """
    Throttle changes to no more than 5 per second. Over a network X session,
    updating on every set() call can slow down the processing we're trying to
    monitor. While in general I'd want to parameterize the rate, it takes
    enough overhead to parameterize a mixin that it doesn't yet seem
    worthwhile. Use this when the overhead of each display() call far exceeds
    the cost of time.time() -- and where the rate of incoming display() calls
    makes display() itself take a significant fraction of the overall time.
    """
    __quiesce_time = 1./5                 # 200 ms
    __last_display = 0                    # epoch: let first call through

    def display(self):
        now = time.time()
        if (now > self.__last_display) >= self.__quiesce_time:
            __last_display = now
            super(Throttle, self).display()

class Percent(object):
    def get_display_list(self):
        return super(Percent, self).get_display_list() + \
               [" (%s%%)" % int(((100. * self.curval) / self.maxval) + 0.5)]

class NofTotal(object):
    def set(self, value, maxval=None):
        if maxval is not None:
            # Every time our caller changes max, reselect the format string we
            # use for both maxval and curval, and use it to format maxval.
            # ProgressBarImplBase.__init__() always passes initial maxval, so
            # we should be able to count on setting __fmt, __max.
            self.__fmt = self.get_format(maxval)
            self.__max = self.format(maxval)
        super(NofTotal, self).set(value, maxval)

    def get_display_list(self):
        return super(NofTotal, self).get_display_list() + \
               [": %s of %s" % (self.format(self.curval), self.__max)]

    def get_format(self, maxval):
        """
        Find a plausible format string for number values. This default
        implementation tries to find a reasonable human display for floating-
        point values. Override if (for instance) you know you're always
        dealing with int values.
        """
        if maxval < 10:
            fmt = "%.2f"
        elif maxval < 100:
            fmt = "%.1f"
        else:
            fmt = "%d"
        # Now figure out how wide maxval is with that precision
        width = len(fmt % maxval)
        # Set overall format based on that width
        return "%%%s%s" % (width, fmt[1:])

    def format(self, value):
        """override this to use different kinds of units"""
        return self.__fmt % value

class Count(NofTotal):
    """specialize NofTotal for integer counts"""
    def get_format(self, maxval):
        # How wide is maxval with integer formatting?
        width = len("%d" % maxval)
        # overall format uses that width
        return "%%%sd" % width

class Size(NofTotal):
    """specialize NofTotal for size in bytes, kilobytes, megabytes, ..."""
    # Don't bother overriding get_format(); that's only consumed by the base-
    # class default format(). Since we're overriding format(), it's moot.
    def format(self, value):
        return pickUnits(value, 1024, "gb", "mb", "kb", "b")

class TimeBase(object):
    """
    Base class for all time-related mixins. Every such mixin needs access to a
    ProgressTimer object, but ideally, if we want multiple time-based mixins,
    they should all reference the same ProgressTimer instance. Fortunately
    Python de-dups base classes, which gives us what we want.
    """
    def __init__(self, title, maxval, label):
        # For now, initialize the ProgressTimer to start now with count 0.
        # It's significantly trickier to initialize it otherwise.
        self.timer = ProgressTimer(total=maxval)
        super(TimeBase, self).__init__(title, maxval, label)

    def set(self, value, max=None):
        # intercept every set() call to properly update the ProgressTimer
        if max is not None:
            self.timer.total = max
        self.timer.count = value
        # forward the call
        super(TimeBase, self).set(value, max)

class TimeLeft(TimeBase):
    def get_display_list(self):
        return super(TimeLeft, self).get_display_list() + \
               [", ", duration(self.timer.timeleft, levels=2), " remaining"]

class Elapsed(TimeBase):
    def get_display_list(self):
        return super(Elapsed, self).get_display_list() + \
               [", ", duration(self.timer.elapsed, levels=2), " elapsed"]

class TotalTime(TimeBase):
    def get_display_list(self):
        return super(TotalTime, self).get_display_list() + \
               [", ", duration(self.timer.totaltime, levels=2), " overall"]

class Finish(TimeBase):
    def get_display_list(self):
        return super(Finish, self).get_display_list() + \
               self._finish_format(self.timer.finish)

    @staticmethod
    def _finish_format(finish):
        # This formatter for the finish timestamp depends on whether we expect
        # to finish today.
        today = datetime.date.today()
        finishdate = datetime.date.fromtimestamp(finish)
        if finishdate == today:
            # if we'll finish today, don't bother mentioning the date
            dformat = ""
        elif finishdate == today + datetime.timedelta(days=1):
            # if we'll finish tomorrow, say so idiomatically
            dformat = " tomorrow"
        else:
            # otherwise explicitly state the date
            dformat = " %Y-%m-%d"
        # formatter return convention: list of strings
        return [format_time(''.join((", ETA", dformat, " %I:%M %p")), finish)]

def FinishAs(format):
    """
    To use Finish, you just specify Finish in the list of mixins. This
    function is analogous, but parameterized: e.g. FinishAs(', %I:%M %p') (any
    strftime() format). Remember to include leading space and/or punctuation.
    Returns a custom subclass for use as a mixin.
    Don't use FinishAs() in a loop, since every call generates a new class.
    """
    # Beware using a common formatting method that references an overridden
    # class attribute: if the client specifies multiple mixins with that same
    # implementation, only one of the attribute overrides will "win,"
    # duplicating that format instead of providing both messages. Better to
    # bind params directly to the overridden get_display_list() method using
    # (e.g.) lambda or functools.partial().
    return _make_timer_mixin("finish",
                             lambda finish: [format_time(format, finish)])


def ElapsedAs(formatter):
    """formatter: callable(elapsed) which returns a list of strings"""
    return _make_timer_mixin("elapsed", formatter)

def TimeLeftAs(formatter):
    """formatter: callable(timeleft) which returns a list of strings"""
    return _make_timer_mixin("timeleft", formatter)

def TotalTimeAs(formatter):
    """formatter: callable(totaltime) which returns a list of strings"""
    return _make_timer_mixin("totaltime", formatter)

# module-static counter used to ensure uniqueness of generated class names
_unique = 0

def _make_timer_mixin(attr, formatter):
    """
    Helper for MumbleAs() timer mixin functions.
    attr:      string name of ProgressTimer attribute to format
    formatter: callable(attr value) returning list of strings
    """
    # Start with a unique name
    global _unique
    subclassname = "TimerMixin_%s" % _unique
    _unique += 1
    # This type() call is equivalent to:
    # class subclassname(TimeBase):
    #     pass
    subclass = type(subclassname, (TimeBase,), {})
    # We generate the class before overriding its get_display_list() method
    # because our get_display_list() override needs to reference its own class
    # object (in the super() call).
    subclass.get_display_list = lambda self: \
        super(subclass, self).get_display_list() + \
        formatter(getattr(self.timer, attr))
    return subclass


# ****************************************************************************
#   wx
# ****************************************************************************
# If wxPython is installed on the host system, use that, no matter what
# platform we're running on.
@factory("wx")
def make_wx_progress_bar(mixins, *args, **kwds):
    # ImportError here will just kick us out to try the next registered
    # factory function.
    import wx

    # wx won't let us open a ProgressDialog until we've instantiated an App
    # object. Instantiate it just once for the module so that we can be used
    # for multiple copy2() calls without worrying about instantiating multiple
    # App objects.
    global _app
    try:
        # Set redirect=False because we assume our caller is a console script
        # that just wants to pop up a progress dialog during copy operations.
        # If we allow redirect to default to True, then we also get a little
        # wx App window containing stdout while the progress dialog is displayed.
        _app = wx.App(redirect=False)
    except:
        # It may even be that whoever imports this module already has a wx.App
        # instance in hand. We don't know how wx reacts to multiple App
        # instances -- but if our caller already has one, use theirs; we don't
        # need ours to succeed in that case. Notice that we never again
        # reference it.
        pass

    class ProgressBarImpl(ProgressBarImplBase, wx.ProgressDialog):
        """ProgressBar implementation based on wxPython's ProgressDialog"""
        def __init__(self, title, maxval, label):
            wx.ProgressDialog.__init__(self, title, label, maxval,
                                       style=wx.PD_SMOOTH|wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|
                                       wx.PD_ESTIMATED_TIME|wx.PD_REMAINING_TIME)
            # We can only do ProgressBarImplBase initialization once we have
            # enough machinery in place to be able to call display().
            ProgressBarImplBase.__init__(self, title, maxval, label)
            self.Show(True)

        def title(self, newstr=""):
            self.SetTitle(newstr)

        def display(self):
            self.Update(self.curval, self._get_display_label())

        def _cleanup(self):
            self.Destroy()

    return make_impl_pair(mixins, ProgressBarImpl, args, kwds)

# ****************************************************************************
#   zenity
# ****************************************************************************
# Put the zenity implementation before the Tkinter implementation. We expect
# Tkinter will work most everywhere; however, on at least one Ubuntu box, the
# Tkinter pack() call doesn't seem to work well: we get a strangely-shaped
# (default?) containing window that truncates the progress bar. For that
# system and any others like it, prefer the zenity implementation.
@factory("zenity")
def make_zenity_progress_bar(mixins, *args, **kwds):
    import subprocess

    class ProgressBarImpl(ProgressBarImplBase):
        def __init__(self, title, maxval, label):
            # This may throw if we can't find zenity on the PATH.
            self.bar = subprocess.Popen(
                ["zenity", "--progress",
                 "--title", title,
                 "--text", label,
                 "--percentage", "0",
                 "--width", "400",
                 "--no-cancel",
                 "--auto-close"],
                stdin=subprocess.PIPE)

            # Now initialize ProgressBarImplBase
            ProgressBarImplBase.__init__(self, title, maxval, label)

        def display(self):
            # This is a little tricky for two reasons.
            # First, we have to quantize to an int percentage. That shouldn't
            # lose any perceptible accuracy.
            percent = int((100. * self.curval)/self.maxval + 0.5)
            # Second, though, we use zenity's --auto-close switch. That has
            # the desirable effect of suppressing the OK button; for our
            # purposes the progress bar is informational only, not a way for
            # the user to interact with the invoking script. But --auto-close
            # means that as soon as we send 100, the progress bar vanishes!
            # What if our caller wants to set 100% and leave it there, perhaps
            # with some updated message, for a moment or two? So even if
            # quantization produces 100%, clamp to 99%, reserving 100 for
            # _cleanup().
            if percent == 100:
                percent = 99
            # The way we talk to zenity is to send it input lines. A line
            # containing only an int percentage sets the progress; a line
            # starting with '#' sets the label; zenity ignores all other lines.
            self.bar.stdin.write("%s\n#%s\n" % (percent, self._get_display_label()))

        def _cleanup(self):
            # Send the magic final token to engage --auto-close.
            self.bar.stdin.write("100\n")
            self.bar.wait()

    return make_impl_pair(mixins, ProgressBarImpl, args, kwds)

# ****************************************************************************
#   EasyDialogs
# ****************************************************************************
@factory("EasyDialogs")
def make_EasyDialogs_progress_bar(mixins, *args, **kwds):
    # EasyDialogs is bundled with every Mac Python
    import EasyDialogs.ProgressBar

    # managed to import EasyDialogs.ProgressBar
    class ProgressBarImpl(EasyDialogs.ProgressBar):
        """ProgressBar implementation based on EasyDialogs.ProgressBar"""
        def __init__(self, *args, **kwds):
            # We intercept __init__() for a peculiar reason. Our
            # TimedProgressBar subclass's set() override wants to
            # reference curval before forwarding the call to the
            # base-class set() method. But the base-class constructor
            # apparently calls set() for the purpose of initializing
            # curval! Our subclass set() ends up referencing curval before
            # it exists. Fix that here.
            self.curval = 0
            EasyDialogs.ProgressBar.__init__(self, *args, **kwds)

        # Our own ProgressBarImplBase class does define one more method than
        # EasyDialogs.ProgressBar, hence this subclass.
        def cleanup(self):
            pass

    return make_impl_pair(mixins, ProgressBarImpl, args, kwds)

# ****************************************************************************
#   Tix.Meter
# ****************************************************************************
# I was excited to read about Tix.Meter (a Tk-based progress bar). But
# although Tix is bundled with Python since about Python 2.2, although I
# can find the Tix module itself, every attempt to invoke Tix.Meter() (on
# each of a number of platforms) results in a TCL error to the effect that
# "tixMeter" is an unknown command. Apparently that's just a documentation
# error, sigh! Don't even bother registering this factory.
##@factory("Tix.Meter")
def make_Tix_Meter_progress_bar(mixins, *args, **kwds):
    import tkinter.tix
    # discover the name of the main script
    import __main__

    class ProgressBarImpl(ProgressBarImplBase, tkinter.tix.Frame):
        def __init__(self, title, maxval, label, master=None):
            tkinter.tix.Frame.__init__(self, master)
            # Change our title from the default 'tk' to the name of the main script.
            self.master.title(os.path.splitext(os.path.basename(__main__.__file__))[0])
            self.pack()

            # Our window has just one control, a Meter.
            self.bar = tkinter.tix.Meter()
            self.bar.pack()

            # Can't do ProgressBarImplBase initialization until we have enough
            # machinery in place to be able to call display().
            ProgressBarImplBase.__init__(self, title, maxval, label)

            # display the window right away
            self.update()

        def display(self):
            self.bar.config(value=float(self.curval)/self.maxval)

    return make_impl_pair(mixins, ProgressBarImpl, args, kwds)

# ****************************************************************************
#   ProgressMeter
# ****************************************************************************
# Fortunately somebody posted a ProgressMeter class -- but their Meter is
# just the widget. We must still wrap it in a frame.
@factory("ProgressMeter")
def make_ProgressMeter_progress_bar(mixins, *args, **kwds):
    import tkinter
    from .ProgressMeter import Meter, center

    class ProgressBarImpl(ProgressBarImplBase, tkinter.Frame):
        def __init__(self, title, maxval, label, master=None):
            tkinter.Frame.__init__(self, master)
            # before fooling with this Frame, make it invisible
            self.master.withdraw()
            # set title of this Frame
            self.master.title(title)
            self.pack()

            # Our Frame has just one control: the Meter
            self.bar = Meter(self.master, relief="ridge", bd=3)
            self.bar.pack(fill='x')

            center(self.master)

            # Try to make this the topmost window. Otherwise it has a
            # distressing tendency to hide behind our own console window.
            try:
                # Documentation indicates that -topmost is platform-specific,
                # though it has worked so far each place we've tried it.
                self.master.wm_attributes("-topmost", 1)
            except Exception as err:
                print("Attempting to set Tkinter ProgressBar topmost produced %s: %s" % \
                      (err.__class__.__name__, err))

            # Initialize ProgressBarImplBase now that we have enough in place
            # to call display()
            ProgressBarImplBase.__init__(self, title, maxval, label)

            # display immediately
            self.update()

        def display(self):
            self.bar.set(self.curval / float(self.maxval), self._get_display_label())

        def _cleanup(self):
            self.master.destroy()

    # attempting to instantiate a Tk object might raise Tkinter.TclError
    return make_impl_pair(mixins, ProgressBarImpl, args, kwds)

# ****************************************************************************
#   FakeProgressBar
# ****************************************************************************
# If this isn't a platform we recognize, simulate the ProgressBar interface
# using ersatz console machinery.
# Define _FakeProgressBarImpl at import time because we don't expect the
# definition to fail: the implementation doesn't depend on any external
# modules. We call it FakeProgressBar because, even if one of our
# ProgressBarImpl definitions succeeds, we can imagine some consuming module
# choosing to use FakeProgressBar (inline progress on the console) instead of
# any GUI one.
class _FakeProgressBarImpl(ProgressBarImplBase):
    """
    stdout-based ProgressBar implementation for when we don't seem to have a
    GUI-based one available.
    """
    def __init__(self, title, maxval, label):
        # Since we don't expect to produce visual cues about how we're doing,
        # implicitly add the Percent mixin.
        try:
            # MAGIC: synthesize a class which splices the Percent mixin into
            # our current class -- and dynamically update this instance's
            # class.
            # Find where _FakeProgressBarImpl is in our actual leaf class's
            # MRO. Convert to list first because index() isn't defined on
            # tuple. If our leaf class doesn't even derive from
            # _FakeProgressBarImpl, things are VERY screwy! In that case just
            # let the ValueError propagate.
            pos = list(self.__class__.__mro__).index(_FakeProgressBarImpl)
            # Split MRO into (classes up to and including
            # _FakeProgressBarImpl) and (classes after _FakeProgressBarImpl).
            before = self.__class__.__mro__[:pos+1]
            after  = self.__class__.__mro__[pos+1:]
            # Construct a tuple that inserts Percent at that point in the
            # list, immediately after _FakeProgressBarImpl. That will become
            # our new set of base classes.
            self.__class__ = type("Percent_" + self.__class__.__name__,
                                  before + (Percent,) + after,
                                  {})
            # Why don't we simply prepend Percent to self.__class__ and call
            # it good? It's because we reached this __init__() method by
            # following a chain of super() calls. super(SomeClass, self)
            # locates SomeClass in self's MRO and directs the call to the next
            # class in that tuple. Supposing that our current 'self' object is
            # actually an instance of a _FakeProgressBarImpl subclass -- that
            # is, we already have some set of mixins -- Python has already
            # called all the __init__() methods in the MRO list, up to and
            # including this _FakeProgressBarImpl.__init__(). We don't want to
            # call any of them twice -- ESPECIALLY not this one! By splicing
            # Percent into the MRO immediately after _FakeProgressBarImpl,
            # we've arranged for our own super() call to pass control to that,
            # and so forth.
        except TypeError:
            # Python will raise TypeError if Percent is already in
            # self.__class__'s inheritance hierarchy. That's fine, we don't
            # want it in there twice!
            pass

        ## print "_FakeProgressBarImpl is now %s -- mro: %s" % \
        ##       (self.__class__.__name__, ", ".join(cls.__name__ for cls in self.__class__.__mro__))
        # If a title is passed, print that on a separate line. We don't
        # override title() because it would be awkward (and consume output
        # lines we don't want to consume) to update it; but we can at least
        # show the initial title. Suppress by passing the empty string.
        if title:
            print(title + ':')
        # Continue initializing: this should pass control to
        # Percent.__init__(), and onward from there.
        super(_FakeProgressBarImpl, self).__init__(title, maxval, label)

    def display(self):
        print("\r" + self._get_display_label(), end=' ')
        sys.stdout.flush()

    def _cleanup(self):
        print()

def FakeProgressBar(*args, **kwds):
    """Use this entry point if you specifically want a FakeProgressBar"""
    mixins = kwds.pop("mixins", ())
    # make_impl_pair() returns (vanilla, instance); only return instance
    return make_impl_pair(mixins, _FakeProgressBarImpl, args, kwds)[1]

# ****************************************************************************
#   AnsiProgressBar
# ****************************************************************************
# How to support both message and progress bar when you only have one text
# row? Inverse video!
class _AnsiProgressBarImpl(_FakeProgressBarImpl):
    # The hardcoded \033[...m sequences are because I can't find any clue that
    # ANSI escapes are present in a standard Python bundle, other than in
    # curses, and the curses symbols are all buried inside the _curses
    # extension.
    baron  = "\033[7m"
    baroff = "\033[m"

    def __init__(self, *args, **kwds):
        # Try to find out how wide terminal is; then subtract a bit just
        # because. In an xterm this value is adjusted as you resize the
        # window; in an emacs shell buffer it appears to be a snapshot of the
        # width at the moment you started the shell.
        self.width = int(os.environ.get("COLUMNS", 80)) - 2
        super(_AnsiProgressBarImpl, self).__init__(*args, **kwds)

    def display(self):
        # Quantize the "progress bar" inverse video block to self.width
        invert = int((self.width * self.curval)/float(self.maxval) + 0.5)
        # Have to pad out to that character width
        text = self._get_display_label().ljust(invert)
        # The leading space is because emacs's ANSI recognition seems to be
        # fooled by an escape character immediately following a CR.
        sys.stdout.writelines(("\r ", self.baron, text[:invert], self.baroff, text[invert:]))
        sys.stdout.flush()

# Although a modern emacs comint buffer does scan ANSI escapes, it doesn't
# seem to properly support inverse video: it changes the foreground color but
# not the background color. That's not really useful for observing progress.
# Use underscores instead of inverse video for that case.
class _ScoreProgressBarImpl(_AnsiProgressBarImpl):
    baron = "\033[4m"

def AnsiProgressBar(*args, **kwds):
    """Use this entry point if you want an AnsiProgressBar"""
    mixins = kwds.pop("mixins", ())
    # use same logic as when we find no GUI implementation
    return make_ansi_progress_bar(mixins, *args, **kwds)[1]

@factory("fake")
def make_ansi_progress_bar(mixins, *args, **kwds):
    # ANSI escapes work in xterm-like emulators, also in emacs comint (shell)
    # buffers for emacs > 23.1. They do not work in emacs compile buffers, nor
    # do they work for emacs <= 23.1. The environment variable INSIDE_EMACS is:
    # - nonexistent outside emacs, of course, or in an old emacs
    # - t in a recent emacs compile buffer
    # - a string like '23.1.1,comint' in a recent emacs comint buffer.
    try:
        INSIDE_EMACS = os.environ["INSIDE_EMACS"]

    except KeyError:
        # Here we're either not inside emacs at all, or in a very old emacs. I
        # wish we didn't have to clear the display to coax Python to read
        # terminfo! I'd like to be able to ask whether this TERM string
        # supports inverse video -- but without modifying the display. As it
        # is, we have a choice of either blacklist or whitelist. These days,
        # the list of TERM values that do NOT support ANSI escapes is probably
        # shorter.
        if os.environ.get("TERM", "dumb") in ["dumb"]:
            vanilla = _FakeProgressBarImpl
        else:
            # Hmm, hope for the best
            vanilla = _AnsiProgressBarImpl

    else:
        # INSIDE_EMACS exists. Try to parse "major.minor.patch,buftype" syntax.
        try:
            version = [int(p) for p in INSIDE_EMACS.split(',')[0].split('.')]

        except ValueError:
            # If we don't find that (e.g. "t" in compile buffer), assume dumb.
            vanilla = _FakeProgressBarImpl

        else:
            # managed to parse version; check it
            if version[:2] <= [23, 1]:
                vanilla = _FakeProgressBarImpl

            else:
                # Here we believe we have a recent emacs version. At least as
                # of emacs 24, underscores seem to work better than inverse
                # video.
                vanilla = _ScoreProgressBarImpl

    return make_impl_pair(mixins, vanilla, args, kwds)

# ****************************************************************************
#   Streams
# ****************************************************************************
class ProgressStream(object):
    """
    Bind a ProgressBar and an input sequence, and run a generator that watches
    items going by in the sequence, advancing the progress bar as we go. This
    is used for monitoring a stream, e.g. of file buffers during a long copy
    operation.
    """
    def __init__(self, title, maxval, label, bar=ProgressBar):
        try:
            self.bar = bar(title, maxval, label)
        except:
            # Frankly, we don't know what a real ProgressBar might do if we're
            # running an unattended overnight task with no access to a user
            # session. Will it be silently ignored, or will it throw an
            # exception? In the latter case, substitute a no-op version. Don't
            # even bother with the fake console one: if the real problem is
            # that we're running without a display screen available, we
            # certainly don't want all the block-by-block progress messages
            # e-mailed to us!
            self.bar = ProgressBarImplBase(title, maxval, label)

    def __call__(self, iterable):
        # Now forward each item in the iterable -- but give the subclass a
        # chance to respond (e.g. by advancing the ProgressBar) for each one.
        for item in iterable:
            yield item
            self.respond(item)
        self.bar.cleanup()

    def respond(self, item):
        """Override this in subclass"""
        raise NotImplementedError

class CountProgressStream(ProgressStream):
    def __init__(self, title, maxval, bar=ProgressBar):
        ProgressStream.__init__(self, title, maxval, "0 of %s" % maxval, bar=bar)
        self.count = 0

    def respond(self, item):
        self.count += 1
        self.bar.label("%s of %s" % (self.count, self.bar.maxval))
        self.bar.set(self.count)

class SizeProgressStream(ProgressStream):
    def __init__(self, title, maxval, bar=ProgressBar):
        self.maxdesc = self.pickUnits(maxval)
        ProgressStream.__init__(self, title, maxval, "0 b of %s" % self.maxdesc, bar=bar)
        self.bytes = 0

    def respond(self, item):
        self.bytes += len(item)
        self.bar.label("%s of %s" % (self.pickUnits(self.bytes), self.maxdesc))
        self.bar.set(self.bytes)

    @staticmethod
    def pickUnits(bytes):
        return pickUnits(bytes, 1024, "gb", "mb", "kb", "b")

# ****************************************************************************
#   test code
# ****************************************************************************
if __name__ == "__main__":
    ## for scale in 9.,: # 99., 999.:
    ##     bar = ProgressBar("%N progress bar demo", scale, "demo in progress",
    ##                       mixins=(Percent, Count))
    ##     for tick in xrange(100):
    ##         bar.set(scale*tick/100)
    ##         time.sleep(0.05)
    ##     bar.label("done!")
    ##     bar.set(scale)
    ##     time.sleep(1)
    ##     bar.cleanup()

    ## bar = ProgressBar("N progress bar demo", 10, "demo in progress",
    ##                   mixins=(Count,))
    ## for x in xrange(10):
    ##     bar.set(x)
    ##     time.sleep(0.1)
    ## bar.label("done!")
    ## bar.set(10)
    ## time.sleep(1)
    ## bar.cleanup()

    ## bar = ProgressBar("no % progress bar demo", 10, "demo in progress")
    ## for x in xrange(10):
    ##     bar.set(x)
    ##     time.sleep(0.1)
    ## bar.label("done!")
    ## bar.set(10)
    ## time.sleep(1)
    ## bar.cleanup()

    import itertools
    from functools import partial

    def dumbfmt(word, duration):
        mins, secs = divmod(int(duration), 60)
        hrs, mins = divmod(mins, 60)
        return [", %d:%02d:%02d %s" % (hrs, mins, secs, word)]

    tmixins = [
        (("Elapsed", Elapsed),
         ("ElapsedAs()", ElapsedAs(partial(dumbfmt, "(so far)")))),
        (("TimeLeft", TimeLeft),
         ("TimeLeftAs", TimeLeftAs(partial(dumbfmt, "(left)")))),
        (("TotalTime", TotalTime),
         ("TotalTimeAs", TotalTimeAs(partial(dumbfmt, "(total)")))),
        (("Finish", Finish),
         ("FinishAs", FinishAs(": (%b %d %Y at %H:%M)"))),
        ]

    def mixin_tuples(possibles):
        # Each level of recursion returns a tuple containing (desc, mixin)
        # pairs. At recursion tail, empty tuple kicks things off.
        if not possibles:
            yield ()
            return
        # At each level of recursion, possibles[0] is a tuple of (desc, mixin)
        # pairs to try. The tricky thing is that to generate exhaustive
        # subsets, we also want to try without any of possibles[0]. Our
        # generator expression produces a 1-tuple from each pair in
        # possibles[0]; to those alternatives we prepend the empty tuple.
        for tup in itertools.chain([()],
                                   ((pair,) for pair in possibles[0])):
            # Now that we have a tuple to try at this level of recursion,
            # prepend it to every possibility at the next level.
            for rest in mixin_tuples(possibles[1:]):
                yield tup + rest

    try:
        for sequence in mixin_tuples(tmixins):
            # Ideally we'd like to transpose ((desc1, mixin1), ...) sequence to
            # ((desc1, desc2, ...), (mixin1, mixin2, ...)). The wonderfully
            # obscure map(None, *sequence) almost does it for us -- but map()
            # distinguishes between single/multiple iterable args. In the single
            # case, it produces single items instead of a 1-tuple. While in
            # general that would be intuitive, for us it introduces a special case
            # that throws the whole thing out the window. Sigh.
            descs = ", ".join(desc for desc, mixin in sequence)
            print()
            bar = AnsiProgressBar(descs, 4, "work",
                                  mixins=tuple(mixin for desc, mixin in sequence))
            for x in range(4):
                bar.set(x)
                time.sleep(0.5)
            ## bar.label("done")
            ## bar.set(4)
            bar.cleanup()

        # compute a completion time tomorrow (test Finish)
        timedone = (datetime.datetime.now() + datetime.timedelta(minutes=10)).time()
        oneday   = datetime.timedelta(days=1)
        today    = datetime.date.today()
        tomorrow = today + oneday
        dayafter = tomorrow + oneday
        for desc, finishday in (("today", today),
                                ("tomorrow", tomorrow),
                                ("day after", dayafter)):
            finish = datetime.datetime.combine(finishday, timedone)
            finisht = time.mktime(finish.timetuple())
            totaltime = finisht - time.time()
            # totaltime is in seconds, so totaltime*2 is the number of
            # half-second ticks it would take us to get there.
            print()
            bar = AnsiProgressBar(desc, int(totaltime*2), "work",
                                  mixins=(Finish,))
            for x in range(3):
                bar.set(x)
                time.sleep(0.5)
            bar.cleanup()

    except KeyboardInterrupt:
        pass
