#!/usr/bin/env python3
import argparse
import re
from six import add_metaclass


class ValidateArgRegex():
    """
    Supports checking if arg matches install, domain, order_id, or IPv6/IPv4 pattern
    """

    patterns = {
        'domain': re.compile(r'^([*]\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    }

    def __init__(self, argtype):
        if argtype not in self.patterns:
            raise KeyError('{} is not a supported argument pattern, choose from:'
                           ' {}'.format(argtype, ','.join(self.patterns)))
        self._argtype = argtype
        self._pattern = self.patterns[argtype]

    def __call__(self, value):
        if not self._pattern.match(value):
            raise argparse.ArgumentTypeError(
                "'{}' is not a valid argument - does not match {} pattern".format(value, self._argtype))
        return value


class Colors(type):
    """
    Metaclass responsible for getting colors and setting new colors.
    You probably want to use Ctext instead of this.
    """
    colors = {
        'default': '\033[0m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'grey': '\033[90m',
        'cyan': '\033[96m',
        'black': '\033[90m',
        'green': '\033[92m',
        'white': '\033[97m',
        'yellow': '\033[93m',
        'magenta': '\033[95m'
    }

    @classmethod
    def __dir__(mcs):
        return mcs.colors.keys()

    @classmethod
    def __getattr__(mcs, color):
        if color not in mcs.colors:
            raise AttributeError('"{0}" is not available, '
                                 'try one of the following: {1}'.format(color, mcs.colors.keys()))

        return Colorizer(color)

    @classmethod
    def __setattr__(mcs, color, value):
        mcs.colors[color] = value

    __getitem__ = __getattr__
    __setitem__ = __setattr__


class Colorizer(object):
    """
    Colorize text.
    You probably want to use Ctext instead of this.
    """
    def __init__(self, color):
        self.color = color

    def __call__(self, text):
        """Return colorized text, end with "default" to prevent color bleed"""
        return '{}{}{}'.format(Colors.colors[self.color], text, Colors.colors['default'])

    def __str__(self):
        return self.__call__(self.color)

    def __repr__(self):
        return self(self.__class__.__name__)

    def __add__(self, obj):
        return '{}{}'.format(Colors.colors[self.color], obj)

    def __radd__(self, obj):
        return '{}{}'.format(obj, Colors.colors[self.color])


@add_metaclass(Colors)
class Ctext:
    """
    Generate colored text strings.

    # Standard usage:
    print(Ctext.blue('this text is blue'))
    print(Ctext['blue']('this text is also blue'))

    # Multiple colors:
    print(Ctext.blue + 'blue text' + Ctext.red + ' now red' + Ctext.default)

    # Setting a custom color
    Ctext.orange = u'\u001b[38;5;202m'
    print(Ctext.orange('this text is orange'))
    """
