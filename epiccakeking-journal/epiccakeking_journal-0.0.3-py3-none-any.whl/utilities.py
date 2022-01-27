import string

from gi.repository import Gtk
from pkg_resources import resource_string

letters = set(string.ascii_letters)


def strip_non_letters(s):
    for start, c in enumerate(s):
        if c in letters:
            break
    for end in range(len(s) - 1, start - 1, -1):
        if s[end] in letters:
            end += 1
            break
    return s[start:end]


def templated(c):
    return Gtk.Template(string=resource_string(__name__, f'ui/{c.__name__}.ui'))(c)
