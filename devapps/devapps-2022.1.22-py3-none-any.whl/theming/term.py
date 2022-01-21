#!/usr/bin/env python
"""
Ansi Escape Tools for Terminal Output

"""
from __future__ import absolute_import, division, print_function

import os
import sys
import time
from collections import OrderedDict
from functools import partial

from theming.unicode_chars import blocks

# https://misc.flogisoft.com/bash/tip_colors_and_formatting


if sys.version_info[0] > 2:
    char = chr
else:
    char = lambda nr: unichr(nr).encode('utf-8')

envget = os.environ.get


RESET = '\x1b[0m'
BRIGHT = '\x1b[1m'
DIM = '\x1b[2m'


class Theme:
    """
    Basic *Semantic* Highlighting Functions.
    Because it makes no sense to hardcode specific colors but the *meaning* of
    something to be shown.

    Offering Appropriate Coloring of Output for:
    - I: Important
    - M: Marked Up
    - L: Low Intensity
    - D: Dimmed Away
    - R: Red (Error)
    - G: Green (OK)

    The color codes are taken from the environ if defined, allowing for
    consistent theming with other tools.
    E.g. echo -e "${M}Big$R Error" equals
         print(M('Big'), R('Error'))

    We use 256 colors - if you have an 8 color term, then detect it on the
    # parent process and overrite these by exporting e.g. `export R="\\e[1;34m"`
    """

    # fmt:off
    I = [11, 'Important', 'Titles, H1, New contexts']
    G = [2, 'Green', 'OK, H2, Success']
    M = [1, 'Marked UP', 'Sub Titles, H3, Important values in dicts']
    R = [124, 'Red', 'Alarm, Error, Warning, Failed']
    L = [5, 'Low Intensity', 'Debug Output, Code, Shell output']
    D = [5, 'Dimm Away', 'Very Unimportant, No Distraction']
    bold = 'MIR'
    dimm = 'D'
    ignore_env = False
    force_colors = False  # even if no tty
    disabled = False  # no coloring
    show_order = 'IGMRLD'
    name = 'Default'
    # fmt:on
    #    colorful
    #    fruity
    #    monokai
    #    paraiso_light
    #    rrt
    #    trac
    #    abap
    #    autumn
    #    default
    #    igor
    #    murphy
    #    pastie
    #    sas
    #    vim
    #    algol
    #    borland
    #    emacs
    #    lovelace
    #    native
    #    perldoc
    #    stata
    #    vs
    #    algol_nu: cool
    #    bw
    #    friendly
    #    manni
    #    paraiso_dark
    #    rainbow_dash
    #    paraiso-dark : good
    pygments_style = 'paraiso-dark'

    # can't derive the termwidth in process, this is expensive:
    default_width = 80
    _cur_width = None
    width_check_secs = 2
    _cur_width_last_check = 0
    _cur_width_check_failing = False

    @classmethod
    def output_shell_exports():
        """prints a sourceable set of export statements so that a theme
        defined in python can be sourced
        (i.e. reversing the definition order, we normally use the shell theme)
        """
        raise NotImplemented

    @classmethod
    def attrs(cls):
        """Other attributes of the Theme"""
        c = cls.color_keys()
        r = {'name': cls.__name__}
        for k in dir(cls):
            if k.startswith('_'):
                continue
            v = getattr(cls, k)
            if isinstance(v, (str, int, bool, float)):
                r[k] = v
        return r

    @classmethod
    def width(cls):
        if cls._cur_width is None and cls._cur_width_last_check > 0:
            return cls.default_width
        if cls._cur_width_check_failing:
            # might have been provided newly with new theme:
            # -> ignore current
            return cls.default_width
        now = time.time()
        if now - cls._cur_width_last_check < cls.width_check_secs:
            return cls._cur_width or cls.default_width
        c = os.popen('tput cols 2>/dev/null').read()
        cls._cur_width_last_check = now
        if not c:
            # thats it, we won't check again:
            cls._cur_width_check_failing = True
            return cls.default_width
        c = cls._cur_width = int(c)
        return c

    @classmethod
    def line(cls, col='L'):
        cols = cls.width()
        return cls.colorize(col)('_' * cols)

    @classmethod
    def colorize(cls, col):
        return getattr(cls, col.lower())

    @classmethod
    def color_keys(cls):
        r = []
        s = cls.show_order
        while s:
            c, s = s[0], s[1:]
            r.append(c) if hasattr(cls, c) else 0
        [r.append(c) for c in dir(cls) if not c in r and cls.is_col_key(c)]
        return r

    @classmethod
    def colorizers(cls):
        """ordered list of colorizer functions"""
        return [cls.colorize(k) for k in cls.color_keys()]

    @staticmethod
    def is_col_key(k):
        return len(k) < 3 and k == k.upper()

    @classmethod
    def setup(cls, **alt_theme):
        """
        We allow to provide new color shortcuts as well but they have to obey
        the convention to be < 3 characters and upper case
        Color names and tags can be given by providing a list and not the code.
        E.g. setup(I=123, X=[333, 'My Title', 'Foo, Bar'])
        """

        def col_def(k, v, dt='Unnamed %s Color', tt='<Untagged>'):
            if not Theme.is_col_key(k):
                return v
            if isinstance(v, int):
                return [v, dt % v, tt]
            # add not given infos:
            v.append(0) if len(v) == 0 else 0
            v.append(dt % v[0]) if len(v) == 1 else 0
            v.append(tt) if len(v) == 2 else 0
            return v[:3]

        [setattr(cls, k, col_def(k, v)) for k, v in alt_theme.items()]
        cols = cls.color_keys()
        [setattr(cls, c.lower(), cls._colorizer(c)) for c in cols]

    @classmethod
    def _colorizer(cls, key, have_tty=sys.stdout.isatty()):
        """returns the callable which colorizes a string"""
        do_cols = have_tty or cls.force_colors
        if cls.disabled:
            do_cols = False

        dflt = getattr(cls, key, [''])[0]

        def colorize(s, into):
            return into % s

        # bold / dimm
        b = '1;' if key in cls.bold else '2;' if key in cls.dimm else ''

        e, t = '', '%s'
        if do_cols:
            if not cls.ignore_env:
                # TODO perf?:
                e = envget(key, '')
                if e.isdigit():
                    e = '1;38;5;%sm' % e
                elif e:
                    e = e.split('[', 1)[1]
            if not e and dflt:
                e = b + '38;5;%sm' % dflt
            if e:
                # turns out to be the safest
                t = ''.join(('\x1b[', e, '%s', RESET))

        return partial(colorize, into=t)

    @classmethod
    def color_prefixes(cls):
        """returns just the prefix w/o the reset at the end"""
        d = lambda k: getattr(cls, k.lower())('XX').split('XX')[0]
        return dict([(k, d(k)) for k in cls.color_keys()])

    @classmethod
    def definition(cls, key):
        d = getattr(cls, key)
        m = {
            'title': d[1],
            'code': d[0],
            'tags': [i.strip() for i in d[2].split(',')],
            'func': getattr(cls, key.lower()),
        }
        return m

    @classmethod
    def print(cls):
        """
        Print the Theme.
        #TODO Not very convincing at the moment, make a bit fancier
        """
        p = print
        kw = cls.attrs()
        p(cls.line('I'))
        p(I('Theme %s' % kw.pop('name')))
        p(cls.line('I'))
        [p('- %s: %s' % (k.ljust(20), M(v))) for k, v in kw.items()]

        p(cls.line())

        for c in cls.color_keys():
            d = cls.definition(c)
            f = d['func']
            p(I(c), '[%s]' % d['code'], d['title'])
            p(cls.line())
            [p('- %s' % f(i)) for i in d['tags']]
            p('')
        [
            p(*l)
            for l in (
                ('',),
                (cls.line('I'),),
                ('Testoutput',),
                ('I: ', I('Title')),
                ('M: ', M('Sub Title')),
                ('R: ', 'This is an ', R('Error')),
                ('G: ', 'But %s worked well (G)' % G('that')),
                ('L: ', L('[debug]'), 'output.....'),
                ('D: ', D('Totally uninteresting')),
            )
        ]


Theme.setup()
# Its colorizer functions are now set - e.g. Theme.r('error')
# they HAVE to be supershort to not distract the reader of code:
M = Theme.m
I = Theme.i
L = Theme.l
R = Theme.r
G = Theme.g
D = Theme.d


# This is to format a column e.g. with Thread Number
# distinctively:

_bnames = 'arrows', 'geometric_shapes', 'box_drawing'
_chars = list(range(48, 232))  # number, letters
[_chars.extend(list(getattr(blocks, k))) for k in _bnames]
# we go down the colums here
# https://misc.flogisoft.com/bash/tip_colors_and_formatting
# to get visually differing colors. hsl would be better
alternating_colors = [col * 10 + row for row in range(0, 10) for col in range(0, 25)]


class Cell:
    """formats one cell"""

    @staticmethod
    def unique(nr, _lchars=len(_chars), _lcols=len(alternating_colors) - 1):
        """
        Returns a visually unique cell in the terminal
        combining bg and fg colors plus symbols in black

        The passed nr argument must be int, and, well, unique for the same
        output
        """
        try:
            symb = char(_chars[nr % _lchars])
        except:
            symb, nr = nr, hash(nr)
        return Cell.colorize(symb, nr)

    @staticmethod
    def colorize(symb, nr, _lcols=len(alternating_colors) - 1):
        bg = alternating_colors[nr % _lcols]
        return '\x1b[1;38;5;201;2;48;5;%sm%s%s' % (bg, symb, RESET)


def unique(s):
    return Cell.unique(s)


def unique_str(s):
    return Cell.colorize(s, nr=hash(s))


def structlog_style():
    """for structlog init w/o colorama (e.g. ax.rx)"""
    #  structlog/dev.py
    C = Theme.color_prefixes()

    # fmt:off
    def style(orig_style):
        class S(orig_style):
            level_critical = level_exception = level_error = C['R']
            level_warn  = C['I']
            level_info  = C['M']
            level_debug = C['L']
            timestamp   = C['D']
            logger_name = C['L']
            kv_key      = C['M']
            kv_value    = C['I']
            reset       = RESET

        return S

    ls = {
        'critical'  : C['R'],
        'exception' : C['R'],
        'error'     : C['R'],
        'warn'      : C['I'],
        'warning'   : C['R'],
        'info'      : C['G'],
        'debug'     : C['L'],
        'notset'    : '',
    }
    # fmt:on

    return style, ls


# old or new version? we keep or now
# def structlog_style(colors=True):
#    '''for structlog init w/o colorama (e.g. ax.rx)'''
#    #  structlog/dev.py
#    C = Theme.color_prefixes()
#    # fmt:off
#    ls = {
#             "critical"  : C['R']
#           , "exception" : C['R']
#           , "error"     : C['R']
#           , "warn"      : C['I']
#           , "warning"   : C['R']
#           , "info"      : C['G']
#           , "debug"     : C['L']
#           }
#    ks = {
#             "timestamp" : C['D']
#           , "kv_key"    : C['L']
#           , "kv_value"  : C['M']
#           , "logger"    : C['M']
#           , "meta"      : C['M']
#           , "event"     : ''
#           , "notset"    : ''
#           }
#    # fmt:on
#    if not colors:
#        ls = dict((k, '') for k in ls)
#        ks = dict((k, '') for k in ks)
#
#    longest_level = len(max(ls, key=lambda l: len(l)))
#    justed_levels = dict((k, k.ljust(longest_level)) for k in ls)
#    return {
#        'level_styles': ls,
#        'longest_level': longest_level,
#        'key_styles': ks,
#        'justed_levels': justed_levels,
#    }
#

# -------------------------------------------------------- oldish 8 color stuff
# TODO gk: check if we can ditch all below:
class ShellColors:
    K = '0;30'
    B = '0;34'
    G = '0;32'
    C = '0;36'
    R = '0;31'
    P = '0;35'
    O = '0;33'
    Y = '1;33'
    W = '1;37'
    # bold:
    BK = '1;30'
    BW = '0;37'
    BB = '1;34'
    BG = '1;32'
    BC = '1;36'
    BR = '1;31'
    BP = '1;35'
    N = '0'
    # distingishable cols, to count up numbers:
    cols = [
        'BG',
        'BB',
        'BW',
        'BC',
        'BR',
        'BP',
        'BK',
        'G',
        'P',
        'B',
        'C',
        'R',
        'P',
        'O',
        'Y',
        'W',
    ]


def colors():
    ret = OrderedDict()
    for c in ShellColors.cols:
        ret[c] = getattr(ShellColors, c)
    return ret


def esc_code(fg, bg=None, for_ps1=0):
    l = len(ShellColors.cols)
    if str(fg).isdigit():
        fg = ShellColors.cols[int(fg) % l]
    fg = '\\033[' + getattr(ShellColors, fg) + 'm'
    if bg is not None:
        if str(bg).isdigit():
            bg = ShellColors.cols[int(bg) % l]
        bg = getattr(ShellColors, bg)
        # no bold for bgs, so no 0; or 1;:
        bg = '\\033[4' + bg[-1] + 'm'
    esc = ''
    end_esc = ''
    if for_ps1:
        esc = '\\['
        end_esc = '\\]'
    ret = esc + fg
    if bg is not None:
        ret += esc + bg
    return ret + end_esc


def colorize(s, fg, bg=None, for_ps1=0):
    ret = '%s%s%s' % (esc_code(fg, bg, for_ps1), s, esc_code('N', bg, for_ps1))
    return ret


def colortable():
    for i in range(1, 256):
        print('%6s' % i, '\x1b[38;5;%smthis is color number %s\x1b[0m' % (i, i))


if __name__ == '__main__':
    colortable()
    print()
    Theme.print()
    print(I('With Environment Ignored'))
    Theme.setup(ignore_env=False)
    Theme.print()
