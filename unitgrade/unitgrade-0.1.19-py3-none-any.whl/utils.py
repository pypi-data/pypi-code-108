import re
import sys
import threading
import time
from collections import namedtuple
from io import StringIO
import numpy as np
import tqdm
from colorama import Fore
from functools import _make_key

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])


def gprint(s):
    print(f"{Fore.GREEN}{s}")


myround = lambda x: np.round(x)  # required for obfuscation.
msum = lambda x: sum(x)
mfloor = lambda x: np.floor(x)


class Logger(object):
    def __init__(self, buffer, write_to_stdout=True):
        # assert False
        self.terminal = sys.stdout
        self.write_to_stdout = write_to_stdout
        self.log = buffer

    def write(self, message):
        if self.write_to_stdout:
            self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        pass


class Capturing(list):
    def __init__(self, *args, stdout=None, unmute=False, **kwargs):
        self._stdout = stdout
        self.unmute = unmute
        super().__init__(*args, **kwargs)

    def __enter__(self, capture_errors=True):  # don't put arguments here.
        self._stdout = sys.stdout if self._stdout == None else self._stdout
        self._stringio = StringIO()
        if self.unmute:
            sys.stdout = Logger(self._stringio)
        else:
            sys.stdout = self._stringio

        if capture_errors:
            self._sterr = sys.stderr
            sys.sterr = StringIO()  # memory hole it
        self.capture_errors = capture_errors
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout
        if self.capture_errors:
            sys.sterr = self._sterr


class Capturing2(Capturing):
    def __exit__(self, *args):
        lines = self._stringio.getvalue().splitlines()
        txt = "\n".join(lines)
        numbers = extract_numbers(rm_progress_bar(txt))
        self.extend(lines)
        del self._stringio  # free up some memory
        sys.stdout = self._stdout
        if self.capture_errors:
            sys.sterr = self._sterr

        self.output = txt
        self.numbers = numbers


def rm_progress_bar(txt):
    # More robust version. Apparently length of bar can depend on various factors, so check for order of symbols.
    nlines = []
    for l in txt.splitlines():
        pct = l.find("%")
        ql = False
        if pct > 0:
            i = l.find("|", pct + 1)
            if i > 0 and l.find("|", i + 1) > 0:
                ql = True
        if not ql:
            nlines.append(l)
    return "\n".join(nlines)


class ActiveProgress():
    def __init__(self, t, start=True, title="my progress bar", show_progress_bar=True, file=None):
        if file == None:
            file = sys.stdout
        self.file = file
        # self.t = t
        self._running = False
        self.title = title
        self.dt = 0.025
        self.n = max(1, int(np.round(t / self.dt)))
        self.show_progress_bar = show_progress_bar
        self.pbar = None

        if start:
            self.start()

    def start(self):
        self._running = True
        if self.show_progress_bar:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        self.time_started = time.time()

    def terminate(self):
        if not self._running:
            print("Stopping a progress bar which is not running (class unitgrade.utils.ActiveProgress")
            pass
            # raise Exception("Stopping a stopped progress bar. ")
        self._running = False
        if self.show_progress_bar:
            self.thread.join()
        if self.pbar is not None:
            self.pbar.update(1)
            self.pbar.close()
            self.pbar = None

        self.file.flush()
        return time.time() - self.time_started

    def run(self):
        self.pbar = tqdm.tqdm(total=self.n, file=self.file, position=0, leave=False, desc=self.title, ncols=100,
                              bar_format='{l_bar}{bar}| [{elapsed}<{remaining}]')
        t_ = time.time()
        for _ in range(self.n - 1):  # Don't terminate completely; leave bar at 99% done until terminate.
            if not self._running:
                self.pbar.close()
                self.pbar = None
                break
            tc = time.time()
            tic = max(0, self.dt - (tc - t_))
            if tic > 0:
                time.sleep(tic)
            t_ = time.time()
            self.pbar.update(1)


def dprint(first, last, nL, extra = "", file=None, dotsym='.', color='white'):
    if file == None:
        file = sys.stdout
    dot_parts = (dotsym * max(0, nL - len(last) - len(first)))
    print(first + dot_parts, end="", file=file)
    last += extra
    print(last, file=file)


def hide(func):
    return func


def makeRegisteringDecorator(foreignDecorator):
    """
        Returns a copy of foreignDecorator, which is identical in every
        way(*), except also appends a .decorator property to the callable it
        spits out.
    """

    def newDecorator(func):
        # Call to newDecorator(method)
        # Exactly like old decorator, but output keeps track of what decorated it
        R = foreignDecorator(func)  # apply foreignDecorator, like call to foreignDecorator(method) would have done
        R.decorator = newDecorator  # keep track of decorator
        # R.original = func         # might as well keep track of everything!
        return R

    newDecorator.__name__ = foreignDecorator.__name__
    newDecorator.__doc__ = foreignDecorator.__doc__
    return newDecorator


hide = makeRegisteringDecorator(hide)


def extract_numbers(txt):
    numeric_const_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
    rx = re.compile(numeric_const_pattern, re.VERBOSE)
    all = rx.findall(txt)
    all = [float(a) if ('.' in a or "e" in a) else int(a) for a in all]
    if len(all) > 500:
        print(txt)
        raise Exception("unitgrade_v1.unitgrade_v1.py: Warning, too many numbers!", len(all))
    return all


def cache(foo, typed=False):
    """ Magic cache wrapper
    https://github.com/python/cpython/blob/main/Lib/functools.py
    """
    maxsize = None
    def wrapper(self, *args, **kwargs):
        key = (self.cache_id(), ("@cache", foo.__name__, _make_key(args, kwargs, typed)))
        # print(self._cache.keys())
        if not self._cache_contains(key):
            value = foo(self, *args, **kwargs)
            self._cache_put(key, value)
        else:
            value = self._cache_get(key)
        return value

    return wrapper


def methodsWithDecorator(cls, decorator):
    """
        Returns all methods in CLS with DECORATOR as the
        outermost decorator.

        DECORATOR must be a "registering decorator"; one
        can make any decorator "registering" via the
        makeRegisteringDecorator function.

        import inspect
        ls = list(methodsWithDecorator(GeneratorQuestion, deco))
        for f in ls:
            print(inspect.getsourcelines(f) ) # How to get all hidden questions.
    """
    for maybeDecorated in cls.__dict__.values():
        if hasattr(maybeDecorated, 'decorator'):
            if maybeDecorated.decorator == decorator:
                print(maybeDecorated)
                yield maybeDecorated