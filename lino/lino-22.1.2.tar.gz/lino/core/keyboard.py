# -*- coding: UTF-8 -*-
# Copyright 2009-2014 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""
This defines the :class:`Hotkey` class and some keystrokes.

The system is not yet heavily used.

"""
from builtins import object


class Hotkey(object):
    "Represents a combination of keystrokes."
    key = None
    keycode = None
    shift = False
    ctrl = False
    alt = False

    def __init__(self, key=None, **kw):
        if key:
            self.key = key.upper()
            self.keycode = ord(self.key)
        for k, v in list(kw.items()):
            setattr(self, k, v)

        self.__dict__.update(keycode=self.keycode, shift=self.shift,
            key = self.key, ctrl=self.ctrl, alt=self.alt)

# ExtJS src/core/EventManager-more.js
RETURN = Hotkey(keycode=13)
ESCAPE = Hotkey(keycode=27)
PAGE_UP = Hotkey(keycode=33)
PAGE_DOWN = Hotkey(keycode=34)
INSERT = Hotkey(keycode=44)
DELETE = Hotkey(keycode=46)
