#!/usr/bin/env python3

from __future__ import print_function
from inspect import stack, getframeinfo
import os
import sys
import time
import datetime
import inspect
import functools
import traceback

class Logging:

    ''' Constructor
        @param [in] dblspace    - True to double space output
        @param [in] linetmpl    - Line templates

                                    ts          = timestamp
                                    file        = filename
                                    line        = line number
                                    function    = Function name

                                    Examples:
                                        '[<<ts>>] <<file>>(<<line>>): '                 -> [10:06:37] ./test.py(147):
                                        '[<<ts>>] <<file>>::<<function>>(<<line>>): '   -> [10:08:47] ./test.py::test_5(147):

        @param [in] tstmpl      - Timestamp template
                                    Examples:
                                        '%H:%M:%S'

        @param [in] reldir      - Relative directory to files to show in logs
                                    None    = Full paths
                                    '-'     = No paths
                                    '.'     = Relative to current working directory
                                    ...     = Relative to specified path
    '''
    def __init__(self, dblspace=False, linetmpl=None, tstmpl='%H:%M:%S', reldir='.'):
        self.console_colors = {
            'BLACK'     : '\033[90m',
            'RED'       : '\033[91m',
            'GREEN'     : '\033[92m',
            'YELLOW'    : '\033[93m',
            'BLUE'      : '\033[94m',
            'MAGENTA'   : '\033[95m',
            'CYAN'      : '\033[96m',
            'WHITE'     : '\033[97m',
            'BOLD'      : '\033[1m',
            'FAINT'     : '\033[2m',
            'ITALIC'    : '\033[3m',
            'UNDERLINE' : '\033[4m',
            'BLINK'     : '\033[5m',
            'NEGATIVE'  : '\033[7m',
            'STRIKEOUT' : '\033[9m',
            'DEFAULT'   : '\033[0m'
        }
        self.console_color_filters = {}
        self.endl = os.linesep
        self.logfile = ''
        self.dblspace = False
        self.linetmpl = linetmpl
        self.tstmpl = tstmpl
        if reldir == '.':
            self.reldir = os.getcwd()
        else:
            self.reldir = reldir

    ''' Adds a single filter to colorize text
        @param [in] f   - Case insensitive filter string,
                          values can be any of
                            black, red, green, yellow, blue,
                            magenta, cyan, white, bold, faint,
                            italic, underline, blink, strikeout

        Example:
        @begincode

            # Color all strings containing 'error' red
            addLogFilter("error:red")

        @endcode
    '''
    def addLogFilter(self, f):
        p = f.split(':')
        if 1 < len(p):
            self.console_color_filters[p[0]] = p[1:]

    ''' Adds a list of filters to colorize text
        @param [in] f   - Comma separated case insensitive filter strings
                          values can be any of
                            black, red, green, yellow, blue,
                            magenta, cyan, white, bold, faint,
                            italic, underline, blink, strikeout

        Example:
        @begincode

            # Color all strings containing 'error' red, 'warning' yellow,
            # Texts containing 'info' will blink
            addLogFilter("error:red,warning:yellow,info:blink")

        @endcode
    '''
    def addLogFilters(self, f):
        p = f.split(',')
        if p:
            for v in p:
                self.addLogFilter(v)

    ''' Returns the active filter strings
    '''
    def getLogFilters(self):
        return self.console_color_filters

    ''' Sets a log file name
        @param [in] fname   - File in which to write logs
    '''
    def setLogFile(self, fname):
        self.logfile = fname

    ''' Enable to add double spacing to log output
    '''
    def setDoubleSpace(self, enable):
        self.dblspace = enable

    ''' Internal log function allow the specification of the logging depth
        @param [in] st      - Stack depth
        @param [in] args    - Log message arguments to format
    '''
    def _Log(self, st, *args):

        def formatStr(s):

            if isinstance(s, Exception):
                try:
                    tb = traceback.TracebackException.from_exception(s)
                    st = tb._str
                    if not st:
                        st = str(s)
                    st += self.endl
                    for d in range(len(tb.stack)-1, -1, -1):
                        filename = os.path.basename(str(tb.stack[d][0]))
                        lineno = str(tb.stack[d][1])
                        fname = str(tb.stack[d][2])
                        line = str(tb.stack[d][3])
                        st += " > %s(%s)::%s() %s%s" % (filename, lineno, fname, line, self.endl)
                    return "[EXCEPTION] " + st
                except Exception as e:
                    return str("[EXCEPTION]" + traceback.format_exc())

            return str(s)

        # Concat args
        if 1 >= len(args):
            s = formatStr(*args)
        else:
            s = ''
            for a in args:
                if 0 < len(s):
                    if ' ' < s[len(s)-1]:
                        s += ' '
                s += formatStr(a)

        # Show file/function/line
        fi = inspect.getframeinfo(inspect.stack()[st][0])

        full = fi.filename
        path = os.path.dirname(full)

        if self.reldir:
            if '-' == self.reldir:
                filename = os.path.basename(fi.filename)
            else:
                usefull = False
                try:
                    if full.split('/')[1] != self.reldir.split('/')[1]:
                        usefull = True
                except Exception as e:
                    usefull = False

                if usefull:
                    filename = os.path.abspath(fi.filename)
                else:
                    filename = "./" + os.path.relpath(full, self.reldir)
        else:
            filename = os.path.abspath(fi.filename)

        # Timestamp
        if self.tstmpl:
            ts = datetime.datetime.now().strftime(self.tstmpl)
        else:
            ts = ''

        # Build template
        if self.linetmpl:
            ls = (self.linetmpl.replace('<<ts>>', ts)
                               .replace('<<file>>', filename)
                               .replace('<<line>>', str(fi.lineno))
                               .replace('<<function>>', str(fi.function))
                )
        else:
            ls = f'[{ts}] {filename}({fi.lineno}): '

        s = str(s)

        # Apply color filters
        beg = ''
        end = ''
        if sys.stdout.isatty():
            try:
                for k,v in self.console_color_filters.items():
                    if 0 <= s.lower().find(k.lower()) or 0 <= ls.lower().find(k.lower()):
                        for c in v:
                            c = c.upper()
                            if 'BLOCK' == c:
                                return
                            elif c in self.console_colors:
                                beg += self.console_colors[c]
                                if not end:
                                    end = self.console_colors['DEFAULT']

            except Exception as e:
                print(e)
                beg = ''
                end = ''

        # Context color
        sctx = ''
        ectx = ''
        if sys.stdout.isatty():
            sctx = self.console_colors['BLUE'] + self.console_colors['FAINT']
            ectx = self.console_colors['DEFAULT']

        # End of line
        endl = self.endl if self.dblspace else ''

        # Print the string
        print(sctx + ls + ectx + beg + s + end + endl)
        sys.stdout.flush()

        # Write to log file if needed
        if self.logfile:
            try:
                with open(self.logfile, "a") as f:
                    f.write(ls + s + self.endl + endl)
                    f.close()
            except Exception as e:
                pass

    ''' Log function
        @param [in] args    - Log message arguments to format
    '''
    def __call__(self, *args):
        self._Log(2, *args)

    ''' Output status string

        This function will output the specified string,
        forced to the specified length, and without a crlf

        @param [in] s   - String to output
        @param [in] mx  - Output string length
    '''
    def showStatus(s, mx=70):
        print("\r" + s.ljust(mx, ' '), end='')
        sys.stdout.flush()

''' Global logging object
'''
log = Logging()
Log = log


''' Plots an array
    @param [in] a       - Array data to plot
    @param [in] fn      - Optional function for retrieving data elements
    @param [in] scalex  - True to scale values to the x axis
    @param [in] scaley  - True to scale values to the y axis
    @param [in] height  - Height of the output plot
    @param [in] width   - Width of the output plot
    @param [in] plot    - Character to use to plot the data
    @param [in] miny    - Minimum Y axis value
    @param [in] maxy    - Maximum Y axis value
    @param [in] marginy - Y axis top and bottom margin
'''
def plotArray(a, fn = None, scalex = True, scaley = True, height = 12, width = 70,
              plot='.', miny = 0, maxy = 100, marginy = 1):

    w = width
    h = height
    m = [[" " for x in range(0, w)] for y in range(0, h)]

    # Get values
    l = len(a)
    v = a if not fn else [fn(x) for x in a]

    # Are we scaling the y axis?
    if scaley:
        miny = min(v) - marginy
        maxy = max(v) + marginy
    rg = maxy - miny
    if 0 == rg:
        rg = 1

    x = 0
    xa = 0
    i = 0
    for i in range(0, l):

        # New y value
        y = (v[i]-miny) * h / rg
        y = int(y)

        # Update x pos
        while xa >= l:
            xa -= l
            x += 1

        if x >= w:
            break

        # Incremental division
        xa += w if scalex else l

        # Limit and choose char to plot
        pt = plot
        if y < 0:
            y = 0
            pt = '_'
        if y >= h:
            y = h - 1
            pt = '^'

        # Plot character
        m[h - y - 1][x] = pt


    # How wide is the y gutter
    j = max([len(str(int(miny))), len(str(int(maxy)))])

    y = h - 1
    pl = None
    ret = ''
    for r in m:
        py = miny+((y+1) * rg / h)
        py = int(py - (1 if 0 > py else 0))
        py = str(py).rjust(j, ' ')
        sy = '  ' if pl == py else py
        pl = py
        ret += "%s : %s" % (sy, ''.join(r)) + "\n"
        y -= 1

    ret += ' ' + (' '*j) + ('-' * (w + 2)) + "\n"
    ret += (' '*j) + '   ' + ''.join([(str((x+1)*10).rjust(9, ' ')+'^') for x in range(0, int(w/10))]) + "\n"

    return ret

''' Returns a string listing object attributes and their type
    @param [in] o   - Object to iterate
'''
def listObjectAttributes(o):
    s = ''
    for a in dir(o):
        s += "%s<%s>%s" % (a, type(getattr(o, a)).__name__, os.linesep)
    return s

''' Returns a formated string of the specified time interval
    @param [in] t   - Time interval in seconds
    @param [in] fmt - Format string
                        $s  - Seconds
                        $S  - Seconds with leading zero
                        $m  - Minutes
                        $M  - Minutes with leading zero
                        $h  - Hours
                        $H  - Hours with leading zero
                        $d  - Days
                        $D  - Days with leading zero
                        $y  - Years
                        $Y  - Years with leading zero
                        $f  - Decimal
                        $F  - Decimal with trailing zeros
                        $+_ - Show full value

    @param [in] dec - Number of decimal digits to include

    @begincode

        print(formatInterval())

    @encode
'''
def formatInterval(t, fmt="$+H:$M:$S", dec=3):

    rep = {
        "$f":   lambda t: ('{0:.%sf}'%dec).format(t-int(t))[2:].rstrip('0'),
        "$F":   lambda t: ('{0:.%sf}'%dec).format(t-int(t))[2:].ljust(dec, '0'),
        "$s":   lambda t: str(int(t) % 60),
        "$+s":  lambda t: str(int(t)),
        "$S":   lambda t: str(int(t) % 60).rjust(2,'0'),
        "$+S":  lambda t: str(int(t)).rjust(2,'0'),
        "$m":   lambda t: str(int(t / 60) % 60),
        "$+m":  lambda t: str(int(t / 60)),
        "$M":   lambda t: str(int(t / 60) % 60).rjust(2,'0'),
        "$+M":  lambda t: str(int(t / 60)).rjust(2,'0'),
        "$h":   lambda t: str(int(t / 60 / 60) % 24),
        "$+h":  lambda t: str(int(t / 60 / 60)),
        "$H":   lambda t: str(int(t / 60 / 60) % 24).rjust(2,'0'),
        "$+H":  lambda t: str(int(t / 60 / 60)).rjust(2,'0'),
        "$d":   lambda t: str(int(t / 24 / 60 / 60) % 365),
        "$+d":  lambda t: str(int(t / 24 / 60 / 60)),
        "$D":   lambda t: str(int(t / 24 / 60 / 60) % 365).rjust(3,'0'),
        "$+D":  lambda t: str(int(t / 24 / 60 / 60)).rjust(3,'0'),
        "$y":   lambda t: str(int(t / 365 / 24 / 60 / 60)),
        "$Y":   lambda t: str(int(t / 365 / 24 / 60 / 60)).rjust(2,'0'),
    }

    for k,v in rep.items():
        if 0 <= fmt.find(k):
            fmt = fmt.replace(k, v(t))

    return fmt
